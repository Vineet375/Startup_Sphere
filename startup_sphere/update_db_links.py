import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from incubator.models import Notification

for n in Notification.objects.filter(link_url__startswith='/startups/'):
    new_url = '/incubator' + n.link_url
    print(f"Updating {n.id} from {n.link_url} to {new_url}")
    n.link_url = new_url
    n.save()
