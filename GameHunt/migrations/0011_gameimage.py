# Generated by Django 5.1.4 on 2025-01-26 04:12

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GameHunt', '0010_game_category_game_description_game_developer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Upload game screenshots. Supported formats: PNG, JPG, JPEG, GIF, WebP', upload_to='game_screenshots/', validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg', 'gif', 'webp'])])),
                ('is_cover', models.BooleanField(default=False, help_text='Mark as cover image')),
                ('caption', models.CharField(blank=True, help_text='Optional image caption', max_length=200, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='GameHunt.game')),
            ],
            options={
                'verbose_name': 'Game Image',
                'verbose_name_plural': 'Game Images',
                'ordering': ['-is_cover', 'uploaded_at'],
            },
        ),
    ]