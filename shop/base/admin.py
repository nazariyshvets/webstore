from django.contrib import admin
from . import models

admin.site.register(models.Category)
admin.site.register(models.Commodity)
admin.site.register(models.CommodityEvaluation)
admin.site.register(models.Comment)
admin.site.register(models.Cart)
admin.site.register(models.CommodityInCart)
admin.site.register(models.Manufacturer)
admin.site.register(models.SoldCommodity)
