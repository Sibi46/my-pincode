from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class FamilyStory(models.Model):
    CATEGORY_CHOICES = [
        ('birthday',    'Birthday'),
        ('achievement', 'Achievement'),
        ('tradition',   'Tradition'),
        ('celebration', 'Celebration'),
        ('vacation',    'Vacation'),
        ('gardening',   'Gardening'),
        ('other',       'Other'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='family_stories')
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    image      = models.ImageField(upload_to='family_stories/', blank=True, null=True)
    category   = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    pincode    = models.CharField(max_length=10, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()


class FamilyStoryLike(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(FamilyStory, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'story')


class FamilyStoryComment(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    story      = models.ForeignKey(FamilyStory, on_delete=models.CASCADE, related_name='comments')
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user} on {self.story}"
