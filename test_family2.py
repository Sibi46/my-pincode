import traceback, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobportal.settings')
django.setup()

from django.test import Client
from jobs.models import User

u = User.objects.filter(is_active=True).first()
c = Client()
c.force_login(u)
try:
    resp = c.get('/community/family/', follow=True)
    print("Status:", resp.status_code)
    print("Redirect chain:", resp.redirect_chain)
    if resp.status_code >= 400:
        content = resp.content.decode('utf-8', 'replace')
        # Find traceback in content
        idx = content.find('Traceback')
        if idx > 0:
            print(content[idx:idx+2000])
        else:
            print(content[:500])
except Exception:
    traceback.print_exc()
