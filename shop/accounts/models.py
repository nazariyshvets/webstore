from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Profile(models.Model):
  user = models.OneToOneField(
      User, on_delete=models.CASCADE, primary_key=True)
  balance = models.DecimalField(
      max_digits=9, decimal_places=2, default=Decimal(0.0))
  bonuses = models.DecimalField(
      max_digits=9, decimal_places=2, default=Decimal(0.0))

  def __str__(self):
    return self.user.username
