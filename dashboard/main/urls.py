from django.urls import re_path

from main.views import (DeepFakeDetectionView, HomeView, LoginView,
                        SurveillanceView, BlacklistView)

urlpatterns = [
    re_path(r'^$', HomeView.as_view()),
    re_path(r'^surveillance/$', SurveillanceView.as_view()),
    re_path(r'^deepfake-detection/$', DeepFakeDetectionView.as_view()),
    re_path(r'^blacklist/$', BlacklistView.as_view()),
    re_path(r'^login/$', LoginView.as_view()),
]
