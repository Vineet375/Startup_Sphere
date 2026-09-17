import os
with open('batch8_views.py', 'r', encoding='utf-8') as f:
    new_views = f.read()

with open('incubator/views.py', 'a', encoding='utf-8') as f:
    f.write(new_views)
