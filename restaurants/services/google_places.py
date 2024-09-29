import requests
from django.conf import settings

def search_restaurants(location, radius=5000, keyword='restaurant'):
    api_key = settings.GOOGLE_API_KEY
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': location,
        'radius': radius,
        'keyword': keyword,
        'key': api_key
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
