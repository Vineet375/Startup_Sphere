import os

file_path = 'core/tests.py'
new_tests = """from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LandingPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@test.com')
        
    def test_get_started_anonymous(self):
        response = self.client.get(reverse('core:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('accounts:register'))
        self.assertNotContains(response, reverse('dashboard:home'))
        
    def test_get_started_authenticated(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('core:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('dashboard:home'))
        # It shouldn't point to register for the get started button. (Note: navbar might still have register depending on logic, but navbar usually hides it when auth'd)
"""

with open(file_path, 'a', encoding='utf-8') as f:
    f.write(new_tests)
