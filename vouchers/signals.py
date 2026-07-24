from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Business


@receiver(pre_save, sender=Business)
def notify_business_on_approval(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = Business.objects.get(pk=instance.pk)
    except Business.DoesNotExist:
        return

    if previous.status != 'approved' and instance.status == 'approved':
        subject = f"Congratulations! Your business is approved – MYPINCOD"
        message = (
            f"Dear {instance.owner_name},\n\n"
            f"Great news! Your business '{instance.business_name}' has been approved on MYPINCOD.\n\n"
            f"You can now log in and:\n"
            f"  • Add your branches\n"
            f"  • Add employees\n"
            f"  • Purchase Voucher Listing Slots\n"
            f"  • Create and publish Gift Vouchers\n\n"
            f"Login here: https://www.mypincod.com/vouchers/dashboard/\n\n"
            f"Regards,\nMYPINCOD Team"
        )
        try:
            send_mail(
                subject, message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True,
            )
        except Exception:
            pass

    if previous.status != 'rejected' and instance.status == 'rejected':
        subject = "Business Registration Update – MYPINCOD"
        message = (
            f"Dear {instance.owner_name},\n\n"
            f"We regret to inform you that your business registration for "
            f"'{instance.business_name}' could not be approved at this time.\n\n"
            f"Reason: {instance.rejection_reason or 'Please contact support for details.'}\n\n"
            f"You may re-apply after addressing the above.\n\n"
            f"Regards,\nMYPINCOD Team"
        )
        try:
            send_mail(
                subject, message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=True,
            )
        except Exception:
            pass
