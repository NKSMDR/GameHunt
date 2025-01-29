# models.py
from django.db import models
from urllib.parse import urlparse, parse_qs
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from decimal import Decimal

class Game(models.Model):
    SECTION_CHOICE = [
        ('featured', 'Featured'),
        ('trending', 'Trending'),
        ('new', 'New Released'),
        ('free', 'Free Games'),
        ('popular', 'Popular Games')
    ]
    
    CATEGORY_CHOICES = [
        ('ACTION', 'Action'),
        ('RPG', 'RPG'),
        ('SPORTS', 'Sports'),
        ('STRATEGY', 'Strategy'),
        ('RACING', 'Racing'),
        ('HORROR', 'Horror'),
    ]
    
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    image_url = models.CharField(max_length=255)
    video_url = models.URLField()
    section = models.CharField(max_length=10, choices=SECTION_CHOICE, default='featured')
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='ACTION')
    developer = models.CharField(max_length=200, null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    reviews_count = models.IntegerField(default=0)
    discount = models.IntegerField(null=True, blank=True)
    languages = models.CharField(max_length=500, default='English')
    platform = models.CharField(max_length=100, default='PC')
    min_requirements = models.TextField(null=True, blank=True)
    recommended_requirements = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'section')

    def clean(self):
        if Game.objects.filter(name=self.name, section=self.section).exclude(pk=self.pk).exists():
            raise ValidationError(f'The game "{self.name}" is already in the "{self.section}" section.')

    @property
    def final_price(self):
        if self.discount:
            discount_amount = (self.price * Decimal(str(self.discount))) /Decimal('100')
            return self.price - discount_amount
        return self.price
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def video_id(self):
        url_parts = urlparse(self.video_url)
        
        if url_parts.netloc == "www.youtube.com" and url_parts.path.startswith("/embed/"):
            return url_parts.path.split("/")[-1]
        
        elif url_parts.netloc == "www.youtube.com" and url_parts.path == "/watch":
            query = parse_qs(url_parts.query)
            return query.get("v", [None])[0]
        
        elif url_parts.netloc == "youtu.be":
            return url_parts.path[1:]
            
        return None

    @property
    def embed_url(self):
        video_id = self.video_id
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return None

    def __str__(self):
        return self.name

class GameImage(models.Model):
    game = models.ForeignKey(Game, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='game_screenshots/', 
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'gif', 'webp'])],
        help_text="Upload game screenshots. Supported formats: PNG, JPG, JPEG, GIF, WebP"
    )
    is_cover = models.BooleanField(default=False, help_text="Mark as cover image")
    caption = models.CharField(max_length=200, blank=True, null=True, help_text="Optional image caption")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_cover', 'uploaded_at']
        verbose_name = 'Game Image'
        verbose_name_plural = 'Game Images'

    def __str__(self):
        return f"{self.game.name} - {self.caption or 'Screenshot'}"

    def save(self, *args, **kwargs):
        if self.is_cover:
            GameImage.objects.filter(game=self.game, is_cover=True).update(is_cover=False)
        super().save(*args, **kwargs)



from django.contrib.auth.models import User

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")

    def __str__(self):
        return f"Cart({self.user.username})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        # Add this to prevent duplicate games in cart
        unique_together = ('cart', 'game')
        # Add index for better performance
        indexes = [
            models.Index(fields=['cart', 'game']),
        ]

    def get_total_price(self):
        return self.game.price

    def __str__(self):
        return f"{self.game.name}"
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="purchases")
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.game.name}"