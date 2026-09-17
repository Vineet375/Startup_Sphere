import os

file_path = 'dashboard/tests.py'
content = """from django.test import TestCase
from django.urls import reverse
from core.models import User

class AdminDashboardTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin_user', password='password123', role='admin')
        self.founder_user = User.objects.create_user(username='founder_user', password='password123', role='founder')

    def test_admin_dashboard_access(self):
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Platform Admin Dashboard')
        
        response = self.client.get(reverse('dashboard:admin_users'))
        self.assertEqual(response.status_code, 200)

    def test_non_admin_blocked(self):
        self.client.login(username='founder_user', password='password123')
        response = self.client.get(reverse('dashboard:admin_users'))
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get(reverse('dashboard:admin_startups'))
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get(reverse('dashboard:admin_ideas'))
        self.assertEqual(response.status_code, 403)
"""
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

incubator_tests_append = """

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
"""

with open('incubator/tests.py', 'a', encoding='utf-8') as f:
    f.write(incubator_tests_append)
