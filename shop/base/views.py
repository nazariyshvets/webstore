from .models import SoldCommodity
from django.db.models import Count, Sum
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.db.models import Sum, F
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


def filter_commodities(search_string, sort):
    commodities = Commodity.objects.filter(title__icontains=search_string)

    if sort in SORT_CHOICES:
        commodities = commodities.order_by(SORT_CHOICES[sort])
    else:
        commodities = commodities.order_by(SORT_CHOICES["rating"])
    return commodities


def index(request):
    categories = Category.objects.all()

    # Get query parameters with default values
    search_string = request.GET.get("search-input", "")
    sort = request.GET.get("sort", "rating")
    commodities_num_per_page = int(
        request.GET.get("commodities-num-per-page", 10))
    page_number = request.GET.get("page")

    # Filter and sort commodities
    commodities = filter_commodities(search_string, sort)

    # Pagination
    paginator = Paginator(commodities, commodities_num_per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        "categories": categories,
        "search_string": search_string,
        "sort": sort,
        "commodities_num_per_page": commodities_num_per_page,
        "page_obj": page_obj,
    }
    return render(request, "base/index.html", context)


def catalogue(request):
    categories = Category.objects.all()
    return render(request, "base/catalogue.html", {"categories": categories})


def category(request, pk):
    # Initial filtering
    commodities = Commodity.objects.filter(category__title=pk)

    # Get unique manufacturers
    all_manufacturers = sorted(
        set(obj["manufacturer"] for obj in commodities.values("manufacturer")))

    # Search and filter by manufacturer
    search_string = request.GET.get("search-input", "")
    selected_manufacturers = request.GET.get("manufacturers", "")
    selected_manufacturers = selected_manufacturers.split(
        ",") if selected_manufacturers else all_manufacturers

    # Filter by search string and selected manufacturers
    commodities = commodities.filter(
        title__icontains=search_string, manufacturer__name__in=selected_manufacturers)

    # Sort commodities based on the selected sort option
    sort = request.GET.get("sort", "rating")
    sort_type = SORT_CHOICES.get(sort, "-rating")
    commodities = commodities.order_by(sort_type)

    # Pagination
    commodities_num_per_page = int(
        request.GET.get("commodities-num-per-page", 10))
    paginator = Paginator(commodities, commodities_num_per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Selected manufacturers as a string for the template
    selected_manufacturers_string = ",".join(selected_manufacturers)

    context = {
        "title": pk,
        "search_string": search_string,
        "sort": sort,
        "commodities_num_per_page": commodities_num_per_page,
        "page_obj": page_obj,
        "all_manufacturers": all_manufacturers,
        "selected_manufacturers_string": selected_manufacturers_string,
    }
    return render(request, "base/category.html", context)


def commodity(request, category_pk, commodity_pk):
    categories = Category.objects.all()
    commodity = Commodity.objects.get(pk=commodity_pk)
    comments = Comment.objects.filter(commodity__id=commodity_pk)
    context = {
        "categories": categories,
        "commodity": commodity,
        "comments": comments,
        "category_pk": category_pk
    }
    return render(request, "base/commodity.html", context)


@login_required
@transaction.atomic
def comment(request, category_pk, commodity_pk):
    commodity = get_object_or_404(Commodity, pk=commodity_pk)

    if request.method == "POST":
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
            comment_text = comment_form.cleaned_data["comment_text"]
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
    commodity_ids = CommodityInCart.objects.filter(
        cart=cart).values_list("commodity")
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
        commodity = Commodity.objects.get(pk=commodity_id)
        CommodityInCart.objects.get_or_create(cart=cart, commodity=commodity)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
@csrf_exempt
def delete_from_cart(request):
    if request.method == "POST":
        cart = request.user.cart
        commodity_id = json.loads(request.body)["commodity_id"]
        CommodityInCart.objects.get(
            cart=cart, commodity__pk=commodity_id).delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def buy(request):
    cart = request.user.cart
    commodities_in_cart = CommodityInCart.objects.filter(cart=cart)
    commodities_in_cart.filter(commodity__quantity=0).delete()
    commodity_ids = commodities_in_cart.values_list('commodity__pk', flat=True)
    commodities = Commodity.objects.filter(pk__in=commodity_ids)

    if not commodities.exists():
        messages.error(request, "Немає товарів для покупки!")
        return redirect("base:cart")

    commodities_price = commodities.aggregate(Sum("price"))["price__sum"]

    if request.user.profile.balance < commodities_price:
        messages.error(request, "Недостатній баланс для покупки!")
        return redirect("base:cart")

    try:
        with transaction.atomic():
            commodities.update(quantity=F('quantity') - 1)

            sold_commodities = [
                SoldCommodity(
                    title=commodity.title,
                    price=commodity.price,
                    category=commodity.category.title,
                    manufacturer=commodity.manufacturer.name,
                    username=request.user.username,
                )
                for commodity in commodities
            ]
            SoldCommodity.objects.bulk_create(sold_commodities)

            request.user.profile.balance -= commodities_price
            request.user.profile.save()

            commodities_in_cart.delete()

            messages.success(request, "Покупку успішно здійснено!")
    except Exception:
        messages.error(request, "Виникла помилка при транзакції!")

    try:
        commodities_purchased.send(
            sender=SoldCommodity, customer=request.user, commodities=commodities)
    except Exception:
        pass

    return redirect("base:cart")


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

    return render(request, "base/form-report.html", {"form": form})


@login_required
@permission_required("base.can_form_report", raise_exception=True)
def report(request, start_date, end_date):
    sold_commodities = SoldCommodity.objects.filter(
        selling_date__range=(start_date, end_date))

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
