from django.core.management.base import BaseCommand
from vouchers.models import BusinessCategory


CATEGORIES = [
    ('Restaurant & Food',     '🍽️'),
    ('Beauty & Spa',          '💆'),
    ('Fitness & Wellness',    '💪'),
    ('Shopping & Retail',     '🛍️'),
    ('Entertainment',         '🎭'),
    ('Travel & Hotels',       '✈️'),
    ('Healthcare',            '🏥'),
    ('Education',             '📚'),
    ('Bakery & Sweets',       '🎂'),
    ('Clothing & Fashion',    '👗'),
    ('Electronics',           '📱'),
    ('Home & Decor',          '🏠'),
    ('Supermarket & Grocery', '🛒'),
    ('Automotive',            '🚗'),
    ('Photography & Media',   '📷'),
]


class Command(BaseCommand):
    help = 'Seed default business categories for the voucher platform'

    def handle(self, *args, **options):
        for name, icon in CATEGORIES:
            obj, created = BusinessCategory.objects.get_or_create(
                name=name, defaults={'icon': icon, 'is_active': True}
            )
            if not created and not obj.is_active:
                obj.is_active = True
                obj.save()
            self.stdout.write(f"{'Created' if created else 'OK'}: {name}")
        self.stdout.write(self.style.SUCCESS(
            f"Done. {BusinessCategory.objects.filter(is_active=True).count()} active categories."
        ))
