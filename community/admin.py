from django.contrib import admin
from .models import FamilyStory, FamilyStoryLike, FamilyStoryComment


@admin.register(FamilyStory)
class FamilyStoryAdmin(admin.ModelAdmin):
    list_display  = ('title', 'user', 'category', 'pincode', 'is_active', 'created_at')
    list_filter   = ('category', 'is_active')
    search_fields = ('title', 'user__username')
    list_editable = ('is_active',)


@admin.register(FamilyStoryComment)
class FamilyStoryCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'created_at')
