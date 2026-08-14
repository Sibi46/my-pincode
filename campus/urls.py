from django.urls import path
from . import views

urlpatterns = [
    # ── PUBLIC / LANDING ─────────────────────────────────────
    path('',                              views.campus_home,              name='campus_home'),

    # ── INSTITUTION REGISTRATION ─────────────────────────────
    path('institution/register/',         views.institution_register,     name='campus_institution_register'),
    path('institution/<int:pk>/',         views.institution_detail,       name='campus_institution_detail'),

    # ── PLACEMENT OFFICER DASHBOARD ──────────────────────────
    path('po/dashboard/',                 views.po_dashboard,             name='campus_po_dashboard'),
    path('po/departments/',               views.po_departments,           name='campus_po_departments'),
    path('po/departments/add/',           views.po_department_add,        name='campus_po_department_add'),
    path('po/hods/add/',                  views.po_hod_add,               name='campus_po_hod_add'),
    path('po/students/',                  views.po_students,              name='campus_po_students'),
    path('po/students/add/',              views.po_student_add,           name='campus_po_student_add'),
    path('po/opportunities/',             views.po_opportunities,         name='campus_po_opportunities'),
    path('po/opportunities/<int:pk>/share/', views.po_share_opportunity,  name='campus_po_share'),
    path('po/applications/',              views.po_applications,          name='campus_po_applications'),

    # ── HOD DASHBOARD ────────────────────────────────────────
    path('hod/dashboard/',                views.hod_dashboard,            name='campus_hod_dashboard'),
    path('hod/opportunities/<int:pk>/share/', views.hod_share_students,   name='campus_hod_share'),

    # ── STUDENT DASHBOARD ────────────────────────────────────
    path('student/register/',             views.student_register,         name='campus_student_register'),
    path('student/dashboard/',            views.student_dashboard,        name='campus_student_dashboard'),
    path('student/opportunities/',        views.student_opportunities,    name='campus_student_opportunities'),
    path('student/opportunities/<int:pk>/', views.opportunity_detail,     name='campus_opportunity_detail'),
    path('student/apply/<int:pk>/',       views.student_apply,            name='campus_student_apply'),
    path('student/applications/',         views.student_applications,     name='campus_student_applications'),
    path('student/application/<int:pk>/', views.application_detail,       name='campus_application_detail'),

    # ── COMPANY ──────────────────────────────────────────────
    path('company/register/',             views.company_register,         name='campus_company_register'),
    path('company/dashboard/',            views.company_dashboard,        name='campus_company_dashboard'),
    path('company/opportunities/post/',   views.opportunity_post,         name='campus_opportunity_post'),
    path('company/opportunities/<int:pk>/edit/', views.opportunity_edit,  name='campus_opportunity_edit'),
    path('company/opportunities/<int:pk>/applications/', views.company_applications, name='campus_company_applications'),
    path('company/applications/<int:pk>/status/', views.update_app_status, name='campus_update_app_status'),
    path('company/applications/<int:pk>/interview/', views.schedule_interview, name='campus_schedule_interview'),

    # ── ADMIN ─────────────────────────────────────────────────
    path('admin/dashboard/',              views.campus_admin_dashboard,   name='campus_admin_dashboard'),
    path('admin/institutions/',           views.admin_institutions,       name='campus_admin_institutions'),
    path('admin/institutions/<int:pk>/verify/', views.admin_verify_institution, name='campus_admin_verify_institution'),
    path('admin/companies/',              views.admin_companies,          name='campus_admin_companies'),
    path('admin/companies/<int:pk>/verify/', views.admin_verify_company,  name='campus_admin_verify_company'),
    path('admin/opportunities/',          views.admin_opportunities,      name='campus_admin_opportunities'),
    path('admin/applications/',           views.admin_applications,       name='campus_admin_applications'),
    path('admin/reports/',                views.admin_reports,            name='campus_admin_reports'),
]
