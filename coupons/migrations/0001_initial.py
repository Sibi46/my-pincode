from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CouponCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_number', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RedemptionCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_number', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Salesman',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='salesman_profile', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_salesmen', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('pincode', models.CharField(max_length=10)),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('salesman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shops', to='coupons.salesman')),
            ],
        ),
        migrations.CreateModel(
            name='CouponBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('start_number', models.PositiveIntegerField()),
                ('end_number', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batches', to='coupons.shop')),
                ('salesman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batches', to='coupons.salesman')),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('number', models.PositiveIntegerField(unique=True)),
                ('status', models.CharField(choices=[('available', 'Available'), ('activated', 'Activated'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='available', max_length=20)),
                ('activated_at', models.DateTimeField(blank=True, null=True)),
                ('points_awarded', models.PositiveIntegerField(blank=True, null=True)),
                ('is_surprise_gift', models.BooleanField(default=False)),
                ('surprise_gift_name', models.CharField(blank=True, max_length=200)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to='coupons.couponbatch')),
                ('activated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='activated_coupons', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SpinWheelSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=100)),
                ('points', models.PositiveIntegerField(default=0)),
                ('is_surprise', models.BooleanField(default=False)),
                ('surprise_gift_name', models.CharField(blank=True, max_length=200)),
                ('probability', models.DecimalField(decimal_places=2, max_digits=5)),
                ('color', models.CharField(default='#6366f1', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('business_name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('points_required', models.PositiveIntegerField()),
                ('quantity_limit', models.PositiveIntegerField(blank=True, null=True)),
                ('quantity_redeemed', models.PositiveIntegerField(default=0)),
                ('expiry', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PointsWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.PositiveIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='opc_wallet', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Redemption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=25, unique=True)),
                ('points_used', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('redeemed', 'Redeemed'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('verified_by_shop', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('redeemed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opc_redemptions', to=settings.AUTH_USER_MODEL)),
                ('reward', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='redemptions', to='coupons.reward')),
            ],
        ),
        migrations.CreateModel(
            name='PointsTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('credit', 'Credit'), ('debit', 'Debit')], max_length=10)),
                ('amount', models.PositiveIntegerField()),
                ('balance_after', models.PositiveIntegerField()),
                ('description', models.CharField(max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='coupons.pointswallet')),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='coupons.coupon')),
                ('redemption', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='coupons.redemption')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
