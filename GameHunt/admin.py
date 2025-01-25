from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
import requests
from .models import Game
from decimal import Decimal

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'name_with_preview',
        'formatted_price',
        'section',
        'category',
        'developer',
        'rating_display',
        'formatted_release_date',
        'video_preview'
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
                'video_preview_field'  # Read-only field for preview
            )
        }),
        ('Pricing', {
            'fields': (
                'price',
                'original_price',
                'discount'
            ),
            'description': 'Set original price and discount, the sale price will be calculated automatically.'
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

    readonly_fields = ('video_preview_field',)
    ordering = ('name', 'section')
    date_hierarchy = 'release_date'
    list_per_page = 25
    list_editable = ('section',)
    list_display_links = ('name_with_preview',)

    # Custom Actions
    actions = ['mark_as_featured', 'clear_discount', 'verify_media_urls']

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(section='featured')
        self.message_user(request, f'{updated} games marked as featured.')
    mark_as_featured.short_description = "Mark selected games as featured"

    def clear_discount(self, request, queryset):
        updated = queryset.update(discount=None, original_price=None)
        self.message_user(request, f'Cleared discounts for {updated} games.')
    clear_discount.short_description = "Clear discounts"

    def verify_media_urls(self, request, queryset):
        success = 0
        failed = []
        for game in queryset:
            try:
                # Verify image URL
                img_response = requests.head(game.image_url, timeout=5)
                if img_response.status_code != 200:
                    failed.append(f"{game.name} (Invalid image URL)")
                    continue
                
                # Verify video URL exists
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

    # Custom display methods
    def name_with_preview(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<img src="{}" style="width: 30px; height: 30px; margin-right: 10px; object-fit: cover; border-radius: 4px;">'
            '{}'
            '</div>',
            obj.image_url, obj.name
        )
    name_with_preview.short_description = 'Game'

    def formatted_price(self, obj):
        if obj.discount:
            original_price_str = f"{obj.original_price:.2f}"
            discounted_price_str = f"{obj.price:.2f}"
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">${}</span>'
                '<br>'
                '<span style="color: #28a745;">${}</span>',
                original_price_str,
                discounted_price_str
            )
        return f"${obj.price:.2f}"
    formatted_price.short_description = 'Price'

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
    rating_display.short_description = 'Rating'

    def formatted_release_date(self, obj):
        if obj.release_date:
            if obj.release_date > timezone.now().date():
                return format_html(
                    '<span style="color: #dc3545;">Coming {}</span>',
                    obj.release_date.strftime('%b %d, %Y')
                )
            return obj.release_date.strftime('%b %d, %Y')
        return '-'
    formatted_release_date.short_description = 'Release Date'

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
    video_preview.short_description = 'Video'

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
    video_preview_field.short_description = 'Video Preview'

    # Custom save validation
    def save_model(self, request, obj, form, change):
        if obj.discount and not obj.original_price:
            obj.original_price = obj.price
        if obj.original_price and obj.discount:
            discount_decimal = Decimal(obj.discount) / Decimal(100)
            multiplier = Decimal(1) - discount_decimal
            obj.price = obj.original_price * multiplier
        
        try:
            super().save_model(request, obj, form, change)
            self.message_user(request, f'Successfully saved {obj.name}')
        except Exception as e:
            self.message_user(request, f'Error saving {obj.name}: {str(e)}', level=messages.ERROR)

    class Media:
        css = {
            'all': ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css']
        } 