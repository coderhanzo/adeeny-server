from rest_framework import serializers
from .models import ProjectDonation
from phonenumber_field.serializerfields import PhoneNumberField
from utils.exceptions import validate_phonenumber

# from utils.utils import Base64FileField


class MonetaryDonationsSerializer(serializers.ModelSerializer):
    # phone_number = serializers.CharField(
    #     validators=[validate_phonenumber], required=True
    # )

    class Meta:
        model = ProjectDonation
        fields = [
            "id",
            "donors_name",
            "phone_number",
            "amount",
            "payment_type",
        ]


class WaqfDonationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDonation
        fields = [
            "id",
            "title",
            "description",
            "upload_image",
            "target_amount",
            "imams_name",
            "payment_type",
            "start_date",
            "end_date",
            "is_active",
        ]
