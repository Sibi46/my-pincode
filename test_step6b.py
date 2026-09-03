import traceback, sys, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()
from django.test import RequestFactory
from jobs.models import User
from community.views import family_setup_wizard
from community.models import FamilySetup

# Test all non-superadmin users
users = User.objects.exclude(username='superadmin').order_by('id')[:20]
rf = RequestFactory()

for u in users:
    try:
        req = rf.get('/community/family/setup/', {'step': '6'})
        req.user = u
        resp = family_setup_wizard(req)
        print(f"OK  {u.username} ({u.user_type}) -> {resp.status_code}")
    except Exception as e:
        print(f"ERR {u.username} ({u.user_type}):")
        traceback.print_exc()
        print("---")
