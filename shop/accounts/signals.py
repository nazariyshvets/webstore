from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from django.contrib.auth.models import User
from .models import Profile
from base.models import Cart

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
  if created:
    Cart.objects.create(user=instance)

@receiver(post_save, sender=User)
def send_greeting_email(sender, instance, created, **kwargs):
  if created:
    title = "Обліковий запис успішно створено"
    message = f"Акаунт з ім'ям користувача @{instance.username} на сайті InterTech було успішно створено"
    receipient = instance.email

    send_mail(title, message, 'InterTech <noreply@host.com>', [receipient,], fail_silently=False)