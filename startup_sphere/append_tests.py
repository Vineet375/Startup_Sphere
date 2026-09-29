import os

# Append GlobalSearchTests to dashboard/tests.py
dashboard_tests_path = r'e:\Projects\GLS SEM-7 Django Project\Startup_Sphere\startup_sphere\dashboard\tests.py'
dashboard_tests_code = '''
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
'''

with open(dashboard_tests_path, 'a') as f:
    f.write('\n' + dashboard_tests_code)

# Append FundingRoundRaisedAmountTests to incubator/tests.py
incubator_tests_path = r'e:\Projects\GLS SEM-7 Django Project\Startup_Sphere\startup_sphere\incubator\tests.py'
incubator_tests_code = '''
from decimal import Decimal
from django.db.models import Sum

class FundingRoundRaisedAmountTests(TestCase):
    def setUp(self):
        self.founder = User.objects.create_user(username='f1', password='password123', role='founder')
        self.investor1 = User.objects.create_user(username='i1', password='password123', role='investor')
        self.investor2 = User.objects.create_user(username='i2', password='password123', role='investor')
        self.startup = Startup.objects.create(name='St1', founder=self.founder)
        self.funding_round = FundingRound.objects.create(
            startup=self.startup, round_name='Seed', target_amount=1000000, status='open'
        )
        
    def test_raised_amount_transitions(self):
        # A: Initial raised amount = 0
        self.assertEqual(self.funding_round.raised_amount, Decimal('0.00'))
        
        # B: Pending application of 100000 -> raised amount must remain 0
        app1 = FundingApplication.objects.create(
            funding_round=self.funding_round, investor=self.investor1, requested_amount=100000, status='pending'
        )
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('0.00'))
        
        self.client.login(username='f1', password='password123')
        
        # C: Pending -> accepted -> raised amount = 100000
        response = self.client.post(reverse('incubator:funding_application_detail', args=[app1.id]), {'status': 'accepted'})
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('100000.00'))
        
        # D: Another application of 200000 -> accepted -> raised amount = 300000
        app2 = FundingApplication.objects.create(
            funding_round=self.funding_round, investor=self.investor2, requested_amount=200000, status='pending'
        )
        response = self.client.post(reverse('incubator:funding_application_detail', args=[app2.id]), {'status': 'accepted'})
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('300000.00'))
        
        # E: First accepted application -> rejected -> raised amount = 200000
        response = self.client.post(reverse('incubator:funding_application_detail', args=[app1.id]), {'status': 'rejected'})
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('200000.00'))
        
        # F: Second accepted application -> withdrawn -> raised amount = 0
        self.client.logout()
        self.client.login(username='i2', password='password123')
        response = self.client.post(reverse('incubator:funding_application_withdraw', args=[app2.id]))
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('0.00'))
        
        # G: Accepted -> accepted again -> must NOT double-count
        self.client.logout()
        self.client.login(username='f1', password='password123')
        # accept app1 again
        self.client.post(reverse('incubator:funding_application_detail', args=[app1.id]), {'status': 'accepted'})
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('100000.00'))
        # submit accepted again
        self.client.post(reverse('incubator:funding_application_detail', args=[app1.id]), {'status': 'accepted'})
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('100000.00'))
        
        # H: Rejected -> rejected -> must not alter the amount
        app3 = FundingApplication.objects.create(
            funding_round=self.funding_round, investor=self.investor2, requested_amount=50000, status='rejected'
        )
        self.client.post(reverse('incubator:funding_application_detail', args=[app3.id]), {'status': 'rejected'})
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('100000.00'))
        
        # I: Multiple accepted applications -> total must equal exactly the sum
        self.client.post(reverse('incubator:funding_application_detail', args=[app3.id]), {'status': 'accepted'})
        self.funding_round.refresh_from_db()
        self.assertEqual(self.funding_round.raised_amount, Decimal('150000.00'))
'''

with open(incubator_tests_path, 'a') as f:
    f.write('\n' + incubator_tests_code)
