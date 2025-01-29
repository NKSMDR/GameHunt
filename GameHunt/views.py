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

from .models import Cart, CartItem, Game,Purchase
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    total = sum(item.game.price for item in cart.items.all())
    return render(request, "cartpage.html", {
        "cart_items": cart.items.all(),
        "total": total,
        "cart_count": cart.items.count(),
    })

def user_has_purchased_game(user, game):
    return Purchase.objects.filter(user=user, game=game).exists()

@login_required
def add_to_cart(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the game is already purchased
    if user_has_purchased_game(request.user, game):  # Implement this function as needed
        messages.error(request, f"You already own {game.name}.")
        return redirect("cart")

    # Check if the game is already in the cart
    try:
        CartItem.objects.create(cart=cart, game=game)
    except IntegrityError:
        # The game is already in the cart; optionally display a message
        from django.contrib import messages
        messages.info(request, f"{game.name} is already in your cart.")
    
    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect("cart")


@login_required
def purchased_games(request):
    purchases = Purchase.objects.filter(user=request.user)
    return render(request, "purchased_games.html", {"purchases": purchases})

#for all games
from django.shortcuts import render
from django.db.models import Q
from .models import Game

def all_games(request):
    # Get filter parameters from request
    category = request.GET.getlist('category')
    section = request.GET.getlist('section')
    sort_by = request.GET.get('sort')
    search_query = request.GET.get('search')

    # Start with all games
    games = Game.objects.all()

    # Apply filters
    if category:
        games = games.filter(category__in=category)
    if section:
        games = games.filter(section__in=section)
    if search_query:
        games = games.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Apply sorting
    if sort_by == 'price':
        games = games.order_by('price')
    elif sort_by == 'popularity':
        games = games.order_by('-reviews_count')
    elif sort_by == 'rating':
        games = games.order_by('-rating')
    else:
        games = games.order_by('-release_date')  # Default sorting

    # Prepare context
    context = {
        'games': games,
        'categories': Game.CATEGORY_CHOICES,
        'sections': Game.SECTION_CHOICE,
        'selected_categories': category,
        'selected_sections': section,
        'sort_by': sort_by,
    }

    return render(request, 'allgames.html', context)
def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')