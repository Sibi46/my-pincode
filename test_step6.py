import traceback, sys, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'jobportal.settings'
import django
django.setup()

from django.test import RequestFactory
from jobs.models import User
from community.views import family_setup_wizard

try:
    u = User.objects.filter(is_active=True).first()
    print("User:", u)
    rf = RequestFactory()
    req = rf.get('/community/family/setup/', {'step': '6'})
    req.user = u
    resp = family_setup_wizard(req)
    print("Status:", resp.status_code)
except Exception:
    traceback.print_exc()
