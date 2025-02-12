from rest_framework import serializers
from .models import Mosque, Sermon, Announcement


class MosqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mosque
        fields = "__all__"


class SermonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sermon
        fields = "__all__"

    # def file_size(value):
    #     limit = 2 * 1024 * 1024
    #     if value.size > limit:
    #         raise serializers.ValidationError(
    #             "File too large. Size should not exceed 2 MiB."
    #         )


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"
