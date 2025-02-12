from django.contrib import admin
from .models import Mosque, Sermon, Announcement, PrayerTime

# Register your models here.
admin.site.register(Mosque)
admin.site.register(Sermon)
admin.site.register(Announcement)
admin.site.register(PrayerTime)
