from django.contrib import admin
from . import models

admin.site.register(models.Payment)
admin.site.register(models.PurchasedCommodity)
admin.site.register(models.Replenishment)
