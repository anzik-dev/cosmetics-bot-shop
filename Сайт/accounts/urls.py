from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/profile/'
    ), name='password_change'),
    path('profile/address/delete/<int:pk>/', views.delete_address, name='delete_address'),  # удаление
]


