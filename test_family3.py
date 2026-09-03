import traceback, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from django.test import RequestFactory
from jobs.models import User
from community.views import family_hub

rf = RequestFactory()
req = rf.get('/community/family/')

for u in User.objects.filter(is_active=True).order_by('id')[:10]:
    req.user = u
    try:
        resp = family_hub(req)
        print(f"OK  {u.username} ({u.user_type}) -> {resp.status_code}")
    except Exception:
        print(f"ERR {u.username} ({u.user_type}):")
        traceback.print_exc()
        print("---")
        break
