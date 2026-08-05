from django.shortcuts import render

MODULES = [
    {'slug': 'family-stories',      'icon': '📸', 'name': 'Family Stories',        'desc': 'Birthdays, achievements, traditions & celebrations',  'color': '#e11d48', 'soon': False},
    {'slug': 'school-corner',       'icon': '🏫', 'name': 'School Corner',          'desc': 'Events, sports day, science fair & admissions',       'color': '#0a66c2', 'soon': True},
    {'slug': 'student-success',     'icon': '🎓', 'name': 'Student Success',        'desc': 'Academics, sports, art, music & scholarships',        'color': '#7c3aed', 'soon': True},
    {'slug': 'kids-corner',         'icon': '🧒', 'name': 'Kids Corner',            'desc': 'Safe space for children\'s stories & activities',     'color': '#f59e0b', 'soon': True},
    {'slug': 'parenting',           'icon': '👨‍👩‍👧', 'name': 'Parenting',              'desc': 'Tips, advice & family activity ideas',               'color': '#059669', 'soon': True},
    {'slug': 'grandparents-archive','icon': '👴', 'name': 'Grandparents Archive',   'desc': 'Elder stories, memories & community wisdom',          'color': '#92400e', 'soon': True},
    {'slug': 'local-heroes',        'icon': '🦸', 'name': 'Local Heroes',           'desc': 'Celebrate unsung heroes in your community',           'color': '#dc2626', 'soon': True},
    {'slug': 'community-events',    'icon': '📅', 'name': 'Community Events',       'desc': 'Local gatherings, festivals & announcements',         'color': '#0891b2', 'soon': True},
    {'slug': 'volunteer',           'icon': '🤝', 'name': 'Volunteer Activities',   'desc': 'Blood donation, tree plantation & health camps',      'color': '#16a34a', 'soon': True},
    {'slug': 'business-stories',    'icon': '🏪', 'name': 'Business Stories',       'desc': 'Local business journeys — not ads, real stories',     'color': '#ea580c', 'soon': True},
    {'slug': 'hall-of-fame',        'icon': '🏆', 'name': 'Hall of Fame',           'desc': 'Top achievers per pincode — recognised & celebrated', 'color': '#ca8a04', 'soon': True},
    {'slug': 'jobs',                'icon': '💼', 'name': 'Jobs',                   'desc': 'Local employment opportunities near your pincode',    'color': '#0a66c2', 'soon': False},
    {'slug': 'marketplace',         'icon': '🛒', 'name': 'Marketplace',            'desc': 'Buy & sell locally within your community',            'color': '#7c3aed', 'soon': True},
    {'slug': 'community-watch',     'icon': '👁️', 'name': 'Community Watch',        'desc': 'Report, block & keep the community safe',             'color': '#374151', 'soon': True},
    {'slug': 'notifications',       'icon': '🔔', 'name': 'Notifications & Search', 'desc': 'Alerts, reminders & pincode-based search',            'color': '#0891b2', 'soon': True},
]


def hub(request):
    return render(request, 'community/hub.html', {'modules': MODULES})


def module_page(request, slug):
    module = next((m for m in MODULES if m['slug'] == slug), None)
    if not module:
        from django.http import Http404
        raise Http404
    # redirect live modules to their real pages
    if slug == 'jobs':
        from django.shortcuts import redirect
        return redirect('/jobs/')
    if slug == 'family-stories':
        return render(request, 'community/family_stories.html', {'module': module})
    return render(request, 'community/coming_soon.html', {'module': module})
