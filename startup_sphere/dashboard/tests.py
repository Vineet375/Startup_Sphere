from django.test import TestCase
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
