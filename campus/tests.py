import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore


def _with_session(request):
    session = SessionStore()
    session.create()
    request.session = session
    return request


# ─────────────────────────────────────────────────────────────────────────────
# SECURITY HARDENING — campus application_detail IDOR fix
# ─────────────────────────────────────────────────────────────────────────────

class CampusApplicationDetailIDORTest(TestCase):
    """MEDIUM IDOR — non-student users must be denied access to application_detail."""

    def _call_view(self, is_student=False, owns_app=True):
        from campus.views import application_detail
        factory = RequestFactory()
        request = factory.get('/campus/application/1/')
        request.user = MagicMock()
        request.user.is_authenticated = True
        _with_session(request)

        mock_student = MagicMock() if is_student else None
        mock_app = MagicMock()
        mock_app.student = mock_student if owns_app else MagicMock()

        with patch('campus.views.get_student', return_value=mock_student), \
             patch('campus.views.get_object_or_404', return_value=mock_app), \
             patch('campus.views.messages'), \
             patch('campus.views.redirect') as mock_redirect, \
             patch('campus.views.render') as mock_render:
            mock_redirect.return_value = MagicMock(status_code=302)
            mock_render.return_value = MagicMock(status_code=200)
            result = application_detail(request, pk=1)
        return result, mock_redirect, mock_render

    def test_non_student_user_is_redirected(self):
        """A logged-in non-student (student=None) must be redirected, not shown the app."""
        result, mock_redirect, mock_render = self._call_view(is_student=False)
        mock_redirect.assert_called_once()
        mock_render.assert_not_called()

    def test_student_owning_app_gets_access(self):
        """A student who owns the application must see it."""
        result, mock_redirect, mock_render = self._call_view(is_student=True, owns_app=True)
        mock_render.assert_called_once()
        mock_redirect.assert_not_called()

    def test_student_not_owning_app_is_redirected(self):
        """A student who does NOT own the application must be redirected."""
        result, mock_redirect, mock_render = self._call_view(is_student=True, owns_app=False)
        mock_redirect.assert_called_once()
        mock_render.assert_not_called()
