import traceback, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from django.test import RequestFactory
from jobs.models import User
from community.models import FamilySetup
from community.views import family_hub

rf = RequestFactory()
req = rf.get('/community/family/')

# Test users with setup_done=True
done_users = FamilySetup.objects.filter(setup_done=True).select_related('user')
print(f"Users with setup done: {done_users.count()}")

for fs in done_users[:5]:
    req.user = fs.user
    try:
        resp = family_hub(req)
        print(f"OK  {fs.user.username} -> {resp.status_code}")
    except Exception:
        print(f"ERR {fs.user.username}:")
        traceback.print_exc()
        print("---")
        break
