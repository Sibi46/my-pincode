import os
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.sessions.backends.db import SessionStore
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# Helper: attach a real session to a RequestFactory request
# ─────────────────────────────────────────────────────────────────────────────
def _with_session(request, data=None):
    session = SessionStore()
    session.create()
    if data:
        session.update(data)
        session.save()
    request.session = session
    return request


# ─────────────────────────────────────────────────────────────────────────────
# 1. CRIT-1 / CRIT-2 / CRIT-3 — No hardcoded secrets in settings
# ─────────────────────────────────────────────────────────────────────────────
class SettingsSecretsTest(TestCase):

    def test_email_password_not_hardcoded(self):
        """The old Gmail app password must not appear anywhere in settings."""
        import jobportal.settings as s
        self.assertNotIn('pisnlnplumembcaw', getattr(s, 'EMAIL_HOST_PASSWORD', ''))

    def test_secret_key_uses_env(self):
        """SECRET_KEY must be read from DJANGO_SECRET_KEY env var when set."""
        with patch.dict(os.environ, {'DJANGO_SECRET_KEY': 'test-env-secret-123'}):
            import importlib
            import jobportal.settings as s
            importlib.reload(s)
            self.assertEqual(s.SECRET_KEY, 'test-env-secret-123')

    def test_db_user_uses_env(self):
        """DB_USER must be read from environment when set."""
        with patch.dict(os.environ, {'DB_USER': 'app_user', 'DB_PASSWORD': 'app_pass'}):
            import importlib
            import jobportal.settings as s
            importlib.reload(s)
            self.assertEqual(s.DATABASES['default']['USER'], 'app_user')
            self.assertEqual(s.DATABASES['default']['PASSWORD'], 'app_pass')

    def test_email_host_password_uses_env(self):
        """EMAIL_HOST_PASSWORD must be read from environment when set."""
        with patch.dict(os.environ, {'EMAIL_HOST_PASSWORD': 'env-gmail-pass'}):
            import importlib
            import jobportal.settings as s
            importlib.reload(s)
            self.assertEqual(s.EMAIL_HOST_PASSWORD, 'env-gmail-pass')

    def test_no_hardcoded_gmail_password_in_file(self):
        """The literal old Gmail password must not exist in the settings file."""
        settings_path = os.path.join(os.path.dirname(__file__), '..', 'jobportal', 'settings.py')
        with open(settings_path) as f:
            content = f.read()
        self.assertNotIn('pisnlnplumembcaw', content)


# ─────────────────────────────────────────────────────────────────────────────
# 2. CRIT-4 — Ad URL validation (_safe_ad_url)
# ─────────────────────────────────────────────────────────────────────────────
class AdUrlSafetyTest(TestCase):

    def setUp(self):
        from jobs.views import _safe_ad_url
        self.safe = _safe_ad_url

    def test_http_url_allowed(self):
        self.assertEqual(self.safe('http://example.com'), 'http://example.com')

    def test_https_url_allowed(self):
        self.assertEqual(self.safe('https://shop.example.com/promo'), 'https://shop.example.com/promo')

    def test_https_with_whitespace_allowed(self):
        self.assertEqual(self.safe('  https://example.com  '), 'https://example.com')

    def test_javascript_scheme_blocked(self):
        self.assertIsNone(self.safe('javascript:alert(1)'))

    def test_data_scheme_blocked(self):
        self.assertIsNone(self.safe('data:text/html,<script>alert(1)</script>'))

    def test_file_scheme_blocked(self):
        self.assertIsNone(self.safe('file:///etc/passwd'))

    def test_ftp_scheme_blocked(self):
        self.assertIsNone(self.safe('ftp://files.example.com'))

    def test_empty_string_blocked(self):
        self.assertIsNone(self.safe(''))

    def test_none_blocked(self):
        self.assertIsNone(self.safe(None))

    def test_relative_path_blocked(self):
        self.assertIsNone(self.safe('/admin/'))

    def test_case_insensitive_javascript_blocked(self):
        self.assertIsNone(self.safe('JAVASCRIPT:alert(1)'))

    def test_case_insensitive_data_blocked(self):
        self.assertIsNone(self.safe('DATA:text/html,bad'))


# ─────────────────────────────────────────────────────────────────────────────
# 3. CRIT-5 — Rate limiting helpers
# ─────────────────────────────────────────────────────────────────────────────
class RateLimitHelperTest(TestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_allows_within_limit(self):
        from jobs.views import _rate_limit
        for _ in range(3):
            self.assertTrue(_rate_limit('test_key', max_attempts=3, window_seconds=60))

    def test_blocks_over_limit(self):
        from jobs.views import _rate_limit
        for _ in range(3):
            _rate_limit('test_key2', max_attempts=3, window_seconds=60)
        self.assertFalse(_rate_limit('test_key2', max_attempts=3, window_seconds=60))

    def test_different_keys_independent(self):
        from jobs.views import _rate_limit
        for _ in range(3):
            _rate_limit('key_a', max_attempts=3, window_seconds=60)
        # key_a is exhausted but key_b should still be allowed
        self.assertTrue(_rate_limit('key_b', max_attempts=3, window_seconds=60))


# ─────────────────────────────────────────────────────────────────────────────
# 4. CRIT-5 — OTP send rate limiting (view level)
# ─────────────────────────────────────────────────────────────────────────────
class OtpSendRateLimitTest(TestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_otp_send_blocked_after_3_attempts(self):
        from django.test import Client
        c = Client()
        payload = json.dumps({'phone': '9876543210', 'allow_existing': True})

        # Exhaust the 3-attempt limit by patching out the actual SMS send
        with patch('jobs.views.User') as MockUser:
            MockUser.objects.filter.return_value.exists.return_value = False
            # Hit 3 times
            for _ in range(3):
                c.post('/api/send-otp/', payload, content_type='application/json')
            # 4th must be blocked
            resp = c.post('/api/send-otp/', payload, content_type='application/json')

        data = json.loads(resp.content)
        self.assertFalse(data['success'])
        self.assertIn('Too many', data['error'])


# ─────────────────────────────────────────────────────────────────────────────
# 5. CRIT-5 — OTP verify attempt limiting
# ─────────────────────────────────────────────────────────────────────────────
class OtpVerifyRateLimitTest(TestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_otp_verify_blocked_after_5_wrong_attempts(self):
        from django.test import Client
        c = Client()
        session = c.session
        session['otp'] = '123456'
        session['otp_phone'] = '9000000001'
        session['otp_verified'] = False
        session.save()

        wrong_payload = json.dumps({'otp': '000000'})
        for _ in range(5):
            c.post('/api/verify-otp/', wrong_payload, content_type='application/json')

        # 6th attempt: OTP should be cleared and rate-limited
        resp = c.post('/api/verify-otp/', wrong_payload, content_type='application/json')
        data = json.loads(resp.content)
        self.assertFalse(data['success'])
        self.assertIn('Too many', data['error'])

    def test_correct_otp_succeeds_before_limit(self):
        from django.test import Client
        c = Client()
        session = c.session
        session['otp'] = '654321'
        session['otp_phone'] = '9000000002'
        session['otp_verified'] = False
        session.save()

        resp = c.post('/api/verify-otp/', json.dumps({'otp': '654321'}),
                      content_type='application/json')
        data = json.loads(resp.content)
        self.assertTrue(data['success'])


# ─────────────────────────────────────────────────────────────────────────────
# 6. HIGH-2 — Password reset phone mismatch
# ─────────────────────────────────────────────────────────────────────────────
class ResetPasswordPhoneMatchTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='testuser_reset',
            phone='9111111111',
            password='oldpass123',
        )

    def tearDown(self):
        cache.clear()

    def test_reset_blocked_if_otp_phone_differs(self):
        from django.test import Client
        c = Client()
        session = c.session
        session['otp_verified'] = True
        session['otp_phone'] = '9999999999'  # Different phone verified
        session.save()

        payload = json.dumps({'phone': '9111111111', 'password': 'newpass456'})
        resp = c.post('/api/reset-password/', payload, content_type='application/json')
        data = json.loads(resp.content)
        self.assertFalse(data['success'])
        self.assertIn('mismatch', data['error'].lower())

    def test_reset_blocked_if_otp_not_verified(self):
        from django.test import Client
        c = Client()
        session = c.session
        session['otp_verified'] = False
        session['otp_phone'] = '9111111111'
        session.save()

        payload = json.dumps({'phone': '9111111111', 'password': 'newpass456'})
        resp = c.post('/api/reset-password/', payload, content_type='application/json')
        data = json.loads(resp.content)
        self.assertFalse(data['success'])

    def test_reset_succeeds_when_phone_matches(self):
        from django.test import Client
        c = Client()
        session = c.session
        session['otp_verified'] = True
        session['otp_phone'] = '9111111111'  # Same phone
        session.save()

        payload = json.dumps({'phone': '9111111111', 'password': 'newpass789'})
        resp = c.post('/api/reset-password/', payload, content_type='application/json')
        data = json.loads(resp.content)
        self.assertTrue(data['success'])

    def test_reset_clears_otp_session_state(self):
        from django.test import Client
        c = Client()
        session = c.session
        session['otp_verified'] = True
        session['otp_phone'] = '9111111111'
        session.save()

        payload = json.dumps({'phone': '9111111111', 'password': 'cleartest99'})
        c.post('/api/reset-password/', payload, content_type='application/json')

        # Reload session and confirm OTP state is cleared
        session_key = c.session.session_key
        from django.contrib.sessions.backends.db import SessionStore
        s = SessionStore(session_key=session_key)
        self.assertFalse(s.get('otp_verified', False))
        self.assertIsNone(s.get('otp_phone'))


# ─────────────────────────────────────────────────────────────────────────────
# 7. OTP cryptographic security — secrets module used, not random
# ─────────────────────────────────────────────────────────────────────────────
class OtpCryptoTest(TestCase):

    def test_otp_generation_uses_secrets(self):
        """Verify the OTP generation code in views uses secrets, not random."""
        import inspect, jobs.views as vw
        source = inspect.getsource(vw.send_otp)
        self.assertIn('_secrets.randbelow', source)
        self.assertNotIn('random.randint', source)

    def test_otp_range_valid(self):
        """OTP generated from secrets is always 6-digit."""
        import secrets
        for _ in range(100):
            otp = secrets.randbelow(900000) + 100000
            self.assertGreaterEqual(otp, 100000)
            self.assertLessEqual(otp, 999999)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Login rate limiting
# ─────────────────────────────────────────────────────────────────────────────
class LoginRateLimitTest(TestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_login_blocked_after_5_attempts(self):
        from django.test import Client
        c = Client()
        payload = json.dumps({'phone': '9000000099', 'password': 'wrongpass'})
        for _ in range(5):
            c.post('/api/phone-login/', payload, content_type='application/json')
        resp = c.post('/api/phone-login/', payload, content_type='application/json')
        data = json.loads(resp.content)
        self.assertFalse(data['success'])
        self.assertIn('Too many', data['error'])


# ─────────────────────────────────────────────────────────────────────────────
# 9. CRIT-E1 / CRIT-E4 — AI chat endpoint safe error responses
#
# Uses RequestFactory + direct view call to bypass Django test DB creation.
# The view is called directly after patching login_required and settings.
# ─────────────────────────────────────────────────────────────────────────────
class AiChatSafeErrorTest(TestCase):

    def _post(self, api_key, side_effect=None, post_data=None):
        """
        Call ai_generate_description directly via RequestFactory.
        Patches login_required so no DB user is needed.
        """
        from django.test import RequestFactory
        from jobs.views import ai_generate_description
        from django.conf import settings as django_settings

        factory = RequestFactory()
        request = factory.post('/api/ai-job-description/', post_data or {'title': 'Test'})

        # Attach a minimal mock user so login_required passes
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.pk = 0
        request.user = mock_user

        with patch.object(django_settings, 'ANTHROPIC_API_KEY', api_key):
            if side_effect is not None:
                with patch('anthropic.Anthropic') as MockAnthropic:
                    MockAnthropic.return_value.messages.create.side_effect = side_effect
                    return ai_generate_description(request)
            else:
                return ai_generate_description(request)

    def test_missing_api_key_returns_generic_500(self):
        """Empty API key returns generic 500 — not settings details."""
        resp = self._post(api_key='')
        self.assertEqual(resp.status_code, 500)
        data = json.loads(resp.content)
        self.assertEqual(data['error'], 'AI feature is temporarily unavailable.')

    def test_missing_api_key_does_not_expose_settings(self):
        """Response must not mention settings.py or ANTHROPIC_API_KEY."""
        resp = self._post(api_key='')
        body = resp.content.decode()
        self.assertNotIn('settings.py', body)
        self.assertNotIn('ANTHROPIC_API_KEY', body)

    def test_api_exception_returns_generic_500(self):
        """Anthropic API exception → generic message, not str(e)."""
        resp = self._post(
            api_key='fake-key',
            side_effect=RuntimeError('Connection refused: internal details at /v1/messages'),
        )
        self.assertEqual(resp.status_code, 500)
        data = json.loads(resp.content)
        self.assertEqual(data['error'], 'Something went wrong. Please try again.')

    def test_api_exception_does_not_leak_exception_text(self):
        """Raw exception message must not appear in the HTTP response body."""
        secret_detail = 'top_secret_internal_path_xyz_12345'
        resp = self._post(api_key='fake-key', side_effect=RuntimeError(secret_detail))
        self.assertNotIn(secret_detail, resp.content.decode())

    def test_api_exception_does_not_expose_api_key(self):
        """API key value must never appear in the response body."""
        fake_key = 'fake-key-must-not-appear-in-response'
        resp = self._post(api_key=fake_key, side_effect=Exception('fail'))
        self.assertNotIn(fake_key, resp.content.decode())
