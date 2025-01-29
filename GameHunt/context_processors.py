from .models import Game

def category_choices(request):
    return {
        'CATEGORY_CHOICES': Game.CATEGORY_CHOICES
    }