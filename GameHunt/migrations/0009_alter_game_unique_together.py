# Generated by Django 5.1.4 on 2025-01-11 07:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GameHunt', '0008_alter_game_section'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='game',
            unique_together={('name', 'section')},
        ),
    ]
