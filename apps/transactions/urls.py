from django.urls import path
from . import views


urlpatterns = [
    path("payments/", views.PaymentsView.as_view()),
    path("collections/", views.CollectionsView.as_view()),
    path(
        "payment-callback/",
        views.PaymentCallbackAPIView.as_view(),
        name="payment-callback",
    ),
    path("name-enquiry/", views.NameEnquiryView.as_view()),
    path("card-payment/", views.CardPaymentAPIView.as_view()),
    path(
        "transaction/<str:transaction_id>/",
        views.TransactionsViewById.as_view(),
        name="peoplespay-transaction-status",
    ),
    path("transactions/", views.TransactionsView.as_view()),
    path("token/", views.TokenView.as_view()),
]
