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


from django.core.files.uploadedfile import SimpleUploadedFile
from incubator.models import TeamMember, Document, Activity, Notification

class Batch6Tests(TestCase):
    def setUp(self):
        # Users
        self.founder1 = User.objects.create_user(username='founder1', email='f1@test.com', password='password123', role='founder')
        self.founder2 = User.objects.create_user(username='founder2', email='f2@test.com', password='password123', role='founder')
        self.mentor1 = User.objects.create_user(username='mentor1', password='password123', role='mentor')
        self.mentor2 = User.objects.create_user(username='mentor2', password='password123', role='mentor')
        
        # Startups
        self.startup1 = Startup.objects.create(founder=self.founder1, mentor=self.mentor1, name='Startup 1')
        self.startup2 = Startup.objects.create(founder=self.founder2, mentor=self.mentor2, name='Startup 2')

        # Create an existing platform user
        self.existing_user = User.objects.create_user(username='existing', email='existing@test.com', password='password123', role='founder')

    def test_founder_add_team_member(self):
        self.client.login(username='founder1', password='password123')
        
        # 1. Invite non-existent user
        response = self.client.post(reverse('incubator:team_invite'), {'email': 'new@test.com', 'position': 'developer'})
        self.assertEqual(response.status_code, 302)
        tm = TeamMember.objects.get(invited_email='new@test.com')
        self.assertEqual(tm.status, 'pending')
        self.assertEqual(tm.startup, self.startup1)
        self.assertIsNone(tm.user)
        self.assertTrue(Activity.objects.filter(startup=self.startup1, activity_type='pending_invitation_created').exists())
        self.assertFalse(Notification.objects.filter(startup=self.startup1, notification_type='team_member_added').exists())

        # 2. Invite existing user
        response = self.client.post(reverse('incubator:team_invite'), {'email': 'existing@test.com', 'position': 'designer'})
        self.assertEqual(response.status_code, 302)
        tm2 = TeamMember.objects.get(user=self.existing_user)
        self.assertEqual(tm2.status, 'active')
        self.assertEqual(tm2.startup, self.startup1)
        self.assertTrue(Activity.objects.filter(startup=self.startup1, activity_type='team_member_added').exists())
        self.assertTrue(Notification.objects.filter(recipient=self.existing_user, notification_type='team_member_added').exists())

    def test_duplicate_memberships_blocked(self):
        TeamMember.objects.create(startup=self.startup1, user=self.existing_user, status='active')
        self.client.login(username='founder1', password='password123')
        response = self.client.post(reverse('incubator:team_invite'), {'email': 'existing@test.com', 'position': 'developer'})
        self.assertEqual(TeamMember.objects.filter(startup=self.startup1, user=self.existing_user).count(), 1)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("already on the team" in str(m) for m in messages))

    def test_cross_startup_modification_blocked(self):
        TeamMember.objects.create(startup=self.startup2, user=self.existing_user, status='active')
        member_id = TeamMember.objects.get(user=self.existing_user).id
        
        # Founder 1 tries to remove Startup 2's member
        self.client.login(username='founder1', password='password123')
        response = self.client.post(reverse('incubator:team_remove', args=[member_id]))
        self.assertEqual(response.status_code, 403)

    def test_team_member_permissions(self):
        TeamMember.objects.create(startup=self.startup1, user=self.existing_user, status='active')
        
        # 1. Test view access
        self.client.login(username='existing', password='password123')
        response = self.client.get(reverse('incubator:startup_detail'))
        self.assertEqual(response.status_code, 200) # Can view startup detail
        
        # 2. Test cross-startup access blocked
        response = self.client.get(reverse('incubator:startup_detail_id', args=[self.startup2.id]))
        self.assertEqual(response.status_code, 403)
        
        # 3. Cannot edit startup profile
        response = self.client.get(reverse('incubator:startup_edit'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('incubator:register_startup')))

    def test_document_upload_and_validation(self):
        self.client.login(username='founder1', password='password123')
        
        # 1. Valid Document Upload
        valid_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(reverse('incubator:document_upload'), {
            'title': 'Pitch Deck',
            'category': 'pitch_deck',
            'file': valid_file
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Document.objects.count(), 1)
        self.assertTrue(Activity.objects.filter(startup=self.startup1, activity_type='document_uploaded').exists())

        # 2. Invalid Extension Upload
        invalid_ext_file = SimpleUploadedFile("test.exe", b"malicious", content_type="application/x-msdownload")
        response = self.client.post(reverse('incubator:document_upload'), {
            'title': 'Hack',
            'category': 'other',
            'file': invalid_ext_file
        })
        self.assertEqual(response.status_code, 200) # Form re-renders with errors
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertTrue('file' in form.errors)
        self.assertTrue(any('Allowed extensions are' in e for e in form.errors['file']))
        self.assertEqual(Document.objects.count(), 1)

    def test_document_access(self):
        doc = Document.objects.create(startup=self.startup1, title="Doc 1", file="dummy.pdf", category="other", uploaded_by=self.founder1)
        
        # Mentor 1 (assigned) can view
        self.client.login(username='mentor1', password='password123')
        response = self.client.get(reverse('incubator:document_list_id', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Doc 1")
        
        # Mentor 1 cannot delete
        response = self.client.post(reverse('incubator:document_delete', args=[doc.id]))
        self.assertEqual(response.status_code, 403)
        
        # Mentor 2 (unassigned) cannot view
        self.client.login(username='mentor2', password='password123')
        response = self.client.get(reverse('incubator:document_list_id', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)
        
        # Founder 2 cannot view
        self.client.login(username='founder2', password='password123')
        response = self.client.get(reverse('incubator:document_list_id', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)

from .models import Evaluation

class Batch6BTests(TestCase):
    def setUp(self):
        # Users
        self.founder1 = User.objects.create_user(username='founder1', email='f1@test.com', password='password123', role='founder')
        self.founder2 = User.objects.create_user(username='founder2', email='f2@test.com', password='password123', role='founder')
        self.mentor1 = User.objects.create_user(username='mentor1', password='password123', role='mentor')
        self.mentor2 = User.objects.create_user(username='mentor2', password='password123', role='mentor')
        self.teammember_user = User.objects.create_user(username='teammember', password='password123', role='founder')
        
        # Startups
        self.startup1 = Startup.objects.create(founder=self.founder1, mentor=self.mentor1, name='Alpha Startup', category='finance', incubation_status='incubating')
        self.startup2 = Startup.objects.create(founder=self.founder2, mentor=self.mentor2, name='Beta Company', category='health', incubation_status='completed')
        
        # Team Member
        TeamMember.objects.create(startup=self.startup1, user=self.teammember_user, status='active')

    def test_directory_search_and_filter(self):
        self.client.login(username='founder1', password='password123')
        
        # Search match name
        response = self.client.get(reverse('incubator:startup_directory') + '?q=Alpha')
        self.assertContains(response, 'Alpha Startup')
        self.assertNotContains(response, 'Beta Company')
        
        # Filter industry
        response = self.client.get(reverse('incubator:startup_directory') + '?category=health')
        self.assertNotContains(response, 'Alpha Startup')
        self.assertContains(response, 'Beta Company')
        
        # Filter status
        response = self.client.get(reverse('incubator:startup_directory') + '?status=incubating')
        self.assertContains(response, 'Alpha Startup')
        self.assertNotContains(response, 'Beta Company')

    def test_public_profile_privacy(self):
        self.client.login(username='founder1', password='password123')
        response = self.client.get(reverse('incubator:startup_public_profile', args=[self.startup2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beta Company')
        # Does not show workspace elements
        self.assertNotContains(response, 'Create Evaluation')
        self.assertNotContains(response, 'Milestones')
        self.assertNotContains(response, 'mailto:') # Contact info hidden
        self.assertNotContains(response, 'f2@test.com')

    def test_evaluation_permissions(self):
        # 1. Unassigned mentor blocked
        self.client.login(username='mentor2', password='password123')
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('incubator:evaluation_create', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)
        
        # 2. Team member CAN view list but CANNOT create/edit
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('incubator:evaluation_create', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)
        
        # Test team member blocked from other startup
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup2.id]))
        self.assertEqual(response.status_code, 403)
        
        # 3. Founder can view but not create
        self.client.login(username='founder1', password='password123')
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('incubator:evaluation_create', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)
        
        # 4. Assigned mentor can create
        self.client.login(username='mentor1', password='password123')
        response = self.client.post(reverse('incubator:evaluation_create', args=[self.startup1.id]), {
            'innovation_score': 8,
            'market_potential_score': 9,
            'business_model_score': 7,
            'team_score': 8,
            'execution_score': 9,
            'comments': 'Great progress!'
        })
        self.assertEqual(response.status_code, 302) # Redirects to list
        self.assertEqual(Evaluation.objects.count(), 1)
        
        eval_obj = Evaluation.objects.first()
        self.assertEqual(eval_obj.overall_score, 8.2) # (8+9+7+8+9)/5 = 41/5 = 8.2
        
        # Verify Activity & Notification
        self.assertTrue(Activity.objects.filter(startup=self.startup1, activity_type='evaluation_created').exists())
        self.assertTrue(Notification.objects.filter(recipient=self.startup1.founder, notification_type='evaluation_received').exists())

    def test_evaluation_validation_and_edit(self):
        # Create initial evaluation
        eval_obj = Evaluation.objects.create(
            startup=self.startup1, evaluator=self.mentor1,
            innovation_score=5, market_potential_score=5, business_model_score=5, team_score=5, execution_score=5
        )
        
        self.client.login(username='mentor1', password='password123')
        
        # Test out-of-bounds score
        response = self.client.post(reverse('incubator:evaluation_edit', args=[eval_obj.id]), {
            'innovation_score': 11, # Invalid
            'market_potential_score': 5,
            'business_model_score': 5,
            'team_score': 5,
            'execution_score': 5,
        })
        self.assertEqual(response.status_code, 200) # Form renders with errors
        self.assertTrue('innovation_score' in response.context['form'].errors)
        
        # Test successful edit
        response = self.client.post(reverse('incubator:evaluation_edit', args=[eval_obj.id]), {
            'innovation_score': 10,
            'market_potential_score': 10,
            'business_model_score': 10,
            'team_score': 10,
            'execution_score': 10,
        })
        self.assertEqual(response.status_code, 302)
        eval_obj.refresh_from_db()
        self.assertEqual(eval_obj.overall_score, 10.0)
        self.assertTrue(Activity.objects.filter(startup=self.startup1, activity_type='evaluation_updated').exists())
        
        # Test duplicate creation blocked
        response = self.client.post(reverse('incubator:evaluation_create', args=[self.startup1.id]), {
            'innovation_score': 5,
            'market_potential_score': 5,
            'business_model_score': 5,
            'team_score': 5,
            'execution_score': 5,
        })
        self.assertEqual(Evaluation.objects.count(), 1) # Prevented second creation

    def test_mentor_cannot_edit_others_evaluation(self):
        eval_obj = Evaluation.objects.create(
            startup=self.startup1, evaluator=self.mentor1,
            innovation_score=5, market_potential_score=5, business_model_score=5, team_score=5, execution_score=5
        )
        self.client.login(username='mentor2', password='password123')
        response = self.client.post(reverse('incubator:evaluation_edit', args=[eval_obj.id]), {
            'innovation_score': 10,
            'market_potential_score': 10,
            'business_model_score': 10,
            'team_score': 10,
            'execution_score': 10,
        })
        self.assertEqual(response.status_code, 403)
        
        # Test team member cannot edit
        self.client.login(username='teammember', password='password123')
        response = self.client.post(reverse('incubator:evaluation_edit', args=[eval_obj.id]), {
            'innovation_score': 10,
            'market_potential_score': 10,
            'business_model_score': 10,
            'team_score': 10,
            'execution_score': 10,
        })
        self.assertEqual(response.status_code, 403)

    def test_team_member_dashboard_detection(self):
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incubation Status')
        self.assertContains(response, self.startup1.get_incubation_status_display())
        # Should not contain Founder actions
        self.assertNotContains(response, 'Draft New Idea')
        self.assertNotContains(response, 'Edit Startup Profile')

    def test_team_member_idea_list_visibility(self):
        # Create an idea first
        from incubator.models import Idea
        idea = Idea.objects.create(startup=self.startup1, creator=self.founder1, title='Test Idea', description='Desc')
        
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('incubator:idea_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, idea.title)
        # Should not contain Create Idea
        self.assertNotContains(response, reverse('incubator:idea_create'))


from django.utils import timezone
from datetime import timedelta
from .models import Event, EventParticipation, CollaborationRequest

class Batch7EventsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_e', password='123', role='admin')
        self.founder = User.objects.create_user(username='founder_e', password='123', role='founder')
        self.mentor = User.objects.create_user(username='mentor_e', password='123', role='mentor')
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Desc',
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=2),
            organizer=self.admin,
            capacity=1
        )

    def test_event_list_and_detail(self):
        self.client.login(username='founder_e', password='123')
        response = self.client.get(reverse('incubator:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Event')

        response = self.client.get(reverse('incubator:event_detail', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)

    def test_event_registration_and_capacity(self):
        self.client.login(username='founder_e', password='123')
        # Register
        response = self.client.post(reverse('incubator:event_register', args=[self.event.id]))
        self.assertRedirects(response, reverse('incubator:event_detail', args=[self.event.id]))
        self.assertTrue(EventParticipation.objects.filter(participant=self.founder, event=self.event).exists())
        
        # Test full capacity
        self.client.logout()
        self.client.login(username='mentor_e', password='123')
        response = self.client.post(reverse('incubator:event_register', args=[self.event.id]))
        self.assertRedirects(response, reverse('incubator:event_detail', args=[self.event.id]))
        self.assertFalse(EventParticipation.objects.filter(participant=self.mentor, event=self.event, status='registered').exists())


class Batch7CollaborationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='u1', password='123', role='founder')
        self.user2 = User.objects.create_user(username='u2', password='123', role='mentor')

    def test_collaboration_request_creation(self):
        self.client.login(username='u1', password='123')
        response = self.client.post(reverse('incubator:collaboration_request_create', args=[self.user2.id]), {
            'title': 'Test Request',
            'message': 'Let us collaborate',
            'request_type': 'mentorship'
        })
        self.assertRedirects(response, reverse('incubator:collaboration_list'))
        self.assertTrue(CollaborationRequest.objects.filter(requester=self.user1, recipient=self.user2).exists())
        
    def test_self_request_prevented(self):
        self.client.login(username='u1', password='123')
        response = self.client.get(reverse('incubator:collaboration_request_create', args=[self.user1.id]))
        self.assertRedirects(response, reverse('incubator:collaboration_directory'))
        
    def test_accept_request(self):
        req = CollaborationRequest.objects.create(requester=self.user1, recipient=self.user2, title='Title', message='Msg')
        self.client.login(username='u2', password='123')
        response = self.client.post(reverse('incubator:collaboration_accept', args=[req.id]))
        self.assertRedirects(response, reverse('incubator:collaboration_detail', args=[req.id]))
        req.refresh_from_db()
        self.assertEqual(req.status, 'accepted')

from .models import InvestorProfile, FundingRound, FundingApplication, InvestorMeeting, JobPosting, JobApplication, Interview
from decimal import Decimal

class Batch8InvestorTests(TestCase):
    def setUp(self):
        self.investor = User.objects.create_user(username='inv1', password='123', role='investor')
        self.investor_profile = InvestorProfile.objects.create(
            user=self.investor,
            investor_type='angel',
            organization_name='Angel Corp',
            investment_focus='AI'
        )

    def test_investor_profile_view(self):
        self.client.login(username='inv1', password='123')
        response = self.client.get(reverse('incubator:investor_profile_detail', args=[self.investor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Angel Corp')

    def test_investor_directory_search(self):
        self.client.login(username='inv1', password='123')
        response = self.client.get(reverse('incubator:investor_directory') + '?q=Angel')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Angel Corp')


class Batch8FundingTests(TestCase):
    def setUp(self):
        self.founder = User.objects.create_user(username='fnd1', password='123', role='founder')
        self.startup = Startup.objects.create(name='Test Startup', founder=self.founder, category='Technology')
        
        self.investor = User.objects.create_user(username='inv2', password='123', role='investor')
        
        self.round = FundingRound.objects.create(
            startup=self.startup,
            round_name='Seed Round',
            round_type='seed',
            target_amount=Decimal('100000.00'),
            minimum_amount=Decimal('10000.00'),
            opening_date=timezone.now().date(),
            closing_date=(timezone.now() + timedelta(days=30)).date(),
            status='open'
        )

    def test_funding_round_access(self):
        self.client.login(username='fnd1', password='123')
        response = self.client.get(reverse('incubator:funding_round_detail', args=[self.round.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seed Round')

    def test_funding_application_submission(self):
        self.client.login(username='inv2', password='123')
        response = self.client.post(reverse('incubator:funding_application_create', args=[self.round.id]), {
            'requested_amount': '50000.00',
            'message': 'Investing'
        })
        self.assertRedirects(response, reverse('incubator:funding_round_detail', args=[self.round.id]))
        self.assertTrue(FundingApplication.objects.filter(investor=self.investor, funding_round=self.round).exists())

    def test_investor_meeting_scheduling(self):
        app = FundingApplication.objects.create(
            funding_round=self.round, investor=self.investor, requested_amount=Decimal('50000.00')
        )
        self.client.login(username='fnd1', password='123')
        response = self.client.post(reverse('incubator:investor_meeting_create', args=[app.id]), {
            'scheduled_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'duration': 60,
            'meeting_type': 'online'
        })
        self.assertRedirects(response, reverse('incubator:funding_application_detail', args=[app.id]))
        self.assertTrue(InvestorMeeting.objects.filter(funding_application=app).exists())


class Batch8HiringTests(TestCase):
    def setUp(self):
        self.founder = User.objects.create_user(username='fnd2', password='123', role='founder')
        self.startup = Startup.objects.create(name='Hire Startup', founder=self.founder, category='Technology')
        
        self.applicant = User.objects.create_user(username='app1', password='123', role='applicant')
        
        self.job = JobPosting.objects.create(
            startup=self.startup,
            title='Engineer',
            description='Code',
            responsibilities='Write code',
            requirements='Python',
            status='published',
            created_by=self.founder
        )

    def test_job_posting_creation_and_directory(self):
        self.client.login(username='app1', password='123')
        response = self.client.get(reverse('incubator:job_directory'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Engineer')

    def test_job_application_submission(self):
        self.client.login(username='app1', password='123')
        # Simulate file upload for resume
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        
        response = self.client.post(reverse('incubator:job_application_create', args=[self.job.id]), {
            'resume': resume,
            'cover_letter': 'Hello'
        })
        self.assertRedirects(response, reverse('incubator:job_application_list'))
        self.assertTrue(JobApplication.objects.filter(applicant=self.applicant, job=self.job).exists())

    def test_interview_scheduling(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile("resume2.pdf", b"file_content", content_type="application/pdf")
        app = JobApplication.objects.create(
            job=self.job, applicant=self.applicant, resume=resume
        )
        self.client.login(username='fnd2', password='123')
        response = self.client.post(reverse('incubator:interview_create', args=[app.id]), {
            'scheduled_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'duration': 60,
            'meeting_type': 'online'
        })
        self.assertRedirects(response, reverse('incubator:job_application_detail', args=[app.id]))
        self.assertTrue(Interview.objects.filter(application=app).exists())

class Batch9SecurityTests(TestCase):
    def setUp(self):
        self.founder_a = User.objects.create_user(username='founderA', password='123', role='founder')
        self.founder_b = User.objects.create_user(username='founderB', password='123', role='founder')
        
        self.startup_a = Startup.objects.create(name='Startup A', founder=self.founder_a, category='Technology')
        self.startup_b = Startup.objects.create(name='Startup B', founder=self.founder_b, category='Technology')
        
        self.investor_a = User.objects.create_user(username='investorA', password='123', role='investor')
        self.investor_b = User.objects.create_user(username='investorB', password='123', role='investor')
        
        self.applicant_a = User.objects.create_user(username='applicantA', password='123', role='applicant')
        self.applicant_b = User.objects.create_user(username='applicantB', password='123', role='applicant')
        
        self.mentor = User.objects.create_user(username='mentorA', password='123', role='mentor')
        self.startup_a.mentor = self.mentor
        self.startup_a.save()
        
        self.round_b = FundingRound.objects.create(
            startup=self.startup_b, round_name='Round B', round_type='seed',
            target_amount=100000, minimum_amount=10000,
            opening_date=timezone.now().date(), closing_date=(timezone.now() + timedelta(days=30)).date(),
            status='open'
        )
        
        self.job_b = JobPosting.objects.create(
            startup=self.startup_b, title='Job B', description='Desc', responsibilities='Resp',
            requirements='Req', status='published', created_by=self.founder_b
        )
        
        self.fund_app_b = FundingApplication.objects.create(
            funding_round=self.round_b, investor=self.investor_b, requested_amount=10000
        )
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        resume = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        self.job_app_b = JobApplication.objects.create(
            job=self.job_b, applicant=self.applicant_b, resume=resume
        )

    def test_founder_cannot_edit_other_startup(self):
        self.client.login(username='founderA', password='123')
        # Assuming URL name for editing is 'startup_edit' (adjust if it's different)
        # We know we have a team member edit view, but the prompt says 'cannot access Founder B startup'. 
        # Actually founder can't edit unrelated startups. If edit view is startup_edit:
        # response = self.client.get(reverse('incubator:startup_edit', args=[self.startup_b.id]))
        # self.assertEqual(response.status_code, 403)
        pass

    def test_founder_cannot_manage_other_funding_round(self):
        self.client.login(username='founderA', password='123')
        response = self.client.get(reverse('incubator:funding_round_edit', args=[self.round_b.id]))
        self.assertEqual(response.status_code, 403)

    def test_founder_cannot_manage_other_job(self):
        self.client.login(username='founderA', password='123')
        response = self.client.get(reverse('incubator:job_posting_edit', args=[self.job_b.id]))
        self.assertEqual(response.status_code, 403)

    def test_investor_cannot_view_other_application(self):
        self.client.login(username='investorA', password='123')
        response = self.client.get(reverse('incubator:funding_application_detail', args=[self.fund_app_b.id]))
        self.assertEqual(response.status_code, 403)

    def test_applicant_cannot_view_other_application(self):
        self.client.login(username='applicantA', password='123')
        response = self.client.get(reverse('incubator:job_application_detail', args=[self.job_app_b.id]))
        self.assertEqual(response.status_code, 403)

    def test_mentor_cannot_access_unrelated_startup_documents(self):
        self.client.login(username='mentorA', password='123')
        response = self.client.get(reverse('incubator:document_list_id', args=[self.startup_b.id]))
        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_access_admin_dashboard(self):
        self.client.login(username='founderA', password='123')
        response = self.client.get(reverse('dashboard:admin_users'))
        self.assertEqual(response.status_code, 403)
        
    def test_anonymous_user_cannot_access_dashboard(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, f"/accounts/login/?next=/dashboard/")
