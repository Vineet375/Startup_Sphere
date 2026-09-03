import os

tests_to_add = """
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
        self.assertEqual(response.status_code, 403)

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
        self.assertFormError(response, 'form', 'file', "File extension 'exe' is not allowed. Allowed extensions are: 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'.")
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
"""

with open('incubator/tests.py', 'a', encoding='utf-8') as f:
    f.write(tests_to_add)
