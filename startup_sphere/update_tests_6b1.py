import os

file_path = 'incubator/tests.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace some assertions in test_evaluation_permissions that check team member access.
# Previously team member was blocked from viewing. Now they should be allowed.

old_team_perm = """        # 2. Team member blocked from list
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)"""

new_team_perm = """        # 2. Team member CAN view list but CANNOT create/edit
        self.client.login(username='teammember', password='password123')
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('incubator:evaluation_create', args=[self.startup1.id]))
        self.assertEqual(response.status_code, 403)
        
        # Test team member blocked from other startup
        response = self.client.get(reverse('incubator:evaluation_list', args=[self.startup2.id]))
        self.assertEqual(response.status_code, 403)"""

if old_team_perm in content:
    content = content.replace(old_team_perm, new_team_perm)
else:
    print("Could not find old_team_perm")

# Also add tests for privacy profile
old_profile_privacy = """    def test_public_profile_privacy(self):
        self.client.login(username='founder1', password='password123')
        response = self.client.get(reverse('incubator:startup_public_profile', args=[self.startup2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beta Company')
        # Does not show workspace elements
        self.assertNotContains(response, 'Create Evaluation')
        self.assertNotContains(response, 'Milestones')"""

new_profile_privacy = """    def test_public_profile_privacy(self):
        self.client.login(username='founder1', password='password123')
        response = self.client.get(reverse('incubator:startup_public_profile', args=[self.startup2.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beta Company')
        # Does not show workspace elements
        self.assertNotContains(response, 'Create Evaluation')
        self.assertNotContains(response, 'Milestones')
        self.assertNotContains(response, 'mailto:') # Contact info hidden
        self.assertNotContains(response, 'f2@test.com')"""

if old_profile_privacy in content:
    content = content.replace(old_profile_privacy, new_profile_privacy)
else:
    print("Could not find old_profile_privacy")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
