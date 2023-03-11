from django.dispatch import receiver
from django.core.mail import send_mail
from django import dispatch

from .models import SoldCommodity

commodities_purchased = dispatch.Signal(["customer", "commodities"])

@receiver(commodities_purchased, sender=SoldCommodity)
def send_email_about_purchase(sender, customer, commodities, **kwargs):
  title = "Покупку успішно здійснено"
  message = f"Покупку на сайті InterTech з акаунта @{customer.username} було успішно здійснено\n"
  message += "Куплені товари:\n"
  for commodity in commodities:
    message += f"{commodity.title} ({commodity.price}₴)\n" 
  receipient = customer.email

  send_mail(title, message, 'InterTech <noreply@host.com>', [receipient,], fail_silently=False)