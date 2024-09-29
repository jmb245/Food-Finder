from django.db import models
from django.contrib.auth.models import User
from .utils import geocode_address

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    cuisine_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    rating = models.FloatField(default=0)  # Default rating set to 0
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    description = models.TextField(default="No description available")  # Default description
    place_id = models.CharField(max_length=255, unique=True, default="")  # Default empty string for place_id

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            from django.conf import settings
            lat, lng = geocode_address(self.location, settings.GOOGLE_API_KEY)
            if lat and lng:
                self.latitude = lat
                self.longitude = lng
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.restaurant.name}"
