from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Business, Branch, GiftVoucher, VoucherPurchase
from .forms import BusinessRegistrationForm, BranchForm


def business_register(request):
    """Any logged-in user can register a business."""
    if not request.user.is_authenticated:
        return redirect(f'/login/?next=/vouchers/business/register/')

    # If user already has a business, redirect to dashboard
    existing = Business.objects.filter(owner=request.user).first()
    if existing:
        return redirect('vouchers:business_dashboard')

    if request.method == 'POST':
        form = BusinessRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.status = 'pending'
            business.save()
            return redirect('vouchers:register_success')
    else:
        form = BusinessRegistrationForm()

    return render(request, 'vouchers/business_register.html', {'form': form})


def business_register_success(request):
    return render(request, 'vouchers/business_register_success.html')


@login_required
def business_dashboard(request):
    business = get_object_or_404(Business, owner=request.user)

    recent_vouchers = GiftVoucher.objects.filter(
        business=business
    ).order_by('-created_at')[:5]

    recent_purchases = VoucherPurchase.objects.filter(
        gift_voucher__business=business
    ).order_by('-purchased_at')[:5]

    total_sales = sum(
        p.amount_paid for p in
        VoucherPurchase.objects.filter(
            gift_voucher__business=business,
            status__in=['paid', 'sent', 'redeemed']
        )
    )

    context = {
        'business': business,
        'recent_vouchers': recent_vouchers,
        'recent_purchases': recent_purchases,
        'total_sales': total_sales,
    }
    return render(request, 'vouchers/business_dashboard.html', context)


def _get_approved_business(request):
    """Return approved business owned by request.user or None."""
    try:
        b = Business.objects.get(owner=request.user)
        return b if b.status == 'approved' else None
    except Business.DoesNotExist:
        return None


@login_required
def branch_list(request):
    business = get_object_or_404(Business, owner=request.user)
    branches = business.branches.all()
    return render(request, 'vouchers/branch_list.html', {
        'business': business,
        'branches': branches,
    })


@login_required
def branch_add(request):
    business = get_object_or_404(Business, owner=request.user)
    if business.status != 'approved':
        messages.error(request, 'Your business must be approved before adding branches.')
        return redirect('vouchers:business_dashboard')

    if request.method == 'POST':
        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save(commit=False)
            branch.business = business
            branch.save()
            messages.success(request, f'Branch "{branch.branch_name}" added successfully.')
            return redirect('vouchers:branch_list')
    else:
        form = BranchForm()

    return render(request, 'vouchers/branch_form.html', {
        'business': business,
        'form': form,
        'action': 'Add',
    })


@login_required
def branch_edit(request, pk):
    business = get_object_or_404(Business, owner=request.user)
    branch = get_object_or_404(Branch, pk=pk, business=business)

    if request.method == 'POST':
        form = BranchForm(request.POST, instance=branch)
        if form.is_valid():
            form.save()
            messages.success(request, f'Branch "{branch.branch_name}" updated.')
            return redirect('vouchers:branch_list')
    else:
        form = BranchForm(instance=branch)

    return render(request, 'vouchers/branch_form.html', {
        'business': business,
        'form': form,
        'branch': branch,
        'action': 'Edit',
    })


@login_required
def branch_toggle(request, pk):
    business = get_object_or_404(Business, owner=request.user)
    branch = get_object_or_404(Branch, pk=pk, business=business)
    branch.is_active = not branch.is_active
    branch.save()
    status = 'activated' if branch.is_active else 'deactivated'
    messages.success(request, f'Branch "{branch.branch_name}" {status}.')
    return redirect('vouchers:branch_list')
