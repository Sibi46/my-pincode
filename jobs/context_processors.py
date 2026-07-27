from django.utils import timezone
from .models import Advertisement


def site_ads(request):
    today = timezone.now().date()
    ads = (Advertisement.objects
           .filter(status='active', start_date__lte=today, end_date__gte=today)
           .exclude(image='')
           .select_related('advertiser', 'package')[:30])

    by_type = {}
    for ad in ads:
        t = ad.package.ad_type
        by_type.setdefault(t, []).append(ad)

    pending_ad_posts = 0
    if request.user.is_authenticated and getattr(request.user, 'admin_role', '') == 'super_admin':
        from .models import AdPost
        pending_ad_posts = AdPost.objects.filter(status='pending').count()

    return {
        'site_ads': ads,
        'ads_by_type': by_type,
        'pending_ad_posts': pending_ad_posts,
    }
