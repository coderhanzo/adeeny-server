import magic
from drf_extra_fields.fields import Base64FileField
from django.core.exceptions import ValidationError

"""
this will encode files to base64 and check mime. 
used in serialisers not models
"""

class Base64File(Base64FileField):
  ALLOWED_TYPES = ("pdf", "jpg", "jpeg", "png")

  def get_file_extension(self, filename, decoded_file):
    mime_type = magic.from_buffer(decoded_file, mime=True)

    return mime_type.split("/")[1]

def validate_image(image):
  file_size = image.size
  limit_mb = 2
  if file_size > limit_mb * 1024 * 1024:
    raise ValidationError(f"image size should be {limit_mb} MB or less")
  valid_mime_type = ["image/jpeg","image/jpg","image/png","image/gif"]
  file_mime_type = image.content_type
  if file_mime_type not in valid_mime_type:
    raise ValidationError(f"Unsupported format")