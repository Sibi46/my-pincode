from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('',                                    views.portal_home,            name='portal_home'),
    path('communities/',                        views.community_list,         name='portal_community_list'),
    path('events/',                             views.events_list,            name='portal_events'),
    path('events/create/',                      views.create_event_standalone, name='portal_create_event_standalone'),
    path('event/<int:pk>/',                     views.event_detail,           name='portal_event_detail'),
    path('videos/',                             views.videos_list,            name='portal_videos'),
    path('search/',                             views.portal_search,          name='portal_search'),

    # Community CRUD
    path('create/',                             views.create_community,       name='portal_create_community'),
    path('c/<str:page_id>/nominations/',        views.nominations_step,       name='portal_nominations_step'),
    path('c/<str:page_id>/',                    views.community_page,         name='portal_community'),
    path('c/<str:page_id>/join/',               views.join_community,         name='portal_join'),
    path('c/<str:page_id>/dashboard/',          views.community_dashboard,    name='portal_dashboard'),
    path('c/<str:page_id>/members/',            views.manage_members,         name='portal_manage_members'),
    path('c/<str:page_id>/leaders/add/',        views.add_leader,             name='portal_add_leader'),
    path('c/<str:page_id>/events/create/',      views.create_event,           name='portal_create_event'),
    path('c/<str:page_id>/post/',               views.create_post,            name='portal_create_post'),
    path('c/<str:page_id>/video/upload/',       views.upload_video,           name='portal_upload_video'),
    path('c/<str:page_id>/volunteer/',          views.volunteer_form,         name='portal_volunteer_form'),
    path('c/<str:page_id>/volunteers/',         views.manage_volunteers,      name='portal_manage_volunteers'),

    # Event management
    path('event/<int:pk>/register/',            views.event_register,         name='portal_event_register'),
    path('event/<int:pk>/edit/',               views.edit_event,             name='portal_edit_event'),
    path('event/<int:pk>/manage/',              views.manage_event,           name='portal_manage_event'),

    # Event extended features
    path('event/<int:pk>/cancel/',   views.event_cancel_registration, name='portal_event_cancel'),
    path('event/<int:pk>/comment/',  views.event_comment,             name='portal_event_comment'),
    path('event/<int:pk>/announce/', views.event_announce,            name='portal_event_announce'),
    path('event/<int:pk>/photos/',   views.event_photo_upload,        name='portal_event_photos'),
    path('event/<int:pk>/rate/',     views.event_rate,                name='portal_event_rate'),
    path('event/<int:pk>/status/',   views.event_update_status,       name='portal_event_status'),

    # Post interactions
    path('post/<int:pk>/like/',                 views.like_post,              name='portal_like_post'),
    path('post/<int:pk>/comment/',              views.comment_post,           name='portal_comment_post'),

    # Videos
    path('video/<int:pk>/delete/',              views.delete_video,           name='portal_delete_video'),

    # Leader acceptance
    path('leader/accept/<str:token>/',          views.leader_accept,          name='portal_leader_accept'),

    # User pages
    path('my/communities/',                     views.my_communities,         name='portal_my_communities'),
    path('my/events/',                          views.my_events,              name='portal_my_events'),
    path('my/notifications/',                   views.portal_notifications,   name='portal_notifications'),

    # Platform admin
    path('admin/communities/',                  views.admin_communities,      name='portal_admin_communities'),
    path('admin/communities/<int:pk>/verify/',  views.admin_verify_community, name='portal_admin_verify'),
    path('admin/communities/<int:pk>/suspend/', views.admin_suspend_community,name='portal_admin_suspend'),
    path('admin/communities/<int:pk>/reject/',  views.admin_reject_community, name='portal_admin_reject'),
    path('admin/communities/<int:pk>/delete/',  views.admin_delete_community, name='portal_admin_delete'),
    path('admin/video/<int:pk>/delete/',        views.admin_delete_video,     name='portal_admin_delete_video'),
    path('admin/event/<int:pk>/delete/',        views.admin_delete_event,     name='portal_admin_delete_event'),
]
