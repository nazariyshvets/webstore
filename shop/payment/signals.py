from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django import dispatch
from django.conf import settings

from .models import Payment

payment_done = dispatch.Signal(
    ["customer", "payment_id", "purchased_commodities"])


@receiver(payment_done, sender=Payment)
def send_payment_email(sender, customer, payment_id, purchased_commodities, **kwargs):
  subject = "Платіж успішно здійснено"
  html_message = render_to_string("payment/paymentEmail.html", {
                                  "payment_id": payment_id, "purchased_commodities": purchased_commodities, "total_amount": sum(item.commodity.price * item.quantity for item in purchased_commodities)})
  plain_message = strip_tags(html_message)
  recipient = customer.email

  try:
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient, ],
        fail_silently=False,
        html_message=html_message,
    )
  except Exception as e:
    print(f"Виникла помилка під час відправлення email: {e}")
