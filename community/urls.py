from django.urls import path
from . import views

urlpatterns = [
    path('',           views.hub,         name='community_hub'),
    path('<slug:slug>/', views.module_page, name='community_module'),
]
