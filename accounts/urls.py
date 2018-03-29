from django.urls import path, re_path
from . import views


urlpatterns = [
	path('<slug:uname>/', views.user, name='user'),
	path('<slug:uname>/arguments', views.user, name='userarguments'),
	path('<slug:uname>/debates', views.userdebates, name='userdebates'),
]
