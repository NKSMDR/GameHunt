from django.db import models
from urllib.parse import urlparse, parse_qs
from django.core.exceptions import ValidationError

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
    
    # Existing fields
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.CharField(max_length=255)
    video_url = models.URLField()
    section = models.CharField(max_length=10, choices=SECTION_CHOICE, default='featured')
    
    # New fields for game detail page
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='ACTION')
    developer = models.CharField(max_length=200, null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    reviews_count = models.IntegerField(default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
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