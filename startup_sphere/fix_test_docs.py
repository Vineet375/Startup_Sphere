import os

file_path = 'incubator/tests.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("reverse('incubator:startup_documents', args=[self.startup_b.id])", "reverse('incubator:document_list_id', args=[self.startup_b.id])")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
