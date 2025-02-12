# views.py
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import authentication, permissions
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
            status=status.HTTP_204_NO_CONTENT,
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
@api_view(["POST"])
def upload_sermons(request):
    if "file" not in request.FILES:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES["file"]
    return Response({"message": "File uploaded successfully", "file_name": file.name}, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_all_sermons(request):
    sermons = Sermon.objects.all()
    serialize = SermonSerializer(sermons, many=True)
    return Response(serialize.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_sermon(request, id):
    sermon = Sermon.objects.get(id=id)
    sermon.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def delete_user(request, id):
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
