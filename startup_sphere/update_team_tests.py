import os

file_path = 'incubator/tests.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_tests = """
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
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('incubator:idea_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.idea1.title)
        # Should not contain Create Idea
        self.assertNotContains(response, reverse('incubator:idea_create'))
"""

if 'def test_team_member_dashboard_detection' not in content:
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(new_tests)
