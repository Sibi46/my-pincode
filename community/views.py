from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import (FamilyStory, FamilyStoryLike, FamilyStoryComment,
                     StudentSuccess, StudentSuccessLike, StudentSuccessComment,
                     KidsPost, KidsPostLike, KidsPostComment,
                     ParentingPost, ParentingLike, ParentingComment,
                     GrandparentStory, GrandparentLike, GrandparentComment,
                     LocalHero, LocalHeroLike, LocalHeroComment,
                     CommunityEvent, EventRSVP, EventComment,
                     VolunteerActivity, VolunteerSignup, VolunteerComment,
                     BusinessStory, BusinessStoryLike, BusinessStoryComment,
                     HallOfFameEntry, HallOfFameVote, HallOfFameComment,
                     MarketplaceListing, ListingInterest, ListingComment,
                     WatchReport, WatchConfirm, WatchComment,
                     Notification, FamilyMember, FamilySetup)

MODULES = [
    {'slug': 'family',       'icon': '👨‍👩‍👧', 'name': 'Family Hub',     'desc': 'Family Stories · Parenting · Grandparents Archive',  'color': '#e11d48', 'soon': False},
    {'slug': 'school-kids', 'icon': '🏫', 'name': 'School & Kids',  'desc': 'School Corner · Student Success · Kids Corner',       'color': '#0a66c2', 'soon': False},
    {'slug': 'local-heroes',        'icon': '🦸', 'name': 'Local Heroes',           'desc': 'Celebrate unsung heroes in your community',           'color': '#dc2626', 'soon': False},
    {'slug': 'community-events',    'icon': '📅', 'name': 'Community Events',       'desc': 'Local gatherings, festivals & announcements',         'color': '#0891b2', 'soon': False},
    {'slug': 'volunteer',           'icon': '🤝', 'name': 'Volunteer Activities',   'desc': 'Blood donation, tree plantation & health camps',      'color': '#16a34a', 'soon': False},
    {'slug': 'business-stories',    'icon': '🏪', 'name': 'Business Stories',       'desc': 'Local business journeys — not ads, real stories',     'color': '#ea580c', 'soon': False},
    {'slug': 'community-watch',     'icon': '👁️', 'name': 'Community Watch',        'desc': 'Report, block & keep the community safe',             'color': '#374151', 'soon': False},
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
    if slug == 'family':
        return redirect('/community/family/')
    if slug == 'school-kids':
        return redirect('/community/school-kids/')
    if slug == 'family-stories':
        return redirect('/community/family/')
    if slug == 'parenting':
        return redirect('/community/family/?tab=parenting')
    if slug == 'grandparents-archive':
        return redirect('/community/family/?tab=grandparents')
    if slug == 'school-corner':
        return redirect('/community/school-kids/')
    if slug == 'student-success':
        return redirect('/community/school-kids/?tab=student')
    if slug == 'kids-corner':
        return redirect('/community/school-kids/?tab=kids')
    if slug == 'local-heroes':
        return redirect('/community/local-heroes/')
    if slug == 'community-events':
        return redirect('/community/events/')
    if slug == 'volunteer':
        return redirect('/community/volunteer/')
    if slug == 'business-stories':
        return redirect('/community/business-stories/')
    if slug == 'hall-of-fame':
        return redirect('/community/hall-of-fame/')
    if slug == 'marketplace':
        return redirect('/community/marketplace/')
    if slug == 'community-watch':
        return redirect('/community/community-watch/')
    if slug == 'notifications':
        return redirect('/community/notifications/')
    return render(request, 'community/coming_soon.html', {'module': module})


# ── FAMILY HUB ────────────────────────────────────────────────────────────────
def family_hub(request):
    setup = None
    if request.user.is_authenticated:
        setup, _ = FamilySetup.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            setup.grandfather_count = int(request.POST.get('grandfather_count', 0))
            setup.grandmother_count = int(request.POST.get('grandmother_count', 0))
            setup.father_count      = int(request.POST.get('father_count', 0))
            setup.mother_count      = int(request.POST.get('mother_count', 0))
            setup.son_count         = int(request.POST.get('son_count', 0))
            setup.daughter_count    = int(request.POST.get('daughter_count', 0))
            setup.uncle_count       = int(request.POST.get('uncle_count', 0))
            setup.aunt_count        = int(request.POST.get('aunt_count', 0))
            setup.cousin_count      = int(request.POST.get('cousin_count', 0))
            setup.pet_count         = int(request.POST.get('pet_count', 0))
            setup.save()
            return redirect('/community/family/')

    ROWS = [
        ('👴', 'Grandfather', 'grandfather_count'),
        ('👵', 'Grandmother', 'grandmother_count'),
        ('👨', 'Father',      'father_count'),
        ('👩', 'Mother',      'mother_count'),
        ('👦', 'Son',         'son_count'),
        ('👧', 'Daughter',    'daughter_count'),
        ('🧔', 'Uncle',       'uncle_count'),
        ('👩‍🦳', 'Aunt',      'aunt_count'),
        ('🧑', 'Cousin',      'cousin_count'),
        ('🐾', 'Pet',         'pet_count'),
    ]
    TYPE_ICON = {
        'grandfather':'👴','grandmother':'👵','father':'👨','mother':'👩',
        'son':'👦','daughter':'👧','uncle':'🧔','aunt':'👩‍🦳','cousin':'🧑','pet':'🐾',
    }
    FIELD_TO_TYPE = {
        'grandfather_count':'grandfather','grandmother_count':'grandmother',
        'father_count':'father','mother_count':'mother','son_count':'son',
        'daughter_count':'daughter','uncle_count':'uncle','aunt_count':'aunt',
        'cousin_count':'cousin','pet_count':'pet',
    }
    setup_rows = [(icon, label, field, getattr(setup, field, 0) if setup else 0)
                  for icon, label, field in ROWS]
    active_tabs = []
    if setup:
        for icon, label, field in ROWS:
            cnt = getattr(setup, field, 0)
            if cnt > 0:
                mtype = FIELD_TO_TYPE[field]
                active_tabs.append((mtype, label, icon, cnt))

    active_type = request.GET.get('tab', active_tabs[0][0] if active_tabs else '')
    members = FamilyMember.objects.filter(member_type=active_type).select_related('creator') if active_type else []

    return render(request, 'community/family_hub.html', {
        'setup':       setup,
        'setup_rows':  setup_rows,
        'active_tabs': active_tabs,
        'active_type': active_type,
        'members':     members,
    })


@login_required
def family_member_create(request):
    if request.method == 'POST':
        m = FamilyMember(
            creator     = request.user,
            member_type = request.POST.get('member_type', 'other'),
            name        = request.POST.get('name', '').strip(),
            why         = request.POST.get('why', '').strip(),
            description = request.POST.get('description', '').strip(),
            about       = request.POST.get('about', '').strip(),
            village     = request.POST.get('village', '').strip(),
            house_name  = request.POST.get('house_name', '').strip(),
            occupation  = request.POST.get('occupation', '').strip(),
            education   = request.POST.get('education', '').strip(),
            phone       = request.POST.get('phone', '').strip(),
            status      = request.POST.get('status', 'living'),
            species     = request.POST.get('species', '').strip(),
            breed       = request.POST.get('breed', '').strip(),
        )
        if request.POST.get('age'):
            try: m.age = int(request.POST['age'])
            except ValueError: pass
        if request.POST.get('dob'):
            from datetime import date
            try:
                parts = request.POST['dob'].split('-')
                m.dob = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except Exception: pass
        if request.POST.get('death_date') and m.status == 'passed':
            from datetime import date
            try:
                parts = request.POST['death_date'].split('-')
                m.death_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except Exception: pass
        if request.FILES.get('photo'):
            m.photo = request.FILES['photo']
        if m.name:
            m.save()
            return redirect(f'/community/family/member/{m.pk}/')
    return render(request, 'community/family_member_create.html', {
        'type_choices': FamilyMember.TYPE_CHOICES,
    })


def family_member_detail(request, pk):
    member = get_object_or_404(FamilyMember, pk=pk)
    return render(request, 'community/family_member_detail.html', {'member': member})


# ── SCHOOL & KIDS HUB ──────────────────────────────────────────────────────────
def school_kids_hub(request):
    tab = request.GET.get('tab', 'school')

    # School Corner
    schools = School.objects.all().order_by('-created_at')

    # Student Success
    ss_stories = StudentSuccess.objects.filter(is_active=True).select_related('user')
    ss_liked   = set()
    if request.user.is_authenticated:
        ss_liked = set(StudentSuccessLike.objects.filter(
            user=request.user).values_list('success_id', flat=True))

    # Kids Corner
    kids_posts = KidsPost.objects.filter(is_active=True).select_related('posted_by')
    kids_liked = set()
    if request.user.is_authenticated:
        kids_liked = set(KidsPostLike.objects.filter(
            user=request.user).values_list('post_id', flat=True))

    return render(request, 'community/school_kids_hub.html', {
        'tab':          tab,
        'schools':      schools,
        'ss_stories':   ss_stories,
        'ss_liked':     ss_liked,
        'ss_cat_icons': SS_CAT_ICONS,
        'kids_posts':   kids_posts,
        'kids_liked':   kids_liked,
        'kids_type_icons': KIDS_TYPE_ICONS,
        'kids_types':   KidsPost.TYPE_CHOICES,
    })


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


# ── SCHOOL CORNER ──────────────────────────────────────────────────────────────
from .models import School, SchoolPost, SchoolPostLike, SchoolPostComment, SchoolFollow, SchoolAdmin

POST_TYPE_ICONS = {
    'annual_day':   '🎭',
    'sports_day':   '⚽',
    'science_fair': '🔬',
    'admission':    '📋',
    'achievement':  '🏆',
    'event':        '📅',
    'announcement': '📢',
    'other':        '📌',
}


def school_list(request):
    q       = request.GET.get('q', '').strip()
    pincode = request.GET.get('pin', '').strip()
    schools = School.objects.all()
    if q:
        schools = schools.filter(name__icontains=q)
    if pincode:
        schools = schools.filter(pincode=pincode)
    return render(request, 'community/school_list.html', {
        'schools': schools, 'q': q, 'pincode': pincode,
    })


def school_detail(request, pk):
    school   = get_object_or_404(School, pk=pk)
    posts    = school.posts.filter(is_active=True)
    post_type = request.GET.get('type', '')
    if post_type:
        posts = posts.filter(post_type=post_type)

    following = (
        request.user.is_authenticated and
        SchoolFollow.objects.filter(user=request.user, school=school).exists()
    )
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(SchoolPostLike.objects.filter(
            user=request.user, post__school=school
        ).values_list('post_id', flat=True))

    is_admin = (request.user.is_authenticated and
                SchoolAdmin.objects.filter(school=school, user=request.user).exists())

    return render(request, 'community/school_detail.html', {
        'school':      school,
        'posts':       posts,
        'following':   following,
        'liked_ids':   liked_ids,
        'post_type':   post_type,
        'type_icons':  POST_TYPE_ICONS,
        'post_types':  SchoolPost.POST_TYPE_CHOICES,
        'is_admin':    is_admin,
    })


@login_required
def school_register(request):
    if request.method == 'POST':
        name  = request.POST.get('name', '').strip()
        stype = request.POST.get('school_type', 'secondary')
        addr  = request.POST.get('address', '').strip()
        pin   = request.POST.get('pincode', '').strip()
        about = request.POST.get('about', '').strip()
        phone     = request.POST.get('phone', '').strip()
        principal = request.POST.get('principal_name', '').strip()
        vice_prin = request.POST.get('vice_principal', '').strip()
        logo  = request.FILES.get('logo')
        cover = request.FILES.get('cover')
        if name:
            school = School.objects.create(
                name=name, school_type=stype, address=addr,
                pincode=pin, about=about, phone=phone,
                principal_name=principal, vice_principal=vice_prin,
                logo=logo, cover=cover, created_by=request.user,
            )
            SchoolAdmin.objects.create(school=school, user=request.user, role='owner', added_by=request.user)
            messages.success(request, f'{name} has been registered! You are the owner.')
            return redirect(f'/community/school-corner/{school.pk}/dashboard/')
    return render(request, 'community/school_register.html', {
        'type_choices': School.TYPE_CHOICES,
    })


@login_required
def school_post_create(request, pk):
    school = get_object_or_404(School, pk=pk)
    if not SchoolAdmin.objects.filter(school=school, user=request.user).exists():
        messages.error(request, 'Only school admins can post.')
        return redirect(f'/community/school-corner/{pk}/')
    if request.method == 'POST':
        title     = request.POST.get('title', '').strip()
        content   = request.POST.get('content', '').strip()
        post_type = request.POST.get('post_type', 'other')
        image     = request.FILES.get('image')
        if title and content:
            SchoolPost.objects.create(
                school=school, posted_by=request.user,
                title=title, content=content,
                post_type=post_type, image=image,
            )
            messages.success(request, 'Post published!')
        return redirect(f'/community/school-corner/{pk}/dashboard/')
    return render(request, 'community/school_post_form.html', {
        'school':      school,
        'post_types':  SchoolPost.POST_TYPE_CHOICES,
        'type_icons':  POST_TYPE_ICONS,
    })


@login_required
def school_dashboard(request, pk):
    school = get_object_or_404(School, pk=pk)
    admin_rec = SchoolAdmin.objects.filter(school=school, user=request.user).first()
    if not admin_rec:
        messages.error(request, 'Access denied.')
        return redirect(f'/community/school-corner/{pk}/')

    admins   = SchoolAdmin.objects.filter(school=school, role='admin').select_related('user', 'added_by')
    teachers = SchoolAdmin.objects.filter(school=school, role='teacher').select_related('user', 'added_by')
    posts    = school.posts.filter(is_active=True).select_related('posted_by')
    error  = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action in ('add_admin', 'add_teacher') and admin_rec.role in ('owner', 'admin'):
            username = request.POST.get('username', '').strip()
            new_role = 'teacher' if action == 'add_teacher' else 'admin'
            if new_role == 'admin' and admin_rec.role != 'owner':
                error = 'Only owners can add admins.'
            else:
                try:
                    from django.contrib.auth import get_user_model
                    User2 = get_user_model()
                    new_user = User2.objects.get(username=username)
                    obj, created = SchoolAdmin.objects.get_or_create(
                        school=school, user=new_user,
                        defaults={'role': new_role, 'added_by': request.user}
                    )
                    if not created:
                        error = f'"{username}" already has a role in this school.'
                    else:
                        messages.success(request, f'{username} added as {new_role}.')
                except Exception:
                    error = f'User "{username}" not found.'

        elif action == 'remove_admin' and admin_rec.role in ('owner', 'admin'):
            uid = request.POST.get('user_id')
            qs = SchoolAdmin.objects.filter(school=school, user_id=uid).exclude(role='owner')
            if admin_rec.role == 'admin':
                qs = qs.filter(role='teacher')
            qs.delete()

        elif action == 'delete_post':
            post_id = request.POST.get('post_id')
            SchoolPost.objects.filter(pk=post_id, school=school).update(is_active=False)

        return redirect(f'/community/school-corner/{pk}/dashboard/')

    return render(request, 'community/school_dashboard.html', {
        'school':     school,
        'admin_rec':  admin_rec,
        'admins':     admins,
        'teachers':   teachers,
        'posts':      posts,
        'error':      error,
        'post_types': SchoolPost.POST_TYPE_CHOICES,
    })


@login_required
def school_follow(request, pk):
    school = get_object_or_404(School, pk=pk)
    follow, created = SchoolFollow.objects.get_or_create(user=request.user, school=school)
    if not created:
        follow.delete()
        following = False
    else:
        following = True
    return JsonResponse({'following': following, 'count': school.follower_count()})


@login_required
def school_post_like(request, pk):
    post = get_object_or_404(SchoolPost, pk=pk)
    like, created = SchoolPostLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.like_count()})


# ── STUDENT SUCCESS ────────────────────────────────────────────────────────────
SS_CAT_ICONS = {
    'academics':   '📚',
    'sports':      '⚽',
    'arts':        '🎨',
    'music':       '🎵',
    'scholarship': '🏅',
    'competition': '🏆',
    'other':       '🎓',
}

SS_CAT_LABELS = {
    'academics':   'Academics',
    'sports':      'Sports',
    'arts':        'Arts',
    'music':       'Music',
    'scholarship': 'Scholarship',
    'competition': 'Competition',
    'other':       'Other',
}


def student_success_feed(request):
    cat = request.GET.get('cat', '')
    stories = StudentSuccess.objects.filter(is_active=True).select_related('user')
    if cat:
        stories = stories.filter(category=cat)

    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(StudentSuccessLike.objects.filter(
            user=request.user).values_list('success_id', flat=True))

    return render(request, 'community/student_success.html', {
        'stories':    stories,
        'liked_ids':  liked_ids,
        'active_cat': cat,
        'cat_icons':  SS_CAT_ICONS,
        'cat_labels': SS_CAT_LABELS,
    })


@login_required
def student_success_post(request):
    if request.method == 'POST':
        title        = request.POST.get('title', '').strip()
        content      = request.POST.get('content', '').strip()
        category     = request.POST.get('category', 'other')
        student_name = request.POST.get('student_name', '').strip()
        school_name  = request.POST.get('school_name', '').strip()
        grade        = request.POST.get('grade', '').strip()
        image        = request.FILES.get('image')
        pincode      = getattr(request.user, 'pincode', '') or ''
        if title and content and student_name:
            StudentSuccess.objects.create(
                user=request.user, title=title, content=content,
                category=category, student_name=student_name,
                school_name=school_name, grade=grade,
                image=image, pincode=pincode,
            )
            messages.success(request, 'Success story shared!')
            return redirect('/community/student-success/')
    return render(request, 'community/student_success_post.html', {
        'cat_icons':  SS_CAT_ICONS,
        'cat_labels': SS_CAT_LABELS,
    })


def student_success_detail(request, pk):
    story    = get_object_or_404(StudentSuccess, pk=pk, is_active=True)
    comments = story.comments.select_related('user').all()
    liked    = (request.user.is_authenticated and
                StudentSuccessLike.objects.filter(user=request.user, success=story).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            StudentSuccessComment.objects.create(user=request.user, success=story, text=text)
        return redirect(f'/community/student-success/{pk}/')
    return render(request, 'community/student_success_detail.html', {
        'story':     story,
        'comments':  comments,
        'liked':     liked,
        'cat_icons': SS_CAT_ICONS,
    })


@login_required
def student_success_like(request, pk):
    story = get_object_or_404(StudentSuccess, pk=pk)
    like, created = StudentSuccessLike.objects.get_or_create(user=request.user, success=story)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': story.like_count()})


@login_required
def student_success_delete(request, pk):
    story = get_object_or_404(StudentSuccess, pk=pk, user=request.user)
    story.delete()
    return redirect('/community/student-success/')


# ── KIDS CORNER ────────────────────────────────────────────────────────────────
KIDS_TYPE_ICONS = {
    'story':    '📖',
    'drawing':  '🎨',
    'craft':    '✂️',
    'poem':     '✍️',
    'joke':     '😄',
    'activity': '🎯',
    'other':    '🧒',
}


def kids_corner_feed(request):
    post_type = request.GET.get('type', '')
    posts = KidsPost.objects.filter(is_active=True).select_related('posted_by')
    if post_type:
        posts = posts.filter(post_type=post_type)

    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(KidsPostLike.objects.filter(
            user=request.user).values_list('post_id', flat=True))

    return render(request, 'community/kids_corner.html', {
        'posts':      posts,
        'liked_ids':  liked_ids,
        'active_type': post_type,
        'type_icons': KIDS_TYPE_ICONS,
        'post_types': KidsPost.TYPE_CHOICES,
    })


@login_required
def kids_corner_post(request):
    if request.method == 'POST':
        title     = request.POST.get('title', '').strip()
        content   = request.POST.get('content', '').strip()
        post_type = request.POST.get('post_type', 'other')
        kid_name  = request.POST.get('kid_name', '').strip()
        age       = request.POST.get('age', '').strip()
        image     = request.FILES.get('image')
        pincode   = getattr(request.user, 'pincode', '') or ''
        if title and content and kid_name:
            KidsPost.objects.create(
                posted_by=request.user, title=title, content=content,
                post_type=post_type, kid_name=kid_name,
                age=int(age) if age.isdigit() else None,
                image=image, pincode=pincode,
            )
            messages.success(request, 'Posted to Kids Corner!')
            return redirect('/community/kids-corner/')
    return render(request, 'community/kids_corner_post.html', {
        'type_icons': KIDS_TYPE_ICONS,
        'post_types': KidsPost.TYPE_CHOICES,
    })


def kids_corner_detail(request, pk):
    post     = get_object_or_404(KidsPost, pk=pk, is_active=True)
    comments = post.comments.select_related('user').all()
    liked    = (request.user.is_authenticated and
                KidsPostLike.objects.filter(user=request.user, post=post).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            KidsPostComment.objects.create(user=request.user, post=post, text=text)
        return redirect(f'/community/kids-corner/{pk}/')
    return render(request, 'community/kids_corner_detail.html', {
        'post':       post,
        'comments':   comments,
        'liked':      liked,
        'type_icons': KIDS_TYPE_ICONS,
    })


@login_required
def kids_corner_like(request, pk):
    post = get_object_or_404(KidsPost, pk=pk)
    like, created = KidsPostLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.like_count()})


@login_required
def kids_corner_delete(request, pk):
    post = get_object_or_404(KidsPost, pk=pk, posted_by=request.user)
    post.delete()
    return redirect('/community/kids-corner/')


# ── PARENTING ──────────────────────────────────────────────────────────────────
PT_CAT_ICONS = {
    'tips':      '💡',
    'activity':  '🎯',
    'health':    '🏥',
    'education': '📚',
    'food':      '🥗',
    'emotion':   '💛',
    'other':     '👨‍👩‍👧',
}


def parenting_feed(request):
    cat   = request.GET.get('cat', '')
    posts = ParentingPost.objects.filter(is_active=True).select_related('user')
    if cat:
        posts = posts.filter(category=cat)
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(ParentingLike.objects.filter(
            user=request.user).values_list('post_id', flat=True))
    return render(request, 'community/parenting.html', {
        'posts':      posts,
        'liked_ids':  liked_ids,
        'active_cat': cat,
        'cat_icons':  PT_CAT_ICONS,
        'categories': ParentingPost.CAT_CHOICES,
    })


@login_required
def parenting_post(request):
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        content  = request.POST.get('content', '').strip()
        category = request.POST.get('category', 'other')
        image    = request.FILES.get('image')
        pincode  = getattr(request.user, 'pincode', '') or ''
        if title and content:
            ParentingPost.objects.create(
                user=request.user, title=title, content=content,
                category=category, image=image, pincode=pincode,
            )
            messages.success(request, 'Your parenting tip has been shared!')
            return redirect('/community/parenting/')
    return render(request, 'community/parenting_post.html', {
        'cat_icons':  PT_CAT_ICONS,
        'categories': ParentingPost.CAT_CHOICES,
    })


def parenting_detail(request, pk):
    post     = get_object_or_404(ParentingPost, pk=pk, is_active=True)
    comments = post.comments.select_related('user').all()
    liked    = (request.user.is_authenticated and
                ParentingLike.objects.filter(user=request.user, post=post).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            ParentingComment.objects.create(user=request.user, post=post, text=text)
        return redirect(f'/community/parenting/{pk}/')
    return render(request, 'community/parenting_detail.html', {
        'post':      post,
        'comments':  comments,
        'liked':     liked,
        'cat_icons': PT_CAT_ICONS,
    })


@login_required
def parenting_like(request, pk):
    post = get_object_or_404(ParentingPost, pk=pk)
    like, created = ParentingLike.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': post.like_count()})


@login_required
def parenting_delete(request, pk):
    post = get_object_or_404(ParentingPost, pk=pk, user=request.user)
    post.delete()
    return redirect('/community/parenting/')


# ── GRANDPARENTS ARCHIVE ───────────────────────────────────────────────────────
GP_CAT_ICONS = {
    'memory':    '🕰️',
    'wisdom':    '📜',
    'recipe':    '🍲',
    'tradition': '🎎',
    'history':   '🏛️',
    'other':     '👴',
}


def grandparents_feed(request):
    cat    = request.GET.get('cat', '')
    stories = GrandparentStory.objects.filter(is_active=True).select_related('user')
    if cat:
        stories = stories.filter(category=cat)
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(GrandparentLike.objects.filter(
            user=request.user).values_list('story_id', flat=True))
    return render(request, 'community/grandparents.html', {
        'stories':    stories,
        'liked_ids':  liked_ids,
        'active_cat': cat,
        'cat_icons':  GP_CAT_ICONS,
        'categories': GrandparentStory.CAT_CHOICES,
    })


@login_required
def grandparents_post(request):
    if request.method == 'POST':
        title      = request.POST.get('title', '').strip()
        content    = request.POST.get('content', '').strip()
        category   = request.POST.get('category', 'memory')
        elder_name = request.POST.get('elder_name', '').strip()
        age        = request.POST.get('age', '').strip()
        era        = request.POST.get('era', '').strip()
        image      = request.FILES.get('image')
        pincode    = getattr(request.user, 'pincode', '') or ''
        if title and content and elder_name:
            GrandparentStory.objects.create(
                user=request.user, title=title, content=content,
                category=category, elder_name=elder_name,
                age=int(age) if age.isdigit() else None,
                era=era, image=image, pincode=pincode,
            )
            messages.success(request, 'Story preserved in the archive!')
            return redirect('/community/grandparents-archive/')
    return render(request, 'community/grandparents_post.html', {
        'cat_icons':  GP_CAT_ICONS,
        'categories': GrandparentStory.CAT_CHOICES,
    })


def grandparents_detail(request, pk):
    story    = get_object_or_404(GrandparentStory, pk=pk, is_active=True)
    comments = story.comments.select_related('user').all()
    liked    = (request.user.is_authenticated and
                GrandparentLike.objects.filter(user=request.user, story=story).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            GrandparentComment.objects.create(user=request.user, story=story, text=text)
        return redirect(f'/community/grandparents-archive/{pk}/')
    return render(request, 'community/grandparents_detail.html', {
        'story':     story,
        'comments':  comments,
        'liked':     liked,
        'cat_icons': GP_CAT_ICONS,
    })


@login_required
def grandparents_like(request, pk):
    story = get_object_or_404(GrandparentStory, pk=pk)
    like, created = GrandparentLike.objects.get_or_create(user=request.user, story=story)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': story.like_count()})


@login_required
def grandparents_delete(request, pk):
    story = get_object_or_404(GrandparentStory, pk=pk, user=request.user)
    story.delete()
    return redirect('/community/grandparents-archive/')


# ── LOCAL HEROES ───────────────────────────────────────────────────────────────
LH_CAT_ICONS = {
    'social':      '🤝',
    'environment': '🌿',
    'education':   '📚',
    'health':      '🏥',
    'sports':      '🏅',
    'arts':        '🎨',
    'other':       '🦸',
}


def local_heroes_feed(request):
    cat   = request.GET.get('cat', '')
    heroes = LocalHero.objects.filter(is_active=True).select_related('posted_by')
    if cat:
        heroes = heroes.filter(category=cat)
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(LocalHeroLike.objects.filter(
            user=request.user).values_list('hero_id', flat=True))
    return render(request, 'community/local_heroes.html', {
        'heroes':     heroes,
        'liked_ids':  liked_ids,
        'active_cat': cat,
        'cat_icons':  LH_CAT_ICONS,
        'categories': LocalHero.CAT_CHOICES,
    })


@login_required
def local_hero_post(request):
    if request.method == 'POST':
        title     = request.POST.get('title', '').strip()
        content   = request.POST.get('content', '').strip()
        category  = request.POST.get('category', 'social')
        hero_name = request.POST.get('hero_name', '').strip()
        image     = request.FILES.get('image')
        pincode   = getattr(request.user, 'pincode', '') or ''
        if title and content and hero_name:
            LocalHero.objects.create(
                posted_by=request.user, title=title, content=content,
                category=category, hero_name=hero_name,
                image=image, pincode=pincode,
            )
            messages.success(request, 'Hero story published!')
            return redirect('/community/local-heroes/')
    return render(request, 'community/local_hero_post.html', {
        'cat_icons':  LH_CAT_ICONS,
        'categories': LocalHero.CAT_CHOICES,
    })


def local_hero_detail(request, pk):
    hero     = get_object_or_404(LocalHero, pk=pk, is_active=True)
    comments = hero.comments.select_related('user').all()
    liked    = (request.user.is_authenticated and
                LocalHeroLike.objects.filter(user=request.user, hero=hero).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            LocalHeroComment.objects.create(user=request.user, hero=hero, text=text)
        return redirect(f'/community/local-heroes/{pk}/')
    return render(request, 'community/local_hero_detail.html', {
        'hero':      hero,
        'comments':  comments,
        'liked':     liked,
        'cat_icons': LH_CAT_ICONS,
    })


@login_required
def local_hero_like(request, pk):
    hero = get_object_or_404(LocalHero, pk=pk)
    like, created = LocalHeroLike.objects.get_or_create(user=request.user, hero=hero)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': hero.like_count()})


@login_required
def local_hero_delete(request, pk):
    hero = get_object_or_404(LocalHero, pk=pk, posted_by=request.user)
    hero.delete()
    return redirect('/community/local-heroes/')


# ── COMMUNITY EVENTS ───────────────────────────────────────────────────────────
import datetime

EV_CAT_ICONS = {
    'festival':  '🎉',
    'sports':    '⚽',
    'cultural':  '🎭',
    'health':    '🏥',
    'education': '📚',
    'religious': '🕌',
    'cleanup':   '🧹',
    'other':     '📅',
}


def events_feed(request):
    cat    = request.GET.get('cat', '')
    today  = datetime.date.today()
    events = CommunityEvent.objects.filter(is_active=True, event_date__gte=today)
    if cat:
        events = events.filter(category=cat)

    my_rsvps = {}
    if request.user.is_authenticated:
        for r in EventRSVP.objects.filter(user=request.user, event__in=events):
            my_rsvps[r.event_id] = r.status

    return render(request, 'community/events.html', {
        'events':     events,
        'my_rsvps':   my_rsvps,
        'active_cat': cat,
        'cat_icons':  EV_CAT_ICONS,
        'categories': CommunityEvent.CAT_CHOICES,
        'today':      today,
    })


@login_required
def event_post(request):
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category    = request.POST.get('category', 'other')
        event_date  = request.POST.get('event_date', '')
        event_time  = request.POST.get('event_time', '') or None
        venue       = request.POST.get('venue', '').strip()
        image       = request.FILES.get('image')
        pincode     = getattr(request.user, 'pincode', '') or ''
        if title and description and event_date and venue:
            CommunityEvent.objects.create(
                posted_by=request.user, title=title, description=description,
                category=category, event_date=event_date, event_time=event_time,
                venue=venue, image=image, pincode=pincode,
            )
            messages.success(request, 'Event posted!')
            return redirect('/community/events/')
    return render(request, 'community/event_post.html', {
        'cat_icons':  EV_CAT_ICONS,
        'categories': CommunityEvent.CAT_CHOICES,
        'today':      datetime.date.today().isoformat(),
    })


def event_detail(request, pk):
    event    = get_object_or_404(CommunityEvent, pk=pk, is_active=True)
    comments = event.comments.select_related('user').all()
    my_rsvp  = None
    if request.user.is_authenticated:
        r = EventRSVP.objects.filter(user=request.user, event=event).first()
        my_rsvp = r.status if r else None
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            EventComment.objects.create(user=request.user, event=event, text=text)
        return redirect(f'/community/events/{pk}/')
    return render(request, 'community/event_detail.html', {
        'event':    event,
        'comments': comments,
        'my_rsvp':  my_rsvp,
        'cat_icons': EV_CAT_ICONS,
    })


@login_required
def event_rsvp(request, pk):
    event  = get_object_or_404(CommunityEvent, pk=pk)
    status = request.POST.get('status', 'going')
    rsvp, created = EventRSVP.objects.get_or_create(user=request.user, event=event,
                                                    defaults={'status': status})
    if not created:
        if rsvp.status == status:
            rsvp.delete()
            status = None
        else:
            rsvp.status = status
            rsvp.save()
    return JsonResponse({
        'status':      status,
        'going':       event.going_count(),
        'interested':  event.interested_count(),
    })


@login_required
def event_delete(request, pk):
    event = get_object_or_404(CommunityEvent, pk=pk, posted_by=request.user)
    event.delete()
    return redirect('/community/events/')


# ── VOLUNTEER ACTIVITIES ───────────────────────────────────────────────────────
VOL_CAT_ICONS = {
    'blood':     '🩸',
    'tree':      '🌳',
    'health':    '🏥',
    'education': '📚',
    'cleanup':   '🧹',
    'food':      '🍱',
    'other':     '🤝',
}


def volunteer_feed(request):
    cat        = request.GET.get('cat', '')
    today      = datetime.date.today()
    activities = VolunteerActivity.objects.filter(is_active=True, activity_date__gte=today)
    if cat:
        activities = activities.filter(category=cat)
    my_signups = set()
    if request.user.is_authenticated:
        my_signups = set(VolunteerSignup.objects.filter(
            user=request.user).values_list('activity_id', flat=True))
    return render(request, 'community/volunteer.html', {
        'activities': activities,
        'my_signups': my_signups,
        'active_cat': cat,
        'cat_icons':  VOL_CAT_ICONS,
        'categories': VolunteerActivity.CAT_CHOICES,
        'today':      today,
    })


@login_required
def volunteer_post(request):
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        desc     = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'other')
        act_date = request.POST.get('activity_date', '')
        act_time = request.POST.get('activity_time', '') or None
        venue    = request.POST.get('venue', '').strip()
        needed   = request.POST.get('volunteers_needed', '0')
        contact  = request.POST.get('contact', '').strip()
        image    = request.FILES.get('image')
        pincode  = getattr(request.user, 'pincode', '') or ''
        if title and desc and act_date and venue:
            VolunteerActivity.objects.create(
                posted_by=request.user, title=title, description=desc,
                category=category, activity_date=act_date, activity_time=act_time,
                venue=venue, volunteers_needed=int(needed) if needed.isdigit() else 0,
                contact=contact, image=image, pincode=pincode,
            )
            messages.success(request, 'Volunteer activity posted!')
            return redirect('/community/volunteer/')
    return render(request, 'community/volunteer_post.html', {
        'cat_icons':  VOL_CAT_ICONS,
        'categories': VolunteerActivity.CAT_CHOICES,
        'today':      datetime.date.today().isoformat(),
    })


def volunteer_detail(request, pk):
    activity = get_object_or_404(VolunteerActivity, pk=pk, is_active=True)
    comments = activity.comments.select_related('user').all()
    signed_up = (request.user.is_authenticated and
                 VolunteerSignup.objects.filter(user=request.user, activity=activity).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            VolunteerComment.objects.create(user=request.user, activity=activity, text=text)
        return redirect(f'/community/volunteer/{pk}/')
    return render(request, 'community/volunteer_detail.html', {
        'activity':  activity,
        'comments':  comments,
        'signed_up': signed_up,
        'cat_icons': VOL_CAT_ICONS,
    })


@login_required
def volunteer_signup(request, pk):
    activity = get_object_or_404(VolunteerActivity, pk=pk)
    signup, created = VolunteerSignup.objects.get_or_create(user=request.user, activity=activity)
    if not created:
        signup.delete()
        signed_up = False
    else:
        signed_up = True
    return JsonResponse({'signed_up': signed_up, 'count': activity.volunteer_count()})


@login_required
def volunteer_delete(request, pk):
    activity = get_object_or_404(VolunteerActivity, pk=pk, posted_by=request.user)
    activity.delete()
    return redirect('/community/volunteer/')


# ── BUSINESS STORIES ───────────────────────────────────────────────────────────
BS_CAT_ICONS = {
    'startup':   '🚀',
    'family':    '🏠',
    'comeback':  '💪',
    'milestone': '🏆',
    'lesson':    '📖',
    'other':     '🏪',
}


def business_stories_feed(request):
    cat    = request.GET.get('cat', '')
    stories = BusinessStory.objects.filter(is_active=True).select_related('user')
    if cat:
        stories = stories.filter(category=cat)
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(BusinessStoryLike.objects.filter(
            user=request.user).values_list('story_id', flat=True))
    return render(request, 'community/business_stories.html', {
        'stories':    stories,
        'liked_ids':  liked_ids,
        'active_cat': cat,
        'cat_icons':  BS_CAT_ICONS,
        'categories': BusinessStory.CAT_CHOICES,
    })


@login_required
def business_story_post(request):
    if request.method == 'POST':
        title         = request.POST.get('title', '').strip()
        content       = request.POST.get('content', '').strip()
        category      = request.POST.get('category', 'other')
        business_name = request.POST.get('business_name', '').strip()
        years         = request.POST.get('years', '').strip()
        image         = request.FILES.get('image')
        pincode       = getattr(request.user, 'pincode', '') or ''
        if title and content and business_name:
            BusinessStory.objects.create(
                user=request.user, title=title, content=content,
                category=category, business_name=business_name,
                years=int(years) if years.isdigit() else None,
                image=image, pincode=pincode,
            )
            messages.success(request, 'Business story shared!')
            return redirect('/community/business-stories/')
    return render(request, 'community/business_story_post.html', {
        'cat_icons':  BS_CAT_ICONS,
        'categories': BusinessStory.CAT_CHOICES,
    })


def business_story_detail(request, pk):
    story    = get_object_or_404(BusinessStory, pk=pk, is_active=True)
    comments = story.comments.select_related('user').all()
    liked    = (request.user.is_authenticated and
                BusinessStoryLike.objects.filter(user=request.user, story=story).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            BusinessStoryComment.objects.create(user=request.user, story=story, text=text)
        return redirect(f'/community/business-stories/{pk}/')
    return render(request, 'community/business_story_detail.html', {
        'story':     story,
        'comments':  comments,
        'liked':     liked,
        'cat_icons': BS_CAT_ICONS,
    })


@login_required
def business_story_like(request, pk):
    story = get_object_or_404(BusinessStory, pk=pk)
    like, created = BusinessStoryLike.objects.get_or_create(user=request.user, story=story)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': story.like_count()})


@login_required
def business_story_delete(request, pk):
    story = get_object_or_404(BusinessStory, pk=pk, user=request.user)
    story.delete()
    return redirect('/community/business-stories/')


# ── HALL OF FAME ───────────────────────────────────────────────────────────────
import datetime as _dt

HOF_CAT_ICONS = {
    'academics': '📚',
    'sports':    '⚽',
    'arts':      '🎨',
    'social':    '🤝',
    'business':  '🏪',
    'other':     '🏆',
}


def hall_of_fame_feed(request):
    cat    = request.GET.get('cat', '')
    year   = request.GET.get('year', '')
    entries = HallOfFameEntry.objects.filter(is_active=True)
    if cat:
        entries = entries.filter(category=cat)
    if year:
        entries = entries.filter(year=year)

    voted_ids = set()
    if request.user.is_authenticated:
        voted_ids = set(HallOfFameVote.objects.filter(
            user=request.user).values_list('entry_id', flat=True))

    current_year = _dt.date.today().year
    years = list(range(current_year, current_year - 6, -1))

    return render(request, 'community/hall_of_fame.html', {
        'entries':      entries,
        'voted_ids':    voted_ids,
        'active_cat':   cat,
        'active_year':  year,
        'cat_icons':    HOF_CAT_ICONS,
        'categories':   HallOfFameEntry.CAT_CHOICES,
        'years':        years,
        'current_year': current_year,
    })


@login_required
def hall_of_fame_nominate(request):
    if request.method == 'POST':
        nominee_name = request.POST.get('nominee_name', '').strip()
        category     = request.POST.get('category', 'other')
        achievement  = request.POST.get('achievement', '').strip()
        description  = request.POST.get('description', '').strip()
        year         = request.POST.get('year', str(_dt.date.today().year))
        image        = request.FILES.get('image')
        pincode      = getattr(request.user, 'pincode', '') or ''
        if nominee_name and achievement and description:
            HallOfFameEntry.objects.create(
                nominated_by=request.user, nominee_name=nominee_name,
                category=category, achievement=achievement,
                description=description, year=int(year),
                image=image, pincode=pincode,
            )
            messages.success(request, f'{nominee_name} has been nominated!')
            return redirect('/community/hall-of-fame/')
    current_year = _dt.date.today().year
    return render(request, 'community/hall_of_fame_nominate.html', {
        'cat_icons':    HOF_CAT_ICONS,
        'categories':   HallOfFameEntry.CAT_CHOICES,
        'current_year': current_year,
        'years':        list(range(current_year, current_year - 4, -1)),
    })


def hall_of_fame_detail(request, pk):
    entry    = get_object_or_404(HallOfFameEntry, pk=pk, is_active=True)
    comments = entry.comments.select_related('user').all()
    voted    = (request.user.is_authenticated and
                HallOfFameVote.objects.filter(user=request.user, entry=entry).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            HallOfFameComment.objects.create(user=request.user, entry=entry, text=text)
        return redirect(f'/community/hall-of-fame/{pk}/')
    return render(request, 'community/hall_of_fame_detail.html', {
        'entry':      entry,
        'comments':   comments,
        'voted':      voted,
        'vote_count': entry.vote_count(),
        'cat_icons':  HOF_CAT_ICONS,
    })


@login_required
def hall_of_fame_vote(request, pk):
    entry = get_object_or_404(HallOfFameEntry, pk=pk)
    vote, created = HallOfFameVote.objects.get_or_create(user=request.user, entry=entry)
    if not created:
        vote.delete()
        voted = False
    else:
        voted = True
    return JsonResponse({'voted': voted, 'count': entry.vote_count()})


# ── MARKETPLACE ────────────────────────────────────────────────────────────────
MP_CAT_ICONS = {
    'electronics': '📱', 'furniture': '🛋️', 'clothing': '👗', 'books': '📚',
    'vehicles': '🚗', 'appliances': '🏠', 'sports': '⚽', 'toys': '🧸',
    'food': '🥗', 'services': '🔧', 'other': '🛒',
}
MP_TYPE_ICONS = {
    'sell': '🏷️', 'rent': '🔑', 'free': '🎁', 'wanted': '🔍',
}


def marketplace_feed(request):
    cat  = request.GET.get('cat', '')
    ltype = request.GET.get('type', '')
    listings = MarketplaceListing.objects.filter(is_active=True)
    if cat:
        listings = listings.filter(category=cat)
    if ltype:
        listings = listings.filter(listing_type=ltype)
    interest_ids = set()
    if request.user.is_authenticated:
        interest_ids = set(ListingInterest.objects.filter(
            user=request.user).values_list('listing_id', flat=True))
    return render(request, 'community/marketplace.html', {
        'listings':     listings,
        'interest_ids': interest_ids,
        'active_cat':   cat,
        'active_type':  ltype,
        'cat_icons':    MP_CAT_ICONS,
        'type_icons':   MP_TYPE_ICONS,
        'categories':   MarketplaceListing.CAT_CHOICES,
        'types':        MarketplaceListing.TYPE_CHOICES,
    })


@login_required
def marketplace_post(request):
    if request.method == 'POST':
        listing_type = request.POST.get('listing_type', 'sell')
        price_raw    = request.POST.get('price', '').strip()
        price        = float(price_raw) if price_raw else None
        listing = MarketplaceListing.objects.create(
            user         = request.user,
            title        = request.POST['title'],
            category     = request.POST['category'],
            listing_type = listing_type,
            condition    = request.POST.get('condition', 'good') if listing_type != 'wanted' else '',
            price        = price,
            description  = request.POST['description'],
            pincode      = request.POST.get('pincode', ''),
            contact      = request.POST.get('contact', ''),
            image        = request.FILES.get('image'),
        )
        return redirect(f'/community/marketplace/{listing.pk}/')
    return render(request, 'community/marketplace_post.html', {
        'cat_icons':  MP_CAT_ICONS,
        'type_icons': MP_TYPE_ICONS,
        'categories': MarketplaceListing.CAT_CHOICES,
        'types':      MarketplaceListing.TYPE_CHOICES,
        'conditions': MarketplaceListing.CONDITION_CHOICES,
    })


def marketplace_detail(request, pk):
    listing  = get_object_or_404(MarketplaceListing, pk=pk, is_active=True)
    comments = listing.mp_comments.select_related('user').all()
    interested = (request.user.is_authenticated and
                  ListingInterest.objects.filter(user=request.user, listing=listing).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            ListingComment.objects.create(user=request.user, listing=listing, text=text)
        return redirect(f'/community/marketplace/{pk}/')
    return render(request, 'community/marketplace_detail.html', {
        'listing':    listing,
        'comments':   comments,
        'interested': interested,
        'interest_count': listing.interest_count(),
        'cat_icons':  MP_CAT_ICONS,
        'type_icons': MP_TYPE_ICONS,
    })


@login_required
def marketplace_interest(request, pk):
    listing = get_object_or_404(MarketplaceListing, pk=pk)
    obj, created = ListingInterest.objects.get_or_create(user=request.user, listing=listing)
    if not created:
        obj.delete()
        interested = False
    else:
        interested = True
    return JsonResponse({'interested': interested, 'count': listing.interest_count()})


@login_required
def marketplace_sold(request, pk):
    listing = get_object_or_404(MarketplaceListing, pk=pk, user=request.user)
    listing.is_sold = not listing.is_sold
    listing.save()
    return JsonResponse({'sold': listing.is_sold})


@login_required
def marketplace_delete(request, pk):
    listing = get_object_or_404(MarketplaceListing, pk=pk, user=request.user)
    listing.is_active = False
    listing.save()
    return redirect('/community/marketplace/')


# ── COMMUNITY WATCH ────────────────────────────────────────────────────────────
WATCH_CAT_ICONS = {
    'theft':      '🚨', 'suspicious': '👁️', 'hazard': '⚠️',
    'lost_found': '🔍', 'noise':      '📢', 'stray':  '🐕',
    'infra':      '🏗️', 'other':      '📋',
}
SEVERITY_COLORS = {
    'low':    '#16a34a',
    'medium': '#d97706',
    'high':   '#dc2626',
}


def watch_feed(request):
    cat      = request.GET.get('cat', '')
    severity = request.GET.get('sev', '')
    reports  = WatchReport.objects.filter(is_active=True)
    if cat:
        reports = reports.filter(category=cat)
    if severity:
        reports = reports.filter(severity=severity)
    confirm_ids = set()
    if request.user.is_authenticated:
        confirm_ids = set(WatchConfirm.objects.filter(
            user=request.user).values_list('report_id', flat=True))
    return render(request, 'community/community_watch.html', {
        'reports':      reports,
        'confirm_ids':  confirm_ids,
        'active_cat':   cat,
        'active_sev':   severity,
        'cat_icons':    WATCH_CAT_ICONS,
        'sev_colors':   SEVERITY_COLORS,
        'categories':   WatchReport.CAT_CHOICES,
        'severities':   WatchReport.SEVERITY_CHOICES,
    })


@login_required
def watch_post(request):
    if request.method == 'POST':
        report = WatchReport.objects.create(
            user        = request.user,
            category    = request.POST['category'],
            severity    = request.POST.get('severity', 'medium'),
            title       = request.POST['title'],
            description = request.POST['description'],
            location    = request.POST.get('location', ''),
            pincode     = request.POST.get('pincode', ''),
            image       = request.FILES.get('image'),
        )
        return redirect(f'/community/community-watch/{report.pk}/')
    return render(request, 'community/watch_post.html', {
        'cat_icons':  WATCH_CAT_ICONS,
        'categories': WatchReport.CAT_CHOICES,
        'severities': WatchReport.SEVERITY_CHOICES,
        'sev_colors': SEVERITY_COLORS,
    })


def watch_detail(request, pk):
    report   = get_object_or_404(WatchReport, pk=pk, is_active=True)
    comments = report.watch_comments.select_related('user').all()
    confirmed = (request.user.is_authenticated and
                 WatchConfirm.objects.filter(user=request.user, report=report).exists())
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('comment', '').strip()
        if text:
            WatchComment.objects.create(user=request.user, report=report, text=text)
        return redirect(f'/community/community-watch/{pk}/')
    return render(request, 'community/watch_detail.html', {
        'report':         report,
        'comments':       comments,
        'confirmed':      confirmed,
        'confirm_count':  report.confirm_count(),
        'cat_icons':      WATCH_CAT_ICONS,
        'sev_colors':     SEVERITY_COLORS,
    })


@login_required
def watch_confirm(request, pk):
    report = get_object_or_404(WatchReport, pk=pk)
    obj, created = WatchConfirm.objects.get_or_create(user=request.user, report=report)
    if not created:
        obj.delete()
        confirmed = False
    else:
        confirmed = True
    return JsonResponse({'confirmed': confirmed, 'count': report.confirm_count()})


@login_required
def watch_resolve(request, pk):
    report = get_object_or_404(WatchReport, pk=pk, user=request.user)
    report.is_resolved = not report.is_resolved
    report.save()
    return JsonResponse({'resolved': report.is_resolved})


@login_required
def watch_delete(request, pk):
    report = get_object_or_404(WatchReport, pk=pk, user=request.user)
    report.is_active = False
    report.save()
    return redirect('/community/community-watch/')


# ── NOTIFICATIONS & SEARCH ─────────────────────────────────────────────────────
NOTIF_ICONS = {
    'like':     '❤️',  'comment':  '💬', 'confirm':  '🚨',
    'rsvp':     '📅',  'signup':   '🤝', 'vote':     '⭐',
    'interest': '🛒',  'follow':   '🏫', 'system':   '🔔',
}


@login_required
def notifications_page(request):
    notifs = Notification.objects.filter(user=request.user)
    unread_count = notifs.filter(is_read=False).count()
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'community/notifications.html', {
        'notifs':       notifs[:50],
        'unread_count': unread_count,
        'notif_icons':  NOTIF_ICONS,
    })


@login_required
def notif_mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})


def community_search(request):
    q       = request.GET.get('q', '').strip()
    pincode = request.GET.get('pincode', '').strip()
    results = []

    if q or pincode:
        from django.db.models import Q

        def _filter(qs, title_field, desc_field='description', pin_field='pincode'):
            f = Q()
            if q:
                f &= (Q(**{f'{title_field}__icontains': q}) |
                      Q(**{f'{desc_field}__icontains': q}))
            if pincode and pin_field:
                try:
                    f &= Q(**{f'{pin_field}__icontains': pincode})
                except Exception:
                    pass
            return qs.filter(f) if f else qs.none()

        # Family Stories
        for s in _filter(FamilyStory.objects.filter(is_active=True), 'title')[:5]:
            results.append({'type': 'Family Story', 'icon': '📸', 'title': s.title,
                            'desc': s.content[:80], 'url': f'/community/family-stories/{s.pk}/',
                            'time': s.created_at})
        # Student Success
        for s in _filter(StudentSuccess.objects.filter(is_active=True), 'title')[:5]:
            results.append({'type': 'Student Success', 'icon': '🎓', 'title': s.title,
                            'desc': s.story[:80], 'url': f'/community/student-success/{s.pk}/',
                            'time': s.created_at})
        # Kids Corner
        for s in _filter(KidsPost.objects.filter(is_active=True), 'title', 'content')[:5]:
            results.append({'type': 'Kids Corner', 'icon': '🧒', 'title': s.title,
                            'desc': s.content[:80], 'url': f'/community/kids-corner/{s.pk}/',
                            'time': s.created_at})
        # Parenting
        for s in _filter(ParentingPost.objects.filter(is_active=True), 'title', 'content')[:5]:
            results.append({'type': 'Parenting', 'icon': '👨‍👩‍👧', 'title': s.title,
                            'desc': s.content[:80], 'url': f'/community/parenting/{s.pk}/',
                            'time': s.created_at})
        # Grandparents
        for s in _filter(GrandparentStory.objects.filter(is_active=True), 'title', 'story')[:5]:
            results.append({'type': 'Grandparents', 'icon': '👴', 'title': s.title,
                            'desc': s.story[:80], 'url': f'/community/grandparents-archive/{s.pk}/',
                            'time': s.created_at})
        # Local Heroes
        for s in _filter(LocalHero.objects.filter(is_active=True), 'name', 'story')[:5]:
            results.append({'type': 'Local Hero', 'icon': '🦸', 'title': s.name,
                            'desc': s.story[:80], 'url': f'/community/local-heroes/{s.pk}/',
                            'time': s.created_at})
        # Events
        for s in _filter(CommunityEvent.objects.filter(is_active=True), 'title')[:5]:
            results.append({'type': 'Community Event', 'icon': '📅', 'title': s.title,
                            'desc': s.description[:80], 'url': f'/community/events/{s.pk}/',
                            'time': s.created_at})
        # Volunteer
        for s in _filter(VolunteerActivity.objects.filter(is_active=True), 'title')[:5]:
            results.append({'type': 'Volunteer', 'icon': '🤝', 'title': s.title,
                            'desc': s.description[:80], 'url': f'/community/volunteer/{s.pk}/',
                            'time': s.created_at})
        # Business Stories
        for s in _filter(BusinessStory.objects.filter(is_active=True), 'title', 'content')[:5]:
            results.append({'type': 'Business Story', 'icon': '🏪', 'title': s.title,
                            'desc': s.content[:80], 'url': f'/community/business-stories/{s.pk}/',
                            'time': s.created_at})
        # Hall of Fame
        for s in _filter(HallOfFameEntry.objects.filter(is_active=True), 'nominee_name', 'description')[:5]:
            results.append({'type': 'Hall of Fame', 'icon': '🏆', 'title': s.nominee_name,
                            'desc': s.description[:80], 'url': f'/community/hall-of-fame/{s.pk}/',
                            'time': s.created_at})
        # Marketplace
        for s in _filter(MarketplaceListing.objects.filter(is_active=True), 'title')[:5]:
            results.append({'type': 'Marketplace', 'icon': '🛒', 'title': s.title,
                            'desc': s.description[:80], 'url': f'/community/marketplace/{s.pk}/',
                            'time': s.created_at})
        # Watch
        for s in _filter(WatchReport.objects.filter(is_active=True), 'title', 'description', 'pincode')[:5]:
            results.append({'type': 'Community Watch', 'icon': '👁️', 'title': s.title,
                            'desc': s.description[:80], 'url': f'/community/community-watch/{s.pk}/',
                            'time': s.created_at})

        results.sort(key=lambda x: x['time'], reverse=True)

    return render(request, 'community/search.html', {
        'results': results,
        'q':       q,
        'pincode': pincode,
        'count':   len(results),
    })
