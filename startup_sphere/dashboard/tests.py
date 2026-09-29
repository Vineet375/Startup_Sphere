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


from incubator.models import Startup, Event, JobPosting
from django.utils import timezone
from datetime import timedelta

class GlobalSearchTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='search_user', password='password123', role='founder')
        self.startup = Startup.objects.create(name='SearchTech', tagline='Best search', category='tech', founder=self.user, incubation_status='active')
        self.job = JobPosting.objects.create(startup=self.startup, title='Search Engineer', description='Build search', created_by=self.user, status='published')
        now = timezone.now()
        self.event = Event.objects.create(title='Search Summit', description='Learn search', start_datetime=now + timedelta(days=1), end_datetime=now + timedelta(days=2), status='upcoming')
        
    def test_search_results(self):
        self.client.login(username='search_user', password='password123')
        
        # Test startup name
        response = self.client.get(reverse('dashboard:global_search') + '?q=SearchTech')
        self.assertContains(response, 'SearchTech')
        
        # Test username
        user2 = User.objects.create_user(username='hidden_user', password='password123')
        response = self.client.get(reverse('dashboard:global_search') + '?q=hidden')
        self.assertContains(response, 'hidden_user')
        
        # Test job title
        response = self.client.get(reverse('dashboard:global_search') + '?q=Engineer')
        self.assertContains(response, 'Search Engineer')
        
        # Test event title
        response = self.client.get(reverse('dashboard:global_search') + '?q=Summit')
        self.assertContains(response, 'Search Summit')
        
        # Empty query
        response = self.client.get(reverse('dashboard:global_search') + '?q=')
        self.assertNotContains(response, 'SearchTech')
        
        # Nonexistent query
        response = self.client.get(reverse('dashboard:global_search') + '?q=asdfqwer')
        self.assertNotContains(response, 'SearchTech')
        
        # Partial and case-insensitive
        response = self.client.get(reverse('dashboard:global_search') + '?q=search')
        self.assertContains(response, 'SearchTech')
        self.assertContains(response, 'Search Engineer')
        self.assertContains(response, 'Search Summit')
