"""
Management command: send_birthday_notifications
Run daily (e.g. via cron at 08:00).
Sends birthday-today and 2-day-reminder notifications using jobs.UserNotification.
Idempotent — BirthdayNotificationLog prevents duplicate sends.
"""
import calendar
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from community.models import BirthdayNotificationLog, FamilyMember, FamilySetup
from jobs.models import UserNotification


def _birthday_matches(dob: date, target: date) -> bool:
    """True if dob's month/day equals target's month/day. Feb 29 → Feb 28 in non-leap years."""
    if dob.month == 2 and dob.day == 29:
        if not calendar.isleap(target.year):
            return target.month == 2 and target.day == 28
    return dob.month == target.month and dob.day == target.day


def _notify_year(target: date) -> int:
    """The calendar year this birthday notification belongs to."""
    return target.year


def _send(user, dob_owner_key, family_member, notif_type, title, message, link=''):
    """Create a UserNotification + BirthdayNotificationLog if not already sent."""
    year = date.today().year
    _, created = BirthdayNotificationLog.objects.get_or_create(
        user=user,
        dob_owner_key=dob_owner_key,
        year=year,
        notif_type=notif_type,
        defaults={'family_member': family_member},
    )
    if not created:
        return False  # already sent
    UserNotification.objects.create(
        user=user,
        title=title,
        message=message,
        notif_type='success' if notif_type == 'today' else 'info',
        link=link,
    )
    return True


class Command(BaseCommand):
    help = 'Send birthday-today and 2-day-reminder notifications to family hub users.'

    def handle(self, *args, **options):
        today = date.today()
        in_two = today + timedelta(days=2)

        sent_today = 0
        sent_reminder = 0

        for setup in FamilySetup.objects.select_related('user').iterator():
            user = setup.user

            # ── self_dob ──────────────────────────────────────────────────────
            if setup.self_dob:
                name = setup.self_full_name or user.get_full_name() or 'You'
                if _birthday_matches(setup.self_dob, today):
                    ok = _send(
                        user, 'self', None, 'today',
                        '🎉 Happy Birthday!',
                        f'🎉 Today is your birthday, {name}! Wishing you a wonderful day.',
                        '/community/family/',
                    )
                    if ok:
                        sent_today += 1
                elif _birthday_matches(setup.self_dob, in_two):
                    ok = _send(
                        user, 'self', None, 'reminder',
                        '🎂 Birthday Reminder',
                        f'🎂 Your birthday is in 2 days ({in_two.strftime("%d %b")})! '
                        f'Your family will want to celebrate with you.',
                        '/community/family/',
                    )
                    if ok:
                        sent_reminder += 1

            # ── partner_dob ───────────────────────────────────────────────────
            if setup.partner_dob and setup.partner_full_name:
                name = setup.partner_full_name
                if _birthday_matches(setup.partner_dob, today):
                    ok = _send(
                        user, 'partner', None, 'today',
                        '🎉 It\'s a Birthday!',
                        f'🎉 Today is {name}\'s birthday! '
                        f'Send your wishes and make their day special.',
                        '/community/family/',
                    )
                    if ok:
                        sent_today += 1
                elif _birthday_matches(setup.partner_dob, in_two):
                    ok = _send(
                        user, 'partner', None, 'reminder',
                        '🎂 Birthday Reminder',
                        f'🎂 {name}\'s birthday is in 2 days ({in_two.strftime("%d %b")}). '
                        f'Don\'t forget to wish {name}!',
                        '/community/family/',
                    )
                    if ok:
                        sent_reminder += 1

            # ── FamilyMember DOBs ─────────────────────────────────────────────
            members = (
                FamilyMember.objects
                .filter(creator=user, status='living', dob__isnull=False)
                .only('pk', 'name', 'dob', 'member_type')
            )
            for member in members:
                key = str(member.pk)
                name = member.name
                gift_link = f'/community/family/birthday-gift/{member.pk}/'

                if _birthday_matches(member.dob, today):
                    ok = _send(
                        user, key, member, 'today',
                        '🎉 It\'s a Birthday!',
                        f'🎉 Today is {name}\'s birthday! '
                        f'Send your wishes and make their day special.',
                        gift_link,
                    )
                    if ok:
                        sent_today += 1
                elif _birthday_matches(member.dob, in_two):
                    ok = _send(
                        user, key, member, 'reminder',
                        '🎂 Birthday Reminder',
                        f'🎂 {name}\'s birthday is in 2 days ({in_two.strftime("%d %b")}). '
                        f'Don\'t forget to wish {name}!',
                        gift_link,
                    )
                    if ok:
                        sent_reminder += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Birthday notifications done — '
                f'{sent_today} birthday-today, {sent_reminder} reminders sent.'
            )
        )
