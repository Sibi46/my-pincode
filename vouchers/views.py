from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Business, GiftVoucher, VoucherPurchase
from .forms import BusinessRegistrationForm


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
