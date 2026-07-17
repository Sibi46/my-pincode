from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('',                            views.health_home,          name='health_home'),

    # Conditions
    path('condition/<slug:slug>/',      views.condition_detail,     name='condition_detail'),

    # Food Library
    path('foods/',                      views.food_list,            name='health_food_list'),
    path('foods/<slug:slug>/',          views.food_detail,          name='health_food_detail'),

    # Fruits
    path('fruits/',                     views.fruit_list,           name='health_fruit_list'),
    path('fruits/<slug:slug>/',         views.fruit_detail,         name='health_fruit_detail'),

    # Vegetables
    path('vegetables/',                 views.vegetable_list,       name='health_vegetable_list'),
    path('vegetables/<slug:slug>/',     views.vegetable_detail,     name='health_vegetable_detail'),

    # Herbs
    path('herbs/',                      views.herb_list,            name='health_herb_list'),
    path('herbs/<slug:slug>/',          views.herb_detail,          name='health_herb_detail'),

    # Recipes
    path('recipes/',                    views.recipe_list,          name='health_recipe_list'),
    path('recipes/<slug:slug>/',        views.recipe_detail,        name='health_recipe_detail'),

    # Videos
    path('videos/',                     views.video_list,           name='health_video_list'),

    # AI Chat
    path('chat/',                       views.health_chat,          name='health_chat'),
    path('api/chat/',                   views.health_chat_api,      name='health_chat_api'),

    # User features
    path('favorites/',                  views.health_favorites,     name='health_favorites'),
    path('favorites/toggle/',           views.toggle_favorite,      name='toggle_favorite'),
    path('diary/',                      views.food_diary,           name='food_diary'),
    path('diary/save/',                 views.food_diary_save,      name='food_diary_save'),
    path('planner/',                    views.meal_planner,         name='meal_planner'),
    path('planner/save/',               views.meal_planner_save,    name='meal_planner_save'),
    path('shopping-list/',              views.shopping_list,        name='health_shopping_list'),
    path('progress/',                   views.health_progress,      name='health_progress'),

    # Search
    path('search/',                     views.health_search,        name='health_search'),

    # Admin
    path('admin/',                      views.hadmin_dashboard,     name='hadmin_dashboard'),
    path('admin/conditions/',           views.hadmin_conditions,    name='hadmin_conditions'),
    path('admin/conditions/add/',       views.hadmin_condition_edit, name='hadmin_condition_add'),
    path('admin/conditions/<int:pk>/',  views.hadmin_condition_edit, name='hadmin_condition_edit'),
    path('admin/conditions/<int:pk>/delete/', views.hadmin_condition_delete, name='hadmin_condition_delete'),

    path('admin/foods/',                views.hadmin_foods,         name='hadmin_foods'),
    path('admin/foods/add/',            views.hadmin_food_edit,     name='hadmin_food_add'),
    path('admin/foods/<int:pk>/',       views.hadmin_food_edit,     name='hadmin_food_edit'),
    path('admin/foods/<int:pk>/delete/', views.hadmin_food_delete,  name='hadmin_food_delete'),

    path('admin/fruits/',               views.hadmin_fruits,        name='hadmin_fruits'),
    path('admin/fruits/add/',           views.hadmin_fruit_edit,    name='hadmin_fruit_add'),
    path('admin/fruits/<int:pk>/',      views.hadmin_fruit_edit,    name='hadmin_fruit_edit'),
    path('admin/fruits/<int:pk>/delete/', views.hadmin_fruit_delete, name='hadmin_fruit_delete'),

    path('admin/vegetables/',           views.hadmin_vegetables,    name='hadmin_vegetables'),
    path('admin/vegetables/add/',       views.hadmin_vegetable_edit, name='hadmin_vegetable_add'),
    path('admin/vegetables/<int:pk>/',  views.hadmin_vegetable_edit, name='hadmin_vegetable_edit'),
    path('admin/vegetables/<int:pk>/delete/', views.hadmin_vegetable_delete, name='hadmin_vegetable_delete'),

    path('admin/herbs/',                views.hadmin_herbs,         name='hadmin_herbs'),
    path('admin/herbs/add/',            views.hadmin_herb_edit,     name='hadmin_herb_add'),
    path('admin/herbs/<int:pk>/',       views.hadmin_herb_edit,     name='hadmin_herb_edit'),
    path('admin/herbs/<int:pk>/delete/', views.hadmin_herb_delete,  name='hadmin_herb_delete'),

    path('admin/recipes/',              views.hadmin_recipes,       name='hadmin_recipes'),
    path('admin/recipes/add/',          views.hadmin_recipe_edit,   name='hadmin_recipe_add'),
    path('admin/recipes/<int:pk>/',     views.hadmin_recipe_edit,   name='hadmin_recipe_edit'),
    path('admin/recipes/<int:pk>/delete/', views.hadmin_recipe_delete, name='hadmin_recipe_delete'),

    path('admin/videos/',               views.hadmin_videos,        name='hadmin_videos'),
    path('admin/videos/add/',           views.hadmin_video_edit,    name='hadmin_video_add'),
    path('admin/videos/<int:pk>/',      views.hadmin_video_edit,    name='hadmin_video_edit'),
    path('admin/videos/<int:pk>/delete/', views.hadmin_video_delete, name='hadmin_video_delete'),

    path('admin/settings/',             views.hadmin_settings,      name='hadmin_settings'),
]
