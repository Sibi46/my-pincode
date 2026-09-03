import traceback, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from django.test import Client
from jobs.models import User

users = User.objects.filter(is_active=True).order_by('id')[:5]
c = Client()

for u in users:
    try:
        c.force_login(u)
        resp = c.get('/community/family/', follow=False)
        print(f"{'ERR' if resp.status_code>=400 else 'OK '} {u.username} ({u.user_type}) -> {resp.status_code}")
    except Exception:
        print(f"CRASH {u.username}:")
        traceback.print_exc()
