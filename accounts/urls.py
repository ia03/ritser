from django.urls import path, re_path
from . import views


urlpatterns = [
	path('u/<slug:uname>/', views.userarguments, name='user'),
	path('u/<slug:uname>/arguments', views.userarguments, name='userarguments'),
	path('u/<slug:uname>/debates', views.userdebates, name='userdebates'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/inactive/', views.inactive, name='account_inactive'), #overrides django-allauth
    path('accounts/delete/', views.delete, name='account_delete'),
]
