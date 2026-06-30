from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .forms import CustomUserEditForm, AddressForm
from .models import BonusCard, Address



def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')  # или куда ты хочешь
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user = request.user

    # ----------------- бонусная карточка -----------------
    bonus_card = None
    try:
        bonus_card = BonusCard.objects.get(user=user)
    except BonusCard.DoesNotExist:
        bonus_card = None

    # ----------------- адреса -----------------
    user_addresses = Address.objects.filter(user=user)

    # ----------------- добавление нового адреса -----------------
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = user
            address.save()
            return redirect('profile')
    else:
        form = AddressForm()

    return render(request, 'accounts/profile.html', {
        'user': user,
        'bonus_card': bonus_card,
        'address': user_addresses,  # список адресов пользователя
        'form': form,               # форма добавления нового адреса
    })


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # или куда хочешь
    else:
        form = CustomUserEditForm(instance=user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


    

@login_required
def delete_address(request, pk):
    try:
        adr = Address.objects.get(pk=pk, user=request.user)
        adr.delete()
    except Address.DoesNotExist:
        pass
    return redirect('profile')
