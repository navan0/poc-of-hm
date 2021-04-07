from django.forms import ModelForm, Form
from django import forms

from main.models import CriminalData, SurveillanceCamera


class CriminalDataForm(ModelForm):
    class Meta:
        model = CriminalData
        fields = ('first_name', 'last_name', 'dob', 'image', 'crime_nos')


class BlacklistForm(Form):
    id = forms.IntegerField()
    blacklisted = forms.BooleanField(required=False)


class SurveillanceCameraForm(ModelForm):
    class Meta:
        model = SurveillanceCamera
        fields = ('name', 'surveillance_type', 'ip', 'is_blacklist_cam')
