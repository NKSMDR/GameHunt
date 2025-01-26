from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name='home'),  # Changed from game_list to home to match your template
    path('game/<int:game_id>/', views.game_detail, name='game_detail'),  # New URL pattern for game details
    path('cart/', views.cart_view, name='cart'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)