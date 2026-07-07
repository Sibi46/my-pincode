import datetime
from django.core.management.base import BaseCommand
from jobs.models import Job, UserNotification


class Command(BaseCommand):
    help = 'Expire free-plan jobs past their expiry date and notify employers'

    def handle(self, *args, **options):
        today = datetime.date.today()
        expired_jobs = Job.objects.filter(
            job_plan='free',
            plan_expires_at__lt=today,
            status='active',
        ).select_related('posted_by')

        count = 0
        for job in expired_jobs:
            job.job_plan = 'free_expired'
            job.save(update_fields=['job_plan'])

            UserNotification.objects.create(
                user=job.posted_by,
                title=f'Free Week Ended: {job.title}',
                message=(
                    f'Your 1-week free listing for "{job.title}" has expired. '
                    'Upgrade to 12 weeks for just ₹499 and keep attracting candidates!'
                ),
                notif_type='warning',
                link=f'/jobs/{job.pk}/select-plan/',
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Expired {count} free-plan job(s) and notified employers.'))
