from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, signup_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('games/', views.all_games, name='all_games'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # Game details
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),
    
    # Cart and purchases
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:game_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('purchases/', views.purchased_games, name='purchased_games'),

    #search bar
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)