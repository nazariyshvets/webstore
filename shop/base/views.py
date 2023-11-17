from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
import json

from .models import Category, Commodity, Comment, CommodityEvaluation, CommodityInCart, SoldCommodity
from .forms import EvaluationForm, CommentForm, ReportForm
from .signals import commodities_purchased

SORT_CHOICES = {
    "rating": "-rating",
    "cheap": "price",
    "expensive": "-price",
    "novelty": "-adding_date",
}


def filter_commodities(query, sort):
  commodities = Commodity.objects.filter(title__icontains=query)

  if sort in SORT_CHOICES:
    commodities = commodities.order_by(SORT_CHOICES[sort])
  else:
    commodities = commodities.order_by(SORT_CHOICES["rating"])
  return commodities


def index(request):
  categories = Category.objects.all()

  # Get query parameters with default values
  query = request.GET.get("query", "")
  sort = request.GET.get("sort", "rating")
  limit = int(
      request.GET.get("limit", 10))
  page_number = request.GET.get("page")

  # Filter and sort commodities
  commodities = filter_commodities(query, sort)

  # Pagination
  paginator = Paginator(commodities, limit)
  page_obj = paginator.get_page(page_number)

  context = {
      "categories": categories,
      "query": query,
      "sort": sort,
      "limit": limit,
      "page_obj": page_obj,
  }
  return render(request, "base/index.html", context)


def catalog(request):
  categories = Category.objects.all()
  return render(request, "base/catalog.html", {"categories": categories})


def category(request, pk):
  # Initial filtering
  category_obj = get_object_or_404(Category, pk=pk)
  commodities = Commodity.objects.filter(category__id=pk)

  # Get unique manufacturers
  all_manufacturers = sorted(
      set(obj["manufacturer"] for obj in commodities.values("manufacturer")))

  # Search and filter by manufacturer
  query = request.GET.get("query", "")
  selected_manufacturers = request.GET.get("manufacturers", "")
  selected_manufacturers = selected_manufacturers.split(
      ",") if selected_manufacturers else all_manufacturers

  # Filter by search string and selected manufacturers
  commodities = commodities.filter(
      title__icontains=query, manufacturer__name__in=selected_manufacturers)

  # Sort commodities based on the selected sort option
  sort = request.GET.get("sort", "rating")
  sort_type = SORT_CHOICES.get(sort, "-rating")
  commodities = commodities.order_by(sort_type)

  # Pagination
  limit = int(
      request.GET.get("limit", 10))
  paginator = Paginator(commodities, limit)
  page_number = request.GET.get("page")
  page_obj = paginator.get_page(page_number)

  # Selected manufacturers as a string for the template
  selected_manufacturers = ",".join(selected_manufacturers)

  context = {
      "category": category_obj,
      "query": query,
      "sort": sort,
      "limit": limit,
      "page_obj": page_obj,
      "all_manufacturers": all_manufacturers,
      "selected_manufacturers": selected_manufacturers,
  }

  return render(request, "base/category.html", context)


def commodity(request, category_pk, commodity_pk):
  categories = Category.objects.all()
  commodity = get_object_or_404(Commodity, pk=commodity_pk)
  comments = Comment.objects.filter(commodity__id=commodity_pk)
  context = {
      "categories": categories,
      "commodity": commodity,
      "comments": comments,
      "category_pk": category_pk
  }
  return render(request, "base/commodity.html", context)


@login_required
@require_POST
@transaction.atomic
def comment(request, category_pk, commodity_pk):
  commodity = get_object_or_404(Commodity, pk=commodity_pk)

  user = request.user

  # Handle evaluation
  evaluation_form = EvaluationForm(request.POST)

  if evaluation_form.is_valid():
    value = evaluation_form.cleaned_data["evaluation"]
    evaluation, created = CommodityEvaluation.objects.get_or_create(
        evaluator=user, commodity=commodity, defaults={"value": value}
    )
    if not created:
      evaluation.value = value
      evaluation.save()

  # Handle comment
  comment_form = CommentForm(request.POST)

  if comment_form.is_valid():
    comment_text = comment_form.cleaned_data["comment"]
    Comment.objects.create(
        text=comment_text, author=user, commodity=commodity)

  # Update commodity rating
  evaluations_sum = CommodityEvaluation.objects.filter(
      commodity=commodity).aggregate(Sum("value"))["value__sum"]
  evaluations_count = CommodityEvaluation.objects.filter(
      commodity=commodity).count()
  commodity.rating = evaluations_sum / \
      evaluations_count if evaluations_count > 0 else 3
  commodity.save()

  return redirect(reverse("base:commodity", args=(category_pk, commodity_pk,)))


@login_required
def cart(request):
  cart = request.user.cart
  commodity_in_cart_items = CommodityInCart.objects.filter(cart=cart)
  commodity_ids = commodity_in_cart_items.values_list("commodity")
  commodities = Commodity.objects.filter(pk__in=commodity_ids)

  context = {
      "commodities": commodities,
  }
  return render(request, "base/cart.html", context)


@login_required
@require_POST
@csrf_exempt
def add_to_cart(request):
  commodity_id = json.loads(request.body)["commodity_id"]
  commodity = get_object_or_404(Commodity, pk=commodity_id)
  CommodityInCart.objects.get_or_create(
      cart=request.user.cart, commodity=commodity)

  return JsonResponse({"success": True})


@login_required
def delete_from_cart(request, commodity_pk):
  try:
    commodity_in_cart = CommodityInCart.objects.get(
        commodity__pk=commodity_pk, cart=request.user.cart)
    commodity_in_cart.delete()
    messages.success(request, "Товар видалено із кошика")
  except CommodityInCart.DoesNotExist:
    pass

  return redirect("base:cart")


@login_required
@require_POST
@csrf_exempt
def buy(request):
  try:
    data = json.loads(request.body)

    with transaction.atomic():
      sold_commodities = []  # List to store SoldCommodity instances

      for item in data:
        commodity_id = item.get("commodity_id")
        quantity = item.get("quantity", 1)

        # Retrieve the commodity and check its availability
        commodity = Commodity.objects.get(pk=commodity_id)
        if commodity.quantity < quantity:
          messages.error(
              request, f"Недостатньо товару для {commodity.title}. Доступна кількість {commodity.quantity}")
          return JsonResponse({"success": False, "message": "Недостатньо товару для покупки"})

        # Update commodity quantity
        commodity.quantity -= quantity
        commodity.save()

        # Create SoldCommodity instance
        sold_commodity = SoldCommodity(
            commodity_id=commodity.pk,
            title=commodity.title,
            price=commodity.price,
            category=commodity.category.title,
            manufacturer=commodity.manufacturer.name,
            username=request.user.username,
        )
        sold_commodities.append(sold_commodity)

      # Bulk create SoldCommodity instances
      SoldCommodity.objects.bulk_create(sold_commodities)

      # Update user's balance and clear the cart
      commodities_price = sum(
          item["quantity"] * Commodity.objects.get(pk=item["commodity_id"]).price for item in data)
      if request.user.profile.balance < commodities_price:
        messages.error(request, "Недостатній баланс для покупки!")
        return JsonResponse({"success": False, "message": "Недостатній баланс для покупки"})

      request.user.profile.balance -= commodities_price
      request.user.profile.save()

      # Clear items from the cart
      CommodityInCart.objects.filter(cart=request.user.cart, commodity__pk__in=[
                                     item["commodity_id"] for item in data]).delete()

      messages.success(request, "Покупку успішно здійснено!")

      # Send the commodities_purchased signal
      commodities_purchased.send(
          sender=SoldCommodity,
          customer=request.user,
          commodities=sold_commodities
      )

      return JsonResponse({"success": True, "message": "Покупку успішно здійснено"})

  except ObjectDoesNotExist:
    messages.error(request, "Один чи декілька товарів не знайдено.")
    return JsonResponse({"success": False, "message": "Один чи декілька товарів не знайдено"})

  except Exception as e:
    messages.error(request, f"Виникла помилка: {str(e)}")
    return JsonResponse({"success": False, "message": f"Виникла помилка: {str(e)}"})


@login_required
@permission_required("base.can_form_report", raise_exception=True)
def form_report(request):
  if request.method == "POST":
    form = ReportForm(request.POST)
    if form.is_valid():
      start_date = request.POST["start_date"]
      end_date = request.POST["end_date"]
      return redirect(reverse("base:report", args=(start_date, end_date,)))
  else:
    form = ReportForm()

  return render(request, "base/formReport.html", {"form": form})


@login_required
@permission_required("base.can_form_report", raise_exception=True)
def report(request, start_date, end_date):
  try:
    sold_commodities = SoldCommodity.objects.filter(
        selling_date__range=(start_date, end_date))
  except Exception:
    raise Http404("Сторінку не знайдено")

  if not sold_commodities.exists():
    return render(request, "base/report.html")

  sales_quantity = sold_commodities.count()
  sales_sum = sold_commodities.aggregate(Sum("price"))["price__sum"]
  most_popular_commodity = sold_commodities.values("title", "category", "manufacturer").annotate(
      count=Count("id")
  ).order_by("-count").first()
  most_popular_category = sold_commodities.values("category").annotate(
      count=Count("id")
  ).order_by("-count").first()
  most_popular_manufacturer = sold_commodities.values("manufacturer").annotate(
      count=Count("id")
  ).order_by("-count").first()
  most_expensive_commodity = sold_commodities.order_by("-price").first()
  cheapest_commodity = sold_commodities.order_by("price").first()

  categories = sold_commodities.values("category").annotate(
      sales_quantity=Count("id"),
      sales_sum=Sum("price"),
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

  return render(request, "base/report.html", context)


def redirectPNF(request, exception):
  return redirect("base:index")
