from django.urls import path, re_path
from . import views

urlpatterns = [
	path('<slug:uname>', views.profile, name='profile'),
]