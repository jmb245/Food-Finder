from django.contrib import admin
from django.urls import include, path
from restaurants import views as restaurant_views

urlpatterns = [
    path('', restaurant_views.home_view, name='home'),  # Default home view
    path('admin/', admin.site.urls),
    path('restaurants/', include('restaurants.urls')),
    path('login/', restaurant_views.login_view, name='login'),
    path('signup/', restaurant_views.signup, name='signup'),
    path('logout/', restaurant_views.logout_view, name='logout'),
    path('password-reset/', restaurant_views.password_reset_form_view, name='password_reset_form'),
    path('password-reset/done/', restaurant_views.password_reset_done_view, name='password_reset_done'),
]