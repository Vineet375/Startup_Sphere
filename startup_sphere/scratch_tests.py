
    def test_notification_signals(self):
        from .models import Notification
        
        # Test Mentor Assigned
        self.startup1.mentor = None
        self.startup1.save()
        Notification.objects.all().delete() # clear any old ones
        
        self.startup1.mentor = self.mentor1
        self.startup1.save()
        self.assertTrue(Notification.objects.filter(recipient=self.founder1, notification_type='mentor_assigned').exists())
        self.assertTrue(Notification.objects.filter(recipient=self.mentor1, notification_type='mentor_assigned').exists())
        
        # Test Mentor Changed
        Notification.objects.all().delete()
        self.startup1.mentor = self.mentor2
        self.startup1.save()
        self.assertTrue(Notification.objects.filter(recipient=self.founder1, notification_type='mentor_changed').exists())
        self.assertTrue(Notification.objects.filter(recipient=self.mentor2, notification_type='mentor_changed').exists())
        self.assertFalse(Notification.objects.filter(recipient=self.mentor1, notification_type='mentor_changed').exists())

        # Test Mentor Removed (should safely do nothing to notifications)
        Notification.objects.all().delete()
        self.startup1.mentor = None
        self.startup1.save()
        self.assertEqual(Notification.objects.count(), 0)

        # Test Startup Status Changed
        self.startup1.incubation_status = 'incubating'
        self.startup1.save()
        self.assertTrue(Notification.objects.filter(recipient=self.founder1, notification_type='startup_status_changed').exists())

        # Saving without changes creates no notifications
        count_before = Notification.objects.count()
        self.startup1.save()
        self.assertEqual(Notification.objects.count(), count_before)

    def test_notification_workflows(self):
        from .models import Notification
        Notification.objects.all().delete()
        
        # Idea Submitted
        self.client.login(username='founder1', password='password123')
        self.client.post(reverse('incubator:idea_submit', args=[self.idea1.id]))
        self.assertTrue(Notification.objects.filter(recipient=self.mentor1, notification_type='idea_submitted').exists())
        
        # Under Review
        self.client.login(username='mentor1', password='password123')
        self.client.post(reverse('incubator:mark_under_review', args=[self.idea1.id]))
        self.assertTrue(Notification.objects.filter(recipient=self.founder1, notification_type='idea_under_review').exists())
        
        # Feedback Submitted
        self.client.post(reverse('incubator:add_feedback', args=[self.idea1.id]), {'content': 'Feedback'})
        self.assertTrue(Notification.objects.filter(recipient=self.founder1, notification_type='feedback_received').exists())
        
        # Milestone Created
        self.client.post(reverse('incubator:milestone_create', args=[self.startup1.id]), {
            'title': 'Test MS',
            'status': 'pending',
            'target_date': '2026-10-10'
        })
        self.assertTrue(Notification.objects.filter(recipient=self.founder1, notification_type='milestone_created').exists())
        ms = Milestone.objects.get(title='Test MS')
        
        # Milestone Completed
        self.client.login(username='founder1', password='password123')
        self.client.post(reverse('incubator:milestone_update', args=[ms.id]), {
            'title': 'Test MS',
            'status': 'completed',
            'target_date': '2026-10-10'
        })
        self.assertTrue(Notification.objects.filter(recipient=self.mentor1, notification_type='milestone_completed').exists())

    def test_notification_views_and_security(self):
        from .models import Notification
        Notification.objects.all().delete()
        
        # Create a mock notification for founder1
        notif = Notification.objects.create(
            recipient=self.founder1,
            title="Test",
            message="Msg",
            notification_type="startup_status_changed",
            is_read=False
        )
        
        # Founder can view it
        self.client.login(username='founder1', password='password123')
        response = self.client.get(reverse('incubator:notification_list'))
        self.assertEqual(response.status_code, 200)
        
        # GET request to mark read should fail (POST only)
        response = self.client.get(reverse('incubator:notification_mark_read', args=[notif.id]))
        self.assertEqual(response.status_code, 405) # method not allowed
        
        # Another user cannot mark it as read
        self.client.login(username='mentor1', password='password123')
        response = self.client.post(reverse('incubator:notification_mark_read', args=[notif.id]))
        self.assertEqual(response.status_code, 404) # Not found since it filters by recipient=request.user
        
        # Original user marks it as read
        self.client.login(username='founder1', password='password123')
        response = self.client.post(reverse('incubator:notification_mark_read', args=[notif.id]))
        self.assertEqual(response.status_code, 302)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)
        
        # Mark all read
        Notification.objects.create(recipient=self.founder1, title="Test 2", message="Msg 2", notification_type="startup_status_changed")
        Notification.objects.create(recipient=self.founder1, title="Test 3", message="Msg 3", notification_type="startup_status_changed")
        self.client.post(reverse('incubator:notification_mark_all_read'))
        self.assertFalse(Notification.objects.filter(recipient=self.founder1, is_read=False).exists())

