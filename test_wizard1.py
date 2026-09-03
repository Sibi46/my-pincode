import traceback, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from django.test import RequestFactory
from jobs.models import User
from community.views import family_setup_wizard

rf = RequestFactory()
req = rf.get('/community/family/setup/', {'step': '1'})
u = User.objects.filter(is_active=True).first()
req.user = u

try:
    resp = family_setup_wizard(req)
    print("Status:", resp.status_code)
    if hasattr(resp, 'content'):
        content = resp.content.decode('utf-8', 'replace')
        if 'Error' in content or 'error' in content[:200]:
            print(content[:500])
        else:
            print("Template rendered OK, length:", len(content))
except Exception:
    traceback.print_exc()
