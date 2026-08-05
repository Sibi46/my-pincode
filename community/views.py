from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import FamilyStory, FamilyStoryLike, FamilyStoryComment

MODULES = [
    {'slug': 'family-stories',      'icon': '📸', 'name': 'Family Stories',        'desc': 'Birthdays, achievements, traditions & celebrations',  'color': '#e11d48', 'soon': False},
    {'slug': 'school-corner',       'icon': '🏫', 'name': 'School Corner',          'desc': 'Events, sports day, science fair & admissions',       'color': '#0a66c2', 'soon': True},
    {'slug': 'student-success',     'icon': '🎓', 'name': 'Student Success',        'desc': 'Academics, sports, art, music & scholarships',        'color': '#7c3aed', 'soon': True},
    {'slug': 'kids-corner',         'icon': '🧒', 'name': 'Kids Corner',            'desc': 'Safe space for children\'s stories & activities',     'color': '#f59e0b', 'soon': True},
    {'slug': 'parenting',           'icon': '👨‍👩‍👧', 'name': 'Parenting',              'desc': 'Tips, advice & family activity ideas',               'color': '#059669', 'soon': True},
    {'slug': 'grandparents-archive','icon': '👴', 'name': 'Grandparents Archive',   'desc': 'Elder stories, memories & community wisdom',          'color': '#92400e', 'soon': True},
    {'slug': 'local-heroes',        'icon': '🦸', 'name': 'Local Heroes',           'desc': 'Celebrate unsung heroes in your community',           'color': '#dc2626', 'soon': True},
    {'slug': 'community-events',    'icon': '📅', 'name': 'Community Events',       'desc': 'Local gatherings, festivals & announcements',         'color': '#0891b2', 'soon': True},
    {'slug': 'volunteer',           'icon': '🤝', 'name': 'Volunteer Activities',   'desc': 'Blood donation, tree plantation & health camps',      'color': '#16a34a', 'soon': True},
    {'slug': 'business-stories',    'icon': '🏪', 'name': 'Business Stories',       'desc': 'Local business journeys — not ads, real stories',     'color': '#ea580c', 'soon': True},
    {'slug': 'hall-of-fame',        'icon': '🏆', 'name': 'Hall of Fame',           'desc': 'Top achievers per pincode — recognised & celebrated', 'color': '#ca8a04', 'soon': True},
    {'slug': 'jobs',                'icon': '💼', 'name': 'Jobs',                   'desc': 'Local employment opportunities near your pincode',    'color': '#0a66c2', 'soon': False},
    {'slug': 'marketplace',         'icon': '🛒', 'name': 'Marketplace',            'desc': 'Buy & sell locally within your community',            'color': '#7c3aed', 'soon': True},
    {'slug': 'community-watch',     'icon': '👁️', 'name': 'Community Watch',        'desc': 'Report, block & keep the community safe',             'color': '#374151', 'soon': True},
    {'slug': 'notifications',       'icon': '🔔', 'name': 'Notifications & Search', 'desc': 'Alerts, reminders & pincode-based search',            'color': '#0891b2', 'soon': True},
]

CAT_ICONS = {
    'birthday':    '🎂',
    'achievement': '🏅',
    'tradition':   '🎎',
    'celebration': '🎉',
    'vacation':    '✈️',
    'gardening':   '🌱',
    'other':       '📸',
}

CAT_LABELS = {
    'birthday':    'Birthday',
    'achievement': 'Achievement',
    'tradition':   'Tradition',
    'celebration': 'Celebration',
    'vacation':    'Vacation',
    'gardening':   'Gardening',
    'other':       'Other',
}


# ── COMMUNITY HUB ──────────────────────────────────────────────────────────────
def hub(request):
    return render(request, 'community/hub.html', {'modules': MODULES})


def module_page(request, slug):
    module = next((m for m in MODULES if m['slug'] == slug), None)
    if not module:
        from django.http import Http404
        raise Http404
    if slug == 'jobs':
        return redirect('/jobs/')
    if slug == 'family-stories':
        return redirect('/community/family-stories/')
    return render(request, 'community/coming_soon.html', {'module': module})


# ── FAMILY STORIES ─────────────────────────────────────────────────────────────
def family_stories_feed(request):
    cat = request.GET.get('cat', '')
    stories = FamilyStory.objects.filter(is_active=True).select_related('user')
    if cat:
        stories = stories.filter(category=cat)

    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(FamilyStoryLike.objects.filter(user=request.user).values_list('story_id', flat=True))

    return render(request, 'community/family_stories.html', {
        'stories':   stories,
        'liked_ids': liked_ids,
        'active_cat': cat,
        'cat_icons': CAT_ICONS,
        'cat_labels': CAT_LABELS,
    })


@login_required
def family_story_post(request):
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        content  = request.POST.get('content', '').strip()
        category = request.POST.get('category', 'other')
        image    = request.FILES.get('image')
        pincode  = getattr(request.user, 'pincode', '') or ''

        if title and content:
            FamilyStory.objects.create(
                user=request.user,
                title=title,
                content=content,
                category=category,
                image=image,
                pincode=pincode,
            )
            messages.success(request, 'Your story has been shared!')
            return redirect('/community/family-stories/')

    return render(request, 'community/family_story_post.html', {
        'cat_icons':  CAT_ICONS,
        'cat_labels': CAT_LABELS,
    })


def family_story_detail(request, pk):
    story = get_object_or_404(FamilyStory, pk=pk, is_active=True)
    comments = story.comments.select_related('user').all()
    liked = (
        request.user.is_authenticated and
        FamilyStoryLike.objects.filter(user=request.user, story=story).exists()
    )
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            FamilyStoryComment.objects.create(user=request.user, story=story, text=text)
        return redirect(f'/community/family-stories/{pk}/')

    return render(request, 'community/family_story_detail.html', {
        'story':    story,
        'comments': comments,
        'liked':    liked,
        'cat_icons': CAT_ICONS,
    })


@login_required
def family_story_like(request, pk):
    story = get_object_or_404(FamilyStory, pk=pk)
    like, created = FamilyStoryLike.objects.get_or_create(user=request.user, story=story)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': story.like_count()})


@login_required
def family_story_delete(request, pk):
    story = get_object_or_404(FamilyStory, pk=pk, user=request.user)
    story.delete()
    return redirect('/community/family-stories/')
