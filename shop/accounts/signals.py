from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from base.models import Cart
from .models import Profile


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
    subject = "Обліковий запис успішно створено"
    html_message = render_to_string(
        "accounts/greetingEmail.html", {"user": instance})
    plain_message = strip_tags(html_message)
    recipient = instance.email

    try:
      send_mail(
          subject,
          plain_message,
          settings.DEFAULT_FROM_EMAIL,
          [recipient,],
          fail_silently=False,
          html_message=html_message,
      )
    except Exception as e:
      print(f"Виникла помилка під час відправлення email: {e}")
