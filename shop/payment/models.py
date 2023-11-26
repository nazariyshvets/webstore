from django.db import models
from django.contrib.auth.models import User
from base.models import Commodity


class Payment(models.Model):
  payment_id = models.PositiveBigIntegerField(primary_key=True)
  customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  class Meta:
    permissions = (("can_form_report", "can form report"),)

  def __str__(self):
    return str(self.payment_id)


class PurchasedCommodity(models.Model):
  payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
  commodity = models.ForeignKey(
      Commodity, on_delete=models.SET_NULL, null=True)
  quantity = models.PositiveIntegerField()


class Replenishment(models.Model):
  payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True)
  amount = models.DecimalField(max_digits=9, decimal_places=2)
