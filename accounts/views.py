from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User
from .forms import ProfileForm
from debates.utils import getpage

# Create your views here.

def user(request, uname):

	user = get_object_or_404(User, username=uname)
	
	queryset = user.arguments.all()
	
	argumentslist = queryset.order_by('-created_on')
	
	page = request.GET.get('page', 1)

	arguments = getpage(page, argumentslist, 10)

	context = {
		'puser': user,
		'arguments': arguments,
	}
	return render(request, 'accounts/user.html', context)

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