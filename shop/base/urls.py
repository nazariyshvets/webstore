from django.urls import path
from . import views

app_name = "base"
urlpatterns = [
    path("", views.index, name="index"),
    path("catalogue/", views.catalogue, name="catalogue"),
    path("catalogue/<str:pk>/", views.category, name="category"),
    path("catalogue/<str:category_pk>/<int:commodity_pk>/",
         views.commodity, name="commodity"),
    path("catalogue/<str:category_pk>/<int:commodity_pk>/comment/",
         views.comment, name="comment"),
    path("cart/", views.cart, name="cart"),
    path("cart/buy/", views.buy, name="buy"),
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("delete-from-cart/", views.delete_from_cart, name="delete-from-cart"),
    path("form-report/", views.form_report, name="form-report"),
    path("report/<str:start_date>/<str:end_date>/", views.report, name="report")
]
