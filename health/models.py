from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class HealthSettings(models.Model):
    gemini_api_key  = models.CharField(max_length=200, blank=True)
    ai_system_prompt = models.TextField(default=(
        "You are a friendly healthy food guide assistant for MY PINCOD. "
        "Answer only food and nutrition questions. Give clear, simple answers in easy English. "
        "Never diagnose diseases or replace a doctor. "
        "Always end every response with: '⚠️ This is educational information only, not medical advice. Please consult your doctor.'"
    ))
    daily_tip       = models.TextField(blank=True)
    site_tagline    = models.CharField(max_length=200, default='Eat Right. Live Well.')

    class Meta:
        verbose_name = 'Health Settings'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Health Settings'


class HealthCondition(models.Model):
    name             = models.CharField(max_length=100)
    slug             = models.SlugField(unique=True)
    icon             = models.CharField(max_length=10, default='🩺')
    image            = models.ImageField(upload_to='health/conditions/', blank=True, null=True)
    overview         = models.TextField(blank=True)
    foods_to_eat     = models.TextField(blank=True)
    foods_to_limit   = models.TextField(blank=True)
    fruits_info      = models.TextField(blank=True)
    vegetables_info  = models.TextField(blank=True)
    herbs_info       = models.TextField(blank=True)
    spices_info      = models.TextField(blank=True)
    cooking_methods  = models.TextField(blank=True)
    meal_timing      = models.TextField(blank=True)
    portion_guidance = models.TextField(blank=True)
    faq              = models.TextField(blank=True, help_text='JSON: [{"q":"...","a":"..."}]')
    is_featured      = models.BooleanField(default=False)
    order            = models.PositiveIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Food(models.Model):
    name            = models.CharField(max_length=150)
    slug            = models.SlugField(unique=True)
    image           = models.ImageField(upload_to='health/foods/', blank=True, null=True)
    description     = models.TextField(blank=True)
    scientific_name = models.CharField(max_length=150, blank=True)
    nutrition_facts = models.TextField(blank=True)
    benefits        = models.TextField(blank=True)
    suitable_for    = models.CharField(max_length=300, blank=True)
    avoid_if        = models.CharField(max_length=300, blank=True)
    best_time       = models.CharField(max_length=200, blank=True)
    serving_size    = models.CharField(max_length=150, blank=True)
    cooking_methods = models.TextField(blank=True)
    is_featured     = models.BooleanField(default=False)
    conditions      = models.ManyToManyField(HealthCondition, blank=True, related_name='foods')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Fruit(models.Model):
    name              = models.CharField(max_length=100)
    slug              = models.SlugField(unique=True)
    image             = models.ImageField(upload_to='health/fruits/', blank=True, null=True)
    description       = models.TextField(blank=True)
    nutrition         = models.TextField(blank=True)
    benefits          = models.TextField(blank=True)
    serving_size      = models.CharField(max_length=150, blank=True)
    best_time         = models.CharField(max_length=150, blank=True)
    diabetes_safe     = models.BooleanField(default=True)
    diabetes_note     = models.CharField(max_length=300, blank=True)
    is_featured       = models.BooleanField(default=False)
    conditions        = models.ManyToManyField(HealthCondition, blank=True, related_name='fruits')
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Vegetable(models.Model):
    name            = models.CharField(max_length=100)
    slug            = models.SlugField(unique=True)
    image           = models.ImageField(upload_to='health/vegetables/', blank=True, null=True)
    description     = models.TextField(blank=True)
    nutrition       = models.TextField(blank=True)
    benefits        = models.TextField(blank=True)
    cooking_methods = models.TextField(blank=True)
    best_time       = models.CharField(max_length=150, blank=True)
    serving_size    = models.CharField(max_length=150, blank=True)
    is_featured     = models.BooleanField(default=False)
    conditions      = models.ManyToManyField(HealthCondition, blank=True, related_name='vegetables')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Herb(models.Model):
    name               = models.CharField(max_length=100)
    slug               = models.SlugField(unique=True)
    image              = models.ImageField(upload_to='health/herbs/', blank=True, null=True)
    description        = models.TextField(blank=True)
    traditional_uses   = models.TextField(blank=True)
    scientific_evidence = models.TextField(blank=True)
    preparation        = models.TextField(blank=True)
    benefits           = models.TextField(blank=True)
    precautions        = models.TextField(blank=True)
    is_featured        = models.BooleanField(default=False)
    conditions         = models.ManyToManyField(HealthCondition, blank=True, related_name='herbs')
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    CATEGORY = [
        ('breakfast', 'Breakfast'),
        ('lunch',     'Lunch'),
        ('dinner',    'Dinner'),
        ('snack',     'Snacks'),
        ('drink',     'Drinks'),
    ]
    DIFFICULTY = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]

    name         = models.CharField(max_length=150)
    slug         = models.SlugField(unique=True)
    image        = models.ImageField(upload_to='health/recipes/', blank=True, null=True)
    category     = models.CharField(max_length=20, choices=CATEGORY, default='breakfast')
    description  = models.TextField(blank=True)
    ingredients  = models.TextField(blank=True, help_text='One per line')
    steps        = models.TextField(blank=True, help_text='One step per line')
    nutrition    = models.TextField(blank=True)
    calories     = models.PositiveIntegerField(null=True, blank=True)
    prep_time    = models.PositiveIntegerField(null=True, blank=True, help_text='Minutes')
    cook_time    = models.PositiveIntegerField(null=True, blank=True, help_text='Minutes')
    servings     = models.PositiveIntegerField(default=2)
    difficulty   = models.CharField(max_length=10, choices=DIFFICULTY, default='easy')
    is_featured  = models.BooleanField(default=False)
    conditions   = models.ManyToManyField(HealthCondition, blank=True, related_name='recipes')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return self.name

    @property
    def total_time(self):
        return (self.prep_time or 0) + (self.cook_time or 0)


class Video(models.Model):
    CATEGORY = [
        ('general',   'General Health'),
        ('diabetes',  'Diabetes'),
        ('bp',        'Blood Pressure'),
        ('heart',     'Heart Health'),
        ('weight',    'Weight Loss'),
        ('recipes',   'Recipes'),
        ('herbs',     'Herbs & Spices'),
        ('yoga',      'Yoga & Exercise'),
    ]
    title       = models.CharField(max_length=200)
    youtube_url = models.URLField()
    thumbnail   = models.ImageField(upload_to='health/videos/', blank=True, null=True)
    category    = models.CharField(max_length=20, choices=CATEGORY, default='general')
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    conditions  = models.ManyToManyField(HealthCondition, blank=True, related_name='videos')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return self.title

    @property
    def youtube_id(self):
        import re
        patterns = [
            r'(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})',
        ]
        for p in patterns:
            m = re.search(p, self.youtube_url)
            if m:
                return m.group(1)
        return ''

    @property
    def embed_url(self):
        vid = self.youtube_id
        return f'https://www.youtube.com/embed/{vid}' if vid else ''

    @property
    def thumb_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        vid = self.youtube_id
        return f'https://img.youtube.com/vi/{vid}/hqdefault.jpg' if vid else ''


# ── USER FEATURES ─────────────────────────────────────────────────────────────

class Favorite(models.Model):
    TYPE = [
        ('food',      'Food'),
        ('fruit',     'Fruit'),
        ('vegetable', 'Vegetable'),
        ('herb',      'Herb'),
        ('recipe',    'Recipe'),
        ('video',     'Video'),
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_favorites')
    item_type   = models.CharField(max_length=15, choices=TYPE)
    item_id     = models.PositiveIntegerField()
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item_type', 'item_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} ❤ {self.item_type}:{self.item_id}"


class FoodDiary(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_diaries')
    date         = models.DateField()
    water_glasses = models.PositiveIntegerField(default=0)
    notes        = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} — {self.date}"


class FoodDiaryEntry(models.Model):
    MEAL = [('breakfast','Breakfast'),('lunch','Lunch'),('dinner','Dinner'),('snack','Snacks')]
    diary     = models.ForeignKey(FoodDiary, on_delete=models.CASCADE, related_name='entries')
    meal_type = models.CharField(max_length=15, choices=MEAL)
    food_name = models.CharField(max_length=200)
    quantity  = models.CharField(max_length=100, blank=True)
    calories  = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['meal_type']

    def __str__(self):
        return f"{self.diary.date} {self.meal_type}: {self.food_name}"


class MealPlan(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_plans')
    name       = models.CharField(max_length=150, default='My Meal Plan')
    start_date = models.DateField()
    end_date   = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.user} — {self.name}"


class MealPlanItem(models.Model):
    MEAL = [('breakfast','Breakfast'),('lunch','Lunch'),('dinner','Dinner'),('snack','Snacks')]
    plan      = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='items')
    date      = models.DateField()
    meal_type = models.CharField(max_length=15, choices=MEAL)
    recipe    = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    custom    = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.date} {self.meal_type}: {self.recipe or self.custom}"
