from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Q
from .models import User, ModAction
from .forms import ProfileForm, DeleteUserForm, SetStaffForm
from .utils import DeleteUser
from .decorators import admin_required
from debates.utils import getpage
from django.conf import settings


# Create your views here.


def userarguments(request, uname):

    user = get_object_or_404(User, username=uname)

    if (user.active == 1 or user.active == 3) and not (
            request.user.is_authenticated and request.user.isgmod()):
        return render(request, 'accounts/userinactive.html', {'puser': user})

    queryset = user.arguments.filter(~Q(approvalstatus=3))

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

    if (user.active == 1 or user.active == 3) and not (
            request.user.is_authenticated and request.user.isgmod()):
        return render(request, 'accounts/userinactive.html', {'puser': user})

    queryset = user.debates.filter(~Q(approvalstatus=3))

    debateslist = queryset.order_by('-created_on')

    page = request.GET.get('page', 1)

    debates = getpage(page, debateslist, 10)

    context = {
        'puser': user,
        'debates': debates,
    }
    return render(request, 'accounts/userdebates.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            request.user = form.save(commit=False)
            request.user.stopics.set(form.stopicsl)
            request.user.save()
            return redirect('profile')
    elif request.method == 'GET':
        form = ProfileForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def saveddebates(request):
    user = request.user
    debates_list = user.savedd.all()
    page = request.GET.get('page', 1)
    debates = getpage(page, debates_list, 30)
    context = {
        'debates': debates,
    }
    return render(request, 'accounts/saveddebates.html', context)

@login_required
def savedarguments(request):
    user = request.user
    arguments_list = user.saveda.all()
    page = request.GET.get('page', 1)
    arguments = getpage(page, arguments_list, 25)
    context = {
        'arguments': arguments,
        'usercol': True,
    }
    return render(request, 'accounts/savedarguments.html', context)

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
            DeleteUser(request.user, 1)
            return redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)
    elif request.method == 'GET':
        form = DeleteUserForm(user=request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/delete.html', context)


@login_required
def usermodlogs(request):
    modactions_list = ModAction.objects.filter(user=request.user)
    page = request.GET.get('page', 1)
    modactions = getpage(page, modactions_list, 30)
    context = {
        'modactions': modactions,
    }
    return render(request, 'accounts/usermodlogs.html', context)


@admin_required
def modstatus(request, uname):
    user = get_object_or_404(User, username=uname)
    if request.method == 'POST':
        form = SetStaffForm(request.POST, instance=user, user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                ('You have successfully changed '
                + uname + '\'s mod status.'))
            return redirect(user)
    elif request.method == 'GET':
        form = SetStaffForm(instance=user, user=request.user)
    context = {
        'form': form,
        'puser': user,
    }
    return render(request, 'accounts/modstatus.html', context)