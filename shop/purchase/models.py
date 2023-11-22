from django.db import models
from django.contrib.auth.models import User
from base.models import Commodity


class Payment(models.Model):
  order_id = models.CharField(max_length=255, primary_key=True)
  customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  timestamp = models.DateTimeField(auto_now_add=True)

  class Meta:
    permissions = (("can_form_report", "can form report"),)

  def __str__(self):
    return self.order_id


class PurchasedCommodity(models.Model):
  payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
  commodity = models.ForeignKey(
      Commodity, on_delete=models.SET_NULL, null=True)
  quantity = models.PositiveIntegerField()
