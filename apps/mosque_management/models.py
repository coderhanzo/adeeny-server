from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

# Create your models here.
def upload_to(instance, filename):
    return "mosque_documents/{filename}".format(filename=filename)


class Mosque(models.Model):
    name = models.CharField(verbose_name=_("Mosque Name"), max_length=250, unique=True)
    tel = PhoneNumberField(
        verbose_name=_("Phone Number"),
        blank=True,
        null=True,
    )
    mail = models.EmailField(
        verbose_name=_("Email Address"),
        blank=True,
        null=True,
    )
    imam = models.CharField(
        verbose_name=_("Imam's Name"), max_length=250
    )  # make the name of the imam a foreign key with the imam user/profile
    location = models.CharField(
        max_length=250, blank=True, null=True, verbose_name=_("Mosque Location")
    )
    lat = models.FloatField(verbose_name=_("Latitude"), blank=True, null=True)
    long = models.FloatField(verbose_name=_("Longitude"), blank=True, null=True)

    image = models.ImageField(
        upload_to="mosques/image/",
        verbose_name=_("Mosque Image"),
        blank=True,
        null=True,
    )
    certificate = models.FileField(upload_to="mosques/certificates/", blank=True, null=True, verbose_name=_("Certificate"))

    additional_info = models.TextField(
        verbose_name=_("Additional Content"), blank=True, null=True
    )
    liked_by = models.ManyToManyField(User, related_name="liked_mosques", blank=True)

    def __str__(self):
        return self.name

     # Property to check if the current user has liked the mosque
    def is_liked_by_user(self, user):
        return self.liked_by.filter(id=user.id).exists()


class PrayerTime(models.Model):
    title = models.CharField(max_length=250, default="n/a")
    time = models.TimeField(max_length=250, default="n/a")
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.title


def upload_to(instance, filename):
    return "mosque_sermons/{filename}".format(filename=filename)


class Sermon(models.Model):
    class SermonType(models.TextChoices):
        audio = "AUDIO", _("Audio")
        video = "VIDEO", _("video")
        document = "DOCUMENT", _("Document")

    title = models.CharField(max_length=250, default="n/a")
    description = models.TextField(max_length=500, blank=True, null=True)
    speaker_name = models.CharField(max_length=250, default="n/a")
    sermon_type = models.CharField(
        choices=SermonType.choices, max_length=50, default="n/a"
    )
    docs = models.FileField(upload_to=upload_to, blank=True, null=True)
    audio = models.FileField(upload_to=upload_to, blank=True, null=True)
    video = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.speaker_name}"


class Announcement(models.Model):
    title = models.CharField(max_length=250, default="n/a")
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    time = models.TimeField(auto_now_add=True, blank=True, null=True)
    location = models.CharField(
        max_length=250, blank=True, null=True, verbose_name=_("Mosque Location")
    )
    lat = models.FloatField(verbose_name=_("Latitude"), blank=True, null=True)
    long = models.FloatField(verbose_name=_("Longitude"), blank=True, null=True)

    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return "{0}/{1}".format("annoucement image", filename)

    image = models.FileField(upload_to="user_directory_path", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.title
