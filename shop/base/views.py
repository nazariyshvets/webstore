from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.db.models import Sum
from django.core.paginator import Paginator
import json, collections

from .models import Category, Commodity, Comment, CommodityEvaluation, CommodityInCart, SoldCommodity
from .signals import commodities_purchased

def index(request):
  categories = Category.objects.all()

  search_string = request.GET.get("search-input")
  if search_string is None: search_string = ""
  sort = request.GET.get("sort")
  if sort is None: sort = "rating"
  commodities_num_per_page = request.GET.get("commodities-num-per-page")
  if commodities_num_per_page is None: commodities_num_per_page = 10
  page_number = request.GET.get("page")

  commodities = Commodity.objects.filter(title__icontains=search_string)
  
  if sort == "cheap":
    commodities = commodities.order_by("price")
  elif sort == "expensive":
    commodities = commodities.order_by("-price")
  elif sort == "novelty":
    commodities = commodities.order_by("-adding_date")
  else: commodities = commodities.order_by("-rating") 

  paginator = Paginator(commodities, commodities_num_per_page)
  page_obj = paginator.get_page(page_number)

  context = {
    "categories": categories,
    "search_string": search_string,
    "sort": sort,
    "commodities_num_per_page": commodities_num_per_page,
    "page_obj": page_obj
  }
  return render(request, "base/index.html", context)

def catalogue(request):
  categories = Category.objects.all()
  return render(request, "base/catalogue.html", {"categories": categories})


def category(request, pk):
  commodities = Commodity.objects.filter(category__title=pk)
  all_manufacturers = sorted(list(set([obj["manufacturer"] for obj in commodities.values("manufacturer")])))

  search_string = request.GET.get("search-input")
  if search_string is None: search_string = ""
  sort = request.GET.get("sort")
  if sort is None: sort = "rating"
  commodities_num_per_page = request.GET.get("commodities-num-per-page")
  if commodities_num_per_page is None: commodities_num_per_page = 10
  page_number = request.GET.get("page")
  selected_manufacturers = request.GET.get("manufacturers")
  if not selected_manufacturers:
    selected_manufacturers = all_manufacturers
  else:
    selected_manufacturers = selected_manufacturers.split(",")

  commodities = commodities.filter(title__icontains=search_string)
  commodities = commodities.filter(manufacturer__name__in=selected_manufacturers)
  
  if sort == "cheap":
    commodities = commodities.order_by("price")
  elif sort == "expensive":
    commodities = commodities.order_by("-price")
  elif sort == "novelty":
    commodities = commodities.order_by("-adding_date")
  else: commodities = commodities.order_by("-rating") 

  paginator = Paginator(commodities, commodities_num_per_page)
  page_obj = paginator.get_page(page_number)

  selected_manufacturers_string = ",".join(selected_manufacturers)
  
  context = {
    "title": pk,
    "search_string": search_string,
    "sort": sort,
    "commodities_num_per_page": commodities_num_per_page,
    "page_obj": page_obj,
    "all_manufacturers": all_manufacturers,
    "selected_manufacturers_string": selected_manufacturers_string
  }
  return render(request, "base/category.html", context)

def commodity(request, category_pk, commodity_pk):
  categories = Category.objects.all()
  commodity_obj = Commodity.objects.get(pk=commodity_pk)
  comments = Comment.objects.filter(commodity__id=commodity_pk)
  context = {
    "categories": categories,
    "commodity": commodity_obj,
    "comments": comments,
    "category_pk": category_pk
  }
  return render(request, "base/commodity.html", context)

@login_required
def comment(request, category_pk, commodity_pk):
  if request.method == "POST":
    user = request.user
    commodity = Commodity.objects.get(pk=commodity_pk)
    value = request.POST["evaluation"]
    try:
      user_evaluation = CommodityEvaluation.objects.get(evaluator=user, commodity=commodity)
      user_evaluation.value = value
      user_evaluation.save()
    except CommodityEvaluation.DoesNotExist:
      CommodityEvaluation.objects.create(evaluator=user, commodity=commodity, value=value)

    comment_text = request.POST["comment-textarea"]
    Comment.objects.create(text=comment_text, author=user, commodity=commodity)

    evaluations = CommodityEvaluation.objects.filter(commodity=commodity)
    evaluations_sum = evaluations.aggregate(Sum("value"))["value__sum"]
    evaluations_count = evaluations.count()
    commodity.rating = evaluations_sum/evaluations_count
    commodity.save()
 
  return redirect(reverse("base:commodity", args=(category_pk, commodity_pk,)))


@login_required
def cart(request):
  cart = request.user.cart
  commodity_ids = CommodityInCart.objects.filter(cart=cart).values_list("commodity")
  commodities = Commodity.objects.filter(pk__in=commodity_ids) 
  context = {
    "commodities": commodities
  }
  return render(request, "base/cart.html", context)

@login_required
@csrf_exempt
def add_to_cart(request):
  if request.method == "POST":
    cart = request.user.cart
    commodity_id = json.loads(request.body)["commodity_id"]
    commodity = Commodity.objects.get(id=commodity_id)
    CommodityInCart.objects.get_or_create(cart=cart, commodity=commodity)
    return JsonResponse({"success": True})
  return JsonResponse({"success": False})

@login_required
@csrf_exempt
def delete_from_cart(request):
  if request.method == "POST":
    cart = request.user.cart
    commodity_id = json.loads(request.body)["commodity_id"]
    CommodityInCart.objects.get(cart=cart, commodity__id=commodity_id).delete()
    return JsonResponse({"success": True})
  return JsonResponse({"success": False})

@login_required
def buy(request):
  cart = request.user.cart

  commodities_in_cart = CommodityInCart.objects.filter(cart=cart)
  commodities_in_cart.filter(commodity__quantity=0).delete()
  
  commodity_ids = [commodity_id[0] for commodity_id in commodities_in_cart.values_list("commodity")]
  commodities = Commodity.objects.filter(pk__in=commodity_ids)

  if commodities.count() == 0:
    messages.error(request, "Немає товарів для покупки!")
    return redirect("base:cart")

  commodities_price = commodities.aggregate(Sum("price"))["price__sum"]
  if request.user.profile.balance < commodities_price:
    messages.error(request, "Недостатній баланс для покупки!")
    return redirect("base:cart")
 
  try:
    with transaction.atomic():
      for commodity in commodities:
        commodity.quantity = commodity.quantity - 1
        commodity.save()
        SoldCommodity.objects.create(title=commodity.title, price=commodity.price,
          category=commodity.category.title, manufacturer=commodity.manufacturer.name, username=request.user.username)
      
      request.user.profile.balance -= commodities_price
      request.user.profile.save()
      commodities_in_cart.delete()
    
    messages.success(request, "Покупку успішно здійснено!")
  except Exception:
    messages.error(request, "Виникла помилка при транзакції!")

  try:
    commodities_purchased.send(sender=SoldCommodity, customer=request.user, commodities=commodities)
  except:
    pass

  return redirect("base:cart")

@login_required
@permission_required("base.can_form_report", raise_exception=True)
def form_report(request):
  if request.method == "POST":
    start_date = request.POST["start_date"]
    end_date = request.POST["end_date"]
    return redirect(reverse("base:report", args=(start_date, end_date,)))

  return render(request, "base/form-report.html")

@login_required
@permission_required("base.can_form_report", raise_exception=True)
def report(request, start_date, end_date):
  sold_commodities = SoldCommodity.objects.filter(selling_date__gte=start_date).filter(selling_date__lte=end_date)
  if sold_commodities.count() == 0:
    return render(request, "base/report.html")
  
  sales_quantity = sold_commodities.count()
  sales_sum = sold_commodities.aggregate(Sum("price"))["price__sum"]
  most_popular_commodity = collections.Counter(sold_commodities.values_list("title", "category", "manufacturer")).most_common(1)[0]
  most_popular_category = collections.Counter(sold_commodities.values_list("category")).most_common(1)[0]
  most_popular_manufacturer = collections.Counter(sold_commodities.values_list("manufacturer")).most_common(1)[0]
  most_expensive_commodity = sold_commodities.order_by("-price")[0]
  cheapest_commodity = sold_commodities.order_by("price")[0]

  categories = []
  category_names = sold_commodities.distinct().values_list("category")
  for category_name in category_names:
    sold_commodities_in_category = sold_commodities.filter(category=category_name[0])
    sales_quantity_in_category = sold_commodities_in_category.count()
    sales_sum_in_category = sold_commodities_in_category.aggregate(Sum("price"))["price__sum"]
    categories.append({
      "name": category_name[0],
      "sales_quantity": sales_quantity_in_category,
      "sales_sum": sales_sum_in_category})
  categories = sorted(categories, key=lambda d: d["sales_sum"], reverse=True)

  context = {
    "sales_quantity": sales_quantity,
    "sales_sum": sales_sum,
    "most_popular_commodity": most_popular_commodity,
    "most_popular_category": most_popular_category,
    "most_popular_manufacturer": most_popular_manufacturer,
    "most_expensive_commodity": most_expensive_commodity,
    "cheapest_commodity": cheapest_commodity,
    "categories": categories
  }
  
  return render(request, "base/report.html", context)