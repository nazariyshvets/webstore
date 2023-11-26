from django.urls import path
from . import views

app_name = "payment"
urlpatterns = [
    path("purchase/", views.PurchaseView.as_view(), name="purchase"),
    path("purchase-callback/", views.PurchaseCallbackView.as_view(),
         name="purchase-callback"),
    path("replenishment/", views.replenishment, name="replenishment"),
    path("replenishment-callback/", views.replenishment_callback,
         name="replenishment-callback"),
    path("form-report/", views.form_report, name="form-report"),
    path("report/<str:start_date>/<str:end_date>/", views.report, name="report"),
    path("user-payments/", views.user_payments, name="user-payments"),
]
