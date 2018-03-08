from django.urls import path, re_path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('privacy', views.privacy, name='privacy'),
	path('terms', views.terms, name='terms'),
	path('t/<slug:tname>', views.topic, name='topic'),
]
