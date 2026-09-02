from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Startup, Idea, Feedback, Milestone

User = get_user_model()

class IncubatorRBACTests(TestCase):
    def setUp(self):
        # Users
        self.founder1 = User.objects.create_user(username='founder1', password='password123', role='founder')
        self.founder2 = User.objects.create_user(username='founder2', password='password123', role='founder')
        self.mentor1 = User.objects.create_user(username='mentor1', password='password123', role='mentor')
        self.mentor2 = User.objects.create_user(username='mentor2', password='password123', role='mentor')
        
        # Startups
        self.startup1 = Startup.objects.create(founder=self.founder1, mentor=self.mentor1, name='Startup 1')
        self.startup2 = Startup.objects.create(founder=self.founder2, mentor=self.mentor2, name='Startup 2')
        
        # Ideas
        self.idea1 = Idea.objects.create(startup=self.startup1, creator=self.founder1, title='Idea 1', status='submitted')
        self.idea2 = Idea.objects.create(startup=self.startup2, creator=self.founder2, title='Idea 2', status='submitted')

    def test_founder_ownership_access(self):
        self.client.login(username='founder1', password='password123')
        
        # Can access own startup detail
        response = self.client.get(reverse('incubator:startup_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Startup 1')
        
        # Can access own idea detail
        response = self.client.get(reverse('incubator:idea_detail', args=[self.idea1.id]))
        self.assertEqual(response.status_code, 200)

    def test_founder_cannot_access_another_founder_startup_or_idea(self):
        self.client.login(username='founder1', password='password123')
        
        # Cannot access another founder's startup via ID url
        response = self.client.get(reverse('incubator:startup_detail_id', args=[self.startup2.id]))
        self.assertEqual(response.status_code, 403)
        
        # Cannot access another founder's idea
        response = self.client.get(reverse('incubator:idea_detail', args=[self.idea2.id]))
        self.assertEqual(response.status_code, 403)

    def test_mentor_access_assigned_startup_and_idea(self):
        self.client.login(username='mentor1', password='password123')
        
        # Can access assigned startup
        response = self.client.get(reverse('incubator:startup_detail_id', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 200)
        
        # Can access assigned idea
        response = self.client.get(reverse('incubator:idea_detail', args=[self.idea1.id]))
        self.assertEqual(response.status_code, 200)

    def test_mentor_cannot_access_unassigned_startup_and_idea(self):
        self.client.login(username='mentor1', password='password123')
        
        # Cannot access unassigned startup
        response = self.client.get(reverse('incubator:startup_detail_id', args=[self.startup2.id]))
        self.assertEqual(response.status_code, 403)
        
        # Cannot access unassigned idea
        response = self.client.get(reverse('incubator:idea_detail', args=[self.idea2.id]))
        self.assertEqual(response.status_code, 403)

    def test_mentor_can_submit_feedback_for_assigned_idea(self):
        self.client.login(username='mentor1', password='password123')
        
        response = self.client.post(reverse('incubator:add_feedback', args=[self.idea1.id]), {
            'content': 'Great idea!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Feedback.objects.filter(idea=self.idea1, mentor=self.mentor1).exists())

    def test_unauthorized_feedback_submission_rejected(self):
        self.client.login(username='mentor2', password='password123')
        
        # Mentor 2 cannot submit feedback for Idea 1
        response = self.client.post(reverse('incubator:add_feedback', args=[self.idea1.id]), {
            'content': 'Nice try!'
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Feedback.objects.filter(idea=self.idea1, mentor=self.mentor2).exists())
        
        # Founder cannot submit feedback
        self.client.login(username='founder1', password='password123')
        response = self.client.post(reverse('incubator:add_feedback', args=[self.idea1.id]), {
            'content': 'My own feedback'
        })
        self.assertEqual(response.status_code, 403)

    def test_founder_can_view_feedback(self):
        # Create feedback
        Feedback.objects.create(idea=self.idea1, mentor=self.mentor1, content='Important feedback')
        
        self.client.login(username='founder1', password='password123')
        response = self.client.get(reverse('incubator:idea_detail', args=[self.idea1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Important feedback')

    def test_milestone_permissions(self):
        # Mentor creates milestone
        self.client.login(username='mentor1', password='password123')
        response = self.client.post(reverse('incubator:milestone_create', args=[self.startup1.id]), {
            'title': 'Milestone 1',
            'status': 'pending'
        })
        self.assertEqual(response.status_code, 302)
        milestone = Milestone.objects.get(startup=self.startup1, title='Milestone 1')
        
        # Mentor updates milestone
        response = self.client.post(reverse('incubator:milestone_update', args=[milestone.id]), {
            'title': 'Milestone 1 Updated',
            'status': 'in_progress'
        })
        self.assertEqual(response.status_code, 302)
        milestone.refresh_from_db()
        self.assertEqual(milestone.title, 'Milestone 1 Updated')
        
        # Founder updates status
        self.client.login(username='founder1', password='password123')
        response = self.client.post(reverse('incubator:milestone_update', args=[milestone.id]), {
            'title': 'Ignored Title Change',
            'status': 'completed'
        })
        self.assertEqual(response.status_code, 302)
        milestone.refresh_from_db()
        self.assertEqual(milestone.status, 'completed')
        # Title should not change because founder can only update status
        self.assertEqual(milestone.title, 'Milestone 1 Updated')
        
        # Unauthorized deletion
        self.client.login(username='mentor2', password='password123')
        response = self.client.post(reverse('incubator:milestone_delete', args=[milestone.id]))
        self.assertEqual(response.status_code, 403)
        
        # Mentor deletes milestone
        self.client.login(username='mentor1', password='password123')
        response = self.client.post(reverse('incubator:milestone_delete', args=[milestone.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Milestone.objects.filter(id=milestone.id).exists())

    def test_basic_idea_status_transitions(self):
        self.client.login(username='mentor1', password='password123')
        
        # Mentor marks idea as under review
        response = self.client.post(reverse('incubator:mark_under_review', args=[self.idea1.id]))
        self.assertEqual(response.status_code, 302)
        self.idea1.refresh_from_db()
        self.assertEqual(self.idea1.status, 'under_review')
        
        # Unauthorized transition
        self.client.login(username='mentor2', password='password123')
        response = self.client.post(reverse('incubator:mark_under_review', args=[self.idea1.id]))
        self.assertEqual(response.status_code, 403)


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
        self.idea1.status = 'draft'
        self.idea1.save()
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

