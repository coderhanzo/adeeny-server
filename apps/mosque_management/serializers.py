from rest_framework import serializers
from .models import Mosque, Sermon, Announcement


class MosqueSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    class Meta:
        model = Mosque
        fields = "__all__"

    def get_is_liked(self, obj):
        # Check if the logged-in user has liked the mosque
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_liked_by_user(request.user)
        return False


class SermonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sermon
        fields = "__all__"


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = "__all__"
