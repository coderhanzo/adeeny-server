from django.core.exceptions import ValidationError
from rest_framework import serializers
from phonenumber_field.phonenumber import to_python

# custom validation for phone number to check if its 10 numbers
def validate_phonenumber(self, value):
  phone_number = to_python(value)
  if phone_number and (len(phone_number.national_number) != 10):
    raise serializers.ValidationError("Phone number must be 10 digits")
  elif phone_number == None:
    raise serializers.ValidationError("Phone number is required")
  else:
    return value