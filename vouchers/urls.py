from django.urls import path
from . import views

app_name = 'vouchers'

urlpatterns = [
    path('business/register/',         views.business_register,         name='business_register'),
    path('business/register/success/', views.business_register_success, name='register_success'),
    path('dashboard/',                 views.business_dashboard,        name='business_dashboard'),

    # Branch management
    path('branches/',              views.branch_list,   name='branch_list'),
    path('branches/add/',          views.branch_add,    name='branch_add'),
    path('branches/<int:pk>/edit/', views.branch_edit,  name='branch_edit'),
    path('branches/<int:pk>/toggle/', views.branch_toggle, name='branch_toggle'),
     # Employee management
    path('employees/',                  views.employee_list,   name='employee_list'),
    path('employees/add/',              views.employee_add,    name='employee_add'),
    path('employees/<int:pk>/edit/',    views.employee_edit,   name='employee_edit'),
    path('employees/<int:pk>/toggle/',  views.employee_toggle, name='employee_toggle'),

    # Slot purchase
    path('slots/',     views.slot_history, name='slot_history'),
    path('slots/buy/', views.slot_buy,     name='slot_buy'),
]
