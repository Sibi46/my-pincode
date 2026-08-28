from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0035_merge_0034_alter_user_user_type_0034_localoffer'),
    ]

    operations = [
        migrations.AddField(
            model_name='localoffer',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
