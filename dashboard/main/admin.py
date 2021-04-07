from django.contrib import admin

from main.models import CriminalData, Plugin, SurveillanceCamera

admin.site.register(CriminalData)
admin.site.register(Plugin)
admin.site.register(SurveillanceCamera)
