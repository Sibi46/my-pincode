from django.urls import path
from . import views

urlpatterns = [
    path('',                               views.hub,                   name='community_hub'),

    # Family Stories
    path('family-stories/',                views.family_stories_feed,   name='family_stories'),
    path('family-stories/post/',           views.family_story_post,     name='family_story_post'),
    path('family-stories/<int:pk>/',       views.family_story_detail,   name='family_story_detail'),
    path('family-stories/<int:pk>/like/',  views.family_story_like,     name='family_story_like'),
    path('family-stories/<int:pk>/delete/', views.family_story_delete,  name='family_story_delete'),

    # Module catch-all (coming soon)
    path('<slug:slug>/',                   views.module_page,           name='community_module'),
]
