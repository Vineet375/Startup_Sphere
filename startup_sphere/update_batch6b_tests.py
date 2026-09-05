import os

file_path = 'incubator/tests.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

tests_content = """
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
        self.startup1 = Startup.objects.create(founder=self.founder1, mentor=self.mentor1, name='Alpha Startup', industry='Fintech', status='incubating')
        self.startup2 = Startup.objects.create(founder=self.founder2, mentor=self.mentor2, name='Beta Company', industry='Healthtech', status='graduated')
        
        # Team Member
        TeamMember.objects.create(startup=self.startup1, user=self.teammember_user, status='active')

    def test_directory_search_and_filter(self):
        self.client.login(username='founder1', password='password123')
        
        # Search match name
        response = self.client.get(reverse('incubator:startup_directory') + '?q=Alpha')
        self.assertContains(response, 'Alpha Startup')
        self.assertNotContains(response, 'Beta Company')
        
        # Filter industry
        response = self.client.get(reverse('incubator:startup_directory') + '?industry=Healthtech')
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

    def test_evaluation_permissions(self):
        # 1. Unassigned mentor blocked
        self.client.login(username='mentor2', password='password123')
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('incubator:evaluation_create', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)
        
        # 2. Team member blocked from list
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup1.id]))
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
"""

if "class Batch6BTests" not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(tests_content)
