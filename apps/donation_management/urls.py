from django.urls import path, include
from . import views

urlpatterns = [
    path("create-donation/", views.create_donation, name="create_donation"), # this method will need to be changed when we need to add a payment method
    path("get-all-donations/", views.GetAllDonations.as_view(), name="get_all_donations",), # gets all objects and filters to get objects by date
    path("get-all-waqf-donations/", views.GetAllWaqfDonations.as_view(), name="get_all_waqf_donations",), # gets all objects and filters to get objects by date
    path("delete-waqf-donations/<id>/", views.delete_donation, name="delete_waqf_donation"), # deletes a waqf if the date is in the future, else sets is_active to false if date is in the past
    path("create-waqf-donation/", views.create_waqf_donation, name="create_waqf_donation"),
]
