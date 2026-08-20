from django.contrib import admin
from .models import (
    Category, Community, CommunityLeader, CommunityMember,
    Cause, CauseSupport, Event, EventParticipant,
    VolunteerRequest, Activity, ActivityPhoto,
    Post, PostLike, PostComment, ShortVideo, PortalNotification,
)

admin.site.register(Category)
admin.site.register(Community)
admin.site.register(CommunityLeader)
admin.site.register(CommunityMember)
admin.site.register(Cause)
admin.site.register(CauseSupport)
admin.site.register(Event)
admin.site.register(EventParticipant)
admin.site.register(VolunteerRequest)
admin.site.register(Activity)
admin.site.register(ActivityPhoto)
admin.site.register(Post)
admin.site.register(ShortVideo)
admin.site.register(PortalNotification)
