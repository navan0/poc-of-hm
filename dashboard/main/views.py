import requests
from collections import OrderedDict

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from main.forms import CriminalDataForm, SurveillanceCameraForm, BlacklistForm
from main.models import CriminalData, SurveillanceCamera, surveillance_types
from main.constants import (
    ADD_CRIMINAL_API, FACE_SEARCH_API, BLACKLIST_API, DEEPFAKE_DETECTION_API)


class LoginView(View):
    template_name = "login.html"

    def get(self, request, *args, **kwargs):
        if request.user and request.user.is_authenticated:
            return redirect('/')
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class HomeView(View):
    template_name = "index.html"

    def get_context_data(self, request, id=None):
        criminals = CriminalData.objects.all()
        if id:
            criminals = criminals.filter(id=id)
        search = request.GET.get('search', '')
        if search:
            criminals = criminals.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(dob__icontains=search)
                | Q(crime_nos__icontains=search)).distinct()
        context = {'criminals': criminals}
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        criminal_id = None
        criminal_data_form = CriminalDataForm(request.POST, request.FILES)
        blacklist_form = BlacklistForm(request.POST)
        if criminal_data_form.is_valid():
            criminal_data = criminal_data_form.save()
            response = requests.post(
                ADD_CRIMINAL_API, data={'id': criminal_data.id},
                files={'image': open(criminal_data.image.path, 'rb')}).json()
            return redirect('/')
        elif request.FILES.get('photo'):
            response = requests.post(
                FACE_SEARCH_API, files=request.FILES).json()
            criminal_id = response.get('response')
        elif blacklist_form.is_valid():
            id = blacklist_form.cleaned_data.get('id')
            blacklisted = blacklist_form.cleaned_data.get('blacklisted', False)
            criminal_data = CriminalData.objects.get(id=id)
            criminal_data.blacklisted = blacklisted
            criminal_data.save()
            response = requests.post(
                BLACKLIST_API,
                data={'id': criminal_data.id, 'name': criminal_data.full_name,
                      'blacklisted': blacklisted}).json()
            return redirect('/')
        context = self.get_context_data(request, id=criminal_id)
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class SurveillanceView(View):
    template_name = "surveillance.html"

    def get_context_data(self, request):
        surveillance_type_list = surveillance_types[:-1]
        context = {}
        context['surveillance_types'] = surveillance_type_list
        context['cameras'] = SurveillanceCamera.objects.filter(
            is_blacklist_cam=False)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = SurveillanceCameraForm(request.POST)
        delete_id = request.POST.get('delete_id')
        if delete_id:
            try:
                SurveillanceCamera.objects.get(id=int(delete_id)).delete()
                return redirect('/surveillance/')
            except SurveillanceCamera.DoesNotExist:
                pass
        elif form.is_valid():
            form.save()
            return redirect('/surveillance/')
        context = self.get_context_data(request)
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class BlacklistView(View):
    template_name = "blacklist.html"

    def get_context_data(self, request):
        context = {}
        context['cameras'] = SurveillanceCamera.objects.filter(
            is_blacklist_cam=True)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = dict(OrderedDict(request.POST))
        data['is_blacklist_cam'] = True
        data['surveillance_type'] = 'BLACKLIST'
        form = SurveillanceCameraForm(data)
        delete_id = request.POST.get('delete_id')
        if delete_id:
            try:
                SurveillanceCamera.objects.get(id=int(delete_id)).delete()
                return redirect('/blacklist/')
            except SurveillanceCamera.DoesNotExist:
                pass
        elif form.is_valid():
            form.save()
        return redirect('/blacklist/')


@method_decorator(login_required, name='dispatch')
class DeepFakeDetectionView(View):
    template_name = "deepfake.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        context = {}
        if request.FILES.get('data_file'):
            response = requests.post(
                DEEPFAKE_DETECTION_API, files=request.FILES).json()
            image_str = response.get('image', '')
            if image_str:
                context['image'] = "data:image/png;base64, " + response.get(
                    'image', '')
            else:
                context['image'] = ""
        return render(request, self.template_name, context)
