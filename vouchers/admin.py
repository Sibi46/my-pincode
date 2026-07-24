from django.contrib import admin
from django.utils import timezone
from .models import (
    BusinessCategory, Business, Branch, Employee,
    VoucherSlotPurchase, VoucherCategory, GiftVoucher,
    VoucherPurchase, VoucherRedemption, VoucherAuditLog,
)


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['name']


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 1
    fields = ['branch_name', 'pincode', 'contact_number', 'working_hours', 'is_active']


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1
    fields = ['name', 'mobile', 'email', 'role', 'assigned_branch', 'is_active']


class SlotPurchaseInline(admin.TabularInline):
    model = VoucherSlotPurchase
    extra = 0
    readonly_fields = ['purchased_at', 'purchased_by']
    fields = ['slots_count', 'amount_paid', 'payment_reference', 'purchased_at', 'notes']


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display  = ['business_name', 'owner_name', 'category', 'pincode',
                     'status', 'total_slots_purchased', 'available_slots', 'created_at']
    list_filter   = ['status', 'category']
    search_fields = ['business_name', 'owner_name', 'mobile', 'email', 'pincode']
    readonly_fields = ['created_at', 'updated_at', 'approved_at', 'approved_by',
                       'total_slots_purchased', 'total_slots_used', 'available_slots']
    inlines       = [BranchInline, EmployeeInline, SlotPurchaseInline]
    actions       = ['approve_businesses', 'suspend_businesses']

    fieldsets = [
        ('Business Info', {'fields': [
            'owner', 'business_name', 'owner_name', 'category', 'description'
        ]}),
        ('Contact', {'fields': ['mobile', 'email', 'website']}),
        ('Address', {'fields': ['address', 'pincode', 'city', 'state']}),
        ('Tax', {'fields': ['gst_number', 'pan_number'], 'classes': ['collapse']}),
        ('Media', {'fields': ['logo', 'cover_image']}),
        ('Social Media', {'fields': ['facebook', 'instagram', 'twitter'], 'classes': ['collapse']}),
        ('Status', {'fields': ['status', 'rejection_reason', 'approved_at', 'approved_by']}),
        ('Payment Gateway', {'fields': [
            'payment_gateway', 'payment_gateway_key', 'payment_gateway_secret'
        ], 'classes': ['collapse']}),
        ('Slot Summary', {'fields': [
            'total_slots_purchased', 'total_slots_used', 'available_slots'
        ]}),
        ('Timestamps', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),
    ]

    @admin.action(description='Approve selected businesses')
    def approve_businesses(self, request, queryset):
        queryset.update(status='approved', approved_at=timezone.now(), approved_by=request.user)
        self.message_user(request, f"{queryset.count()} business(es) approved.")

    @admin.action(description='Suspend selected businesses')
    def suspend_businesses(self, request, queryset):
        queryset.update(status='suspended')
        self.message_user(request, f"{queryset.count()} business(es) suspended.")

    def total_slots_purchased(self, obj): return obj.total_slots_purchased
    def available_slots(self, obj): return obj.available_slots


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display  = ['branch_name', 'business', 'pincode', 'contact_number', 'is_active']
    list_filter   = ['is_active', 'business']
    search_fields = ['branch_name', 'pincode', 'business__business_name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display  = ['name', 'business', 'role', 'assigned_branch', 'mobile', 'is_active']
    list_filter   = ['role', 'is_active', 'business']
    search_fields = ['name', 'mobile', 'email', 'business__business_name']


@admin.register(VoucherSlotPurchase)
class VoucherSlotPurchaseAdmin(admin.ModelAdmin):
    list_display  = ['business', 'slots_count', 'amount_paid', 'payment_reference', 'purchased_at']
    list_filter   = ['business']
    search_fields = ['business__business_name', 'payment_reference']
    readonly_fields = ['purchased_at']


@admin.register(VoucherCategory)
class VoucherCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'icon', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['name']


class ApplicableBranchesInline(admin.TabularInline):
    model = GiftVoucher.applicable_branches.through
    extra = 1
    verbose_name = 'Applicable Branch'
    verbose_name_plural = 'Applicable Branches'


@admin.register(GiftVoucher)
class GiftVoucherAdmin(admin.ModelAdmin):
    list_display  = ['voucher_name', 'business', 'voucher_value', 'status',
                     'total_quantity', 'sold_quantity', 'available_quantity',
                     'valid_from', 'expiry_date']
    list_filter   = ['status', 'business', 'category']
    search_fields = ['voucher_name', 'business__business_name', 'product_service_name']
    readonly_fields = ['created_at', 'updated_at', 'published_at', 'available_quantity']
    filter_horizontal = ['applicable_branches']
    actions = ['publish_vouchers', 'pause_vouchers']

    fieldsets = [
        ('Voucher Info', {'fields': [
            'business', 'created_by', 'category',
            'voucher_name', 'product_service_name',
            'product_image', 'header_image',
        ]}),
        ('Value & Content', {'fields': [
            'voucher_value', 'description', 'terms_conditions'
        ]}),
        ('Validity', {'fields': ['valid_from', 'expiry_date']}),
        ('Availability', {'fields': [
            'applicable_branches', 'total_quantity', 'sold_quantity', 'available_quantity'
        ]}),
        ('Status', {'fields': ['status', 'published_at']}),
        ('Timestamps', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),
    ]

    @admin.action(description='Publish selected vouchers')
    def publish_vouchers(self, request, queryset):
        for v in queryset.filter(status='draft'):
            if v.business.available_slots > 0:
                v.status = 'published'
                v.published_at = timezone.now()
                v.save()
        self.message_user(request, "Vouchers published (skipped if no slots available).")

    @admin.action(description='Pause selected vouchers')
    def pause_vouchers(self, request, queryset):
        queryset.filter(status='published').update(status='paused')

    def available_quantity(self, obj): return obj.available_quantity


@admin.register(VoucherPurchase)
class VoucherPurchaseAdmin(admin.ModelAdmin):
    list_display  = ['voucher_code', 'gift_voucher', 'buyer_name', 'receiver_name',
                     'amount_paid', 'status', 'purchased_at']
    list_filter   = ['status', 'gift_voucher__business']
    search_fields = ['voucher_code', 'buyer_name', 'buyer_mobile',
                     'receiver_name', 'receiver_mobile']
    readonly_fields = ['voucher_code', 'purchased_at', 'sent_at', 'qr_code',
                       'otp', 'otp_generated_at']


@admin.register(VoucherRedemption)
class VoucherRedemptionAdmin(admin.ModelAdmin):
    list_display  = ['purchase', 'branch', 'redeemed_by', 'redeemed_at']
    list_filter   = ['branch__business']
    search_fields = ['purchase__voucher_code']
    readonly_fields = ['redeemed_at', 'otp_sent_at', 'otp_verified_at']


@admin.register(VoucherAuditLog)
class VoucherAuditLogAdmin(admin.ModelAdmin):
    list_display  = ['action', 'purchase', 'gift_voucher', 'performed_by', 'created_at']
    list_filter   = ['action']
    search_fields = ['purchase__voucher_code']
    readonly_fields = ['created_at']

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
