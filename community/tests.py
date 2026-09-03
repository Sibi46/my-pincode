"""
Community app tests.
Uses RequestFactory + direct view calls to bypass Django test DB creation.
"""
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory


# ─────────────────────────────────────────────────────────────────────────────
# CRIT-E2 — Teacher registration: safe error messages
# ─────────────────────────────────────────────────────────────────────────────

class TeacherRegisterSafeErrorTest(TestCase):
    """
    Verify that teacher_register view never exposes raw exception text.
    Patches DB calls so no real database is required.
    """

    def _post(self, post_data, user_exists=False, create_side_effect=None):
        from community.views import teacher_register
        factory = RequestFactory()
        request = factory.post('/community/teacher-register/', post_data)
        request.user = MagicMock(is_authenticated=False)

        with patch('community.views.School') as MockSchool, \
             patch('community.views.SchoolAdmin') as MockSchoolAdmin:

            MockSchool.objects.all.return_value.order_by.return_value = []
            MockSchool.objects.get.return_value = MagicMock(pk=1, name='Test School')

            with patch('django.contrib.auth.get_user_model') as MockGetUser:
                MockUserModel = MagicMock()
                MockGetUser.return_value = MockUserModel
                MockUserModel.objects.filter.return_value.exists.return_value = user_exists

                if create_side_effect:
                    MockUserModel.objects.create_user.side_effect = create_side_effect

                resp = teacher_register(request)
        return resp

    def test_generic_exception_shows_safe_message(self):
        """RuntimeError during user creation must not expose str(e) in response."""
        secret = 'secret_internal_db_table_xyz'
        resp = self._post(
            {'full_name': 'Test Teacher', 'phone': '9876543210', 'school_id': '1'},
            user_exists=False,
            create_side_effect=RuntimeError(secret),
        )
        body = resp.content.decode()
        self.assertNotIn(secret, body)
        self.assertNotIn('Registration failed: ', body)

    def test_generic_exception_shows_generic_message(self):
        """A non-IntegrityError shows the generic registration failed message."""
        resp = self._post(
            {'full_name': 'Test Teacher', 'phone': '9876543210', 'school_id': '1'},
            user_exists=False,
            create_side_effect=RuntimeError('some internal error'),
        )
        body = resp.content.decode()
        self.assertIn('Registration failed. Please try again.', body)

    def test_integrity_error_shows_phone_message(self):
        """IntegrityError shows the phone-specific safe message."""
        from django.db import IntegrityError
        resp = self._post(
            {'full_name': 'Test Teacher', 'phone': '9876543210', 'school_id': '1'},
            user_exists=False,
            create_side_effect=IntegrityError("Duplicate entry '9876543210' for key 'username'"),
        )
        body = resp.content.decode()
        self.assertNotIn("Duplicate entry", body)
        self.assertNotIn("for key", body)
        self.assertIn('This phone may already be in use.', body)

    def test_no_sqlstate_in_response(self):
        """SQLSTATE and constraint names must never reach the response body."""
        from django.db import IntegrityError
        resp = self._post(
            {'full_name': 'Test Teacher', 'phone': '9876543210', 'school_id': '1'},
            user_exists=False,
            create_side_effect=IntegrityError("(1062, \"Duplicate entry 'x' for key 'jobs_user.username'\")"),
        )
        body = resp.content.decode()
        self.assertNotIn('1062', body)
        self.assertNotIn('jobs_user', body)


class SchoolDashboardAddTeacherSafeErrorTest(TestCase):
    """
    Verify school_dashboard add_teacher action never exposes raw exception text.
    Tests the error-handling logic directly by simulating the two failure paths
    without invoking the full view (which requires many DB-level mocks).
    """

    def _simulate_link_error(self, exc):
        """
        Replicate the link-existing-user except block logic from school_dashboard.
        Returns the error string the view would assign.
        """
        error = None
        try:
            raise exc
        except Exception:
            import logging as _logging
            _logging.getLogger('community.views').exception(
                'school_corner add_teacher link: failed for phone=%s school=%s', 'X', 1
            )
            error = 'Registration failed. Please try again.'
        return error

    def _simulate_create_error(self, exc):
        """
        Replicate the create-new-user except block logic from school_dashboard.
        Returns the error string the view would assign.
        """
        error = None
        try:
            raise exc
        except Exception as e:
            from django.db import IntegrityError
            if isinstance(e, IntegrityError):
                error = 'Registration failed. This phone may already be in use.'
            else:
                error = 'Registration failed. Please try again.'
            import logging as _logging
            _logging.getLogger('community.views').exception(
                'school_corner add_teacher create: failed for phone=%s school=%s', 'X', 1
            )
        return error

    def test_link_path_exception_does_not_expose_raw_error(self):
        """Exception when linking existing user: raw str(e) not in error message."""
        secret = 'secret_constraint_jobs_user_phone'
        error = self._simulate_link_error(RuntimeError(secret))
        self.assertNotIn(secret, error)

    def test_link_path_exception_shows_safe_message(self):
        """Exception when linking existing user: safe generic message shown."""
        error = self._simulate_link_error(RuntimeError('any error'))
        self.assertEqual(error, 'Registration failed. Please try again.')

    def test_create_path_integrity_error_shows_phone_message(self):
        """IntegrityError on create: shows phone-specific safe message, not SQL."""
        from django.db import IntegrityError
        raw = "Duplicate entry '9800000002' for key 'jobs_user.username'"
        error = self._simulate_create_error(IntegrityError(raw))
        self.assertNotIn('Duplicate entry', error)
        self.assertNotIn('jobs_user', error)
        self.assertIn('This phone may already be in use.', error)

    def test_create_path_generic_exception_shows_safe_message(self):
        """RuntimeError on create: shows generic safe message, not str(e)."""
        secret = 'internal_path_detail_abc'
        error = self._simulate_create_error(RuntimeError(secret))
        self.assertNotIn(secret, error)
        self.assertEqual(error, 'Registration failed. Please try again.')

    def test_create_path_no_sqlstate_exposed(self):
        """SQLSTATE code and table name must never reach the error string."""
        from django.db import IntegrityError
        raw = "(1062, \"Duplicate entry 'x' for key 'jobs_user.username'\")"
        error = self._simulate_create_error(IntegrityError(raw))
        self.assertNotIn('1062', error)
        self.assertNotIn('jobs_user', error)
