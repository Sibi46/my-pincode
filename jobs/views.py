from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, F, Count
from django.utils import timezone
from .models import (Job, JobApplication, CompanyProfile, ShopProfile,
                     JobSeekerProfile, SeekerCertificate, SavedJob, Interview,
                     Conversation, Message, OfferLetter,
                     Advertiser, AdPackage, Advertisement, AdPayment,
                     State, District, AdminProfile, Industry, JobRole,
                     PaymentPlan, Discount, Complaint, SystemNotification, PinCode,
                     UserNotification, SavedCandidate, Wallet, WalletTransaction,
                     EmployerSubscription, BillingRecord,
                     PointsWallet, PointsTransaction, Referral)

User = get_user_model()


# ── HOME ──────────────────────────────────────────────────────────────────────
def home(request):
    from django.utils import timezone as tz
    today = tz.now().date()

    # ── Ads ─────────────────────────────────────────────
    ads_active         = Advertisement.objects.filter(status='active', start_date__lte=today, end_date__gte=today)
    homepage_banners   = ads_active.filter(package__ad_type='homepage_banner')[:3]
    featured_employers = ads_active.filter(package__ad_type='featured_employer')[:6]
    featured_job_ads   = ads_active.filter(package__ad_type='featured_job')[:6]
    sidebar_ad         = ads_active.filter(package__ad_type='sidebar').first()
    popup_ad           = ads_active.filter(package__ad_type='popup').first()
    if homepage_banners:
        banner_pks = list(homepage_banners.values_list('pk', flat=True))
        Advertisement.objects.filter(pk__in=banner_pks).update(views=F('views') + 1)

    # ── Approved advertiser banners ──────────────────────
    advertiser_banners = Advertiser.objects.filter(status='approved', banner_image__isnull=False).exclude(banner_image='')[:6]

    # ── Jobs & employers ────────────────────────────────
    featured_jobs = Job.objects.filter(status='active').select_related('posted_by').order_by('-created_at')[:8]

    # ── Stats — cached 5 min to avoid COUNT on every request ─────────────────
    from django.core.cache import cache
    stats = cache.get('homepage_stats')
    if not stats:
        stats = {
            'total_jobs':      Job.objects.filter(status='active').count(),
            'total_employers': User.objects.filter(user_type__in=User.EMPLOYER_TYPES).count(),
            'total_seekers':   User.objects.filter(user_type__in=['employee', 'individual', 'freelancer']).count(),
            'total_districts': District.objects.filter(is_active=True).count(),
        }
        cache.set('homepage_stats', stats, 300)
    total_jobs      = stats['total_jobs']
    total_employers = stats['total_employers']
    total_seekers   = stats['total_seekers']
    total_districts = stats['total_districts']

    # ── Industries ───────────────────────────────────────
    industries = Industry.objects.filter(is_active=True).order_by('order')[:12]

    # ── Jobs by District — single aggregated query instead of N+1 ───────────
    active_pin_job_counts = dict(
        Job.objects.filter(status='active')
        .values('pincode')
        .annotate(cnt=Count('id'))
        .values_list('pincode', 'cnt')
    )
    active_districts = District.objects.filter(is_active=True).prefetch_related('pincodes')[:12]
    districts_jobs = []
    for d in active_districts:
        pin_list = [p.code for p in d.pincodes.all()]
        d.job_count = sum(active_pin_job_counts.get(p, 0) for p in pin_list)
        districts_jobs.append(d)
    districts_jobs.sort(key=lambda d: d.job_count, reverse=True)

    # ── Jobs by PIN Code — reuse the counts dict, no extra queries ────────────
    pincode_jobs = [
        {'pin': pin, 'count': active_pin_job_counts.get(pin.code, 0)}
        for pin in PinCode.objects.filter(is_active=True).select_related('district', 'district__state')[:20]
        if active_pin_job_counts.get(pin.code, 0) > 0
    ]
    pincode_jobs.sort(key=lambda x: x['count'], reverse=True)

    return render(request, 'index.html', {
        'featured_jobs':       featured_jobs,
        'homepage_banners':    homepage_banners,
        'featured_employers':  featured_employers,
        'featured_job_ads':    featured_job_ads,
        'sidebar_ad':          sidebar_ad,
        'popup_ad':            popup_ad,
        'industries':          industries,
        'districts_jobs':      districts_jobs,
        'pincode_jobs':        pincode_jobs,
        'total_jobs':          total_jobs,
        'total_employers':     total_employers,
        'total_seekers':       total_seekers,
        'total_districts':     total_districts,
        'advertiser_banners':  advertiser_banners,
    })


# ── REGISTER ─────────────────────────────────────────────────────────────────
def register(request):
    ref_code = request.GET.get('ref', '').strip().upper()
    return render(request, 'register.html', {'ref_code': ref_code})


def register_process(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def err(msg):
        if is_ajax:
            return JsonResponse({'success': False, 'error': msg})
        messages.error(request, msg)
        return redirect('register')

    user_type  = request.POST.get('user_type', '').strip()
    password   = request.POST.get('password', '')
    phone      = request.POST.get('phone', '').strip()
    email      = request.POST.get('email', '').strip()
    first_name = request.POST.get('first_name', '').strip()
    last_name  = request.POST.get('last_name', '').strip()
    address    = request.POST.get('address', '').strip()
    city       = request.POST.get('city', '').strip()
    pincode    = request.POST.get('pincode', '').strip()
    whatsapp   = request.POST.get('whatsapp', '').strip()
    ref_code   = request.POST.get('ref_code', '').strip().upper()

    username = phone if phone else email
    if not username:
        return err('Phone or email is required.')

    if not password:
        return err('Password is required.')

    if User.objects.filter(username=username).exists():
        return err('An account already exists with this phone/email. Please login instead.')

    from .utils import generate_referral_code
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        whatsapp=whatsapp,
        user_type=user_type,
        address=address,
        city=city,
        pincode=pincode,
        referral_code=generate_referral_code(),
    )

    # Track referral and award signup bonus
    if ref_code:
        referrer = User.objects.filter(referral_code=ref_code).first()
        if referrer and referrer != user:
            Referral.objects.create(referrer=referrer, referred=user, bonus_signup=True)
            from .utils import award_referral_points
            award_referral_points(
                referrer, 50, 'referral_signup',
                f'{user.get_full_name() or user.username} joined using your referral link!'
            )

    org_name = (
        request.POST.get('org_name', '').strip()
        or request.POST.get('company_name', '').strip()
        or f"{first_name} {last_name}".strip()
    )

    if user_type in User.EMPLOYER_TYPES:
        CompanyProfile.objects.create(
            user=user,
            company_name=org_name,
            industry=request.POST.get('industry', '').strip(),
            website=request.POST.get('website', '').strip(),
            company_size=request.POST.get('company_size', '').strip(),
        )
        if user_type == 'shop':
            ShopProfile.objects.create(
                user=user,
                shop_name=org_name,
                shop_type=request.POST.get('shop_type', '').strip(),
                owner_name=first_name,
                website=request.POST.get('website', '').strip(),
            )
    elif user_type in ('employee', 'individual', 'freelancer'):
        JobSeekerProfile.objects.create(
            user=user,
            job_category=request.POST.get('job_category', ''),
            primary_skill=request.POST.get('primary_skill', ''),
            rate=request.POST.get('rate', ''),
        )

    login(request, user, backend='jobs.backends.PhoneOrEmailBackend')
    request.session['show_referral_popup'] = True

    if user_type in User.EMPLOYER_TYPES:
        redirect_url = '/employer/dashboard/'
    elif user_type in ('employee', 'individual', 'freelancer'):
        redirect_url = '/jobseeker/profile/'
    else:
        redirect_url = '/dashboard/'

    if is_ajax:
        return JsonResponse({'success': True, 'redirect': redirect_url})
    return redirect(redirect_url)


# ── AUTH ──────────────────────────────────────────────────────────────────────
def forgot_password(request):
    phone = request.GET.get('phone', '')
    return render(request, 'forgot_password.html', {'prefill_phone': phone})


def reset_password(request):
    """Reset password after OTP verification."""
    if request.method != 'POST':
        return JsonResponse({'success': False})
    import json
    data     = json.loads(request.body)
    phone    = data.get('phone', '').strip()
    password = data.get('password', '').strip()

    if not request.session.get('otp_verified'):
        return JsonResponse({'success': False, 'error': 'OTP not verified'})
    if not password or len(password) < 6:
        return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters'})

    User = get_user_model()
    user = User.objects.filter(phone=phone).first()
    if not user:
        return JsonResponse({'success': False, 'error': 'No account found with this mobile number'})

    user.set_password(password)
    user.save()
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    request.session.pop('otp_verified', None)
    redirect_url = '/employer/dashboard/' if user.is_employer() else '/jobseeker/dashboard/'
    return JsonResponse({'success': True, 'redirect': redirect_url})


def login_view(request):
    next_url = request.GET.get('next', '') or request.POST.get('next', '')

    if request.user.is_authenticated:
        return redirect(next_url or 'dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(next_url or 'dashboard')
        messages.error(request, 'Invalid phone/email or password.')

    return render(request, 'login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    role = request.user.admin_role
    if role == 'super_admin':
        return redirect('super_admin_dashboard')
    if role == 'state_admin':
        return redirect('state_admin_dashboard')
    if role == 'district_admin':
        return redirect('district_admin_dashboard')
    if request.user.user_type in User.EMPLOYER_TYPES:
        return redirect('employer_dashboard')
    if request.user.user_type == 'advertiser' or hasattr(request.user, 'advertiser'):
        return redirect('advertiser_dashboard')
    return redirect('jobseeker_dashboard')


# ── JOBS ──────────────────────────────────────────────────────────────────────
def job_list(request):
    jobs = Job.objects.filter(status='active', is_approved=True, job_plan__in=['free', 'paid'], posted_by__user_type__in=User.EMPLOYER_TYPES)

    collar    = request.GET.get('collar', '')
    category  = request.GET.get('category', '')
    pincode   = request.GET.get('pincode', '')
    q         = request.GET.get('q', '')
    radius_km = request.GET.get('radius', '')

    if collar:
        jobs = jobs.filter(collar_type=collar)
    if category:
        jobs = jobs.filter(category__icontains=category)
    if q:
        jobs = jobs.filter(Q(title__icontains=q) | Q(category__icontains=q) | Q(location__icontains=q))

    nearby_pairs = None
    radius_error = None

    if pincode and radius_km:
        # Nearby radius search
        try:
            from .utils import geocode_pincode, jobs_within_radius
            radius_km = float(radius_km)
            lat, lng = geocode_pincode(pincode)
            if lat:
                nearby_pairs = jobs_within_radius(lat, lng, radius_km, queryset=jobs)
                # nearby_pairs is [(job, dist_km), ...]
                jobs = [pair[0] for pair in nearby_pairs]
            else:
                radius_error = f"Could not locate pincode {pincode}. Showing all results."
                jobs = jobs.filter(pincode=pincode) if pincode else jobs
        except (ValueError, TypeError):
            radius_error = "Invalid radius value."
            jobs = jobs.filter(pincode=pincode) if pincode else jobs
    elif pincode:
        jobs = jobs.filter(pincode=pincode)

    total = len(jobs) if isinstance(jobs, list) else jobs.count()

    return render(request, 'job_list.html', {
        'jobs':         jobs,
        'nearby_pairs': nearby_pairs,
        'collar':       collar,
        'q':            q,
        'pincode':      pincode,
        'radius':       radius_km,
        'radius_error': radius_error,
        'total':        total,
    })


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, status='active', is_approved=True, job_plan__in=['free', 'paid'])
    already_applied = False
    is_saved = False
    if request.user.is_authenticated:
        already_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
        is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    related = Job.objects.filter(collar_type=job.collar_type, status='active', is_approved=True, job_plan__in=['free', 'paid']).exclude(pk=pk)[:3]
    return render(request, 'job_detail.html', {
        'job': job,
        'already_applied': already_applied,
        'is_saved': is_saved,
        'related': related,
    })


@login_required
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk, status='active', is_approved=True, job_plan__in=['free', 'paid'])
    if request.method == 'POST':
        if not JobApplication.objects.filter(job=job, applicant=request.user).exists():
            JobApplication.objects.create(
                job=job,
                applicant=request.user,
                cover_note=request.POST.get('cover_note', ''),
            )
            messages.success(request, 'Application submitted successfully!')
            # Referral bonus: first application by a referred seeker
            try:
                ref = Referral.objects.get(referred=request.user, bonus_action=False)
                first_app = JobApplication.objects.filter(applicant=request.user).count() == 1
                if first_app:
                    from .utils import award_referral_points
                    award_referral_points(
                        ref.referrer, 25, 'referral_apply',
                        f'{request.user.get_full_name() or request.user.username} applied for their first job!'
                    )
                    ref.bonus_action = True
                    ref.save(update_fields=['bonus_action'])
            except Referral.DoesNotExist:
                pass
        else:
            messages.warning(request, 'You have already applied for this job.')
    return redirect('job_detail', pk=pk)


# ── POST JOB ──────────────────────────────────────────────────────────────────
@login_required
def post_job(request):
    # Block if employer profile is incomplete
    user = request.user
    if user.is_employer():
        try:
            prof = user.company
        except Exception:
            prof = None
        score = 0
        if prof and prof.company_name: score += 10
        if user.pincode:               score += 20
        if user.city:                  score += 15
        if user.address:               score += 15
        if prof and prof.industry:     score += 20
        if prof and prof.company_size: score += 10
        if prof and prof.website:      score += 10
        if score < 70:
            return redirect('employer_dashboard')

    if request.method == 'POST':
        import datetime
        p = request.POST
        last_date_str = p.get('last_date', '')
        last_date = None
        if last_date_str:
            try:
                last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        action = p.get('action', 'publish')
        status = 'draft' if action == 'draft' else 'active'

        Job.objects.create(
            posted_by       = request.user,
            title           = p.get('title', ''),
            collar_type     = p.get('collar_type', 'white'),
            industry        = p.get('industry', ''),
            category        = p.get('category', ''),
            description     = p.get('description', ''),
            job_type        = p.get('job_type', 'full_time'),
            experience      = p.get('experience', ''),
            education       = p.get('education', ''),
            gender_preference = p.get('gender_preference', 'any'),
            age_min         = p.get('age_min') or None,
            age_max         = p.get('age_max') or None,
            skills          = p.get('skills', ''),
            language        = p.get('language', 'Any'),
            salary_min      = p.get('salary_min') or None,
            salary_max      = p.get('salary_max') or None,
            salary_type     = p.get('salary_type', 'month'),
            benefits        = p.get('benefits', ''),
            vacancies       = p.get('vacancies', 1),
            shift           = p.get('shift', 'day'),
            working_days    = p.get('working_days', ''),
            accommodation   = 'accommodation' in p,
            food_provided   = 'food_provided' in p,
            transport       = 'transport' in p,
            location        = p.get('location', ''),
            pincode         = p.get('pincode', ''),
            latitude        = p.get('latitude') or None,
            longitude       = p.get('longitude') or None,
            contact_phone   = p.get('contact_phone', ''),
            is_urgent       = 'is_urgent' in p,
            interview_type  = p.get('interview_type', 'walkin'),
            last_date       = last_date,
            status          = status,
        )
        if status == 'draft':
            messages.success(request, 'Job saved as draft.')
        else:
            messages.success(request, 'Job submitted! Admin will review and approve it shortly.')
            request.session['show_job_posted_popup'] = p.get('title', 'Your job')
            # Referral bonus: first job posted by a referred employer
            try:
                ref = Referral.objects.get(referred=request.user, bonus_action=False)
                first_job = Job.objects.filter(posted_by=request.user).count() == 1
                if first_job:
                    from .utils import award_referral_points
                    award_referral_points(
                        ref.referrer, 100, 'referral_job',
                        f'{request.user.get_full_name() or request.user.username} posted their first job!'
                    )
                    ref.bonus_action = True
                    ref.save(update_fields=['bonus_action'])
            except Referral.DoesNotExist:
                pass
        return redirect('employer_dashboard')

    industries = Industry.objects.filter(is_active=True).prefetch_related('roles')
    return render(request, 'post_job.html', {'industries': industries})


@login_required
def job_select_plan(request, pk):
    import datetime
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)

    if not job.is_approved:
        messages.warning(request, 'This job is still pending admin approval.')
        return redirect('employer_dashboard')

    if job.job_plan and job.job_plan not in ('', 'free_expired'):
        messages.info(request, 'A plan is already active for this job.')
        return redirect('employer_dashboard')

    is_upgrade = job.job_plan == 'free_expired'

    if request.method == 'POST':
        plan = request.POST.get('plan')

        if plan == 'free':
            job.job_plan = 'free'
            job.plan_expires_at = datetime.date.today() + datetime.timedelta(weeks=1)
            job.save()
            from .utils import notify_seekers_for_job
            notify_seekers_for_job(job)
            messages.success(request, 'Free plan activated! Your job is now live for 1 week.')
            return redirect('employer_dashboard')

        elif plan == 'paid_confirm':
            screenshot = request.FILES.get('screenshot')
            if not screenshot:
                messages.error(request, 'Please upload the payment screenshot.')
                return render(request, 'job_select_plan.html', {'job': job, 'show_qr': True, 'is_upgrade': is_upgrade})
            job.job_plan = 'paid_pending'
            job.payment_screenshot = screenshot
            job.save()
            messages.success(request, 'Payment screenshot submitted! Admin will verify and activate your plan shortly.')
            return redirect('employer_dashboard')

    return render(request, 'job_select_plan.html', {'job': job, 'show_qr': False, 'is_upgrade': is_upgrade})


@login_required
def edit_job(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        import datetime
        p = request.POST
        last_date_str = p.get('last_date', '')
        last_date = None
        if last_date_str:
            try:
                last_date = datetime.datetime.strptime(last_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        action = p.get('action', 'publish')
        job.title             = p.get('title', job.title)
        job.collar_type       = p.get('collar_type', job.collar_type)
        job.industry          = p.get('industry', job.industry)
        job.category          = p.get('category', job.category)
        job.description       = p.get('description', job.description)
        job.job_type          = p.get('job_type', job.job_type)
        job.experience        = p.get('experience', job.experience)
        job.education         = p.get('education', job.education)
        job.gender_preference = p.get('gender_preference', job.gender_preference)
        job.age_min           = p.get('age_min') or None
        job.age_max           = p.get('age_max') or None
        job.skills            = p.get('skills', job.skills)
        job.language          = p.get('language', job.language)
        job.salary_min        = p.get('salary_min') or None
        job.salary_max        = p.get('salary_max') or None
        job.salary_type       = p.get('salary_type', job.salary_type)
        job.benefits          = p.get('benefits', job.benefits)
        job.vacancies         = p.get('vacancies', job.vacancies)
        job.shift             = p.get('shift', job.shift)
        job.working_days      = p.get('working_days', job.working_days)
        job.accommodation     = 'accommodation' in p
        job.food_provided     = 'food_provided' in p
        job.transport         = 'transport' in p
        job.location          = p.get('location', job.location)
        job.pincode           = p.get('pincode', job.pincode)
        job.latitude          = p.get('latitude') or None
        job.longitude         = p.get('longitude') or None
        job.contact_phone     = p.get('contact_phone', job.contact_phone)
        job.is_urgent         = 'is_urgent' in p
        job.interview_type    = p.get('interview_type', job.interview_type)
        job.last_date         = last_date
        job.status            = 'draft' if action == 'draft' else 'active'
        job.save()
        messages.success(request, 'Job updated successfully!')
        return redirect('employer_dashboard')

    industries = Industry.objects.filter(is_active=True).prefetch_related('roles')
    return render(request, 'edit_job.html', {'job': job, 'industries': industries})


# ── DASHBOARDS ────────────────────────────────────────────────────────────────
@login_required
def employer_dashboard(request):
    user = request.user

    # ── Auto-expire free plans ──
    import datetime
    today = datetime.date.today()
    to_expire = Job.objects.filter(posted_by=user, job_plan='free', plan_expires_at__lt=today, status='active')
    for _job in to_expire:
        _job.job_plan = 'free_expired'
        _job.save(update_fields=['job_plan'])
        UserNotification.objects.get_or_create(
            user=user,
            link=f'/jobs/{_job.pk}/select-plan/',
            defaults={
                'title': f'Free Week Ended: {_job.title}',
                'message': f'Your 1-week free listing for "{_job.title}" has expired. Upgrade to 12 weeks for ₹499!',
                'notif_type': 'warning',
            },
        )

    # ── Jobs ──
    active_jobs       = Job.objects.filter(posted_by=user, status='active', is_approved=True, job_plan__in=['free', 'paid']).order_by('-created_at')
    expired_jobs      = Job.objects.filter(posted_by=user, status='active', is_approved=True, job_plan='free_expired').order_by('-created_at')
    paid_pending_jobs = Job.objects.filter(posted_by=user, status='active', is_approved=True, job_plan='paid_pending').order_by('-created_at')
    plan_pending      = Job.objects.filter(posted_by=user, status='active', is_approved=True, job_plan='').order_by('-created_at')
    approval_pending  = Job.objects.filter(posted_by=user, status='active', is_approved=False).order_by('-created_at')
    pending_jobs      = Job.objects.filter(posted_by=user, status='draft').order_by('-created_at')
    closed_jobs       = Job.objects.filter(posted_by=user, status='closed').order_by('-created_at')

    # ── Applications ──
    all_apps    = JobApplication.objects.filter(job__posted_by=user).select_related('applicant', 'job').order_by('-applied_at')
    shortlisted = all_apps.filter(status='shortlisted')

    # ── Saved candidates ──
    saved_candidates = SavedCandidate.objects.filter(employer=user).select_related('candidate')

    # ── Messages ──
    user_convs       = Conversation.objects.filter(Q(user_a=user) | Q(user_b=user))
    unread_msg_count = Message.objects.filter(conversation__in=user_convs, is_read=False).exclude(sender=user).count()
    recent_convs     = user_convs.select_related('user_a', 'user_b', 'job').order_by('-updated_at')[:8]
    recent_messages  = [{'conv': c, 'other': c.other_user(user),
                         'last': c.messages.order_by('-sent_at').first(),
                         'unread': c.unread_for(user)} for c in recent_convs]

    # ── Notifications ──
    notifs       = UserNotification.objects.filter(user=user)[:12]
    unread_notif_count = UserNotification.objects.filter(user=user, is_read=False).count()

    # ── Wallet ──
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet_txns = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')[:10]

    # ── Subscription ──
    current_sub = EmployerSubscription.objects.filter(
        employer=user, status='active'
    ).select_related('plan').first()
    available_plans = PaymentPlan.objects.filter(
        is_active=True, plan_type__startswith='employer'
    )

    # ── Billing history ──
    billing_records = BillingRecord.objects.filter(user=user).order_by('-created_at')[:10]

    # ── Profile ──
    try:
        profile = user.company
    except Exception:
        profile = None

    # ── Profile completion ──
    def _pct(u, p):
        score = 0
        if p and p.company_name: score += 10
        if u.pincode:             score += 20
        if u.city:                score += 15
        if u.address:             score += 15
        if p and p.industry:      score += 20
        if p and p.company_size:  score += 10
        if p and p.website:       score += 10
        return score

    profile_pct = _pct(user, profile)
    profile_incomplete = profile_pct < 70

    show_referral_popup = request.session.pop('show_referral_popup', False)
    referral_link = request.build_absolute_uri(f'/register/?ref={request.user.referral_code}') if request.user.referral_code else ''
    job_posted_title = request.session.pop('show_job_posted_popup', None)

    from .models import Flick, FlickLike
    recent_flicks = Flick.objects.select_related('user').prefetch_related('likes')[:12]
    liked_ids = set(FlickLike.objects.filter(user=request.user).values_list('flick_id', flat=True))

    return render(request, 'employer_dashboard.html', {
        'active_jobs':        active_jobs,
        'expired_jobs':       expired_jobs,
        'paid_pending_jobs':  paid_pending_jobs,
        'plan_pending':       plan_pending,
        'approval_pending':   approval_pending,
        'pending_jobs':       pending_jobs,
        'closed_jobs':        closed_jobs,
        'all_apps':           all_apps,
        'shortlisted':        shortlisted,
        'saved_candidates':   saved_candidates,
        'unread_msg_count':   unread_msg_count,
        'recent_messages':    recent_messages,
        'notifs':             notifs,
        'unread_notif_count': unread_notif_count,
        'wallet':             wallet,
        'wallet_txns':        wallet_txns,
        'current_sub':        current_sub,
        'available_plans':    available_plans,
        'billing_records':    billing_records,
        'profile':            profile,
        'profile_pct':        profile_pct,
        'profile_incomplete': profile_incomplete,
        'show_referral_popup': show_referral_popup,
        'referral_link':      referral_link,
        'job_posted_title':   job_posted_title,
        'recent_flicks':      recent_flicks,
        'liked_ids':          liked_ids,
    })


@login_required
def employer_profile_save(request):
    if request.method != 'POST':
        return redirect('employer_dashboard')
    user = request.user
    p = request.POST
    user.city    = p.get('city', '').strip()
    user.address = p.get('address', '').strip()
    user.pincode = p.get('pincode', '').strip()
    user.email   = p.get('email', '').strip()
    user.whatsapp = p.get('whatsapp', '').strip()
    user.save()
    try:
        prof = user.company
    except Exception:
        prof = None
    if prof:
        prof.industry     = p.get('industry', '').strip()
        prof.company_size = p.get('company_size', '').strip()
        prof.website      = p.get('website', '').strip()
        prof.save()
    return redirect('employer_dashboard')


@login_required
def jobseeker_dashboard(request):
    applications = JobApplication.objects.filter(applicant=request.user).select_related('job')
    try:
        profile = request.user.seeker
        qs = Job.objects.filter(status='active', is_approved=True, job_plan__in=['free', 'paid'])
        if profile.job_category and profile.job_category != 'any':
            qs = qs.filter(collar_type=profile.job_category)
        recommended = qs.order_by('-created_at')[:4]
    except Exception:
        profile = None
        recommended = Job.objects.filter(status='active', is_approved=True, job_plan__in=['free', 'paid']).order_by('-created_at')[:4]
    notifs = UserNotification.objects.filter(user=request.user).order_by('-created_at')[:12]
    unread_notif_count = UserNotification.objects.filter(user=request.user, is_read=False).count()
    show_referral_popup = request.session.pop('show_referral_popup', False)
    referral_link = request.build_absolute_uri(f'/register/?ref={request.user.referral_code}') if request.user.referral_code else ''
    from .models import Flick, FlickLike
    recent_flicks = Flick.objects.filter(user=request.user).select_related('user').prefetch_related('likes').order_by('-created_at')[:12]
    liked_ids = set(FlickLike.objects.filter(user=request.user).values_list('flick_id', flat=True))
    return render(request, 'jobseeker_dashboard.html', {
        'applications':       applications,
        'recommended':        recommended,
        'profile':            profile,
        'notifs':             notifs,
        'unread_notif_count': unread_notif_count,
        'show_referral_popup': show_referral_popup,
        'referral_link':      referral_link,
        'recent_flicks':      recent_flicks,
        'liked_ids':          liked_ids,
    })


@login_required
def seeker_profile(request):
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
    states    = State.objects.filter(is_active=True).order_by('name')
    districts = District.objects.filter(is_active=True).order_by('name')
    industries = Industry.objects.filter(is_active=True).prefetch_related('roles')
    certificates = profile.certificates.all()

    if request.method == 'POST':
        p = request.POST
        f = request.FILES

        # ── Personal ──────────────────────────────────────────
        user = request.user
        first_name = p.get('first_name', '').strip()
        last_name  = p.get('last_name', '').strip()
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.address  = p.get('address', '').strip()
        user.city     = p.get('city', '').strip()
        user.pincode  = p.get('pincode', '').strip()
        user.whatsapp = p.get('whatsapp', '').strip()
        user.save()

        dob_str = p.get('dob', '').strip()
        try:
            from datetime import date
            profile.dob = date.fromisoformat(dob_str) if dob_str else None
        except ValueError:
            profile.dob = None

        profile.gender   = p.get('gender', '')
        if 'photo' in f:
            profile.photo = f['photo']

        # ── Location ──────────────────────────────────────────
        district_id = p.get('district', '')
        state_id    = p.get('state', '')
        profile.district_id       = int(district_id) if district_id else None
        profile.state_id          = int(state_id)    if state_id    else None
        profile.preferred_location = p.get('preferred_location', '').strip()
        profile.preferred_pincode  = p.get('preferred_pincode',  '').strip()
        profile.open_to_relocate   = 'open_to_relocate' in p

        # ── Career ────────────────────────────────────────────
        profile.job_category    = p.get('job_category', 'any')
        profile.industry        = p.get('industry', '').strip()
        profile.preferred_roles = p.get('preferred_roles', '').strip()
        profile.availability    = p.get('availability', 'immediate')

        # ── Salary ────────────────────────────────────────────
        sal_min = p.get('salary_min', '').strip()
        sal_max = p.get('salary_max', '').strip()
        profile.salary_min  = int(sal_min) if sal_min.isdigit() else None
        profile.salary_max  = int(sal_max) if sal_max.isdigit() else None
        profile.salary_type = p.get('salary_type', 'month')
        profile.rate        = p.get('rate', '').strip()

        # ── Qualifications ────────────────────────────────────
        profile.education         = p.get('education', '').strip()
        profile.education_details = p.get('education_details', '').strip()
        profile.experience        = p.get('experience', '').strip()
        profile.skills            = p.get('skills', '').strip()
        profile.languages         = p.get('languages', '').strip()
        profile.primary_skill     = p.get('primary_skill', '').strip()

        # ── Documents ─────────────────────────────────────────
        if 'resume' in f:
            profile.resume = f['resume']
        if 'driving_license' in f:
            profile.driving_license = f['driving_license']
        if 'portfolio_file' in f:
            profile.portfolio_file = f['portfolio_file']
        profile.portfolio_url = p.get('portfolio_url', '').strip()

        profile.profile_completed = True
        profile.save()

        # ── Certificates (add new ones) ────────────────────────
        cert_titles = p.getlist('cert_title')
        cert_issuers = p.getlist('cert_issuer')
        cert_years  = p.getlist('cert_year')
        cert_files  = f.getlist('cert_file')
        for i, title in enumerate(cert_titles):
            title = title.strip()
            if not title:
                continue
            cert = SeekerCertificate(
                seeker=profile,
                title=title,
                issued_by=cert_issuers[i] if i < len(cert_issuers) else '',
                issued_year=cert_years[i] if i < len(cert_years) else '',
            )
            if i < len(cert_files) and cert_files[i]:
                cert.file = cert_files[i]
            cert.save()

        # ── Delete removed certificates ────────────────────────
        delete_cert_ids = p.getlist('delete_cert')
        if delete_cert_ids:
            SeekerCertificate.objects.filter(
                pk__in=delete_cert_ids, seeker=profile
            ).delete()

        return redirect('seeker_profile')

    pct = profile.completion_percent()
    ctx = {
        'profile':              profile,
        'certificates':         certificates,
        'states':               states,
        'districts':            districts,
        'industries':           industries,
        'user':                 request.user,
        'skills_list':          [s.strip() for s in (profile.skills or '').split(',') if s.strip()],
        'langs_list':           [l.strip() for l in (profile.languages or '').split(',') if l.strip()],
        'roles_list':           [r.strip() for r in (profile.preferred_roles or '').split(',') if r.strip()],
        'completion_pct':       pct,
        'completion_remaining': 100 - pct,
    }
    return render(request, 'seeker_profile.html', ctx)


@login_required
def seeker_cert_delete(request, cert_id):
    SeekerCertificate.objects.filter(pk=cert_id, seeker__user=request.user).delete()
    return redirect('seeker_profile')




# ── OTP via 2Factor.in ────────────────────────────────────────────────────────
def send_otp(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    import json, random, requests as _req
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
    except Exception:
        phone = request.POST.get('phone', '').strip()

    if not phone or len(phone) != 10 or not phone.isdigit():
        return JsonResponse({'success': False, 'error': 'Enter a valid 10-digit mobile number.'})

    otp = str(random.randint(100000, 999999))

    from django.conf import settings as _s
    api_key  = _s.TWO_FACTOR_API_KEY
    template = _s.TWO_FACTOR_OTP_TEMPLATE
    url = f'https://2factor.in/API/V1/{api_key}/SMS/{phone}/{otp}/{template}'

    try:
        resp   = _req.get(url, timeout=10)
        result = resp.json()
    except Exception:
        return JsonResponse({'success': False, 'error': 'SMS service unavailable. Try again.'})

    if result.get('Status') == 'Success':
        request.session['otp']         = otp
        request.session['otp_phone']   = phone
        request.session['otp_verified'] = False
        request.session.modified = True
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': result.get('Details', 'Failed to send OTP.')})


def verify_otp(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    import json
    data    = json.loads(request.body)
    entered = data.get('otp', '').strip()
    stored  = request.session.get('otp', '')

    if not stored:
        return JsonResponse({'success': False, 'error': 'OTP expired. Please resend.'})

    if entered == stored:
        request.session['otp_verified'] = True
        request.session.pop('otp', None)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Wrong OTP. Please try again.'})


def check_phone(request):
    """Check if a phone number is already registered."""
    if request.method != 'POST':
        return JsonResponse({'exists': False})
    import json
    data  = json.loads(request.body)
    phone = data.get('phone', '').strip()
    User  = get_user_model()
    user  = User.objects.filter(phone=phone).first()
    if user:
        return JsonResponse({'exists': True, 'name': user.first_name or user.username})
    return JsonResponse({'exists': False})


def phone_login(request):
    """Login with phone number + password (for returning users)."""
    if request.method != 'POST':
        return JsonResponse({'success': False})
    import json
    data     = json.loads(request.body)
    phone    = data.get('phone', '').strip()
    password = data.get('password', '')
    User     = get_user_model()
    user     = User.objects.filter(phone=phone).first()
    if user and user.check_password(password):
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        redirect_url = '/employer/dashboard/' if user.is_employer() else '/jobseeker/dashboard/'
        return JsonResponse({'success': True, 'redirect': redirect_url})
    return JsonResponse({'success': False, 'error': 'Wrong password. Try again.'})


def quick_register(request):
    """Create basic user profile after OTP verification from onboarding modal."""
    if request.method != 'POST':
        return JsonResponse({'success': False})

    import json
    data     = json.loads(request.body)
    name     = data.get('name', '').strip()
    phone    = data.get('phone', '').strip()
    pincode  = data.get('pincode', '').strip()
    job_type = data.get('job_type', 'find')
    collar   = data.get('collar', '')
    password = data.get('password', '').strip()

    if not request.session.get('otp_verified'):
        return JsonResponse({'success': False, 'error': 'OTP not verified'})
    if not name or not phone or not pincode:
        return JsonResponse({'success': False, 'error': 'Missing required fields'})
    if not password or len(password) < 6:
        return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters'})

    User = get_user_model()

    if User.objects.filter(phone=phone).exists():
        return JsonResponse({'success': False, 'error': 'This phone number is already registered. Please sign in.'})

    user_type = 'employee' if job_type == 'find' else 'individual_employer'
    username  = phone
    if User.objects.filter(username=username).exists():
        import random
        username = phone + str(random.randint(10, 99))

    user = User.objects.create_user(
        username   = username,
        first_name = name,
        phone      = phone,
        pincode    = pincode,
        user_type  = user_type,
        password   = password,
    )

    # Store collar preference in seeker profile
    if job_type == 'find' and collar:
        from .models import JobSeekerProfile
        profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
        profile.job_category = collar
        profile.save()

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    request.session.pop('otp_verified', None)

    redirect_url = '/post-job/' if job_type == 'post' else '/jobseeker/profile/'
    return JsonResponse({'success': True, 'redirect': redirect_url})


# ── SAVE JOB ──────────────────────────────────────────────────────────────────
@login_required
def save_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    saved, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created:
        saved.delete()
        return JsonResponse({'saved': False, 'msg': 'Job removed from saved list'})
    return JsonResponse({'saved': True, 'msg': 'Job saved!'})


@login_required
def saved_jobs(request):
    saves = SavedJob.objects.filter(user=request.user).select_related('job')
    return render(request, 'saved_jobs.html', {'saves': saves})


# ── WITHDRAW APPLICATION ───────────────────────────────────────────────────────
@login_required
def withdraw_application(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, applicant=request.user)
    if app.status in ('pending', 'shortlisted'):
        app.status = 'withdrawn'
        app.save()
        messages.success(request, 'Application withdrawn.')
    else:
        messages.error(request, 'Cannot withdraw at this stage.')
    return redirect('jobseeker_dashboard')


# ── MESSAGING ─────────────────────────────────────────────────────────────────
def _get_or_create_conv(user1, user2, job=None):
    a, b = (user1, user2) if user1.pk < user2.pk else (user2, user1)
    conv, _ = Conversation.objects.get_or_create(user_a=a, user_b=b, job=job)
    return conv


def _render_bubble(msg, me):
    from django.template.loader import render_to_string
    return render_to_string('partials/msg_bubble.html', {'msg': msg, 'me': me})


def _msg_to_dict(msg, me):
    d = {
        'id':      msg.pk,
        'sender':  msg.sender_id,
        'mine':    msg.sender_id == me.id,
        'type':    msg.msg_type,
        'content': msg.content,
        'time':    msg.sent_at.strftime('%I:%M %p'),
        'is_read': msg.is_read,
        'html':    _render_bubble(msg, me),
    }
    if msg.file:
        d['file_url']  = msg.file.url
        d['file_name'] = msg.file_name
    if msg.msg_type == 'interview_invite':
        d['invite'] = {
            'date':     str(msg.invite_date) if msg.invite_date else '',
            'time':     str(msg.invite_time) if msg.invite_time else '',
            'mode':     msg.invite_mode,
            'location': msg.invite_location,
            'link':     msg.invite_link,
            'notes':    msg.invite_notes,
            'status':   msg.invite_status,
        }
    return d


def _sidebar_data(user):
    convs = Conversation.objects.filter(
        Q(user_a=user) | Q(user_b=user)
    ).select_related('user_a', 'user_b', 'job').order_by('-updated_at')
    rows = []
    for c in convs:
        last = c.messages.order_by('-sent_at').first()
        rows.append({'conv': c, 'other': c.other_user(user),
                     'last': last, 'unread': c.unread_for(user)})
    return rows


@login_required
def chat_list(request):
    sidebar      = _sidebar_data(request.user)
    total_unread = sum(d['unread'] for d in sidebar)
    return render(request, 'messages.html', {
        'conversations': sidebar,
        'total_unread':  total_unread,
        'active_conv':   None,
    })


@login_required
def chat_room(request, conv_id, **_):
    conv = get_object_or_404(Conversation, pk=conv_id)
    me   = request.user
    if conv.user_a != me and conv.user_b != me:
        return redirect('chat_list')
    conv.messages.filter(is_read=False).exclude(sender=me).update(
        is_read=True, read_at=timezone.now()
    )
    sidebar = _sidebar_data(me)
    msgs    = conv.messages.select_related('sender').order_by('sent_at')
    return render(request, 'messages.html', {
        'conversations': sidebar,
        'active_conv':   conv,
        'other':         conv.other_user(me),
        'msgs':          msgs,
        'total_unread':  sum(d['unread'] for d in sidebar),
    })


@login_required
def start_conversation(request, user_id, job_id=0):
    other = get_object_or_404(User, pk=user_id)
    job   = Job.objects.filter(pk=job_id).first() if job_id else None
    conv  = _get_or_create_conv(request.user, other, job)
    return redirect('chat_room', conv_id=conv.pk)


@login_required
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    conv = get_object_or_404(Conversation, pk=request.POST.get('conv_id'))
    me   = request.user
    if conv.user_a != me and conv.user_b != me:
        return JsonResponse({'ok': False}, status=403)

    other    = conv.other_user(me)
    msg_type = request.POST.get('msg_type', 'text')
    content  = request.POST.get('content', '').strip()
    f        = request.FILES.get('file')

    msg = Message(conversation=conv, sender=me, receiver=other,
                  job=conv.job, msg_type=msg_type, content=content)

    if msg_type == 'interview_invite':
        msg.invite_date     = request.POST.get('invite_date') or None
        msg.invite_time     = request.POST.get('invite_time') or None
        msg.invite_mode     = request.POST.get('invite_mode', '')
        msg.invite_location = request.POST.get('invite_location', '')
        msg.invite_link     = request.POST.get('invite_link', '')
        msg.invite_notes    = request.POST.get('invite_notes', '')
        msg.invite_status   = 'pending'
        msg.content         = content or 'Interview Invitation'

    if f:
        ext          = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        msg.msg_type = 'image' if ext in ('jpg','jpeg','png','gif','webp') else (msg_type if msg_type == 'resume' else 'file')
        msg.file      = f
        msg.file_name = f.name

    msg.save()
    conv.save()   # bumps updated_at

    UserNotification.objects.create(
        user=other,
        title=f'New message from {me.get_full_name() or me.username}',
        message=(content or (f.name if f else ''))[:80],
        notif_type='info',
        link=f'/messages/{conv.pk}/',
    )
    return JsonResponse({'ok': True, 'msg_id': msg.pk, 'html': _render_bubble(msg, me)})


@login_required
def poll_messages(request, conv_id):
    conv = get_object_or_404(Conversation, pk=conv_id)
    me   = request.user
    if conv.user_a != me and conv.user_b != me:
        return JsonResponse({'ok': False}, status=403)
    after    = int(request.GET.get('after', 0))
    new_msgs = conv.messages.filter(pk__gt=after).exclude(sender=me)
    new_msgs.filter(is_read=False).update(is_read=True, read_at=timezone.now())
    return JsonResponse({'ok': True, 'messages': [_msg_to_dict(m, me) for m in new_msgs]})


@login_required
def respond_invite(request, msg_id):
    msg    = get_object_or_404(Message, pk=msg_id, msg_type='interview_invite')
    me     = request.user
    action = request.POST.get('action', '')
    if msg.receiver == me and action in ('accepted', 'rejected'):
        msg.invite_status = action
        msg.save()
        UserNotification.objects.create(
            user=msg.sender,
            title=f'Interview {action.title()} by {me.get_full_name() or me.username}',
            message=f'Your interview invitation was {action}.',
            notif_type='success' if action == 'accepted' else 'warning',
            link=f'/messages/{msg.conversation_id}/',
        )
    return JsonResponse({'ok': True, 'status': msg.invite_status})


@login_required
def chat_messages_api(request, user_id, job_id=0):
    other = get_object_or_404(User, pk=user_id)
    conv  = _get_or_create_conv(request.user, other)
    return redirect('chat_room', conv_id=conv.pk)


# ==============================================================
# ADVERTISER MODULE
# ==============================================================

@login_required
def ads_gallery(request):
    """Public page: show all ads same style as home page."""
    ads = Advertisement.objects.select_related('advertiser', 'package').order_by('-created_at')
    advertiser_banners = Advertiser.objects.filter(
        status='approved', banner_image__isnull=False
    ).exclude(banner_image='')
    return render(request, 'ads_gallery.html', {
        'ads': ads,
        'advertiser_banners': advertiser_banners,
    })


def advertiser_register(request):
    """Only registered employer accounts can apply to advertise."""
    user = request.user

    # Block non-employer users
    if not user.is_employer():
        messages.error(request, 'Only registered business accounts (Company, Shop, Factory, etc.) can post advertisements. Please register as an employer first.')
        return redirect('register')

    # Already has an advertiser profile
    if hasattr(user, 'advertiser'):
        messages.info(request, 'You already have an advertiser profile.')
        return redirect('advertiser_dashboard')

    if request.method == 'POST':
        adv = Advertiser.objects.create(
            business_name  = request.POST.get('business_name', '').strip(),
            contact_person = request.POST.get('contact_person', user.get_full_name()).strip(),
            phone          = request.POST.get('phone', user.phone).strip(),
            email          = request.POST.get('email', user.email).strip(),
            address        = request.POST.get('address', '').strip(),
            description    = request.POST.get('description', '').strip(),
            gst            = request.POST.get('gst', '').strip(),
            website        = request.POST.get('website', '').strip(),
            status         = 'pending',
            user           = user,
        )
        if 'banner_image' in request.FILES:
            adv.banner_image = request.FILES['banner_image']
            adv.save()

        return redirect('advertiser_register_success')

    from .models import Flick, FlickLike
    recent_flicks = Flick.objects.select_related('user').order_by('-created_at')[:16]
    liked_ids = set()
    if request.user.is_authenticated:
        liked_ids = set(FlickLike.objects.filter(user=request.user).values_list('flick_id', flat=True))
    return render(request, 'advertiser_register.html', {'user': user, 'recent_flicks': recent_flicks, 'liked_ids': liked_ids})


def advertiser_register_success(request):
    return render(request, 'advertiser_register_success.html')


@login_required
def advertiser_dashboard(request):
    try:
        adv = request.user.advertiser
    except Advertiser.DoesNotExist:
        messages.info(request, 'Please register as an advertiser first.')
        return redirect('advertiser_register')
    ads = adv.ads.select_related('package').order_by('-created_at')
    total_views  = sum(a.views  for a in ads)
    total_clicks = sum(a.clicks for a in ads)
    active_count = ads.filter(status='active').count()
    expiring     = [a for a in ads if a.is_expiring_soon()]
    packages     = AdPackage.objects.filter(is_active=True)
    return render(request, 'advertiser_dashboard.html', {
        'adv': adv, 'ads': ads,
        'total_views': total_views, 'total_clicks': total_clicks,
        'active_count': active_count, 'expiring': expiring,
        'packages': packages,
    })


@login_required
def create_advertisement(request):
    try:
        adv = request.user.advertiser
    except Advertiser.DoesNotExist:
        return redirect('advertiser_register')

    if adv.status != 'approved':
        messages.error(request, 'Your advertiser account is pending admin approval.')
        return redirect('advertiser_dashboard')

    packages = AdPackage.objects.filter(is_active=True)

    if request.method == 'POST':
        pkg_id = request.POST.get('package')
        pkg = get_object_or_404(AdPackage, pk=pkg_id, is_active=True)
        ad = Advertisement.objects.create(
            advertiser = adv,
            package    = pkg,
            title      = request.POST.get('title', '').strip(),
            link_url   = request.POST.get('link_url', '').strip(),
            content    = request.POST.get('content', '').strip(),
            district   = request.POST.get('district', '').strip(),
            state      = request.POST.get('state', '').strip(),
            status     = 'pending_payment',
        )
        if 'image' in request.FILES:
            ad.image = request.FILES['image']
            ad.save()
        import decimal
        gst   = (pkg.price * decimal.Decimal('0.18')).quantize(decimal.Decimal('0.01'))
        total = pkg.price + gst
        import random, string
        inv   = ''.join(random.choices(string.digits, k=8))
        AdPayment.objects.create(
            advertisement  = ad,
            amount         = pkg.price,
            gst_amount     = gst,
            total_amount   = total,
            invoice_number = inv,
        )
        return redirect('ad_payment', ad_id=ad.pk)

    # Pre-fill website from company/shop/advertiser profile
    user = request.user
    prefill_website = (
        adv.website
        or (user.company.website if hasattr(user, 'company') else '')
        or (user.shop.website    if hasattr(user, 'shop')    else '')
    )
    return render(request, 'create_ad.html', {'packages': packages, 'prefill_website': prefill_website})


@login_required
def ad_payment(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id, advertiser__user=request.user)
    payment = ad.payment
    if request.method == 'POST':
        method = request.POST.get('method', 'upi')
        import uuid
        from django.utils import timezone as tz
        payment.status         = 'paid'
        payment.payment_method = method
        payment.transaction_id = str(uuid.uuid4())[:18].upper()
        payment.paid_at        = tz.now()
        payment.save()
        from datetime import date, timedelta
        ad.status     = 'pending_review'
        ad.start_date = date.today()
        ad.end_date   = date.today() + timedelta(days=ad.package.duration_days)
        ad.save()
        messages.success(request, f'Payment successful! Ad is under review and will go live soon.')
        return redirect('ad_payment_success', ad_id=ad.pk)
    return render(request, 'ad_payment.html', {'ad': ad, 'payment': payment})


@login_required
def ad_payment_success(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id, advertiser__user=request.user)
    return render(request, 'ad_payment_success.html', {'ad': ad})


@login_required
def ad_performance(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id, advertiser__user=request.user)
    return render(request, 'ad_performance.html', {'ad': ad})


@login_required
def renew_ad(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id, advertiser__user=request.user)
    if request.method == 'POST':
        import decimal
        pkg   = ad.package
        gst   = (pkg.price * decimal.Decimal('0.18')).quantize(decimal.Decimal('0.01'))
        total = pkg.price + gst
        import random, string
        inv   = ''.join(random.choices(string.digits, k=8))
        new_ad = Advertisement.objects.create(
            advertiser = ad.advertiser,
            package    = pkg,
            title      = ad.title,
            image      = ad.image,
            link_url   = ad.link_url,
            content    = ad.content,
            district   = ad.district,
            state      = ad.state,
            status     = 'pending_payment',
        )
        AdPayment.objects.create(
            advertisement  = new_ad,
            amount         = pkg.price,
            gst_amount     = gst,
            total_amount   = total,
            invoice_number = inv,
        )
        return redirect('ad_payment', ad_id=new_ad.pk)
    return render(request, 'renew_ad.html', {'ad': ad})


def ad_click_track(request, ad_id):
    """Tracks click and redirects to destination."""
    try:
        ad = Advertisement.objects.get(pk=ad_id, status='active')
        Advertisement.objects.filter(pk=ad_id).update(clicks=ad.clicks + 1)
        if ad.link_url:
            return redirect(ad.link_url)
    except Advertisement.DoesNotExist:
        pass
    return redirect('home')


# ── ADMIN: Advertiser Management ─────────────────────────────────────────────

def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_advertisers(request):
    from urllib.parse import quote
    status_filter = request.GET.get('status', 'pending')
    advs = Advertiser.objects.filter(status=status_filter).order_by('-created_at')
    counts = {s: Advertiser.objects.filter(status=s).count()
              for s in ('pending', 'approved', 'rejected', 'suspended')}
    for adv in advs:
        phone = ''.join(ch for ch in (adv.phone or '') if ch.isdigit())
        if phone and not phone.startswith('91'):
            phone = '91' + phone
        name = adv.contact_person or adv.business_name
        msg = f"Hi {name}, we received your advertiser registration ({adv.business_name}) on Pincode Job Portal. Are you interested in proceeding? Please confirm."
        adv.wa_link = f"https://wa.me/{phone}?text={quote(msg)}" if phone else ''
    return render(request, 'admin_advertisers.html', {
        'advs': advs, 'status_filter': status_filter, 'counts': counts,
    })


@admin_required
def admin_approve_advertiser(request, adv_id):
    adv = get_object_or_404(Advertiser, pk=adv_id)
    adv.status      = 'approved'
    adv.approved_at = timezone.now()
    adv.save()
    messages.success(request, f'{adv.business_name} approved!')
    return redirect('admin_advertisers')


@admin_required
def admin_reject_advertiser(request, adv_id):
    adv = get_object_or_404(Advertiser, pk=adv_id)
    adv.status         = 'rejected'
    adv.rejection_note = request.POST.get('note', '')
    adv.save()
    messages.info(request, f'{adv.business_name} rejected.')
    return redirect('admin_advertisers')


@admin_required
def admin_ad_list(request):
    from urllib.parse import quote
    status_filter = request.GET.get('status', 'pending_review')
    ads = Advertisement.objects.filter(status=status_filter).select_related('advertiser', 'package').order_by('-created_at')
    for ad in ads:
        phone = ''.join(ch for ch in (ad.advertiser.phone or '') if ch.isdigit())
        if phone and not phone.startswith('91'):
            phone = '91' + phone
        name = ad.advertiser.contact_person or ad.advertiser.business_name
        msg = f"Hi {name}, we received your ad '{ad.title}' on Pincode Job Portal. Are you interested in proceeding? Please confirm."
        ad.wa_link = f"https://wa.me/{phone}?text={quote(msg)}" if phone else ''
    return render(request, 'admin_ad_list.html', {'ads': ads, 'status_filter': status_filter})


@admin_required
def admin_set_ad_image(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id)
    if request.method == 'POST' and 'image' in request.FILES:
        ad.image = request.FILES['image']
        ad.save()
        messages.success(request, f'Image updated for "{ad.title}".')
    status_filter = request.POST.get('status_filter', 'pending_review')
    return redirect(f"/admin-panel/ads/?status={status_filter}")


@admin_required
def admin_activate_ad(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id)
    ad.status = 'active'
    ad.save()
    Advertisement.objects.filter(pk=ad_id).update(views=ad.views)
    messages.success(request, f'Ad "{ad.title}" is now live!')
    return redirect('admin_ad_list')


@admin_required
def admin_reject_ad(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id)
    ad.status = 'rejected'
    ad.save()
    messages.info(request, f'Ad "{ad.title}" rejected.')
    return redirect('admin_ad_list')


@admin_required
def admin_delete_ad(request, ad_id):
    ad = get_object_or_404(Advertisement, pk=ad_id)
    title = ad.title
    status_filter = request.POST.get('status_filter', 'pending_review')
    ad.delete()
    messages.success(request, f'Ad "{title}" deleted.')
    return redirect(f'/admin-panel/ads/?status={status_filter}')


# ── ADMIN USERS LIST ────────────────────────────────────────────────────────
@admin_required
def admin_users(request):
    return _users_list(request)


def super_admin_users(request):
    if not request.user.is_authenticated or request.user.admin_role != 'super_admin':
        messages.error(request, 'Super Admin access required.')
        return redirect('login')
    return _users_list(request)


def _users_list(request):
    from django.db.models import Q
    search   = request.GET.get('q', '').strip()
    utype    = request.GET.get('type', '')

    qs = User.objects.exclude(user_type='advertiser').order_by('-date_joined')

    if utype == 'employer':
        qs = qs.filter(user_type__in=User.EMPLOYER_TYPES)
    elif utype == 'jobseeker':
        qs = qs.filter(user_type__in=['employee', 'individual', 'freelancer'])
    elif utype == 'admin':
        qs = qs.exclude(admin_role='')

    if search:
        qs = qs.filter(
            Q(first_name__icontains=search) | Q(last_name__icontains=search) |
            Q(phone__icontains=search) | Q(email__icontains=search) |
            Q(pincode__icontains=search) | Q(city__icontains=search)
        )

    employer_count  = User.objects.filter(user_type__in=User.EMPLOYER_TYPES).count()
    jobseeker_count = User.objects.filter(user_type__in=['employee','individual','freelancer']).count()
    admin_count     = User.objects.exclude(admin_role='').count()

    return render(request, 'admin_users.html', {
        'users': qs,
        'search': search,
        'utype': utype,
        'employer_count': employer_count,
        'jobseeker_count': jobseeker_count,
        'admin_count': admin_count,
        'total_count': User.objects.exclude(user_type='advertiser').count(),
    })


# ── ADMIN PANEL LOGIN ────────────────────────────────────────────────────────
def admin_panel_login(request):
    if request.method != 'POST':
        return redirect('home')
    phone    = request.POST.get('phone', '').strip()
    password = request.POST.get('password', '').strip()
    user = authenticate(request, username=phone, password=password)
    if user and getattr(user, 'admin_role', None):
        login(request, user, backend='jobs.backends.PhoneOrEmailBackend')
        role = user.admin_role
        if role == 'super_admin':
            return redirect('/super-admin/')
        elif role == 'state_admin':
            return redirect('/state-admin/')
        else:
            return redirect('/district-admin/')
    messages.error(request, 'Invalid phone number / password, or not an admin account.')
    return redirect('home')


# ── NEARBY JOBS API ──────────────────────────────────────────────────────────
def nearby_jobs_api(request):
    """
    GET /api/nearby-jobs/?pincode=600001&radius=5&collar=blue&q=driver
    Returns JSON list of jobs within radius_km, sorted by distance.
    """
    pincode   = request.GET.get('pincode', '').strip()
    radius_km = float(request.GET.get('radius', 5))
    collar    = request.GET.get('collar', '')
    q         = request.GET.get('q', '')

    if not pincode:
        return JsonResponse({'error': 'pincode is required'}, status=400)

    from .utils import geocode_pincode, jobs_within_radius

    lat, lng = geocode_pincode(pincode)
    if lat is None:
        return JsonResponse({'error': f'Could not geocode pincode {pincode}'}, status=404)

    base_qs = Job.objects.filter(status='active')
    if collar:
        base_qs = base_qs.filter(collar_type=collar)
    if q:
        base_qs = base_qs.filter(Q(title__icontains=q) | Q(category__icontains=q))

    pairs = jobs_within_radius(lat, lng, radius_km, queryset=base_qs)

    results = []
    for job, dist in pairs:
        results.append({
            'id':          job.pk,
            'title':       job.title,
            'category':    job.category,
            'industry':    job.industry,
            'collar':      job.collar_type,
            'location':    job.location,
            'pincode':     job.pincode,
            'distance_km': dist,
            'salary':      job.salary_display(),
            'job_type':    job.job_type,
            'is_urgent':   job.is_urgent,
            'url':         f'/jobs/{job.pk}/',
        })

    return JsonResponse({
        'center':    {'lat': lat, 'lng': lng, 'pincode': pincode},
        'radius_km': radius_km,
        'count':     len(results),
        'jobs':      results,
    })


# ── AI JOB DESCRIPTION ───────────────────────────────────────────────────────
@login_required
def ai_generate_description(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    from django.conf import settings as django_settings
    api_key = getattr(django_settings, 'ANTHROPIC_API_KEY', '').strip()
    if not api_key:
        return JsonResponse({'error': 'API key not configured. Add ANTHROPIC_API_KEY in settings.py.'}, status=500)
    try:
        import anthropic
        title       = request.POST.get('title', '').strip()
        industry    = request.POST.get('industry', '').strip()
        role        = request.POST.get('category', '').strip()
        job_type    = request.POST.get('job_type', '').strip()
        experience  = request.POST.get('experience', '').strip()
        salary_min  = request.POST.get('salary_min', '').strip()
        salary_max  = request.POST.get('salary_max', '').strip()
        salary_type = request.POST.get('salary_type', 'month').strip()
        collar      = request.POST.get('collar_type', '').strip()

        salary_text = ''
        if salary_min and salary_max:
            salary_text = f'₹{salary_min}–₹{salary_max} per {salary_type}'
        elif salary_min:
            salary_text = f'₹{salary_min}+ per {salary_type}'

        prompt = f"""Write a professional job description for a job posting on an Indian job portal.

Job Details:
- Title: {title or role}
- Industry: {industry}
- Role: {role}
- Type: {job_type.replace('_', ' ').title()}
- Experience: {experience}
- Salary: {salary_text or 'Negotiable'}
- Collar type: {collar} collar

Write 3–4 short paragraphs:
1. About the role (2–3 sentences)
2. Key responsibilities (4–5 bullet points)
3. What we're looking for (3–4 bullet points)
4. One closing sentence inviting applications

Keep it clear, professional, and suitable for Indian job seekers. Do not include headings or markdown — plain text only."""

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=600,
            messages=[{'role': 'user', 'content': prompt}]
        )
        description = message.content[0].text.strip()
        return JsonResponse({'description': description})
    except Exception as e:
        msg = str(e)
        if 'credit balance is too low' in msg or '400' in msg:
            return JsonResponse({'error': 'Insufficient API credits. Please add credits at console.anthropic.com → Plans & Billing.'}, status=402)
        return JsonResponse({'error': msg}, status=500)


# ── INTERVIEW ─────────────────────────────────────────────────────────────────
@login_required
def schedule_interview(request, app_id):
    app = get_object_or_404(JobApplication, pk=app_id, job__posted_by=request.user)
    if request.method == 'POST':
        import datetime as dt
        Interview.objects.update_or_create(
            application=app,
            defaults={
                'date':     dt.datetime.strptime(request.POST['date'], '%Y-%m-%d').date(),
                'time':     dt.datetime.strptime(request.POST['time'], '%H:%M').time(),
                'mode':     request.POST.get('mode', 'in_person'),
                'location': request.POST.get('location', ''),
                'link':     request.POST.get('link', ''),
                'notes':    request.POST.get('notes', ''),
                'status':   'scheduled',
            }
        )
        app.status = 'interview_scheduled'
        app.save()
        messages.success(request, 'Interview scheduled and candidate notified.')
        return redirect('employer_dashboard')
    return render(request, 'schedule_interview.html', {'app': app})


@login_required
def accept_interview(request, app_id):
    app = get_object_or_404(JobApplication, pk=app_id, applicant=request.user)
    if hasattr(app, 'interview'):
        app.interview.status = 'accepted'
        app.interview.save()
        app.status = 'interview_accepted'
        app.save()
        messages.success(request, 'Interview accepted! Check your schedule.')
    return redirect('jobseeker_dashboard')


@login_required
def reject_interview(request, app_id):
    app = get_object_or_404(JobApplication, pk=app_id, applicant=request.user)
    if hasattr(app, 'interview'):
        app.interview.status = 'rejected'
        app.interview.save()
        app.status = 'interview_rejected'
        app.save()
        messages.info(request, 'Interview declined.')
    return redirect('jobseeker_dashboard')


# ── OFFER LETTER ──────────────────────────────────────────────────────────────
@login_required
def send_offer_letter(request, app_id):
    app = get_object_or_404(JobApplication, pk=app_id, job__posted_by=request.user)
    if request.method == 'POST':
        import datetime as dt
        OfferLetter.objects.update_or_create(
            application=app,
            defaults={
                'position':     request.POST.get('position', app.job.title),
                'salary':       request.POST.get('salary', ''),
                'joining_date': dt.datetime.strptime(request.POST['joining_date'], '%Y-%m-%d').date(),
                'content':      request.POST.get('content', ''),
            }
        )
        app.status = 'offer_sent'
        app.save()
        messages.success(request, 'Offer letter sent to candidate.')
        return redirect('employer_dashboard')
    return render(request, 'offer_letter_form.html', {'app': app})


@login_required
def download_offer_letter(request, app_id):
    app    = get_object_or_404(JobApplication, pk=app_id, applicant=request.user)
    offer  = get_object_or_404(OfferLetter, application=app)
    return render(request, 'offer_letter_print.html', {'offer': offer, 'app': app})


# ==============================================================
# ADMIN HIERARCHY MODULE  (Super → State → District)
# ==============================================================
from functools import wraps

def super_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.admin_role != 'super_admin':
            messages.error(request, 'Super Admin access required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def state_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.admin_role not in ('super_admin', 'state_admin'):
            messages.error(request, 'State Admin access required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def district_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.admin_role:
            messages.error(request, 'Admin access required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── SUPER ADMIN ──────────────────────────────────────────────────────────────

@super_admin_required
def super_admin_dashboard(request):
    total_users     = User.objects.count()
    total_jobs      = Job.objects.count()
    active_jobs     = Job.objects.filter(status='active').count()
    total_apps      = JobApplication.objects.count()
    total_states    = State.objects.count()
    total_districts = District.objects.count()
    total_adverts   = Advertiser.objects.count()
    pending_adverts = Advertiser.objects.filter(status='pending').count()
    open_complaints = Complaint.objects.filter(status='open').count()
    employer_count  = User.objects.filter(user_type__in=User.EMPLOYER_TYPES, admin_role='').count()
    jobseeker_count = User.objects.filter(user_type__in=['employee','individual','freelancer'], admin_role='').count()
    recent_users       = User.objects.order_by('-date_joined')[:8]
    state_list         = State.objects.annotate(d_count=Count('districts')).order_by('name')
    recent_jobs        = Job.objects.select_related('posted_by').order_by('-created_at')[:6]
    industries         = Industry.objects.filter(is_active=True)
    notifications      = SystemNotification.objects.filter(is_active=True)[:5]
    pending_jobs_count = Job.objects.filter(status='active', is_approved=False).count()
    paid_verify_count  = Job.objects.filter(job_plan='paid_pending').count()
    return render(request, 'super_admin_dashboard.html', {
        'total_users': total_users, 'total_jobs': total_jobs, 'active_jobs': active_jobs,
        'total_apps': total_apps, 'total_states': total_states, 'total_districts': total_districts,
        'total_adverts': total_adverts, 'pending_adverts': pending_adverts,
        'open_complaints': open_complaints, 'recent_users': recent_users,
        'state_list': state_list, 'recent_jobs': recent_jobs,
        'industries': industries, 'notifications': notifications,
        'employer_count': employer_count, 'jobseeker_count': jobseeker_count,
        'pending_jobs_count': pending_jobs_count, 'paid_verify_count': paid_verify_count,
    })


@super_admin_required
def manage_states(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip().upper()
        if name and code:
            State.objects.get_or_create(name=name, defaults={'code': code, 'created_by': request.user})
            messages.success(request, f'State "{name}" created.')
        return redirect('manage_states')
    states = State.objects.annotate(d_count=Count('districts')).order_by('name')
    return render(request, 'manage_states.html', {'states': states})


@super_admin_required
def toggle_state(request, pk):
    state = get_object_or_404(State, pk=pk)
    state.is_active = not state.is_active
    state.save()
    messages.success(request, f'State "{state.name}" {"activated" if state.is_active else "deactivated"}.')
    return redirect('manage_states')


@super_admin_required
def manage_districts(request, state_id):
    state = get_object_or_404(State, pk=state_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            District.objects.get_or_create(state=state, name=name)
            messages.success(request, f'District "{name}" created.')
        return redirect('manage_districts', state_id=state_id)
    districts = state.districts.all()
    return render(request, 'manage_districts.html', {'state': state, 'districts': districts})


@super_admin_required
def create_state_admin(request):
    states = State.objects.filter(is_active=True)
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        phone    = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        state_id = request.POST.get('state_id')
        state    = get_object_or_404(State, pk=state_id)
        if not phone or not phone.isdigit() or len(phone) != 10:
            messages.error(request, 'Enter a valid 10-digit mobile number.')
        elif User.objects.filter(username=phone).exists():
            messages.error(request, 'A login already exists with this mobile number.')
        else:
            parts = fullname.split(' ', 1)
            user  = User.objects.create_user(
                username=phone, password=password,
                first_name=parts[0], last_name=parts[1] if len(parts) > 1 else '',
                phone=phone, admin_role='state_admin'
            )
            AdminProfile.objects.create(user=user, role='state_admin', state=state, appointed_by=request.user)
            messages.success(request, f'State Admin "{fullname}" created for {state.name}. Login with mobile {phone}.')
            return redirect('manage_state_admins')
    return render(request, 'create_state_admin.html', {'states': states})


@super_admin_required
def manage_state_admins(request):
    admins = AdminProfile.objects.filter(role='state_admin').select_related('user', 'state').order_by('state__name')
    return render(request, 'manage_state_admins.html', {'admins': admins})


@super_admin_required
def toggle_admin(request, pk):
    profile = get_object_or_404(AdminProfile, pk=pk)
    profile.is_active = not profile.is_active
    profile.user.is_active = profile.is_active
    profile.user.save()
    profile.save()
    messages.success(request, f'Admin {"activated" if profile.is_active else "suspended"}.')
    return redirect(request.META.get('HTTP_REFERER', 'super_admin_dashboard'))


@super_admin_required
def manage_industries(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name   = request.POST.get('name', '').strip()
            collar = request.POST.get('collar', 'both')
            icon   = request.POST.get('icon', 'fas fa-industry').strip()
            if name:
                Industry.objects.get_or_create(name=name, defaults={'collar': collar, 'icon': icon})
                messages.success(request, f'Industry "{name}" added.')
        elif action == 'toggle':
            pk = request.POST.get('pk')
            ind = get_object_or_404(Industry, pk=pk)
            ind.is_active = not ind.is_active
            ind.save()
        return redirect('manage_industries')
    industries = Industry.objects.annotate(role_count=Count('roles'))
    return render(request, 'manage_industries.html', {'industries': industries})


@super_admin_required
def manage_job_roles(request, industry_id=None):
    industries = Industry.objects.filter(is_active=True)
    selected   = get_object_or_404(Industry, pk=industry_id) if industry_id else industries.first()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add' and selected:
            name = request.POST.get('name', '').strip()
            if name:
                JobRole.objects.get_or_create(industry=selected, name=name)
                messages.success(request, f'Job role "{name}" added.')
        elif action == 'toggle':
            role = get_object_or_404(JobRole, pk=request.POST.get('pk'))
            role.is_active = not role.is_active
            role.save()
        return redirect('manage_job_roles', industry_id=selected.pk if selected else 1)
    roles = selected.roles.all() if selected else []
    return render(request, 'manage_job_roles.html', {'industries': industries, 'selected': selected, 'roles': roles})


@super_admin_required
def manage_payment_plans(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            PaymentPlan.objects.create(
                name          = request.POST.get('name', '').strip(),
                plan_type     = request.POST.get('plan_type', 'employer_basic'),
                price         = request.POST.get('price', 0),
                duration_days = request.POST.get('duration_days', 30),
                job_posts     = request.POST.get('job_posts', 5),
                features      = request.POST.get('features', '').strip(),
                is_featured   = 'is_featured' in request.POST,
            )
            messages.success(request, 'Payment plan created.')
        elif action == 'toggle':
            plan = get_object_or_404(PaymentPlan, pk=request.POST.get('pk'))
            plan.is_active = not plan.is_active
            plan.save()
        return redirect('manage_payment_plans')
    plans = PaymentPlan.objects.all()
    return render(request, 'manage_payment_plans.html', {'plans': plans})


@super_admin_required
def manage_discounts(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            Discount.objects.create(
                code          = request.POST.get('code', '').strip().upper(),
                description   = request.POST.get('description', '').strip(),
                discount_type = request.POST.get('discount_type', 'percent'),
                value         = request.POST.get('value', 0),
                min_amount    = request.POST.get('min_amount', 0),
                max_uses      = request.POST.get('max_uses', 0),
                valid_from    = request.POST.get('valid_from') or None,
                valid_until   = request.POST.get('valid_until') or None,
            )
            messages.success(request, 'Discount code created.')
        elif action == 'toggle':
            d = get_object_or_404(Discount, pk=request.POST.get('pk'))
            d.is_active = not d.is_active
            d.save()
        return redirect('manage_discounts')
    discounts = Discount.objects.all().order_by('-created_at')
    return render(request, 'manage_discounts.html', {'discounts': discounts})


@super_admin_required
def manage_pincodes(request, district_id=None):
    districts = District.objects.select_related('state').order_by('state__name', 'name')
    selected  = get_object_or_404(District, pk=district_id) if district_id else None
    if request.method == 'POST' and selected:
        code      = request.POST.get('code', '').strip()
        area_name = request.POST.get('area_name', '').strip()
        if code:
            PinCode.objects.get_or_create(district=selected, code=code, defaults={'area_name': area_name})
            messages.success(request, f'PIN {code} added.')
        return redirect('manage_pincodes', district_id=selected.pk)
    pincodes = selected.pincodes.all() if selected else []
    return render(request, 'manage_pincodes.html', {'districts': districts, 'selected': selected, 'pincodes': pincodes})


@super_admin_required
def manage_notifications(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            SystemNotification.objects.create(
                title       = request.POST.get('title', '').strip(),
                message     = request.POST.get('message', '').strip(),
                notif_type  = request.POST.get('notif_type', 'info'),
                target_role = request.POST.get('target_role', '').strip(),
                created_by  = request.user,
            )
            messages.success(request, 'Notification created.')
        elif action == 'toggle':
            n = get_object_or_404(SystemNotification, pk=request.POST.get('pk'))
            n.is_active = not n.is_active
            n.save()
        return redirect('manage_notifications')
    notifs = SystemNotification.objects.all()
    return render(request, 'manage_notifications.html', {'notifs': notifs})


@login_required
def mark_all_notifications_read(request):
    UserNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


@login_required
@login_required
def update_interview_type(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})
    import json
    data = json.loads(request.body)
    job_id   = data.get('job_id')
    itype    = data.get('interview_type', '').strip()
    if itype not in ('walkin', 'online'):
        return JsonResponse({'success': False, 'error': 'Invalid type'})
    try:
        job = Job.objects.get(id=job_id, posted_by=request.user)
        job.interview_type = itype
        job.save(update_fields=['interview_type'])
        return JsonResponse({'success': True, 'interview_type': itype})
    except Job.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Job not found'})


def api_pincode_lookup(request, pin):
    import re
    if not re.fullmatch(r'\d{6}', pin):
        return JsonResponse({'success': False, 'error': 'Invalid PIN code'})

    from .models import PinCode, District, State
    import requests as _req

    # Try local DB first
    try:
        pc = PinCode.objects.select_related('district__state').get(code=pin)
        return JsonResponse({
            'success': True,
            'area': pc.area_name or pc.district.name,
            'district': pc.district.name,
            'state': pc.district.state.name,
        })
    except PinCode.DoesNotExist:
        pass

    # Fall back to India Post API
    try:
        resp   = _req.get(f'https://api.postalpincode.in/pincode/{pin}', timeout=8)
        data   = resp.json()
        if data and data[0].get('Status') == 'Success' and data[0].get('PostOffice'):
            po       = data[0]['PostOffice'][0]
            area     = po.get('Name', '')
            district = po.get('District', '')
            state    = po.get('State', '')

            # Cache in local DB if district exists
            try:
                dist_obj = District.objects.get(name__iexact=district)
                PinCode.objects.get_or_create(
                    code=pin,
                    defaults={'district': dist_obj, 'area_name': area}
                )
            except District.DoesNotExist:
                pass

            return JsonResponse({'success': True, 'area': area, 'district': district, 'state': state})
        return JsonResponse({'success': False, 'error': 'PIN code not found'})
    except Exception:
        return JsonResponse({'success': False, 'error': 'Lookup unavailable'})


def terms(request):
    return render(request, 'terms.html')


def privacy(request):
    return render(request, 'privacy.html')


def favicon(request):
    return HttpResponse(status=204)


# ── FLICKS ────────────────────────────────────────────────────────────────────

@login_required
def flicks_feed(request):
    from .models import Flick, FlickLike
    flicks = Flick.objects.select_related('user').prefetch_related('likes', 'comments').order_by('-created_at')
    liked_ids = set(FlickLike.objects.filter(user=request.user).values_list('flick_id', flat=True))
    return render(request, 'flicks.html', {'flicks': flicks, 'liked_ids': liked_ids})


@login_required
def post_flick(request):
    from .models import Flick
    if request.method == 'POST':
        title   = request.POST.get('title', '').strip()
        caption = request.POST.get('caption', '').strip()
        video   = request.FILES.get('video')
        image   = request.FILES.get('image')
        if not caption and not video and not image:
            messages.error(request, 'Add a caption, image, or video.')
            return redirect('post_flick')
        Flick.objects.create(user=request.user, title=title, caption=caption,
                             video=video, image=image)
        messages.success(request, 'Flick posted!')
        return redirect('flicks_feed')
    return render(request, 'post_flick.html')


@login_required
def like_flick(request, pk):
    from .models import Flick, FlickLike
    if request.method != 'POST':
        return JsonResponse({'success': False})
    flick = get_object_or_404(Flick, pk=pk)
    like, created = FlickLike.objects.get_or_create(flick=flick, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'success': True, 'liked': liked, 'count': flick.like_count()})


@login_required
def comment_flick(request, pk):
    from .models import Flick, FlickComment
    if request.method != 'POST':
        return JsonResponse({'success': False})
    import json
    data = json.loads(request.body)
    text = data.get('text', '').strip()
    if not text:
        return JsonResponse({'success': False, 'error': 'Empty comment'})
    flick = get_object_or_404(Flick, pk=pk)
    c = FlickComment.objects.create(flick=flick, user=request.user, text=text)
    return JsonResponse({
        'success': True,
        'name': request.user.get_full_name() or request.user.username,
        'text': c.text,
        'time': c.created_at.strftime('%d %b %Y'),
    })


@login_required
def delete_flick(request, pk):
    from .models import Flick
    flick = get_object_or_404(Flick, pk=pk, user=request.user)
    flick.delete()
    messages.success(request, 'Flick deleted.')
    return redirect('flicks_feed')


def referral_dashboard(request):
    user = request.user
    if not user.referral_code:
        from .utils import generate_referral_code
        user.referral_code = generate_referral_code()
        user.save(update_fields=['referral_code'])

    wallet, _ = PointsWallet.objects.get_or_create(user=user)
    transactions = wallet.transactions.all()[:20]
    referrals = Referral.objects.filter(referrer=user).select_related('referred').order_by('-created_at')

    referral_link = request.build_absolute_uri(f'/register/?ref={user.referral_code}')

    return render(request, 'referral.html', {
        'wallet': wallet,
        'transactions': transactions,
        'referrals': referrals,
        'referral_link': referral_link,
    })


@super_admin_required
def national_analytics(request):
    jobs_by_collar = {
        'white': Job.objects.filter(collar_type='white').count(),
        'blue':  Job.objects.filter(collar_type='blue').count(),
    }
    apps_by_status = {s: JobApplication.objects.filter(status=s).count()
                      for s, _ in JobApplication._meta.get_field('status').choices}
    advertisers_by_status = {s: Advertiser.objects.filter(status=s).count()
                              for s, _ in Advertiser.ADVERTISER_STATUS}
    top_states = State.objects.annotate(d_count=Count('districts')).order_by('-d_count')[:10]
    return render(request, 'national_analytics.html', {
        'jobs_by_collar': jobs_by_collar,
        'apps_by_status': apps_by_status,
        'advertisers_by_status': advertisers_by_status,
        'top_states': top_states,
        'total_revenue': AdPayment.objects.filter(status='paid').count(),
    })


# ─── STATE ADMIN ──────────────────────────────────────────────────────────────

@state_admin_required
def state_admin_dashboard(request):
    profile  = getattr(request.user, 'admin_profile', None)
    state    = profile.state if profile and profile.state else None
    districts= state.districts.all() if state else District.objects.none()
    pending_employers = User.objects.filter(
        user_type__in=User.EMPLOYER_TYPES, is_active=True
    ).count()
    state_jobs = Job.objects.filter(pincode__in=[]).count()
    open_complaints = Complaint.objects.filter(status='open').count()
    district_admins = AdminProfile.objects.filter(role='district_admin', state=state) if state else []
    return render(request, 'state_admin_dashboard.html', {
        'state': state, 'districts': districts,
        'pending_employers': pending_employers,
        'open_complaints': open_complaints,
        'district_admins': district_admins,
        'district_count': districts.count(),
    })


@state_admin_required
def create_district_admin(request):
    profile  = getattr(request.user, 'admin_profile', None)
    state    = profile.state if profile else None
    districts= state.districts.all() if state else District.objects.all()
    if request.method == 'POST':
        fullname    = request.POST.get('fullname', '').strip()
        phone       = request.POST.get('phone', '').strip()
        password    = request.POST.get('password', '').strip()
        district_id = request.POST.get('district_id')
        district    = get_object_or_404(District, pk=district_id)
        if not phone or not phone.isdigit() or len(phone) != 10:
            messages.error(request, 'Enter a valid 10-digit mobile number.')
        elif User.objects.filter(username=phone).exists():
            messages.error(request, 'A login already exists with this mobile number.')
        else:
            parts = fullname.split(' ', 1)
            user  = User.objects.create_user(
                username=phone, password=password,
                first_name=parts[0], last_name=parts[1] if len(parts) > 1 else '',
                phone=phone, admin_role='district_admin'
            )
            AdminProfile.objects.create(
                user=user, role='district_admin',
                state=district.state, district=district,
                appointed_by=request.user
            )
            messages.success(request, f'District Admin created for {district.name}. Login with mobile {phone}.')
            return redirect('state_admin_dashboard')
    return render(request, 'create_district_admin.html', {'districts': districts, 'state': state})


@state_admin_required
def verify_employers(request):
    employers = User.objects.filter(
        user_type__in=User.EMPLOYER_TYPES
    ).order_by('-date_joined')
    return render(request, 'verify_employers.html', {'employers': employers})


@state_admin_required
def suspend_user(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    target.is_active = not target.is_active
    target.save()
    action = 'activated' if target.is_active else 'suspended'
    messages.success(request, f'User "{target.username}" {action}.')
    return redirect(request.META.get('HTTP_REFERER', 'state_admin_dashboard'))


@state_admin_required
def state_reports(request):
    profile  = getattr(request.user, 'admin_profile', None)
    state    = profile.state if profile else None
    districts = state.districts.all() if state else District.objects.none()
    district_stats = []
    for d in districts:
        d.job_count = Job.objects.filter(pincode__in=d.pincodes.values_list('code', flat=True)).count()
        d.app_count = JobApplication.objects.filter(
            job__pincode__in=d.pincodes.values_list('code', flat=True)
        ).count()
        district_stats.append(d)
    total_jobs = Job.objects.count()
    total_applications = JobApplication.objects.count()
    total_employers = User.objects.filter(user_type__in=User.EMPLOYER_TYPES).count()
    open_complaints = Complaint.objects.filter(status='open').count()
    white_jobs = Job.objects.filter(collar_type='white').count()
    blue_jobs  = Job.objects.filter(collar_type='blue').count()
    recent_employers = User.objects.filter(user_type__in=User.EMPLOYER_TYPES).order_by('-date_joined')[:10]
    app_statuses = ['applied', 'shortlisted', 'interviewed', 'offered', 'rejected']
    return render(request, 'state_reports.html', {
        'state': state,
        'district_stats': district_stats,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_employers': total_employers,
        'open_complaints': open_complaints,
        'white_jobs': white_jobs,
        'blue_jobs': blue_jobs,
        'recent_employers': recent_employers,
        'apps_applied':     JobApplication.objects.filter(status='applied').count(),
        'apps_shortlisted': JobApplication.objects.filter(status='shortlisted').count(),
        'apps_interviewed': JobApplication.objects.filter(status='interviewed').count(),
        'apps_offered':     JobApplication.objects.filter(status='offered').count(),
        'apps_rejected':    JobApplication.objects.filter(status='rejected').count(),
    })


# ─── DISTRICT ADMIN ───────────────────────────────────────────────────────────

@district_admin_required
def district_admin_dashboard(request):
    profile  = getattr(request.user, 'admin_profile', None)
    district = profile.district if profile else None
    pending_employers  = Advertiser.objects.filter(status='pending').count()
    pending_ads        = Advertisement.objects.filter(status='pending_review').count()
    open_complaints    = Complaint.objects.filter(status='open', district=district).count()
    recent_jobs        = Job.objects.order_by('-created_at')[:8]
    recent_complaints  = Complaint.objects.filter(district=district).order_by('-created_at')[:5]
    return render(request, 'district_admin_dashboard.html', {
        'district': district, 'pending_employers': pending_employers,
        'pending_ads': pending_ads, 'open_complaints': open_complaints,
        'recent_jobs': recent_jobs, 'recent_complaints': recent_complaints,
    })


@district_admin_required
def approve_employers_district(request):
    employers = User.objects.filter(user_type__in=User.EMPLOYER_TYPES).order_by('-date_joined')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action  = request.POST.get('action')
        target  = get_object_or_404(User, pk=user_id)
        if action == 'approve':
            target.is_active = True
            target.save()
            messages.success(request, f'{target.username} approved.')
        elif action == 'block':
            target.is_active = False
            target.save()
            messages.info(request, f'{target.username} blocked.')
        return redirect('approve_employers_district')
    return render(request, 'approve_employers_district.html', {'employers': employers})


@district_admin_required
def moderate_jobs(request):
    tab = request.GET.get('tab', 'all')

    if request.method == 'POST':
        job_id  = request.POST.get('job_id')
        action  = request.POST.get('action')
        back_tab = request.POST.get('back_tab', 'all')
        job     = get_object_or_404(Job, pk=job_id)
        if action == 'suspend':
            job.status = 'closed'
            job.save()
            messages.success(request, f'Job "{job.title}" suspended.')
        elif action == 'activate':
            job.status = 'active'
            job.save()
            messages.success(request, f'Job "{job.title}" reactivated.')
        elif action == 'approve':
            job.is_approved = True
            job.status = 'active'
            job.save()
            UserNotification.objects.create(
                user=job.posted_by,
                title=f'Job Approved! Choose Your Plan — {job.title}',
                message='Your job is approved! 🎉 Start with 1 Week FREE, or go straight to 12 Weeks for ₹499. Tap to choose.',
                notif_type='success',
                link=f'/jobs/{job.pk}/select-plan/',
            )
            messages.success(request, f'Job "{job.title}" approved. Employer notified to select a plan.')
        elif action == 'reject':
            job.is_approved = False
            job.status = 'closed'
            job.save()
            messages.success(request, f'Job "{job.title}" rejected.')
        elif action == 'activate_plan':
            import datetime
            job.job_plan = 'paid'
            job.plan_expires_at = datetime.date.today() + datetime.timedelta(weeks=12)
            job.save()
            from .utils import notify_seekers_for_job
            notify_seekers_for_job(job)
            UserNotification.objects.create(
                user=job.posted_by,
                title='Your Plan is Activated!',
                message=f'Your payment has been verified. "{job.title}" is now live for 12 weeks. Job seekers can now find and apply!',
                notif_type='success',
                link=f'/jobs/{job.pk}/',
            )
            messages.success(request, f'Plan activated for "{job.title}". Employer notified.')
        return redirect(f'/district-admin/jobs/?tab={back_tab}')

    base_qs = Job.objects.select_related('posted_by').order_by('is_approved', '-created_at')

    if tab == 'pending':
        jobs = base_qs.filter(status='active', is_approved=False)
    elif tab == 'payment':
        jobs = base_qs.filter(job_plan__in=['paid_pending', 'paid']).exclude(payment_screenshot='').exclude(payment_screenshot__isnull=True)
    else:
        jobs = base_qs

    pending_count = base_qs.filter(status='active', is_approved=False).count()
    payment_count = base_qs.filter(job_plan='paid_pending').count()

    return render(request, 'moderate_jobs.html', {
        'jobs':          jobs,
        'pending_count': pending_count,
        'payment_count': payment_count,
        'tab':           tab,
    })


@district_admin_required
def handle_complaints(request):
    profile  = getattr(request.user, 'admin_profile', None)
    district = profile.district if profile else None
    complaints = Complaint.objects.filter(district=district).order_by('-created_at')
    return render(request, 'handle_complaints.html', {'complaints': complaints, 'district': district})


@district_admin_required
def resolve_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    if request.method == 'POST':
        complaint.resolution  = request.POST.get('resolution', '').strip()
        complaint.status      = request.POST.get('status', 'resolved')
        complaint.assigned_to = request.user
        complaint.resolved_at = timezone.now()
        complaint.save()
        messages.success(request, 'Complaint updated.')
        return redirect('handle_complaints')
    return render(request, 'resolve_complaint.html', {'complaint': complaint})


@district_admin_required
def district_reports(request):
    profile  = getattr(request.user, 'admin_profile', None)
    district = profile.district if profile else None
    pin_codes = district.pincodes.values_list('code', flat=True) if district else []
    total_jobs         = Job.objects.filter(pincode__in=pin_codes).count() if pin_codes else Job.objects.count()
    total_applications = JobApplication.objects.count()
    total_employers    = User.objects.filter(user_type__in=User.EMPLOYER_TYPES).count()
    total_complaints   = Complaint.objects.filter(district=district).count()
    white_jobs = Job.objects.filter(collar_type='white').count()
    blue_jobs  = Job.objects.filter(collar_type='blue').count()
    from datetime import date, timedelta
    month_start = date.today().replace(day=1)
    recent_jobs = Job.objects.filter(created_at__date__gte=month_start).select_related('posted_by').order_by('-created_at')[:15]
    complaints  = Complaint.objects.filter(district=district).order_by('-created_at')[:10]
    return render(request, 'district_reports.html', {
        'district': district,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_employers': total_employers,
        'total_complaints': total_complaints,
        'white_jobs': white_jobs,
        'blue_jobs': blue_jobs,
        'recent_jobs': recent_jobs,
        'complaints': complaints,
        'comp_open':        Complaint.objects.filter(district=district, status='open').count(),
        'comp_in_progress': Complaint.objects.filter(district=district, status='in_progress').count(),
        'comp_resolved':    Complaint.objects.filter(district=district, status='resolved').count(),
        'comp_closed':      Complaint.objects.filter(district=district, status='closed').count(),
    })


# ─── PUBLIC: Submit Complaint ──────────────────────────────────────────────────
@login_required
def submit_complaint(request):
    if request.method == 'POST':
        Complaint.objects.create(
            submitted_by   = request.user,
            complaint_type = request.POST.get('complaint_type', 'other'),
            subject        = request.POST.get('subject', '').strip(),
            description    = request.POST.get('description', '').strip(),
        )
        messages.success(request, 'Complaint submitted. Our team will review it shortly.')
        return redirect('dashboard')
    return render(request, 'submit_complaint.html', {})


# ── SAVE CANDIDATE ────────────────────────────────────────────────────────────
@login_required
def save_candidate(request, user_id):
    candidate = get_object_or_404(User, pk=user_id)
    obj, created = SavedCandidate.objects.get_or_create(employer=request.user, candidate=candidate)
    if not created:
        obj.delete()
        return JsonResponse({'saved': False})
    return JsonResponse({'saved': True})


# ── PROFILE REDIRECT ──────────────────────────────────────────────────────────
@login_required
def profile_redirect(request):
    if request.user.is_employer():
        return redirect('employer_dashboard')
    return redirect('seeker_profile')


# ── CANDIDATE SEARCH ──────────────────────────────────────────────────────────
def candidates(request):
    if request.user.is_authenticated and not request.user.is_employer():
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Only employers can view candidates.")
    profiles = JobSeekerProfile.objects.select_related('user').filter(
        profile_completed=True,
        user__user_type__in=['employee', 'individual', 'freelancer']
    )

    skill    = request.GET.get('skill', '').strip()
    city     = request.GET.get('city', '').strip()
    pincode  = request.GET.get('pincode', '').strip()
    collar   = request.GET.get('collar', '').strip()
    exp      = request.GET.get('exp', '').strip()
    avail    = request.GET.get('avail', '').strip()

    if skill:
        profiles = profiles.filter(
            Q(primary_skill__icontains=skill) | Q(skills__icontains=skill) | Q(preferred_roles__icontains=skill)
        )
    if city:
        profiles = profiles.filter(user__city__icontains=city)
    if pincode:
        profiles = profiles.filter(user__pincode=pincode)
    if collar:
        profiles = profiles.filter(job_category=collar)
    if exp == 'fresher':
        profiles = profiles.filter(experience__in=['', 'fresher', '0'])
    if avail == 'immediate':
        profiles = profiles.filter(availability='immediate')

    return render(request, 'candidates.html', {
        'profiles': profiles[:50],
        'skill': skill, 'city': city, 'pincode': pincode,
        'collar': collar, 'total': profiles.count(),
    })


def candidate_profile(request, user_id):
    if request.user.is_authenticated and not request.user.is_employer():
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Only employers can view candidate profiles.")
    seeker_user = get_object_or_404(User, pk=user_id, user_type__in=['employee', 'individual', 'freelancer'])
    try:
        profile = seeker_user.seeker
    except JobSeekerProfile.DoesNotExist:
        from django.http import Http404
        raise Http404
    return render(request, 'candidate_profile.html', {'p': profile, 'seeker_user': seeker_user})
