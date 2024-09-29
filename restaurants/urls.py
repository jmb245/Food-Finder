# urls.py
from django.urls import path
from . import views
from .views import map_view, login_view, logout_view, signup, restaurant_detail_view, favorites_view

urlpatterns = [
    path('map/', map_view, name='map_view'),  # Restaurant map view
    path('', views.map_view, name='map_view'),  # Default route to map view
    path('login/', login_view, name='login'),  # Login view
    path('logout/', logout_view, name='logout'),  # Logout view
    path('signup/', signup, name='signup'),  # Signup view
    path('restaurant/<str:place_id>/', views.restaurant_detail_view, name='restaurant_detail'),
    path('restaurant/<int:restaurant_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites_view, name='favorites'),
]
