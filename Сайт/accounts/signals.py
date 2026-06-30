from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import BonusCard

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_bonus_card(sender, instance, created, **kwargs):
    if created:
        BonusCard.objects.create(user=instance, discount_percent=10, bonus_points=0)