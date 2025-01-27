from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, signup_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),  # Changed from game_list to home to match your template
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),  # New URL pattern for game details
    path('cart/', views.cart_view, name='cart'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('games/', views.all_games, name='all_games'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)