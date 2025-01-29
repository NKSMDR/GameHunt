# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import JsonResponse

# Local imports
from .models import Game, GameImage, Cart, CartItem, Purchase
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

#gamepage
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


def login_view(request):
    # Get the 'next' parameter from the URL
    next_url = request.GET.get('next', None)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            # If there's a next URL, redirect there, otherwise go home
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    # Pass the next parameter to the template
    return render(request, 'loginpage.html', {'next': next_url})



def signup_view(request):
    # Get the 'next' parameter from the URL
    next_url = request.GET.get('next')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        next_url = request.POST.get('next')  # Get next from POST if it exists
        
        # Validate username
        if not username:
            messages.error(request, 'Username is required.')
            return render(request, 'signup.html', {'next': next_url})
            
        # Validate password length
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'signup.html', {'next': next_url})
            
        if password == confirm_password:
            try:
                # Check if username exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists.')
                    return render(request, 'signup.html', {'next': next_url})
                    
                # Create new user
                user = User.objects.create_user(username=username, password=password)
                # Log the user in immediately after signup
                login(request, user)
                messages.success(request, 'Account created successfully!')
                
                # Redirect to next URL if it exists, otherwise go home
                if next_url:
                    return redirect(next_url)
                return redirect('home')
                
            except Exception as e:
                messages.error(request, 'An error occurred during registration.')
                return render(request, 'signup.html', {'next': next_url})
        else:
            messages.error(request, 'Passwords do not match.')
            
    # For GET request or if we hit an error
    return render(request, 'signup.html', {'next': next_url})

def all_games(request):
    games = Game.objects.all()
    return render(request, 'allgames.html', {'games': games})



@login_required
def cart_view(request):
    try:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total = sum(item.game.price for item in cart.items.all())
        return render(request, "cartpage.html", {
            "cart_items": cart.items.all(),
            "total": total,
            "cart_count": cart.items.count(),
        })
    except Exception as e:
        messages.error(request, "An error occurred while loading your cart.")
        return redirect('home')

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
        messages.success(request, f"{game.name} has been added to your cart.")
    except IntegrityError:
        # The game is already in the cart; optionally display a message
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

# def all_games(request):
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


def all_games(request):
    # Get filter parameters from request
    selected_categories = request.GET.getlist('category')
    selected_sections = request.GET.getlist('section')
    sort_by = request.GET.get('sort')
    search_query = request.GET.get('search')

    # Start with all games
    games = Game.objects.all()

    # Apply category filters
    if selected_categories:
        games = games.filter(category__in=selected_categories)

   
    # Apply search filter
    if search_query:
        games = games.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Apply sorting
    if sort_by == 'price_low':
        games = games.order_by('price')
    elif sort_by == 'price_high':
        games = games.order_by('-price')
    elif sort_by == 'popularity':
        games = games.order_by('-reviews_count')
    elif sort_by == 'rating':
        games = games.order_by('-rating')
    elif sort_by == 'newest':
        games = games.order_by('-release_date')
    else:
        games = games.order_by('-release_date')  # Default sorting

    # Prepare context
    context = {
        'games': games,
        'CATEGORY_CHOICES': Game.CATEGORY_CHOICES,
        'selected_categories': selected_categories,
        'sort_by': sort_by,
        'search_query': search_query,
    }

    return render(request, 'allgames.html', context)




def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)
        
    suggestions = Game.objects.filter(name__icontains=query)[:5].values('name')
    return JsonResponse(list(suggestions), safe=False)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')