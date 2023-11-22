from django.urls import path
from . import views

app_name = "purchase"
urlpatterns = [
    path("pay/", views.PayView.as_view(), name="pay"),
    path("pay-callback/", views.PayCallbackView.as_view(), name="pay-callback"),
    path("form-report/", views.form_report, name="form-report"),
    path("report/<str:start_date>/<str:end_date>/", views.report, name="report"),
    path("user-payments/", views.user_payments, name="user-payments"),
]
