# views.py
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.authentication import (
    JWTAuthentication,
    JWTStatelessUserAuthentication,
)
from .models import Mosque, Sermon, Announcement
from .serializers import MosqueSerializer, SermonSerializer, AnnouncementSerializer
from rest_framework.permissions import IsAuthenticated
from apps.users.custom_permissions import IsAdmin, IsAssociate, IsImam, IsSuperAdmin


@api_view(["POST"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def create_mosque(request):
    serializer = MosqueSerializer(data=request.data)
    if Mosque.objects.filter(name=request.data["name"]).exists():
        return Response(
            {"error": "Mosque with this name already exists"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAdmin])
@authentication_classes([JWTAuthentication])
def delete_mosque(request, id):
    try:
        mosque = Mosque.objects.get(id=id)
        mosque.delete()
        return Response(
            {"message": "Mosque deleted successfully"},
            status=status.HTTP_200_OK,
        )
    except Mosque.DoesNotExist:
        return Response({"error": "Mosque not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def get_all_mosques(request):
    is_liked = request.query_params.get("is_liked", None)
    if is_liked is not None:
        mosques = Mosque.objects.filter(is_liked=True if is_liked == "true" else False)
    else:
        mosques = Mosque.objects.all()
    serializer = MosqueSerializer(mosques, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# returns all mosque with the is_liked field set to true
@api_view(["GET"])
def get_liked_mosques(request):
    mosque = Mosque.objects.filter(is_liked=True)
    serialize = MosqueSerializer(mosque, many=True)
    return Response(serialize.data, status=status.HTTP_200_OK)


# creating an annoucement and checks if the title already exists
@api_view(["POST"])
def create_announcement(request):
    serializer = AnnouncementSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# returns all annoucements
@api_view(["GET"])
def get_all_announcements(request):
    announcements = Announcement.objects.all()
    serialize = AnnouncementSerializer(announcements, many=True)
    return Response(serialize.data, status=status.HTTP_200_OK)


# deleting annoucement
@api_view(["DELETE"])
def delete_announcement(request, id):
    announcement = Announcement.objects.get(id=id)
    announcement.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# creating sermons
class SermonView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SermonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, id, *args, **kwargs):
        try:
            sermon = Sermon.objects.get(id=id)  # Get the sermon instance by ID
        except Sermon.DoesNotExist:
            return Response(
                {"detail": "Sermon not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Allow partial updates
        serializer = SermonSerializer(sermon, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_all_sermons(request):
    sermons = Sermon.objects.all()
    serialize = SermonSerializer(sermons, many=True)
    return Response(serialize.data, status=status.HTTP_200_OK)


# @api_view(["DELETE"])
# def delete_sermon(request, id):
#     sermon = Sermon.objects.get(id=id)
#     sermon.delete()
#     return Response({"message":""},status=status.HTTP_204_NO_CONTENT)

@api_view(["DELETE"])
def delete_sermon(request, id):
    try:
        sermon = Sermon.objects.get(id=id)
    except Sermon.DoesNotExist:
        return Response(
            {"message": "Sermon not found"}, status=status.HTTP_404_NOT_FOUND
        )
    sermon.delete()
    return Response(
        {"message": "Sermon deleted successfully"}, status=status.HTTP_204_NO_CONTENT
    )


class LikeMosqueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id, *args, **kwargs):
        try:
            mosque = Mosque.objects.get(id=id)
        except Mosque.DoesNotExist:
            return Response(
                {"detail": "Mosque not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user = request.user

        # Toggle like status
        if mosque.liked_by.filter(id=user.id).exists():
            mosque.liked_by.remove(user)  # Unlike the mosque
            message = "Mosque unliked successfully."
        else:
            mosque.liked_by.add(user)  # Like the mosque
            message = "Mosque liked successfully."

        return Response({"detail": message}, status=status.HTTP_200_OK)



class FavouritedMosquesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            # Retrieve all mosques liked by the user using the related_name 'liked_mosques'
            liked_mosques = user.liked_mosques.all()
            serializer = MosqueSerializer(liked_mosques, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            # Handle the case where the user or related objects do not exist
            return Response(
                {"detail": "User or related data not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            # Handle any other unexpected errors
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )