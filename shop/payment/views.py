from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.datetime_safe import datetime
from uuid import uuid4
from decimal import Decimal

from base.models import Commodity, CommodityInCart, Cart
from accounts.models import Profile
from .liqpay.liqpay3 import LiqPay
from .models import Payment, PurchasedCommodity, Replenishment
from .forms import ReportForm, ReplenishmentForm
from .decorators import retry_decorator
from .signals import payment_done


@method_decorator([login_required, require_POST], name="dispatch")
class PurchaseView(TemplateView):
  template_name = "payment/pay.html"

  def post(self, request, *args, **kwargs):
    try:
      ids_str = request.POST.get("ids", "")
      ids = [int(id) for id in ids_str.split(",")]
      quantities_str = request.POST.get("quantities", "")
      quantities = [int(quantity) for quantity in quantities_str.split(",")]
      quantities_dict = dict(zip(ids, quantities))
      commodities = Commodity.objects.filter(pk__in=ids)
      description = ""
      amount = 0

      for commodity in commodities:
        quantity = quantities_dict.get(commodity.pk, 0)
        description += f"{commodity.title} ({quantity} шт) - {commodity.price * quantity}₴\n"
        amount += commodity.price * quantity

        if commodity.quantity < quantity:
          messages.error(
              request, f"Недостатньо товару для {commodity.title}. Доступна кількість: {commodity.quantity} шт")
          return redirect(reverse("base:cart"))

      # Check whether the user has enough money to buy commodities
      user_balance = request.user.profile.balance
      if user_balance < amount:
        messages.error(
            request, f"Недостатній баланс для покупки. Доступний баланс: {user_balance}₴")
        return redirect(reverse("base:cart"))

      liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
      params = {
          "action": "pay",
          "amount": str(round(amount, 2)),
          "currency": "UAH",
          "description": description,
          "order_id": str(uuid4()),
          "version": "3",
          "sandbox": 1,  # sandbox mode, set to 1 to enable it
          # url to callback view
          "server_url": "https://webstore-eta.vercel.app/purchase-callback/",
          "info": f"{request.user.id};{ids_str};{quantities_str}"
      }
      signature = liqpay.cnb_signature(params)
      data = liqpay.cnb_data(params)
      return render(request, self.template_name, {"signature": signature, "data": data, "title": "Покупка"})
    except Exception as e:
      messages.error(request, f"Виникла помилка: {str(e)}")
      return redirect(reverse("base:cart"))


@method_decorator([require_POST, csrf_exempt, retry_decorator], name="dispatch")
class PurchaseCallbackView(View):
  def post(self, request, *args, **kwargs):
    liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
    data = request.POST.get("data")
    signature = request.POST.get("signature")
    sign = liqpay.str_to_sign(
        settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
    if sign == signature:
      response = liqpay.decode_data_from_str(data)

      if response.get("status") == "sandbox":
        payment_id = int(response.get("payment_id"))
        info = response.get("info").split(";")
        user_id = int(info[0])
        ids = [int(id) for id in info[1].split(",")]
        quantities = [int(quantity)
                      for quantity in info[2].split(",")]
        quantities_dict = dict(zip(ids, quantities))
        user_profile = Profile.objects.get(user__pk=user_id)
        commodities = Commodity.objects.filter(pk__in=ids)
        purchased_commodities = []  # List to store PurchasedCommodity instances

        with transaction.atomic():
          payment = Payment.objects.create(
              payment_id=payment_id, customer=user_profile.user)

          for commodity in commodities:
            quantity = quantities_dict.get(commodity.pk, 0)
            commodity.quantity -= quantity
            commodity.save()

            # Create a PurchasedCommodity instance
            purchased_commodity = PurchasedCommodity(
                payment=payment,
                commodity=commodity,
                quantity=quantity
            )
            purchased_commodities.append(purchased_commodity)

          # Bulk create PurchasedCommodity instances
          PurchasedCommodity.objects.bulk_create(purchased_commodities)

          user_profile.balance -= Decimal(response.get("amount"))
          user_profile.save()

          # Clear items from the cart
          cart = Cart.objects.get(user__pk=user_id)
          CommodityInCart.objects.filter(
              cart=cart, commodity__pk__in=ids).delete()

        # Send the payment_done signal
        payment_done.send(
            sender=Payment,
            customer=user_profile.user,
            payment_id=payment_id,
            purchased_commodities=purchased_commodities
        )

    return HttpResponse()


@login_required
def replenishment(request):
  if request.method == "POST":
    form = ReplenishmentForm(request.POST)

    if form.is_valid():
      liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
      amount = form.cleaned_data["amount"]
      params = {
          "action": "pay",
          "amount": str(round(amount, 2)),
          "currency": "UAH",
          "description": "Поповнення балансу",
          "order_id": str(uuid4()),
          "version": "3",
          "sandbox": 1,  # sandbox mode, set to 1 to enable it
          # url to callback view
          "server_url": "https://webstore-eta.vercel.app/replenishment-callback/",
          "info": f"{request.user.id}"
      }
      signature = liqpay.cnb_signature(params)
      data = liqpay.cnb_data(params)

      return render(request, "payment/pay.html", {"signature": signature, "data": data, "title": "Поповненя балансу"})

    messages.error(request, "Виникла помилка. Неправильна інформація")
  else:
    form = ReplenishmentForm()

  return render(request, "base/formPage.html", {"form": form, "title": "Поповнення балансу"})


@require_POST
@csrf_exempt
@retry_decorator
def replenishment_callback(request):
  liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
  data = request.POST.get("data")
  signature = request.POST.get("signature")
  sign = liqpay.str_to_sign(
      settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
  if sign == signature:
    response = liqpay.decode_data_from_str(data)

    if response.get("status") == "sandbox":
      amount = Decimal(response.get("amount"))
      user_id = int(response.get("info"))
      user_profile = Profile.objects.get(user__pk=user_id)
      payment_id = int(response.get("payment_id"))

      with transaction.atomic():
        payment = Payment.objects.create(
            payment_id=payment_id, customer=user_profile.user)
        Replenishment.objects.create(payment=payment, amount=amount)
        user_profile.balance += amount
        user_profile.save()

  return HttpResponse()


@login_required
@permission_required("payment.can_form_report", raise_exception=True)
def form_report(request):
  if request.method == "POST":
    form = ReportForm(request.POST)
    if form.is_valid():
      start_date = form.cleaned_data["start_date"]
      end_date = form.cleaned_data["end_date"]
      return redirect(reverse("payment:report", args=(start_date, end_date,)))
  else:
    form = ReportForm()

  return render(request, "base/formPage.html", {"form": form, "title": "Сформувати звіт про продажі"})


@login_required
@permission_required("payment.can_form_report", raise_exception=True)
def report(request, start_date, end_date):
  try:
    start_date = datetime.strptime(
        start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    end_date = datetime.strptime(
        end_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    purchased_commodities = PurchasedCommodity.objects.filter(
        payment__timestamp__range=(start_date, end_date)
    )
  except Exception:
    raise Http404("Page not found")

  if not purchased_commodities.exists():
    messages.info(request, "Немає даних про куплені товари")
    return redirect(reverse("payment:form-report"))

  sales_quantity = purchased_commodities.aggregate(
      total_quantity=Sum("quantity")
  )["total_quantity"]

  sales_sum = purchased_commodities.annotate(
      total_price=Sum(F("quantity") * F("commodity__price"))
  ).aggregate(total_sum=Sum("total_price"))["total_sum"]

  most_popular_commodity = purchased_commodities.values("commodity__title", "commodity__category__title", "commodity__manufacturer__name").annotate(
      total_quantity=Sum("quantity")).order_by("-total_quantity").first()

  most_popular_category = purchased_commodities.values("commodity__category__title").annotate(
      total_quantity=Sum("quantity")
  ).order_by("-total_quantity").first()

  most_popular_manufacturer = purchased_commodities.values("commodity__manufacturer__name").annotate(
      total_quantity=Sum("quantity")
  ).order_by("-total_quantity").first()

  most_expensive_commodity = purchased_commodities.order_by(
      "-commodity__price").first()
  cheapest_commodity = purchased_commodities.order_by(
      "commodity__price").first()

  categories = purchased_commodities.values("commodity__category__title").annotate(
      sales_quantity=Sum("quantity"),
      sales_sum=Sum(F("quantity") * F("commodity__price")),
  ).order_by("-sales_sum")

  context = {
      "sales_quantity": sales_quantity,
      "sales_sum": sales_sum,
      "most_popular_commodity": most_popular_commodity,
      "most_popular_category": most_popular_category,
      "most_popular_manufacturer": most_popular_manufacturer,
      "most_expensive_commodity": most_expensive_commodity,
      "cheapest_commodity": cheapest_commodity,
      "categories": categories,
  }

  return render(request, "payment/report.html", context)


@login_required
@require_GET
def user_payments(request):
  user_payments = Payment.objects.filter(
      customer=request.user).order_by("-timestamp")

  purchased_commodities_data = []
  replenishment_data = []

  for payment in user_payments:
    commodities_data = []
    replenishment_amount = None

    purchased_commodities = PurchasedCommodity.objects.filter(payment=payment)
    for item in purchased_commodities:
      item_title = item.commodity.title if item.commodity else ""
      item_price = item.commodity.price if item.commodity else 0
      commodity_data = {
          "title": item_title,
          "quantity": item.quantity,
          "price": item.quantity * item_price,
      }
      commodities_data.append(commodity_data)

    replenishment = Replenishment.objects.filter(payment=payment).first()
    if replenishment:
      replenishment_amount = replenishment.amount

    payment_info = {
        "payment_id": payment.payment_id,
        "datetime": payment.timestamp,
        "commodities": commodities_data,
        "total_price": sum(item["price"] for item in commodities_data),
        "replenishment_amount": replenishment_amount,
    }

    if commodities_data:
      purchased_commodities_data.append(payment_info)
    elif replenishment_amount is not None:
      replenishment_data.append(payment_info)

  context = {
      "purchased_commodities": purchased_commodities_data,
      "replenishment_data": replenishment_data,
  }

  return render(request, "payment/userPayments.html", context)
