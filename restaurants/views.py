import requests
from django.conf import settings
from .models import Restaurant, Favorite
from .utils import haversine, calculate_distance
from geopy.geocoders import Nominatim
from .services.google_places import search_restaurants
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def geocode_address(address, api_key):
    """Use Google Geocoding API to get latitude and longitude for an address."""
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        return None, None


def map_view(request):
    name = request.GET.get('name', '')
    cuisine_type = request.GET.get('cuisine_type', '')
    location = request.GET.get('location', '')
    distance_range = request.GET.get('distance_range', 50)  # Default to max 50 km
    rating_range = request.GET.get('rating_range', 0)  # Default rating filter to 0 (show all)

    # Handle user's location
    if location:
        geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={settings.GOOGLE_API_KEY}'
        geocode_response = requests.get(geocode_url).json()
        if geocode_response['status'] == 'OK':
            user_lat = geocode_response['results'][0]['geometry']['location']['lat']
            user_lon = geocode_response['results'][0]['geometry']['location']['lng']
        else:
            user_lat, user_lon = None, None
    else:
        user_lat, user_lon = None, None

    # Default location to Atlanta if user location is unavailable
    if not user_lat or not user_lon:
        user_lat, user_lon = 33.7490, -84.3880  # Default to Atlanta

    # API call to get nearby restaurants using Google Places API
    places_url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={user_lat},{user_lon}&radius=50000&type=restaurant&key={settings.GOOGLE_API_KEY}'

    if name:
        places_url += f"&keyword={name}"
    if cuisine_type:
        places_url += f"&keyword={cuisine_type}"

    response = requests.get(places_url)
    places_data = response.json()

    restaurants = places_data.get('results', [])

    # Filter restaurants by distance and rating range
    filtered_restaurants = [
        restaurant for restaurant in restaurants
        if restaurant.get('rating', 0) >= float(rating_range)
        and calculate_distance(user_lat, user_lon, restaurant['geometry']['location']['lat'], restaurant['geometry']['location']['lng']) <= float(distance_range)
    ]

    context = {
        'restaurants': filtered_restaurants,
        'google_maps_api_key': settings.GOOGLE_API_KEY,
        'user_lat': user_lat,
        'user_lon': user_lon,
    }

    return render(request, 'restaurants/map.html', context)
def home_view(request):
    # Redirect to map or any other page you want as the home page
    return redirect('map_view')  # Redirect to the restaurant map page

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'restaurants/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout


# Signup View

def password_reset_form_view(request):
    # Handle password reset form logic
    pass

def password_reset_done_view(request):
    # Handle post password reset logic
    pass


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user to the database
            login(request, user)  # Log in the user after signup
            return redirect('home')  # Redirect to the homepage or any other page
    else:
        form = UserCreationForm()

    return render(request, 'restaurants/signup.html', {'form': form})


def restaurant_detail_view(request, place_id):
    """Fetch restaurant details from Google Places API."""
    if not request.user.is_authenticated:
        return render(request, 'restaurants/restaurant_detail.html', {'login_required': True})

    # Google Places Details API URL
    details_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={settings.GOOGLE_API_KEY}'
    response = requests.get(details_url)
    restaurant_data = response.json().get('result', {})

    # Handle missing 'geometry' data gracefully
    geometry = restaurant_data.get('geometry')
    if geometry:
        latitude = geometry['location']['lat']
        longitude = geometry['location']['lng']
    else:
        latitude = 33.7490  # Fallback (Atlanta's coordinates)
        longitude = -84.3880

    # Check if the restaurant exists in the local database by place_id
    restaurant_db, created = Restaurant.objects.get_or_create(
        place_id=place_id,  # Assuming you've added a place_id field to your Restaurant model
        defaults={
            'name': restaurant_data.get('name', 'No Name'),
            'location': restaurant_data.get('formatted_address', 'No Address'),
            'cuisine_type': 'Unknown',
            'latitude': latitude,
            'longitude': longitude,
            'rating': restaurant_data.get('rating', 0),
            'description': restaurant_data.get('description', 'No description available')
        }
    )

    # Check if the restaurant is already in the user's favorites
    is_favorite = Favorite.objects.filter(user=request.user, restaurant=restaurant_db).exists()

    # Prepare context data
    context = {
        'restaurant': restaurant_data,
        'restaurant_db': restaurant_db,
        'is_favorite': is_favorite,
        'user_lat': request.GET.get('user_lat', None),
        'user_lon': request.GET.get('user_lon', None),
        'google_maps_api_key': settings.GOOGLE_API_KEY,
        'latitude': latitude,
        'longitude': longitude,
    }

    return render(request, 'restaurants/restaurant_detail.html', context)


def favorites_view(request):
    if not request.user.is_authenticated:
        # Show message if not logged in
        return render(request, 'restaurants/favorites.html', {'login_required': True})
    else:
        # Fetch the user's favorites
        favorites = Favorite.objects.filter(user=request.user).select_related('restaurant')
        return render(request, 'restaurants/favorites.html', {'favorites': favorites, 'login_required': False})


@login_required
def toggle_favorite(request, restaurant_id):
    """Add or remove restaurant from favorites."""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)

    if not created:
        # If the favorite already exists, remove it
        favorite.delete()

    # Redirect back to the restaurant detail page
    return redirect('restaurant_detail', place_id=restaurant.place_id)





def restaurant_detail(request, place_id):  # <-- Make sure to accept place_id here
    # Replace this line with how you're getting the restaurant data. For example, using Google Places API or your database.
    restaurant = get_object_or_404(Restaurant, place_id=place_id)  # <-- Change this according to your model or API
    return render(request, 'restaurants/restaurant_details.html', {'restaurant': restaurant})




