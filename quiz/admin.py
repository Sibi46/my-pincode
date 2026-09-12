from django.contrib import admin
from .models import Quiz, QuizQuestion, UserQuizAnswer

class QuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 0

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'is_active', 'question_count', 'created_at']
    inlines = [QuestionInline]

@admin.register(UserQuizAnswer)
class UserQuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'answer', 'is_correct', 'answered_at']
