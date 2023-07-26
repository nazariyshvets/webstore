from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    title = models.CharField(max_length=100, primary_key=True)
    picture = models.URLField(
        default="https://jphxdckjtcxleelhjfhy.supabase.co/storage/v1/object/public/images/default.png")

    def __str__(self):
        return self.title


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


class Commodity(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    rating = models.FloatField(default=3)
    adding_date = models.DateField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    picture = models.URLField(
        default="https://jphxdckjtcxleelhjfhy.supabase.co/storage/v1/object/public/images/default.png")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-rating"]

    def __str__(self):
        return self.title


class CommodityEvaluation(models.Model):
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    value = models.PositiveIntegerField(default=3)


class Comment(models.Model):
    text = models.TextField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    sending_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sending_datetime"]


class Cart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.user.username


class CommodityInCart(models.Model):
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)


class SoldCommodity(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    category = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    selling_date = models.DateField(auto_now_add=True)
    username = models.CharField(max_length=100)

    class Meta:
        permissions = (("can_form_report", "can form report"),)

    def __str__(self):
        return self.title
