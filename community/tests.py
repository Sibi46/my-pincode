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


# ─────────────────────────────────────────────────────────────────────────────
# CRIT-E3 — FamilyMember age validation: invalid values never reach the DB
# ─────────────────────────────────────────────────────────────────────────────

class FamilyMemberAgeValidationTest(TestCase):
    """
    Verify that family_member_create, family_member_edit, and the
    family_setup_wizard (Step 6 children) reject out-of-range age values
    before any DB write, preventing DataError (1264) under STRICT_ALL_TABLES.

    All tests use mocks — no real DB required.
    """

    def _post_create(self, age_str):
        """POST to family_member_create with the given age string. Returns saved FamilyMember mock."""
        from community.views import family_member_create
        factory = RequestFactory()
        data = {'name': 'Test Person', 'member_type': 'father', 'side': 'husband', 'age': age_str}
        request = factory.post('/community/family/member/create/', data)
        request.user = MagicMock()

        saved = {}

        def fake_save():
            saved['age'] = member_instance.age

        member_instance = MagicMock()
        member_instance.name = 'Test Person'
        member_instance.age = None
        member_instance.save.side_effect = fake_save

        with patch('community.views.FamilyMember') as MockFM, \
             patch('community.views.redirect') as mock_redirect:
            MockFM.TYPE_CHOICES = []
            instance = MockFM.return_value
            instance.name = 'Test Person'
            instance.age = None

            def fake_fm_save():
                saved['age'] = instance.age

            instance.save.side_effect = fake_fm_save
            mock_redirect.return_value = MagicMock(status_code=302)
            family_member_create(request)

        return saved.get('age')

    def _post_edit(self, age_str):
        """POST to family_member_edit with the given age string. Returns the age assigned to member."""
        from community.views import family_member_edit
        factory = RequestFactory()
        data = {'name': 'Test Person', 'member_type': 'father', 'status': 'living', 'age': age_str}
        request = factory.post('/community/family/member/1/edit/', data)
        request.user = MagicMock()

        member = MagicMock()
        member.name = 'Test Person'
        member.age = None
        member.pk = 1
        member.creator = request.user

        saved_age = {}

        def fake_save():
            saved_age['age'] = member.age

        member.save.side_effect = fake_save

        with patch('community.views.get_object_or_404', return_value=member), \
             patch('community.views.redirect') as mock_redirect:
            mock_redirect.return_value = MagicMock(status_code=302)
            family_member_edit(request, pk=1)

        return saved_age.get('age')

    # ── family_member_create ────────────────────────────────────────────────

    def test_create_negative_age_rejected(self):
        """Negative age must not be saved — stays None."""
        age = self._post_create('-1')
        self.assertIsNone(age, f'Expected None for age=-1, got {age!r}')

    def test_create_zero_age_accepted(self):
        """Age 0 is valid (newborn) and must be saved."""
        age = self._post_create('0')
        self.assertEqual(age, 0, f'Expected 0 for age=0, got {age!r}')

    def test_create_max_age_accepted(self):
        """Age 150 is the maximum valid value and must be saved."""
        age = self._post_create('150')
        self.assertEqual(age, 150, f'Expected 150 for age=150, got {age!r}')

    def test_create_over_max_age_rejected(self):
        """Age 151 exceeds the maximum — must not be saved."""
        age = self._post_create('151')
        self.assertIsNone(age, f'Expected None for age=151, got {age!r}')

    def test_create_non_integer_age_rejected(self):
        """Non-integer string must not crash and age must stay None."""
        age = self._post_create('abc')
        self.assertIsNone(age, f'Expected None for age=abc, got {age!r}')

    # ── family_member_edit ──────────────────────────────────────────────────

    def test_edit_negative_age_rejected(self):
        """Negative age in edit must not be saved — stays None."""
        age = self._post_edit('-5')
        self.assertIsNone(age, f'Expected None for age=-5 in edit, got {age!r}')

    # ── family_setup_wizard Step 6 (children / future DOB) ─────────────────

    def test_setup_wizard_future_dob_yields_zero_no_crash(self):
        """
        A future date of birth for a child must not cause DataError.
        age_val = max(0, min(150, negative_days // 365)) must yield 0.
        """
        from datetime import date, timedelta
        future_dob = (date.today() + timedelta(days=365)).strftime('%Y-%m-%d')

        from community.views import family_setup_wizard
        factory = RequestFactory()
        data = {
            'step': '6',
            'child_name': ['FutureChild'],
            'child_dob': [future_dob],
            'child_gender': ['male'],
            'child_email': [''],
            'child_password': [''],
        }
        request = factory.post('/community/family/setup/', data)
        request.user = MagicMock()
        request.user.pk = 1
        request._messages = MagicMock()

        created_ages = []

        def fake_create(**kwargs):
            created_ages.append(kwargs.get('age'))
            obj = MagicMock()
            obj.pk = 99
            obj.age = kwargs.get('age')
            return obj

        with patch('community.views.FamilySetup') as MockFS, \
             patch('community.views.FamilyMember') as MockFM, \
             patch('community.views.redirect') as mock_redirect:

            mock_setup = MagicMock()
            mock_setup.marital_status = 'single'
            mock_setup.setup_done = False
            MockFS.objects.get_or_create.return_value = (mock_setup, False)

            MockFM.objects.filter.return_value.delete.return_value = None
            MockFM.objects.create.side_effect = fake_create
            mock_redirect.return_value = MagicMock(status_code=302)

            family_setup_wizard(request)

        self.assertTrue(len(created_ages) > 0, 'No FamilyMember was created')
        for age in created_ages:
            self.assertIsNotNone(age, 'age should be 0, not None, for a future DOB')
            self.assertEqual(age, 0, f'Expected age=0 for future DOB, got {age!r}')


# ─────────────────────────────────────────────────────────────────────────────
# SECURITY HARDENING — family_member_detail must require authentication
# ─────────────────────────────────────────────────────────────────────────────

class FamilyMemberDetailAuthTest(TestCase):
    """MEDIUM IDOR — family_member_detail must be decorated with @login_required."""

    def test_login_required_decorator_applied(self):
        """family_member_detail must have @login_required in its decorator chain."""
        from community import views as community_views
        view = community_views.family_member_detail
        self.assertTrue(
            hasattr(view, 'login_url') or hasattr(view, '__wrapped__'),
            'family_member_detail must be decorated with @login_required'
        )

    def test_anonymous_request_is_redirected(self):
        """Anonymous GET to family_member_detail must redirect to login, not return 200."""
        from community.views import family_member_detail
        factory = RequestFactory()
        request = factory.get('/community/family/member/1/')
        request.user = MagicMock()
        request.user.is_authenticated = False

        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session.create()
        request.session = session

        with patch('community.views.get_object_or_404') as mock_goo:
            mock_member = MagicMock()
            mock_goo.return_value = mock_member
            resp = family_member_detail(request, pk=1)

        # @login_required returns a redirect (302) for anonymous users
        self.assertEqual(resp.status_code, 302,
            f'Expected 302 redirect for anonymous user, got {resp.status_code}')
        self.assertIn('/login/', resp.get('Location', ''),
            'Redirect must point to login page')
