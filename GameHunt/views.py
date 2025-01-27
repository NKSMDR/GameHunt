from django.shortcuts import render, get_object_or_404, redirect
from .models import Game, GameImage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
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
# views.py
def login_view(request):
    return render(request, 'loginpage.html')  # Make sure to create login.html with your template
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')  # Redirect to home or dashboard
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'loginpage.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            try:
                User.objects.get(username=username)
                messages.error(request, 'Username already exists.')
            except ObjectDoesNotExist:
                User.objects.create_user(username=username, password=password)
                messages.success(request, 'Account created successfully!')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'signup.html')

def all_games(request):
    games = Game.objects.all()
    return render(request, 'allgames.html', {'games': games})