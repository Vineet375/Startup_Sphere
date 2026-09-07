import os

file_path = 'incubator/tests.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_test = """    def test_team_member_idea_list_visibility(self):
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('incubator:idea_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.idea1.title)
        # Should not contain Create Idea
        self.assertNotContains(response, reverse('incubator:idea_create'))"""

new_test = """    def test_team_member_idea_list_visibility(self):
        # Create an idea first
        from incubator.models import Idea
        idea = Idea.objects.create(startup=self.startup1, creator=self.founder1, title='Test Idea', description='Desc')
        
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('incubator:idea_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, idea.title)
        # Should not contain Create Idea
        self.assertNotContains(response, reverse('incubator:idea_create'))"""

if old_test in content:
    content = content.replace(old_test, new_test)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
