from django.urls import path
from . import views

app_name = 'vouchers'

urlpatterns = [
    path('business/register/',         views.business_register,         name='business_register'),
    path('business/register/success/', views.business_register_success, name='register_success'),
    path('dashboard/',                 views.business_dashboard,        name='business_dashboard'),
]
