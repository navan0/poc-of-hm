from django.contrib.postgres.fields import ArrayField
from django.db import models

from main.constants import SURVEILLANCE_ENDPOINTS

from dashboard.settings import SERVICE_ENDPOINT

surveillance_types = (
    ('FACE_MASK_DETECTION', 'Face Mask Detection'),
    ('CROWD_COUNTING', 'Crowd Counting'),
    ('SOCIAL_DISTANCING', 'Social Distancing Monitoring'),
    ('SPEED_MONITORING', 'Speed Monitoring'),
    ('BLACKLIST', 'Blacklisted Face Detection')
)


class Plugin(models.Model):
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=False)


class CriminalData(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    crime_nos = ArrayField(models.CharField(max_length=50))
    image = models.ImageField()
    blacklisted = models.BooleanField(default=False)

    @property
    def full_name(self):
        return ' '.join((self.first_name, self.last_name))


class SurveillanceCamera(models.Model):
    name = models.CharField(max_length=50)
    ip = models.CharField(max_length=100)
    surveillance_type = models.CharField(
        max_length=32, choices=surveillance_types)
    is_blacklist_cam = models.BooleanField(default=False)

    @property
    def video_source(self):
        return SERVICE_ENDPOINT+SURVEILLANCE_ENDPOINTS[
            self.surveillance_type]+'?video='+self.ip
