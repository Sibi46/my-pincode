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
]
