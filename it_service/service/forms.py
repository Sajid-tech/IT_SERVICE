from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Service, Subscription

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'payment_terms', 'price', 'package', 'tax', 'image', 'active']

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['address']
#builtin form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('username','email','password1','password2')    # here filed are tupe
