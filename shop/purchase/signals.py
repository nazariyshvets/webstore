from django.dispatch import receiver
from django.core.mail import send_mail
from django import dispatch
from django.conf import settings

from .models import Payment

payment_done = dispatch.Signal(["customer", "payment_id", "purchased_commodities"])


@receiver(payment_done, sender=Payment)
def send_payment_email(sender, customer, payment_id, purchased_commodities, **kwargs):
  title = "Покупку успішно здійснено"
  message = f"Покупку на сайті InterTech з акаунта @{customer.username} було успішно здійснено\n"
  message += f"ID транзакції: {payment_id}\n"
  message += "Куплені товари:\n"
  amount = 0

  for item in purchased_commodities:
    message += f"{item.commodity.title} ({item.quantity} шт) - {item.commodity.price * item.quantity}₴\n"
    amount += item.commodity.price * item.quantity

  message += f"Разом: {amount}₴"
  receipient = customer.email

  send_mail(title, message, settings.DEFAULT_FROM_EMAIL,
            [receipient,], fail_silently=True)
