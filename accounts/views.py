from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from .models import User
from .forms import ProfileForm, DeleteUserForm
from debates.utils import getpage
from django.conf import settings
from allauth.account.models import EmailAddress

# Create your views here.


def userarguments(request, uname):

	user = get_object_or_404(User, username=uname)
	
	if (user.active == 1 or user.active == 3) and not (request.user.is_authenticated and request.user.isgmod()):
		return render(request, 'accounts/userinactive.html', {'puser': user})
	
	queryset = user.arguments.all()
	
	argumentslist = queryset.order_by('-created_on')
	
	page = request.GET.get('page', 1)

	arguments = getpage(page, argumentslist, 10)

	context = {
		'puser': user,
		'arguments': arguments,
	}
	return render(request, 'accounts/user.html', context)

def userdebates(request, uname):

	user = get_object_or_404(User, username=uname)
	
	if (user.active == 1 or user.active == 3) and not (request.user.is_authenticated and request.user.isgmod()):
		return render(request, 'accounts/userinactive.html', {'puser': user})
	
	queryset = user.debates.all()
	
	debateslist = queryset.order_by('-created_on')
	
	page = request.GET.get('page', 1)

	debates = getpage(page, debateslist, 10)

	context = {
		'puser': user,
		'debates': debates,
	}
	return render(request, 'accounts/userdebates.html', context)

@login_required()
def profile(request):
	if request.method == 'POST':
		form = ProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			request.user = form.save(commit=False)
			request.user.stopics.set(form.stopicsl)
			request.user.save()
			return HttpResponseRedirect(reverse('profile'))
	elif request.method == 'GET':
		form = ProfileForm(instance=request.user)
	
	context = {
		'form': form,
	}
	return render(request, 'accounts/profile.html', context)
	
def inactive(request):
	useriaid = request.session.pop('useriaid', -1)
	context = {
		
	}
	if useriaid == -1:
		context['useria'] = None
	else:
		context['useria'] = User.objects.get(id=useriaid)
	return render(request, 'account/account_inactive.html', context)

def delete(request):
	if request.method == 'POST':
		form = DeleteUserForm(request.POST, user=request.user)
		if form.is_valid():
			request.user.active = 1
			request.user.is_active = False
			request.user.email = ""
			request.user.save()
			EmailAddress.objects.filter(user=request.user).delete()
			logout(request)
			return HttpResponseRedirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)
	elif request.method == 'GET':
		form = DeleteUserForm(user=request.user)
	context = {
		'form': form,
	}
	return render(request, 'accounts/delete.html', context)