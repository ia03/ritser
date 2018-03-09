from django.urls import path, re_path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('privacy', views.privacy, name='privacy'),
	path('terms', views.terms, name='terms'),
	path('about', views.about, name='about'),
	path('t/<slug:tname>', views.topic, name='topic'),
	path('t/<slug:tname>/info', views.topicinfo, name='topicinfo'),
]
