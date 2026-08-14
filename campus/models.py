from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


# ── INSTITUTION ──────────────────────────────────────────────────────────────

class Institution(models.Model):
    TYPE_CHOICES = [
        ('engineering',  'Engineering College'),
        ('arts_science', 'Arts & Science College'),
        ('polytechnic',  'Polytechnic'),
        ('medical',      'Medical College'),
        ('law',          'Law College'),
        ('management',   'Management Institute'),
        ('school',       'School'),
        ('other',        'Other'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending Verification'),
        ('verified',  'Verified'),
        ('rejected',  'Rejected'),
        ('suspended', 'Suspended'),
    ]

    name             = models.CharField(max_length=300)
    institution_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='arts_science')
    affiliation      = models.CharField(max_length=300, blank=True)
    address          = models.TextField(blank=True)
    pincode          = models.CharField(max_length=6, db_index=True)
    city             = models.CharField(max_length=100, blank=True)
    district         = models.CharField(max_length=100, blank=True)
    state            = models.CharField(max_length=100, blank=True)
    phone            = models.CharField(max_length=15, blank=True)
    email            = models.EmailField(blank=True)
    website          = models.URLField(blank=True)
    logo             = models.ImageField(upload_to='campus/institution/logos/', blank=True, null=True)
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    verified_at      = models.DateTimeField(null=True, blank=True)
    verified_by      = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='verified_institutions')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PlacementOfficer(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='placement_officer')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='placement_officers')
    designation = models.CharField(max_length=200, blank=True)
    phone       = models.CharField(max_length=15, blank=True)
    email       = models.EmailField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.institution.name}"


class Department(models.Model):
    institution    = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='departments')
    name           = models.CharField(max_length=200)
    code           = models.CharField(max_length=20, blank=True)
    courses        = models.TextField(blank=True)
    year_structure = models.CharField(max_length=100, blank=True)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.institution.name} — {self.name}"


class HOD(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hod_profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='hods')
    phone      = models.CharField(max_length=15, blank=True)
    email      = models.EmailField(blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.department.name}"


class Student(models.Model):
    YEAR_CHOICES = [(str(i), f'Year {i}') for i in range(1, 6)]

    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    institution  = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='students')
    department   = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    roll_number  = models.CharField(max_length=50, blank=True)
    course       = models.CharField(max_length=200, blank=True)
    year         = models.CharField(max_length=1, choices=YEAR_CHOICES, default='1')
    skills       = models.TextField(blank=True)
    resume       = models.FileField(upload_to='campus/student/resumes/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"

    def skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]


# ── COMPANY ───────────────────────────────────────────────────────────────────

class CampusCompany(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('verified',  'Verified'),
        ('rejected',  'Rejected'),
        ('suspended', 'Suspended'),
    ]

    user           = models.OneToOneField(User, on_delete=models.CASCADE, related_name='campus_company')
    company_name   = models.CharField(max_length=300)
    industry       = models.CharField(max_length=100, blank=True)
    description    = models.TextField(blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    designation    = models.CharField(max_length=200, blank=True)
    phone          = models.CharField(max_length=15, blank=True)
    email          = models.EmailField(blank=True)
    website        = models.URLField(blank=True)
    address        = models.TextField(blank=True)
    pincode        = models.CharField(max_length=6, blank=True)
    logo           = models.ImageField(upload_to='campus/company/logos/', blank=True, null=True)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    verified_at    = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Campus Company'
        verbose_name_plural = 'Campus Companies'

    def __str__(self):
        return self.company_name


# ── OPPORTUNITY ───────────────────────────────────────────────────────────────

class Opportunity(models.Model):
    TYPE_CHOICES = [
        ('fulltime',   'Full-time Job'),
        ('parttime',   'Part-time Job'),
        ('internship', 'Internship'),
        ('apprentice', 'Apprenticeship'),
        ('project',    'Project'),
        ('volunteer',  'Learning Volunteering'),
        ('other',      'Other'),
    ]
    WORK_MODE_CHOICES = [
        ('onsite', 'On-site'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('published', 'Published'),
        ('closed',    'Closed'),
        ('archived',  'Archived'),
    ]

    company           = models.ForeignKey(CampusCompany, on_delete=models.CASCADE, related_name='opportunities')
    title             = models.CharField(max_length=300)
    opp_type          = models.CharField(max_length=15, choices=TYPE_CHOICES, default='internship')
    description       = models.TextField()
    openings          = models.PositiveIntegerField(default=1)
    dept_eligibility  = models.TextField(blank=True)
    year_eligibility  = models.CharField(max_length=50, blank=True)
    skills_required   = models.TextField(blank=True)
    qualification     = models.CharField(max_length=200, blank=True)
    experience        = models.CharField(max_length=100, blank=True, default='Fresher')
    salary            = models.CharField(max_length=100, blank=True)
    location          = models.CharField(max_length=200, blank=True)
    work_mode         = models.CharField(max_length=10, choices=WORK_MODE_CHOICES, default='onsite')
    apply_start       = models.DateField(null=True, blank=True)
    apply_end         = models.DateField(null=True, blank=True)
    interview_process = models.TextField(blank=True)
    contact_person    = models.CharField(max_length=200, blank=True)
    attachment        = models.FileField(upload_to='campus/opportunity/attachments/', blank=True, null=True)
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Opportunities'

    def __str__(self):
        return f"{self.title} — {self.company.company_name}"


class OpportunityPincode(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='target_pincodes')
    pincode     = models.CharField(max_length=6, db_index=True)

    def __str__(self):
        return f"{self.opportunity.title} → {self.pincode}"


class OpportunityShare(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='shares')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='opportunity_shares')
    department  = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='opportunity_shares', null=True, blank=True)
    shared_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_opportunities')
    shared_at   = models.DateTimeField(auto_now_add=True)
    note        = models.TextField(blank=True)

    def __str__(self):
        return f"{self.opportunity.title} → {self.institution.name}"


# ── APPLICATION ───────────────────────────────────────────────────────────────

class Application(models.Model):
    STATUS_CHOICES = [
        ('applied',      'Applied'),
        ('acknowledged', 'Acknowledged'),
        ('shortlisted',  'Shortlisted'),
        ('interview',    'Interview Scheduled'),
        ('interviewed',  'Interview Done'),
        ('selected',     'Selected'),
        ('rejected',     'Rejected'),
        ('internship',   'Internship Confirmed'),
        ('placed',       'Job Placed'),
        ('withdrawn',    'Withdrawn'),
    ]

    student      = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='applications')
    opportunity  = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    resume       = models.FileField(upload_to='campus/application/resumes/', blank=True, null=True)
    status       = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')
    company_note = models.TextField(blank=True)
    po_note      = models.TextField(blank=True)
    student_note = models.TextField(blank=True)
    final_outcome = models.CharField(max_length=15, choices=STATUS_CHOICES, blank=True)
    applied_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'opportunity')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student} → {self.opportunity.title}"


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    status      = models.CharField(max_length=15, choices=Application.STATUS_CHOICES)
    changed_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    note        = models.TextField(blank=True)
    changed_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']


class Interview(models.Model):
    MODE_CHOICES = [
        ('online',  'Online'),
        ('offline', 'In-person'),
        ('phone',   'Phone'),
    ]
    application  = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    scheduled_at = models.DateTimeField()
    mode         = models.CharField(max_length=10, choices=MODE_CHOICES, default='offline')
    location     = models.CharField(max_length=300, blank=True)
    link         = models.URLField(blank=True)
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview: {self.application.student} @ {self.scheduled_at}"


# ── NOTIFICATION ──────────────────────────────────────────────────────────────

class CampusNotification(models.Model):
    TYPE_CHOICES = [
        ('new_opportunity',    'New Opportunity'),
        ('opportunity_shared', 'Opportunity Shared'),
        ('application',        'Application Submitted'),
        ('status_change',      'Status Changed'),
        ('interview',          'Interview Scheduled'),
        ('selected',           'Selected'),
        ('rejected',           'Rejected'),
        ('general',            'General'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campus_notifications')
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    title      = models.CharField(max_length=300)
    message    = models.TextField(blank=True)
    link       = models.CharField(max_length=500, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.title}"


# ── AUDIT LOG ─────────────────────────────────────────────────────────────────

class AuditLog(models.Model):
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action     = models.CharField(max_length=200)
    model_name = models.CharField(max_length=100, blank=True)
    object_id  = models.PositiveIntegerField(null=True, blank=True)
    detail     = models.TextField(blank=True)
    ip         = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.action}"
