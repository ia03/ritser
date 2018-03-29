from django.urls import path, re_path
from . import views


urlpatterns = [
	path('<slug:uname>/', views.userarguments, name='user'),
	path('<slug:uname>/arguments', views.userarguments, name='userarguments'),
	path('<slug:uname>/debates', views.userdebates, name='userdebates'),
]
