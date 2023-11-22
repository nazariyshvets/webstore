from django.urls import path
from . import views

app_name = "base"
urlpatterns = [
    path("", views.index, name="index"),
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<str:pk>/", views.category, name="category"),
    path("catalog/<str:category_pk>/<int:commodity_pk>/",
         views.commodity, name="commodity"),
    path("catalog/<str:category_pk>/<int:commodity_pk>/comment/",
         views.comment, name="comment"),
    path("cart/", views.cart, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("delete-from-cart/<int:commodity_pk>",
         views.delete_from_cart, name="delete-from-cart"),
]
