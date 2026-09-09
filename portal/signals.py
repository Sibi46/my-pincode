from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import PortalNotification

JOIN_POINTS     = 5   # points on community join approval
ATTEND_POINTS   = 10  # points on event attendance confirmation


@receiver(post_save, sender=PortalNotification)
def push_notification(sender, instance, created, **kwargs):
    if not created:
        return
    channel_layer = get_channel_layer()
    group_name = f'notif_user_{instance.user_id}'
    async_to_sync(channel_layer.group_send)(group_name, {
        'type': 'send_notification',
        'message': instance.message,
        'link': instance.link or '',
        'notif_type': instance.notif_type,
    })


@receiver(post_save, sender='portal.CommunityMember')
def award_join_points(sender, instance, created, **kwargs):
    """Award 5 points when membership is approved (first time only)."""
    if instance.status != 'approved':
        return
    from .models import MemberPoints, award_points
    # Only award once — check if they already have a join-points log
    from .models import PointAuditLog
    already = PointAuditLog.objects.filter(
        user=instance.user,
        community=instance.community,
        action='Joined community',
    ).exists()
    if not already:
        award_points(instance.user, instance.community, JOIN_POINTS, 'Joined community')
        PortalNotification.objects.create(
            user=instance.user,
            notif_type='points',
            message=f'🎉 You earned {JOIN_POINTS} points for joining {instance.community.name}!',
            link=f'/portal/c/{instance.community.slug}/my-contribution/',
        )


@receiver(post_save, sender='portal.Participation')
def award_attendance_points(sender, instance, created, **kwargs):
    """Award 10 points when event participation is confirmed (first time only)."""
    if instance.status != 'approved' or not instance.event:
        return
    from .models import award_points, PointAuditLog
    action_note = f'Attended event: {instance.event.title}'
    already = PointAuditLog.objects.filter(
        user=instance.user,
        community=instance.community,
        action=action_note,
    ).exists()
    if not already:
        award_points(instance.user, instance.community, ATTEND_POINTS, action_note)
        PortalNotification.objects.create(
            user=instance.user,
            notif_type='points',
            message=f'🏅 You earned {ATTEND_POINTS} points for attending "{instance.event.title}"!',
            link=f'/portal/c/{instance.community.slug}/my-contribution/',
        )
