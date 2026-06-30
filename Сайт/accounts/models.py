from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()
    class Meta:
        verbose_name_plural = "Пользователи"
    
    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or None

    def __str__(self):
        return self.get_full_name()

class BonusCard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    discount_percent = models.IntegerField(default=10, verbose_name='Процент скидки')
    bonus_points = models.FloatField(default=0, verbose_name='Количество бонусов')
    class Meta:
        verbose_name_plural = "Бонусные карты"

    def __str__(self):
        return f"{getattr(self.user, 'email', str(self.user))} - {self.bonus_points} бонусов"
    
class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,verbose_name='Пользователь')
    city = models.CharField(max_length=100,verbose_name='Город')
    address = models.CharField(max_length=100,verbose_name='Адрес')
    class Meta:
        verbose_name_plural = "Адреса"
    def __str__(self):
        return f"{self.address}, {self.city}"


# Create your models here.
