# Generated by Django 5.1.4 on 2025-01-27 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GameHunt', '0014_delete_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='original_price',
        ),
        migrations.AlterField(
            model_name='game',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
