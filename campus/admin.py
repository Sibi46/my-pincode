from django.contrib import admin
from .models import (
    Institution, PlacementOfficer, Department, HOD, Student,
    CampusCompany, Opportunity, OpportunityPincode, OpportunityShare,
    Application, ApplicationStatusHistory, Interview,
    CampusNotification, AuditLog,
)

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'institution_type', 'pincode', 'city', 'status', 'created_at']
    list_filter  = ['status', 'institution_type']
    search_fields = ['name', 'pincode', 'city']

@admin.register(CampusCompany)
class CampusCompanyAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'industry', 'pincode', 'status', 'created_at']
    list_filter  = ['status']
    search_fields = ['company_name', 'pincode']

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'opp_type', 'status', 'openings', 'created_at']
    list_filter  = ['opp_type', 'status', 'work_mode']
    search_fields = ['title', 'company__company_name']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'opportunity', 'status', 'applied_at']
    list_filter  = ['status']

admin.site.register(PlacementOfficer)
admin.site.register(Department)
admin.site.register(HOD)
admin.site.register(Student)
admin.site.register(OpportunityPincode)
admin.site.register(OpportunityShare)
admin.site.register(ApplicationStatusHistory)
admin.site.register(Interview)
admin.site.register(CampusNotification)
admin.site.register(AuditLog)
