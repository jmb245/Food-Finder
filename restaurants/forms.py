from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class RestaurantSearchForm(forms.Form):
    name = forms.CharField(label='Search', max_length=100, required=False)
    cuisine = forms.CharField(label='Cuisine Type', max_length=50, required=False)
    location = forms.CharField(label='Location', max_length=100, required=False)

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="Username",  # Visible label for the form
        widget=forms.TextInput(attrs={'placeholder': 'Create a username'})
    )
    password1 = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

class LoginForm(AuthenticationForm):
    pass