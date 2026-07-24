from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class BusinessCategory(models.Model):
    name      = models.CharField(max_length=100)
    icon      = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    order     = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Business Category'
        verbose_name_plural = 'Business Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Business(models.Model):
    STATUS_PENDING   = 'pending'
    STATUS_APPROVED  = 'approved'
    STATUS_SUSPENDED = 'suspended'
    STATUS_REJECTED  = 'rejected'
    STATUS_CHOICES = [
        ('pending',   'Pending Approval'),
        ('approved',  'Approved'),
        ('suspended', 'Suspended'),
        ('rejected',  'Rejected'),
    ]

    owner    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    category = models.ForeignKey(BusinessCategory, on_delete=models.SET_NULL, null=True, blank=True)

    business_name = models.CharField(max_length=200)
    owner_name    = models.CharField(max_length=100)
    description   = models.TextField(blank=True)

    mobile  = models.CharField(max_length=15)
    email   = models.EmailField()
    website = models.URLField(blank=True)

    address = models.TextField()
    pincode = models.CharField(max_length=10)
    city    = models.CharField(max_length=100, blank=True)
    state   = models.CharField(max_length=100, blank=True)

    gst_number = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)

    logo        = models.ImageField(upload_to='vouchers/business/logos/',  blank=True, null=True)
    cover_image = models.ImageField(upload_to='vouchers/business/covers/', blank=True, null=True)

    facebook  = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter   = models.URLField(blank=True)

    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    approved_at      = models.DateTimeField(null=True, blank=True)
    approved_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='approved_businesses')

    payment_gateway        = models.CharField(max_length=50, blank=True)
    payment_gateway_key    = models.CharField(max_length=200, blank=True)
    payment_gateway_secret = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'
        ordering = ['-created_at']

    def __str__(self):
        return self.business_name

    @property
    def total_slots_purchased(self):
        return self.slot_purchases.aggregate(total=models.Sum('slots_count'))['total'] or 0

    @property
    def total_slots_used(self):
        return self.gift_vouchers.filter(status__in=['published', 'paused']).count()

    @property
    def available_slots(self):
        return self.total_slots_purchased - self.total_slots_used


class Branch(models.Model):
    business       = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='branches')
    branch_name    = models.CharField(max_length=200)
    address        = models.TextField()
    pincode        = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=15)
    working_hours  = models.CharField(max_length=200, blank=True)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        ordering = ['branch_name']

    def __str__(self):
        return f"{self.business.business_name} – {self.branch_name}"


class Employee(models.Model):
    ROLE_CHOICES = [
        ('business_owner',    'Business Owner'),
        ('marketing_manager', 'Marketing Manager'),
        ('branch_manager',    'Branch Manager'),
    ]

    business        = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='employees')
    user            = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='voucher_employee_profiles')
    assigned_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='employees')

    name      = models.CharField(max_length=100)
    mobile    = models.CharField(max_length=15)
    email     = models.EmailField()
    role      = models.CharField(max_length=30, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f"{self.name} ({self.get_role_display()}) – {self.business.business_name}"


class VoucherSlotPurchase(models.Model):
    business          = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='slot_purchases')
    purchased_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    slots_count       = models.PositiveIntegerField()
    amount_paid       = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=100, blank=True)
    notes             = models.TextField(blank=True)
    purchased_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Voucher Slot Purchase'
        verbose_name_plural = 'Voucher Slot Purchases'
        ordering = ['-purchased_at']

    def __str__(self):
        return f"{self.business.business_name} – {self.slots_count} slots – Rs.{self.amount_paid}"


class VoucherCategory(models.Model):
    name      = models.CharField(max_length=100)
    icon      = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    order     = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Voucher Category'
        verbose_name_plural = 'Voucher Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class GiftVoucher(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('published', 'Published'),
        ('paused',    'Paused'),
        ('expired',   'Expired'),
        ('deleted',   'Deleted'),
    ]

    business   = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='gift_vouchers')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_vouchers')
    category   = models.ForeignKey(VoucherCategory, on_delete=models.SET_NULL, null=True, blank=True)

    voucher_name         = models.CharField(max_length=200)
    product_service_name = models.CharField(max_length=200)
    product_image        = models.ImageField(upload_to='vouchers/products/', blank=True, null=True)
    header_image         = models.ImageField(upload_to='vouchers/headers/', blank=True, null=True)

    voucher_value    = models.DecimalField(max_digits=10, decimal_places=2)
    description      = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)

    valid_from  = models.DateField()
    expiry_date = models.DateField()

    applicable_branches = models.ManyToManyField(Branch, blank=True, related_name='vouchers')
    total_quantity      = models.PositiveIntegerField()
    sold_quantity       = models.PositiveIntegerField(default=0)

    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Gift Voucher'
        verbose_name_plural = 'Gift Vouchers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.voucher_name} – {self.business.business_name}"

    @property
    def available_quantity(self):
        return self.total_quantity - self.sold_quantity

    @property
    def is_available(self):
        today = timezone.now().date()
        return (
            self.status == 'published' and
            self.valid_from <= today <= self.expiry_date and
            self.available_quantity > 0
        )


class VoucherPurchase(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Payment Pending'),
        ('paid',      'Paid'),
        ('sent',      'Sent to Receiver'),
        ('redeemed',  'Redeemed'),
        ('expired',   'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    gift_voucher = models.ForeignKey(GiftVoucher, on_delete=models.CASCADE, related_name='purchases')

    voucher_code = models.CharField(max_length=30, unique=True)
    qr_code      = models.ImageField(upload_to='vouchers/qrcodes/', blank=True, null=True)

    buyer_name   = models.CharField(max_length=100)
    buyer_mobile = models.CharField(max_length=15)
    buyer_email  = models.EmailField()
    buyer_user   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='purchased_vouchers')

    receiver_name   = models.CharField(max_length=100)
    receiver_mobile = models.CharField(max_length=15)
    receiver_email  = models.EmailField()
    receiver_user   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='received_vouchers')

    personal_message = models.TextField(blank=True)

    amount_paid       = models.DecimalField(max_digits=10, decimal_places=2)
    payment_reference = models.CharField(max_length=200, blank=True)
    payment_gateway   = models.CharField(max_length=50, blank=True)

    otp              = models.CharField(max_length=6, blank=True)
    otp_generated_at = models.DateTimeField(null=True, blank=True)

    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    purchased_at = models.DateTimeField(auto_now_add=True)
    sent_at      = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Voucher Purchase'
        verbose_name_plural = 'Voucher Purchases'
        ordering = ['-purchased_at']

    def __str__(self):
        return f"{self.voucher_code} – {self.receiver_name}"


class VoucherRedemption(models.Model):
    purchase    = models.OneToOneField(VoucherPurchase, on_delete=models.CASCADE, related_name='redemption')
    branch      = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='redemptions')
    redeemed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='redemptions_done')

    otp_sent_at     = models.DateTimeField(null=True, blank=True)
    otp_verified_at = models.DateTimeField(null=True, blank=True)
    redeemed_at     = models.DateTimeField(auto_now_add=True)
    notes           = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Voucher Redemption'
        verbose_name_plural = 'Voucher Redemptions'

    def __str__(self):
        return f"Redeemed: {self.purchase.voucher_code}"


class VoucherAuditLog(models.Model):
    ACTION_CHOICES = [
        ('created',       'Voucher Created'),
        ('published',     'Voucher Published'),
        ('paused',        'Voucher Paused'),
        ('purchased',     'Voucher Purchased'),
        ('sent',          'Voucher Sent'),
        ('otp_generated', 'OTP Generated'),
        ('otp_failed',    'OTP Failed'),
        ('redeemed',      'Voucher Redeemed'),
        ('expired',       'Voucher Expired'),
        ('cancelled',     'Voucher Cancelled'),
    ]

    purchase     = models.ForeignKey(VoucherPurchase, on_delete=models.CASCADE,
                                     related_name='audit_logs', null=True, blank=True)
    gift_voucher = models.ForeignKey(GiftVoucher, on_delete=models.CASCADE,
                                     related_name='audit_logs', null=True, blank=True)
    action       = models.CharField(max_length=30, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    note         = models.TextField(blank=True)
    ip_address   = models.GenericIPAddressField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Voucher Audit Log'
        verbose_name_plural = 'Voucher Audit Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_action_display()} – {self.created_at:%d %b %Y %H:%M}"
