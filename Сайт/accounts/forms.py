from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser
from .models import Address


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'email': 'Электронная почта',
        'password1': 'Пароль',
        'password2': 'Повторите пароль',
    }

class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('city', 'address')