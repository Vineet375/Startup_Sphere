import os

file_path = 'incubator/tests.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_edit_test = """    def test_mentor_cannot_edit_others_evaluation(self):
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
        self.assertEqual(response.status_code, 403)"""

new_edit_test = """    def test_mentor_cannot_edit_others_evaluation(self):
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
        self.assertEqual(response.status_code, 403)"""

if old_edit_test in content:
    content = content.replace(old_edit_test, new_edit_test)
else:
    print("Could not find old_edit_test")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
