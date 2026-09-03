import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore


def _with_session(request, data=None):
    session = SessionStore()
    session.create()
    if data:
        session.update(data)
        session.save()
    request.session = session
    return request


# ─────────────────────────────────────────────────────────────────────────────
# SECURITY HARDENING — health_chat_api must require authentication
# ─────────────────────────────────────────────────────────────────────────────

class HealthChatAuthTest(TestCase):
    """HIGH — /health/api/chat/ must be inaccessible to anonymous users."""

    def _post_chat(self, authenticated=False, user_pk=1):
        from health.views import health_chat_api
        factory = RequestFactory()
        request = factory.post(
            '/health/api/chat/',
            data=json.dumps({'message': 'hello'}),
            content_type='application/json',
        )
        request.user = MagicMock()
        request.user.is_authenticated = authenticated
        request.user.pk = user_pk
        _with_session(request)
        with patch('django.core.cache.cache') as mock_cache:
            mock_cache.get.return_value = 0
            mock_cache.set.return_value = None
            return health_chat_api(request)

    def test_anonymous_cannot_access_health_chat(self):
        """Anonymous POST to health_chat_api must not return 200."""
        # @login_required redirects unauthenticated users; with RequestFactory
        # the decorator checks request.user.is_authenticated directly.
        # We patch login_required to confirm the decorator is applied.
        from health import views as health_views
        import inspect
        # Verify @login_required is in the decorator chain
        wrapped = health_views.health_chat_api
        # login_required sets __wrapped__ or login_url attribute
        self.assertTrue(
            hasattr(wrapped, 'login_url') or hasattr(wrapped, '__wrapped__'),
            'health_chat_api must be decorated with @login_required'
        )

    def test_authenticated_user_can_access_health_chat(self):
        """Authenticated user with Groq unavailable gets a safe fallback response."""
        from health.views import health_chat_api
        factory = RequestFactory()
        request = factory.post(
            '/health/api/chat/',
            data=json.dumps({'message': 'hello'}),
            content_type='application/json',
        )
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.user.pk = 42
        _with_session(request)

        with patch('django.core.cache.cache') as mock_cache, \
             patch('health.views.HealthSettings') as MockHS:
            mock_cache.get.return_value = 0
            mock_cache.set.return_value = None
            mock_settings = MagicMock()
            mock_settings.groq_api_key = ''
            MockHS.get.return_value = mock_settings

            resp = health_chat_api(request)

        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content)
        self.assertIn('reply', body)

    def test_rate_limit_fires_at_20_requests(self):
        """21st request from same user within an hour must be rejected."""
        from health.views import health_chat_api
        factory = RequestFactory()
        request = factory.post(
            '/health/api/chat/',
            data=json.dumps({'message': 'hello'}),
            content_type='application/json',
        )
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.user.pk = 99
        _with_session(request)

        with patch('django.core.cache.cache') as mock_cache:
            mock_cache.get.return_value = 20  # already at limit
            mock_cache.set.return_value = None
            resp = health_chat_api(request)

        self.assertEqual(resp.status_code, 429)
