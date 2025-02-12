from re import A
from django.utils import timezone
from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
    JWTStatelessUserAuthentication,
)
from .models import ProjectDonation
from .serializers import MonetaryDonationsSerializer, WaqfDonationsSerializer


# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def create_donation(request):
    serializer = MonetaryDonationsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAllDonations(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        date = request.query_params.get("date", None)
        if date:
            donations = ProjectDonation.objects.filter(date=date)
        else:
            donations = ProjectDonation.objects.all()

        serializer = MonetaryDonationsSerializer(donations, many=True)
        return Response(serializer.data)


# WAQF DONATIONS
class GetAllWaqfDonations(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        date = request.query_params.get("date", None)
        if date:
            donations = ProjectDonation.objects.filter(date=date)
        else:
            donations = ProjectDonation.objects.all()

        serializer = WaqfDonationsSerializer(donations, many=True)
        return Response(serializer.data)


# create waqf donations
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def create_waqf_donation(request):
    roles = request.user.roles
    threshold = 1000000  # Set the threshold amount here

    # Checking user roles first
    if roles not in ["ADMIN", "IMAM", "ASSOCIATE"]:
        return Response(
            {"error": "You do not have permission to make this donation."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # handle the amount check
    if "amount" in request.data:
        amount = float(
            request.data["amount"]
        )  # Convert to int for comparison, assuming amount is a number
        if amount > threshold:
            return Response(
                {"error": f"Amount must be less than or equal to {threshold}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # If both checks pass, proceed with saving the data
    serializer = WaqfDonationsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# delete a donation when it reaches end date - set it to inactive
@api_view(["DELETE"])
def delete_donation(request, id):
    try:
        obj = ProjectDonation.objects.get(id=id)
    except ProjectDonation.DoesNotExist:
        return Response({"error": "Waqf not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if the end date is set and compare it
    if obj.end_date is not None and obj.end_date <= timezone.now():
        obj.is_active = False
        obj.save()
        serializer = WaqfDonationsSerializer(obj)
        return Response(
            {"message": "Project has ended", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    else:
        obj.delete()
        return Response({"message": "WAQF deleted"}, status=status.HTTP_204_NO_CONTENT)
