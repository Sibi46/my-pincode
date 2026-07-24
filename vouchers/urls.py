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

     # Gift Voucher management
    path('vouchers/',                   views.voucher_list,    name='voucher_list'),
    path('vouchers/create/',            views.voucher_create,  name='voucher_create'),
    path('vouchers/<int:pk>/edit/',     views.voucher_edit,    name='voucher_edit'),
    path('vouchers/<int:pk>/publish/',  views.voucher_publish,  name='voucher_publish'),
    path('vouchers/<int:pk>/pause/',    views.voucher_pause,    name='voucher_pause'),
    path('vouchers/<int:pk>/resume/',   views.voucher_resume,   name='voucher_resume'),
    path('vouchers/<int:pk>/delete/',   views.voucher_delete,   name='voucher_delete'),
    # Marketplace (public)
    path('marketplace/',          views.marketplace,     name='marketplace'),
    path('marketplace/<int:pk>/', views.voucher_detail,  name='voucher_detail'),
      # Customer purchase
    path('buy/<int:pk>/',     views.voucher_purchase,  name='voucher_purchase'),
    path('confirm/<int:pk>/', views.purchase_confirm,  name='purchase_confirm'),
  # Redemption
    path('redeem/',                  views.redeem_lookup,    name='redeem_lookup'),
    path('redeem/<int:pk>/send-otp/', views.redeem_send_otp, name='redeem_send_otp'),
    path('redeem/<int:pk>/verify/',   views.redeem_verify,   name='redeem_verify'),
     # Admin panel
    path('admin-panel/',                             views.admin_dashboard,        name='admin_dashboard'),
    path('admin-panel/business/<int:pk>/approve/',   views.admin_approve_business, name='admin_approve_business'),
    path('admin-panel/business/<int:pk>/reject/',    views.admin_reject_business,  name='admin_reject_business'),
    path('admin-panel/slot/<int:pk>/approve/',       views.admin_approve_slot,     name='admin_approve_slot'),
    path('admin-panel/slot/<int:pk>/reject/',        views.admin_reject_slot,      name='admin_reject_slot'),
]
