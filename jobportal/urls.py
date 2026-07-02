from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from jobs import views

urlpatterns = [
    path('admin/',                  admin.site.urls),
    path('',                        views.home,               name='home'),

    # Auth
    path('register/',               views.register,           name='register'),
    path('register/process/',       views.register_process,   name='register_process'),
    path('login/',                  views.login_view,         name='login'),
    path('logout/',                 views.logout_view,        name='logout'),
    path('dashboard/',              views.dashboard,          name='dashboard'),

    # OTP
    path('api/send-otp/',           views.send_otp,           name='send_otp'),
    path('api/verify-otp/',         views.verify_otp,         name='verify_otp'),
    path('api/quick-register/',     views.quick_register,     name='quick_register'),
    path('api/check-phone/',        views.check_phone,        name='check_phone'),
    path('api/phone-login/',        views.phone_login,        name='phone_login'),

    # Jobs
    path('jobs/',                   views.job_list,           name='job_list'),
    path('jobs/<int:pk>/',          views.job_detail,         name='job_detail'),
    path('jobs/<int:pk>/apply/',    views.apply_job,          name='apply_job'),
    path('post-job/',               views.post_job,           name='post_job'),
    path('jobs/<int:pk>/edit/',     views.edit_job,           name='edit_job'),

    # Dashboards
    path('employer/dashboard/',        views.employer_dashboard,  name='employer_dashboard'),
    path('jobseeker/dashboard/',       views.jobseeker_dashboard, name='jobseeker_dashboard'),
    path('jobseeker/profile/',         views.seeker_profile,      name='seeker_profile'),
    path('jobseeker/certificate/<int:cert_id>/delete/', views.seeker_cert_delete, name='seeker_cert_delete'),


    # Job Seeker Actions
    path('jobs/<int:pk>/save/',              views.save_job,              name='save_job'),
    path('jobs/saved/',                      views.saved_jobs,            name='saved_jobs'),
    path('jobs/<int:pk>/withdraw/',          views.withdraw_application,  name='withdraw_application'),

    # Messaging
    path('messages/',                            views.chat_list,          name='chat_list'),
    path('messages/<int:conv_id>/',              views.chat_room,          name='chat_room'),
    path('messages/start/<int:user_id>/',        views.start_conversation, name='start_conversation'),
    path('messages/start/<int:user_id>/<int:job_id>/', views.start_conversation, name='start_conversation_job'),
    path('messages/send/',                       views.send_message,       name='send_message'),
    path('messages/poll/<int:conv_id>/',         views.poll_messages,      name='poll_messages'),
    path('messages/invite/<int:msg_id>/respond/', views.respond_invite,    name='respond_invite'),
    # Legacy chat redirect
    path('chat/<int:user_id>/<int:job_id>/', views.chat_messages_api, name='chat_api'),

    # Interview
    path('interview/schedule/<int:app_id>/', views.schedule_interview,    name='schedule_interview'),
    path('interview/accept/<int:app_id>/',   views.accept_interview,      name='accept_interview'),
    path('interview/reject/<int:app_id>/',   views.reject_interview,      name='reject_interview'),

    # Offer Letter
    path('offer/send/<int:app_id>/',         views.send_offer_letter,     name='send_offer_letter'),
    path('offer/download/<int:app_id>/',     views.download_offer_letter, name='download_offer_letter'),

    # Advertiser — Public
    path('advertise/',                        views.ads_gallery,              name='ads_gallery'),
    path('advertise/register/',               views.advertiser_register,      name='advertiser_register'),
    path('advertise/success/',                views.advertiser_register_success, name='advertiser_register_success'),

    # Advertiser — Logged-in
    path('advertiser/dashboard/',             views.advertiser_dashboard,     name='advertiser_dashboard'),
    path('advertiser/create-ad/',             views.create_advertisement,     name='create_advertisement'),
    path('advertiser/payment/<int:ad_id>/',   views.ad_payment,               name='ad_payment'),
    path('advertiser/payment/<int:ad_id>/success/', views.ad_payment_success, name='ad_payment_success'),
    path('advertiser/performance/<int:ad_id>/', views.ad_performance,         name='ad_performance'),
    path('advertiser/renew/<int:ad_id>/',     views.renew_ad,                 name='renew_ad'),
    path('ads/click/<int:ad_id>/',            views.ad_click_track,           name='ad_click_track'),

    # Advertiser — Ad Panel (old admin)
    path('admin-panel/advertisers/',          views.admin_advertisers,          name='admin_advertisers'),
    path('admin-panel/advertisers/<int:adv_id>/approve/', views.admin_approve_advertiser, name='admin_approve_advertiser'),
    path('admin-panel/advertisers/<int:adv_id>/reject/',  views.admin_reject_advertiser,  name='admin_reject_advertiser'),
    path('admin-panel/ads/',                  views.admin_ad_list,              name='admin_ad_list'),
    path('admin-panel/ads/<int:ad_id>/activate/', views.admin_activate_ad,      name='admin_activate_ad'),
    path('admin-panel/ads/<int:ad_id>/reject/',   views.admin_reject_ad,        name='admin_reject_ad'),
    path('admin-panel/ads/<int:ad_id>/delete/',   views.admin_delete_ad,        name='admin_delete_ad'),
    path('api/ai-job-description/',               views.ai_generate_description, name='ai_generate_description'),
    path('api/nearby-jobs/',                      views.nearby_jobs_api,         name='nearby_jobs_api'),
    path('admin-panel/login/',                    views.admin_panel_login,       name='admin_panel_login'),
    path('admin-panel/ads/<int:ad_id>/image/',    views.admin_set_ad_image,     name='admin_set_ad_image'),

    # ── SUPER ADMIN ─────────────────────────────────────────
    path('super-admin/',                               views.super_admin_dashboard, name='super_admin_dashboard'),
    path('super-admin/states/',                        views.manage_states,         name='manage_states'),
    path('super-admin/states/<int:pk>/toggle/',        views.toggle_state,          name='toggle_state'),
    path('super-admin/states/<int:state_id>/districts/', views.manage_districts,    name='manage_districts'),
    path('super-admin/state-admins/',                  views.manage_state_admins,   name='manage_state_admins'),
    path('super-admin/state-admins/create/',           views.create_state_admin,    name='create_state_admin'),
    path('super-admin/admins/<int:pk>/toggle/',        views.toggle_admin,          name='toggle_admin'),
    path('super-admin/industries/',                    views.manage_industries,     name='manage_industries'),
    path('super-admin/job-roles/',                     views.manage_job_roles,      name='manage_job_roles'),
    path('super-admin/job-roles/<int:industry_id>/',   views.manage_job_roles,      name='manage_job_roles_industry'),
    path('super-admin/payment-plans/',                 views.manage_payment_plans,  name='manage_payment_plans'),
    path('super-admin/discounts/',                     views.manage_discounts,      name='manage_discounts'),
    path('super-admin/pincodes/',                      views.manage_pincodes,       name='manage_pincodes'),
    path('super-admin/pincodes/<int:district_id>/',    views.manage_pincodes,       name='manage_pincodes_district'),
    path('super-admin/notifications/',                 views.manage_notifications,  name='manage_notifications'),
    path('super-admin/analytics/',                     views.national_analytics,    name='national_analytics'),

    # ── STATE ADMIN ─────────────────────────────────────────
    path('state-admin/',                               views.state_admin_dashboard, name='state_admin_dashboard'),
    path('state-admin/district-admins/create/',        views.create_district_admin, name='create_district_admin'),
    path('state-admin/employers/',                     views.verify_employers,      name='verify_employers'),
    path('state-admin/users/<int:user_id>/suspend/',   views.suspend_user,          name='suspend_user'),
    path('state-admin/reports/',                       views.state_reports,         name='state_reports'),

    # ── DISTRICT ADMIN ──────────────────────────────────────
    path('district-admin/',                            views.district_admin_dashboard,   name='district_admin_dashboard'),
    path('district-admin/employers/',                  views.approve_employers_district, name='approve_employers_district'),
    path('district-admin/jobs/',                       views.moderate_jobs,              name='moderate_jobs'),
    path('district-admin/complaints/',                 views.handle_complaints,          name='handle_complaints'),
    path('district-admin/complaints/<int:complaint_id>/resolve/', views.resolve_complaint, name='resolve_complaint'),
    path('district-admin/reports/',                    views.district_reports,           name='district_reports'),

    # ── PUBLIC ──────────────────────────────────────────────
    path('complaint/submit/',                          views.submit_complaint,      name='submit_complaint'),

    # ── UTILITY ─────────────────────────────────────────────
    path('profile/',                                   views.profile_redirect,      name='profile_redirect'),
    path('candidates/',                                views.candidates,            name='candidates'),
    path('candidates/save/<int:user_id>/',             views.save_candidate,        name='save_candidate'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
