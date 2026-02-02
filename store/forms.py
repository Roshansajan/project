from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']


# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control rounded-0', 
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control rounded-0', 
        'placeholder': 'Password'
    }))

# Registration Form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control rounded-0', 
        'placeholder': 'Email Address'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control rounded-0', 
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control rounded-0', 
        'placeholder': 'Last Name'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control rounded-0'})