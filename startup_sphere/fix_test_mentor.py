import os

file_path = 'incubator/tests.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("self.startup_a.mentor.add(self.mentor)", "self.startup_a.mentor = self.mentor\n        self.startup_a.save()")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
