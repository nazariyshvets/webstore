from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import Category, Commodity, Comment, CommodityEvaluation, CommodityInCart
from .forms import EvaluationForm, CommentForm

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


@require_GET
def index(request):
  categories = Category.objects.all()

  # Get query parameters with default values
  query = request.GET.get("query", "")
  sort = request.GET.get("sort", "rating")
  limit = int(
      request.GET.get("limit", 10))
  page_number = int(request.GET.get("page", "1"))

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


@require_GET
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
  page_number = int(request.GET.get("page", "1"))
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
  commodity_ids = commodity_in_cart_items.values_list("commodity__id")
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


def redirectPNF(request, exception):
  messages.error(request, "Сторінку не знайдено")
  return redirect("base:index")
