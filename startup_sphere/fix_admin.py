import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.filter(username='admin').first()
if user:
    user.set_password('admin123')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("Admin user updated.")
else:
    User.objects.create_superuser('admin', 'admin@startupsphere.com', 'admin123', role='admin')
    print("Admin user created.")
