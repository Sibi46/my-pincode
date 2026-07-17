import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.text import slugify
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import (
    HealthSettings, HealthCondition, Food, Fruit, Vegetable,
    Herb, Recipe, Video, Favorite, FoodDiary, FoodDiaryEntry,
    MealPlan, MealPlanItem,
)


def super_admin_required(view_func):
    from functools import wraps
    from django.contrib.auth import get_user_model
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.admin_role != 'super_admin':
            messages.error(request, 'Super Admin access required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── HOME ──────────────────────────────────────────────────────────────────────

def health_home(request):
    settings    = HealthSettings.get()
    conditions  = HealthCondition.objects.filter(is_featured=True)[:6]
    all_conds   = HealthCondition.objects.all()[:12]
    foods       = Food.objects.filter(is_featured=True)[:8]
    fruits      = Fruit.objects.filter(is_featured=True)[:6]
    recipes     = Recipe.objects.filter(is_featured=True)[:6]
    videos      = Video.objects.filter(is_featured=True)[:4]
    return render(request, 'health/home.html', {
        'settings': settings,
        'conditions': conditions,
        'all_conditions': all_conds,
        'featured_foods': foods,
        'featured_fruits': fruits,
        'featured_recipes': recipes,
        'featured_videos': videos,
    })


# ── CONDITIONS ────────────────────────────────────────────────────────────────

def condition_detail(request, slug):
    condition = get_object_or_404(HealthCondition, slug=slug)
    foods     = condition.foods.all()[:8]
    fruits    = condition.fruits.all()[:8]
    vegetables = condition.vegetables.all()[:8]
    herbs     = condition.herbs.all()[:6]
    recipes   = condition.recipes.all()[:6]
    videos    = condition.videos.all()[:4]
    faq = []
    if condition.faq:
        try:
            faq = json.loads(condition.faq)
        except Exception:
            pass
    return render(request, 'health/condition_detail.html', {
        'condition': condition,
        'foods': foods, 'fruits': fruits,
        'vegetables': vegetables, 'herbs': herbs,
        'recipes': recipes, 'videos': videos,
        'faq': faq,
    })


# ── FOOD ──────────────────────────────────────────────────────────────────────

def food_list(request):
    q   = request.GET.get('q', '')
    qs  = Food.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(benefits__icontains=q))
    return render(request, 'health/food_list.html', {'foods': qs, 'q': q})


def food_detail(request, slug):
    food    = get_object_or_404(Food, slug=slug)
    related = Food.objects.exclude(pk=food.pk)[:4]
    is_fav  = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='food', item_id=food.pk).exists()
    return render(request, 'health/food_detail.html', {'food': food, 'related': related, 'is_fav': is_fav})


# ── FRUITS ────────────────────────────────────────────────────────────────────

def fruit_list(request):
    q  = request.GET.get('q', '')
    qs = Fruit.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
    return render(request, 'health/fruit_list.html', {'fruits': qs, 'q': q})


def fruit_detail(request, slug):
    fruit   = get_object_or_404(Fruit, slug=slug)
    is_fav  = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='fruit', item_id=fruit.pk).exists()
    return render(request, 'health/fruit_detail.html', {'fruit': fruit, 'is_fav': is_fav})


# ── VEGETABLES ────────────────────────────────────────────────────────────────

def vegetable_list(request):
    q  = request.GET.get('q', '')
    qs = Vegetable.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
    return render(request, 'health/vegetable_list.html', {'vegetables': qs, 'q': q})


def vegetable_detail(request, slug):
    veg    = get_object_or_404(Vegetable, slug=slug)
    is_fav = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='vegetable', item_id=veg.pk).exists()
    return render(request, 'health/vegetable_detail.html', {'veg': veg, 'is_fav': is_fav})


# ── HERBS ─────────────────────────────────────────────────────────────────────

def herb_list(request):
    q  = request.GET.get('q', '')
    qs = Herb.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
    return render(request, 'health/herb_list.html', {'herbs': qs, 'q': q})


def herb_detail(request, slug):
    herb   = get_object_or_404(Herb, slug=slug)
    is_fav = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='herb', item_id=herb.pk).exists()
    return render(request, 'health/herb_detail.html', {'herb': herb, 'is_fav': is_fav})


# ── RECIPES ───────────────────────────────────────────────────────────────────

def recipe_list(request):
    q        = request.GET.get('q', '')
    category = request.GET.get('cat', '')
    qs       = Recipe.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category:
        qs = qs.filter(category=category)
    return render(request, 'health/recipe_list.html', {
        'recipes': qs, 'q': q, 'category': category,
        'categories': Recipe.CATEGORY,
    })


def recipe_detail(request, slug):
    recipe  = get_object_or_404(Recipe, slug=slug)
    is_fav  = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, item_type='recipe', item_id=recipe.pk).exists()
    ingredients = [i.strip() for i in recipe.ingredients.splitlines() if i.strip()]
    steps       = [s.strip() for s in recipe.steps.splitlines() if s.strip()]
    return render(request, 'health/recipe_detail.html', {
        'recipe': recipe, 'is_fav': is_fav,
        'ingredients': ingredients, 'steps': steps,
    })


# ── VIDEOS ────────────────────────────────────────────────────────────────────

def video_list(request):
    category = request.GET.get('cat', '')
    qs       = Video.objects.all()
    if category:
        qs = qs.filter(category=category)
    return render(request, 'health/video_list.html', {
        'videos': qs, 'category': category,
        'categories': Video.CATEGORY,
    })


# ── AI CHAT ───────────────────────────────────────────────────────────────────

def health_chat(request):
    return render(request, 'health/chat.html')


def health_chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        body    = json.loads(request.body)
        message = body.get('message', '').strip()
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    settings = HealthSettings.get()
    api_key  = settings.gemini_api_key

    if not api_key:
        return JsonResponse({'reply': (
            "AI assistant is not configured yet. "
            "Please ask the admin to add the Gemini API key in Health Settings.\n\n"
            "⚠️ This is educational information only, not medical advice."
        )})

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model  = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"{settings.ai_system_prompt}\n\nUser: {message}"
        resp   = model.generate_content(prompt)
        reply  = resp.text
    except ImportError:
        reply = ("AI library not installed on server. "
                 "Run: pip install google-generativeai\n\n"
                 "⚠️ This is educational information only, not medical advice.")
    except Exception as e:
        reply = (f"AI is temporarily unavailable. Please try again later.\n\n"
                 "⚠️ This is educational information only, not medical advice.")

    return JsonResponse({'reply': reply})


# ── FAVORITES ─────────────────────────────────────────────────────────────────

@login_required
def health_favorites(request):
    favs = Favorite.objects.filter(user=request.user).order_by('-created_at')
    data = {'foods': [], 'fruits': [], 'vegetables': [], 'herbs': [], 'recipes': [], 'videos': []}
    for f in favs:
        try:
            if f.item_type == 'food':
                data['foods'].append(Food.objects.get(pk=f.item_id))
            elif f.item_type == 'fruit':
                data['fruits'].append(Fruit.objects.get(pk=f.item_id))
            elif f.item_type == 'vegetable':
                data['vegetables'].append(Vegetable.objects.get(pk=f.item_id))
            elif f.item_type == 'herb':
                data['herbs'].append(Herb.objects.get(pk=f.item_id))
            elif f.item_type == 'recipe':
                data['recipes'].append(Recipe.objects.get(pk=f.item_id))
            elif f.item_type == 'video':
                data['videos'].append(Video.objects.get(pk=f.item_id))
        except Exception:
            pass
    return render(request, 'health/favorites.html', {'data': data})


@login_required
def toggle_favorite(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        body      = json.loads(request.body)
        item_type = body.get('type')
        item_id   = int(body.get('id'))
    except Exception:
        return JsonResponse({'error': 'Invalid'}, status=400)
    obj, created = Favorite.objects.get_or_create(
        user=request.user, item_type=item_type, item_id=item_id
    )
    if not created:
        obj.delete()
        return JsonResponse({'saved': False})
    return JsonResponse({'saved': True})


# ── FOOD DIARY ────────────────────────────────────────────────────────────────

@login_required
def food_diary(request):
    from datetime import date
    today  = date.today()
    d_str  = request.GET.get('date', str(today))
    try:
        from datetime import datetime
        diary_date = datetime.strptime(d_str, '%Y-%m-%d').date()
    except Exception:
        diary_date = today
    diary, _  = FoodDiary.objects.get_or_create(user=request.user, date=diary_date)
    entries   = diary.entries.all()
    recent    = FoodDiary.objects.filter(user=request.user).exclude(date=diary_date)[:7]
    return render(request, 'health/diary.html', {
        'diary': diary, 'entries': entries,
        'diary_date': diary_date, 'today': today,
        'recent': recent,
        'meal_types': FoodDiaryEntry.MEAL,
    })


@login_required
def food_diary_save(request):
    if request.method != 'POST':
        return redirect('food_diary')
    from datetime import date, datetime
    diary_date = request.POST.get('date', str(date.today()))
    try:
        diary_date = datetime.strptime(diary_date, '%Y-%m-%d').date()
    except Exception:
        diary_date = date.today()

    diary, _ = FoodDiary.objects.get_or_create(user=request.user, date=diary_date)

    action = request.POST.get('action', '')
    if action == 'add_entry':
        meal_type = request.POST.get('meal_type', '')
        food_name = request.POST.get('food_name', '').strip()
        quantity  = request.POST.get('quantity', '').strip()
        calories  = request.POST.get('calories', '') or None
        if food_name:
            FoodDiaryEntry.objects.create(
                diary=diary, meal_type=meal_type,
                food_name=food_name, quantity=quantity,
                calories=int(calories) if calories else None,
            )
    elif action == 'delete_entry':
        entry_id = request.POST.get('entry_id')
        FoodDiaryEntry.objects.filter(pk=entry_id, diary__user=request.user).delete()
    elif action == 'update_water':
        diary.water_glasses = int(request.POST.get('water_glasses', 0))
        diary.save()
    elif action == 'update_notes':
        diary.notes = request.POST.get('notes', '')
        diary.save()

    return redirect(f'/health/diary/?date={diary_date}')


# ── MEAL PLANNER ──────────────────────────────────────────────────────────────

@login_required
def meal_planner(request):
    plans   = MealPlan.objects.filter(user=request.user)
    recipes = Recipe.objects.all()
    active  = plans.first()
    items   = {}
    if active:
        for item in active.items.select_related('recipe'):
            key = f"{item.date}_{item.meal_type}"
            items[key] = item
    return render(request, 'health/planner.html', {
        'plans': plans, 'active': active,
        'items': items, 'recipes': recipes,
        'meal_types': MealPlanItem.MEAL,
    })


@login_required
def meal_planner_save(request):
    if request.method != 'POST':
        return redirect('meal_planner')
    action = request.POST.get('action')
    if action == 'create_plan':
        from datetime import datetime
        name  = request.POST.get('name', 'My Meal Plan').strip()
        start = request.POST.get('start_date')
        end   = request.POST.get('end_date')
        try:
            start = datetime.strptime(start, '%Y-%m-%d').date()
            end   = datetime.strptime(end,   '%Y-%m-%d').date()
            MealPlan.objects.create(user=request.user, name=name, start_date=start, end_date=end)
            messages.success(request, f'Meal plan "{name}" created.')
        except Exception:
            messages.error(request, 'Invalid dates.')
    elif action == 'add_item':
        from datetime import datetime
        plan_id   = request.POST.get('plan_id')
        plan      = get_object_or_404(MealPlan, pk=plan_id, user=request.user)
        item_date = request.POST.get('item_date')
        meal_type = request.POST.get('meal_type')
        recipe_id = request.POST.get('recipe_id') or None
        custom    = request.POST.get('custom', '').strip()
        try:
            item_date = datetime.strptime(item_date, '%Y-%m-%d').date()
            recipe    = Recipe.objects.get(pk=recipe_id) if recipe_id else None
            MealPlanItem.objects.update_or_create(
                plan=plan, date=item_date, meal_type=meal_type,
                defaults={'recipe': recipe, 'custom': custom}
            )
        except Exception:
            messages.error(request, 'Could not save item.')
    elif action == 'delete_plan':
        plan_id = request.POST.get('plan_id')
        MealPlan.objects.filter(pk=plan_id, user=request.user).delete()
        messages.success(request, 'Plan deleted.')
    return redirect('meal_planner')


# ── SHOPPING LIST ─────────────────────────────────────────────────────────────

@login_required
def shopping_list(request):
    plan_id = request.GET.get('plan')
    plan    = None
    items   = []
    if plan_id:
        plan = get_object_or_404(MealPlan, pk=plan_id, user=request.user)
        seen = set()
        for mi in plan.items.select_related('recipe'):
            if mi.recipe:
                for line in mi.recipe.ingredients.splitlines():
                    line = line.strip()
                    if line and line not in seen:
                        items.append(line)
                        seen.add(line)
    plans = MealPlan.objects.filter(user=request.user)
    return render(request, 'health/shopping_list.html', {
        'plan': plan, 'items': items, 'plans': plans,
    })


# ── PROGRESS ──────────────────────────────────────────────────────────────────

@login_required
def health_progress(request):
    from datetime import date, timedelta
    today     = date.today()
    diary_count = FoodDiary.objects.filter(user=request.user).count()
    plan_count  = MealPlan.objects.filter(user=request.user).count()
    fav_count   = Favorite.objects.filter(user=request.user).count()
    streak = 0
    for i in range(30):
        d = today - timedelta(days=i)
        if FoodDiary.objects.filter(user=request.user, date=d).exists():
            streak += 1
        else:
            break
    return render(request, 'health/progress.html', {
        'diary_count': diary_count, 'plan_count': plan_count,
        'fav_count': fav_count, 'streak': streak,
    })


# ── SEARCH ────────────────────────────────────────────────────────────────────

def health_search(request):
    q   = request.GET.get('q', '').strip()
    results = {}
    if q:
        results['conditions']  = HealthCondition.objects.filter(name__icontains=q)
        results['foods']       = Food.objects.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
        results['fruits']      = Fruit.objects.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
        results['vegetables']  = Vegetable.objects.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
        results['herbs']       = Herb.objects.filter(Q(name__icontains=q) | Q(benefits__icontains=q))
        results['recipes']     = Recipe.objects.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return render(request, 'health/search.html', {'q': q, 'results': results})


# ── ADMIN VIEWS ───────────────────────────────────────────────────────────────

@super_admin_required
def hadmin_dashboard(request):
    return render(request, 'health/admin/dashboard.html', {
        'cond_count':  HealthCondition.objects.count(),
        'food_count':  Food.objects.count(),
        'fruit_count': Fruit.objects.count(),
        'veg_count':   Vegetable.objects.count(),
        'herb_count':  Herb.objects.count(),
        'recipe_count': Recipe.objects.count(),
        'video_count': Video.objects.count(),
        'user_count':  Favorite.objects.values('user').distinct().count(),
    })


def _hadmin_crud(request, Model, template, list_url, fields, slug_from='name'):
    if request.method == 'POST':
        pk     = request.POST.get('pk')
        action = request.POST.get('action', 'save')
        if action == 'delete' and pk:
            Model.objects.filter(pk=pk).delete()
            messages.success(request, 'Deleted.')
            return redirect(list_url)
        data = {f: request.POST.get(f, '') for f in fields if f not in ('image',)}
        for bool_field in ('is_featured', 'diabetes_safe'):
            if bool_field in fields:
                data[bool_field] = bool_field in request.POST
        if 'slug' in fields and not data.get('slug'):
            data['slug'] = slugify(data.get(slug_from, ''))
        if pk:
            obj = get_object_or_404(Model, pk=pk)
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
            messages.success(request, 'Updated.')
        else:
            obj = Model(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
            messages.success(request, 'Created.')
        return redirect(list_url)
    return None


@super_admin_required
def hadmin_conditions(request):
    return render(request, 'health/admin/condition_list.html',
                  {'items': HealthCondition.objects.all()})


@super_admin_required
def hadmin_condition_edit(request, pk=None):
    obj = get_object_or_404(HealthCondition, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','icon','overview','foods_to_eat','foods_to_limit',
                  'fruits_info','vegetables_info','herbs_info','spices_info',
                  'cooking_methods','meal_timing','portion_guidance','faq','order']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = HealthCondition(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_conditions')
    return render(request, 'health/admin/condition_edit.html', {'obj': obj})


@super_admin_required
def hadmin_condition_delete(request, pk):
    get_object_or_404(HealthCondition, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_conditions')


@super_admin_required
def hadmin_foods(request):
    return render(request, 'health/admin/food_list.html',
                  {'items': Food.objects.all()})


@super_admin_required
def hadmin_food_edit(request, pk=None):
    obj = get_object_or_404(Food, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','description','scientific_name','nutrition_facts',
                  'benefits','suitable_for','avoid_if','best_time','serving_size','cooking_methods']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Food(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_foods')
    return render(request, 'health/admin/food_edit.html', {'obj': obj})


@super_admin_required
def hadmin_food_delete(request, pk):
    get_object_or_404(Food, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_foods')


@super_admin_required
def hadmin_fruits(request):
    return render(request, 'health/admin/fruit_list.html',
                  {'items': Fruit.objects.all()})


@super_admin_required
def hadmin_fruit_edit(request, pk=None):
    obj = get_object_or_404(Fruit, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','description','nutrition','benefits',
                  'serving_size','best_time','diabetes_note']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured']   = 'is_featured' in request.POST
        data['diabetes_safe'] = 'diabetes_safe' in request.POST
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Fruit(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_fruits')
    return render(request, 'health/admin/fruit_edit.html', {'obj': obj})


@super_admin_required
def hadmin_fruit_delete(request, pk):
    get_object_or_404(Fruit, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_fruits')


@super_admin_required
def hadmin_vegetables(request):
    return render(request, 'health/admin/vegetable_list.html',
                  {'items': Vegetable.objects.all()})


@super_admin_required
def hadmin_vegetable_edit(request, pk=None):
    obj = get_object_or_404(Vegetable, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','description','nutrition','benefits',
                  'cooking_methods','best_time','serving_size']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Vegetable(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_vegetables')
    return render(request, 'health/admin/vegetable_edit.html', {'obj': obj})


@super_admin_required
def hadmin_vegetable_delete(request, pk):
    get_object_or_404(Vegetable, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_vegetables')


@super_admin_required
def hadmin_herbs(request):
    return render(request, 'health/admin/herb_list.html',
                  {'items': Herb.objects.all()})


@super_admin_required
def hadmin_herb_edit(request, pk=None):
    obj = get_object_or_404(Herb, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','description','traditional_uses',
                  'scientific_evidence','preparation','benefits','precautions']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Herb(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_herbs')
    return render(request, 'health/admin/herb_edit.html', {'obj': obj})


@super_admin_required
def hadmin_herb_delete(request, pk):
    get_object_or_404(Herb, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_herbs')


@super_admin_required
def hadmin_recipes(request):
    return render(request, 'health/admin/recipe_list.html',
                  {'items': Recipe.objects.all()})


@super_admin_required
def hadmin_recipe_edit(request, pk=None):
    obj = get_object_or_404(Recipe, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['name','slug','category','description','ingredients','steps',
                  'nutrition','difficulty']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        for int_field in ['calories','prep_time','cook_time','servings']:
            val = request.POST.get(int_field, '') or None
            data[int_field] = int(val) if val else None
        if not data['slug']:
            data['slug'] = slugify(data['name'])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        else:
            obj = Recipe(**data)
            if 'image' in request.FILES:
                obj.image = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_recipes')
    return render(request, 'health/admin/recipe_edit.html', {
        'obj': obj, 'categories': Recipe.CATEGORY, 'difficulties': Recipe.DIFFICULTY,
    })


@super_admin_required
def hadmin_recipe_delete(request, pk):
    get_object_or_404(Recipe, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_recipes')


@super_admin_required
def hadmin_videos(request):
    return render(request, 'health/admin/video_list.html',
                  {'items': Video.objects.all()})


@super_admin_required
def hadmin_video_edit(request, pk=None):
    obj = get_object_or_404(Video, pk=pk) if pk else None
    if request.method == 'POST':
        fields = ['title','youtube_url','category','description']
        data = {f: request.POST.get(f, '') for f in fields}
        data['is_featured'] = 'is_featured' in request.POST
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            if 'image' in request.FILES:
                obj.thumbnail = request.FILES['image']
            obj.save()
        else:
            obj = Video(**data)
            if 'image' in request.FILES:
                obj.thumbnail = request.FILES['image']
            obj.save()
        messages.success(request, 'Saved.')
        return redirect('hadmin_videos')
    return render(request, 'health/admin/video_edit.html', {
        'obj': obj, 'categories': Video.CATEGORY,
    })


@super_admin_required
def hadmin_video_delete(request, pk):
    get_object_or_404(Video, pk=pk).delete()
    messages.success(request, 'Deleted.')
    return redirect('hadmin_videos')


@super_admin_required
def hadmin_settings(request):
    settings = HealthSettings.get()
    if request.method == 'POST':
        settings.gemini_api_key   = request.POST.get('gemini_api_key', '').strip()
        settings.ai_system_prompt = request.POST.get('ai_system_prompt', '').strip()
        settings.daily_tip        = request.POST.get('daily_tip', '').strip()
        settings.site_tagline     = request.POST.get('site_tagline', '').strip()
        settings.save()
        messages.success(request, 'Settings saved.')
        return redirect('hadmin_settings')
    return render(request, 'health/admin/settings.html', {'settings': settings})
