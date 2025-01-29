# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
import requests
from .models import Game, GameImage
from decimal import Decimal
from django.utils.html import format_html

class GameImageInline(admin.TabularInline):
    model = GameImage
    extra = 3
    fields = ('image', 'caption', 'is_cover')
    readonly_fields = ('uploaded_at',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    @admin.display(description='Game')
    def name_with_preview(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<img src="{}" style="width: 30px; height: 30px; margin-right: 10px; object-fit: cover; border-radius: 4px;">'
            '{}'
            '</div>',
            obj.image_url, obj.name
        )

    @admin.display(description='Price')
    def formatted_price(self, obj):
        if obj.discount:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">${}</span>'
                '<br>'
                '<span style="color: #28a745;">${}</span>',
                obj.price,
                obj.final_price
            )
        return format_html('${}', obj.price)

    @admin.display(description='Rating')
    def rating_display(self, obj):
        if obj.rating:
            stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
            return format_html(
                '<span style="color: #ffc107;">{}</span>'
                '<br>'
                '<small>({} reviews)</small>',
                stars, obj.reviews_count
            )
        return '-'

    @admin.display(description='Release Date')
    def formatted_release_date(self, obj):
        if obj.release_date:
            if obj.release_date > timezone.now().date():
                return format_html(
                    '<span style="color: #dc3545;">Coming {}</span>',
                    obj.release_date.strftime('%b %d, %Y')
                )
            return obj.release_date.strftime('%b %d, %Y')
        return '-'

    @admin.display(description='Video')
    def video_preview(self, obj):
        if obj.video_id:
            return format_html(
                '<a href="{}" target="_blank" class="button" '
                'style="background-color: #007bff; color: white; padding: 5px 10px; '
                'border-radius: 4px; text-decoration: none;">'
                '<i class="fas fa-play"></i> Preview</a>',
                obj.video_url
            )
        return '-'

    def video_preview_field(self, obj):
        if obj.video_id:
            return format_html(
                '<div style="max-width: 560px;">'
                '<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">'
                '<iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" '
                'src="https://www.youtube.com/embed/{}" frameborder="0" allowfullscreen></iframe>'
                '</div></div>',
                obj.video_id
            )
        return 'No video available'

    list_display = (
        'name_with_preview',
        'formatted_price',
        'section',
        'category',
        'developer',
        'rating_display',
        'formatted_release_date',
        'video_preview',
        'image_count'
    )

    list_filter = (
        'section',
        'category',
        'platform',
        'release_date'
    )

    search_fields = (
        'name',
        'developer',
        'publisher'
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'description',
                'section',
                'category'
            )
        }),
        ('Media', {
            'fields': (
                'image_url',
                'video_url',
                'video_preview_field'
            )
        }),
        ('Pricing', {
            'fields': (
                'price',
                'discount',
            ),
            'description': 'Enter the base price and optional discount percentage (0-100)'
        }),
        ('Game Details', {
            'fields': (
                'developer',
                'publisher',
                'release_date',
                'platform',
                'languages'
            )
        }),
        ('Ratings & Reviews', {
            'fields': (
                'rating',
                'reviews_count'
            )
        }),
        ('System Requirements', {
            'classes': ('collapse',),
            'fields': (
                'min_requirements',
                'recommended_requirements'
            )
        })
    )

    readonly_fields = ['video_preview_field']
    ordering = ('name', 'section')
    date_hierarchy = 'release_date'
    list_per_page = 25
    list_editable = ('section',)
    list_display_links = ('name_with_preview',)
    inlines = [GameImageInline]

    actions = ['mark_as_featured', 'clear_discount', 'verify_media_urls']

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Image Count'

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(section='featured')
        self.message_user(request, f'{updated} games marked as featured.')
    mark_as_featured.short_description = "Mark selected games as featured"

    def clear_discount(self, request, queryset):
        updated = queryset.update(discount=None)
        self.message_user(request, f'Cleared discounts for {updated} games.')
    clear_discount.short_description = "Clear discounts"

    def verify_media_urls(self, request, queryset):
        success = 0
        failed = []
        for game in queryset:
            try:
                img_response = requests.head(game.image_url, timeout=5)
                if img_response.status_code != 200:
                    failed.append(f"{game.name} (Invalid image URL)")
                    continue
                
                if game.video_id is None:
                    failed.append(f"{game.name} (Invalid video URL)")
                    continue 
                
                success += 1
            except requests.RequestException:
                failed.append(f"{game.name} (Connection error)")
        
        if success:
            self.message_user(request, f'Successfully verified {success} games.')
        if failed:
            self.message_user(request, f'Failed to verify: {", ".join(failed)}', level=messages.ERROR)
    verify_media_urls.short_description = "Verify media URLs"

@admin.register(GameImage)
class GameImageAdmin(admin.ModelAdmin):
    list_display = ('game', 'is_cover', 'uploaded_at')
    list_filter = ('game', 'is_cover')

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_staff', 'is_active')
    exclude = ('password', 'last_login')
    readonly_fields = ('date_joined',)

from django.contrib import admin
from .models import Game, Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user",)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "game")
