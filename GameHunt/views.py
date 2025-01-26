from django.shortcuts import render, get_object_or_404
from .models import Game, GameImage

def home(request):
    featured_games = Game.objects.filter(section='featured')
    trending_games = Game.objects.filter(section='trending')
    new_released_games = Game.objects.filter(section='new')
    free_games = Game.objects.filter(section='free')
    popular_games = Game.objects.filter(section='popular')
    
    context = {
        'featured_games': featured_games,
        'trending_games': trending_games,
        'new_released_games': new_released_games,
        'free_games': free_games,
        'popular_games': popular_games,
    }
    return render(request, 'home.html', context)

def game_detail(request, game_id):
    # Get the main game
    game = get_object_or_404(Game, id=game_id)
     
    # Get related games (games in the same section)
    related_games = Game.objects.filter(
        section=game.section
    ).exclude(id=game_id)[:4]  # Limit to 4 related games
    
    # Get all images for the game, with cover image first
    game_images = game.images.all()
    
    context = {
        'game': game,
        'game_images': game_images,
        'related_games': related_games,
    }
    return render(request, 'gamepage.html', context)

def cart_view(request):
    # Optional: Add cart logic if needed
    return render(request, 'cartpage.html')