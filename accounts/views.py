from django.shortcuts import render, get_object_or_404
from .models import User

# Create your views here.

def profile(request, uname):

	user = get_object_or_404(User, username=uname)


	context = {
		'user': user,
	}
	return render(request, 'accounts/profile.html', context)

def signup(request):
	
	
	context = {
		
	}
	return render(request, 'accounts/signup.html', context)