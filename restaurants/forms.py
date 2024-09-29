from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RestaurantSearchForm(forms.Form):
    name = forms.CharField(label='Search', max_length=100, required=False)
    cuisine = forms.CharField(label='Cuisine Type', max_length=50, required=False)
    location = forms.CharField(label='Location', max_length=100, required=False)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Include email if needed

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    pass