from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import PermissionDenied
from .models import Topic, Debate, Argument, Report, RevisionData
from .forms import (DebateForm, ArgumentForm, TopicForm, BanForm,
                    UnsuspendForm, DeleteForm, MoveForm, UpdateSlvlForm,
                    ReportForm,)
from .utils import getpage, newdiff, debateslist, htmldiffs, clean, able_to_submit
from accounts.utils import DeleteUser
from accounts.models import User, ModAction, SavedDebate, SavedArgument
from accounts.decorators import mod_required, gmod_required
from ipware import get_client_ip
import reversion
from reversion.models import Version
from haystack.query import SearchQuerySet
from allauth.account.decorators import verified_email_required
from itertools import chain

# Create your views here.


def index(request):
    context = {
        'nbar': 'home',
        'oendjs': True,
    }
    return render(request, 'debates/index.html', context)


def about(request):
    context = {
        'nbar': 'about',
    }
    return render(request, 'debates/about.html', context)


def rules(request):
    return render(request, 'debates/rules.html')


def privacy(request):
    return render(request, 'debates/privacy.html')


def terms(request):
    return render(request, 'debates/terms.html')


def topic(request, tname):

    topic = get_object_or_404(Topic, name=tname)
    mods = topic.moderators.all()
    user = request.user
    fmods = mods[:10]  # first 10 mods
    sortc = request.COOKIES.get('dsort')
    sorta = request.GET.get('sort', '')
    query = debateslist(topic)

    if (sorta == 'top'):
        debates_list = query.order_by('-karma')  # default
        sortb = "&sort=top"
    elif (sorta == 'lowest'):
        debates_list = query.order_by('karma')
        sortb = "&sort=lowest"
    elif (sorta == 'new'):
        if topic.slvl > 1:
            debates_list = query.order_by('-approved_on')
        else:
            debates_list = query.order_by('-created_on')
        sortb = "&sort=new"
    elif (sorta == 'random'):
        debates_list = query.order_by('?')
        sortb = "&sort=random"
    elif (sortc == 'top'):
        debates_list = query.order_by('-karma')
        sortb = "&sort=top"
    elif (sortc == 'lowest'):
        debates_list = query.order_by('karma')
        sortb = "&sort=lowest"
    elif (sortc == 'new'):
        if topic.slvl > 1:
            debates_list = query.order_by('-approved_on')
        else:
            debates_list = query.order_by('-created_on')
        sortb = "&sort=new"
    elif (sortc == 'random'):
        debates_list = query.order_by('?')
        sortb = "&sort=random"
    else:
        debates_list = query.order_by('-karma')  # default
        sortb = "&sort=top"

    if (sorta == ''):
        sorta = sortb
    else:
        sorta = ''

    page = request.GET.get('page', 1)

    debates = getpage(page, debates_list, 30)

    context = {
        'fmods': fmods,
        'able_to_submit': able_to_submit(user, topic),
        'mods': mods,
        'topic': topic,
        'ctopicn': topic.name.capitalize(),
        'debates': debates,
        'sorta': sorta,
        'topicdebateslist': True,
    }
    return render(request, 'debates/topic.html', context)


def topicinfo(request, tname):

    topic = get_object_or_404(Topic, name=tname)
    mods = topic.moderators.all()

    debates = topic.debates.all()
    context = {
        'mods': mods,
        'able_to_submit': able_to_submit(request.user, topic),
        'topic': topic,
        'ctopicn': topic.name.capitalize(),
        'debates': debates,
    }
    return render(request, 'debates/topicinfo.html', context)


def debate(request, tname, did, ds=None):
    topic = get_object_or_404(Topic, name=tname)
    debate = get_object_or_404(Debate, id=did)
    if debate.topic != topic or ds != debate.slugify():
        return redirect(debate)
    user = request.user
    try:
        apprs = int(request.GET.get('apprs', '-1'))
    except ValueError:
        return redirect(debate)
    if (apprs == -1):
        if (debate.slvl == 0):
            cquery = Q(
                approvalstatus=0) | Q(
                approvalstatus=1) | Q(
                approvalstatus=2)
        elif (debate.slvl == 1 or debate.slvl == 2):
            cquery = Q(approvalstatus=0) | Q(approvalstatus=1)
        else:
            cquery = Q(approvalstatus=0)
    elif (apprs == 0):
        cquery = Q(approvalstatus=0)
    elif (apprs == 1):
        cquery = Q(approvalstatus=1)
    elif (apprs == 2):
        cquery = Q(approvalstatus=2)
    else:
        return redirect(debate)
    querysetf = debate.arguments.filter(Q(side=0) & cquery)
    queryseta = debate.arguments.filter(Q(side=1) & cquery)

    if (apprs == -1):
        # filter by no. of approved arguments by user and approvalstatus
        argumentslistf = querysetf.order_by(
            'approvalstatus', 'order', '-owner__approvedargs')
    else:
        # filter by no. of approved arguments by user
        argumentslistf = querysetf.order_by('order', '-owner__approvedargs')

    pagef = request.GET.get('pagef', 1)

    argumentsf = getpage(pagef, argumentslistf, 10)

    if (apprs == -1):
        # filter by no. of approved arguments by user and approvalstatus
        argumentslista = queryseta.order_by(
            'approvalstatus', 'order', '-owner__approvedargs')
    else:
        # filter by no. of approved arguments by user
        argumentslista = queryseta.order_by('order', '-owner__approvedargs')

    pagea = request.GET.get('pagea', 1)

    argumentsa = getpage(pagea, argumentslista, 10)

    if (user.is_authenticated):
        if (debate.users_upvoting.filter(id=user.id).count() == 1):
            vote = 1
        elif (debate.users_downvoting.filter(id=user.id).count() == 1):
            vote = -1
        else:
            vote = 0
    else:
        vote = 0



    context = {
        'debate': debate,
        'topic': topic,
        'argumentsf': argumentsf,
        'argumentsa': argumentsa,
        'pagef': pagef,
        'pagea': pagea,
        'apprs': apprs,
        'vote': vote,
        'debv': True,
        'usercol': True,
    }
    return render(request, 'debates/debate.html', context)


def argument(request, tname, did, aid, ds=None, ars=None):
    topic = get_object_or_404(Topic, name=tname)
    debate = get_object_or_404(Debate, id=did)
    argument = get_object_or_404(Argument, id=aid)
    if argument.debate != debate or argument.topic != topic or (
        debate.slugify() != ds or argument.slugify() != ars):
        return redirect(argument)

    context = {
        'argument': argument,
        'topic': topic,
        'debate': debate,
    }
    return render(request, 'debates/argument.html', context)


@login_required
def submitdebate(request):
    user = request.user
    if request.method == 'POST':
        form = DebateForm(request.POST, user=user, edit=0)
        if form.is_valid():
            with reversion.create_revision():
                titchg = htmldiffs(
                   '',
                   form.cleaned_data['question'])
                bodchg = htmldiffs(
                   '',
                   form.cleaned_data['description'])
                debate = form.save(commit=False)
                debate.karma = 1
                debate.save()
                debate.users_upvoting.add(user)
                reversion.set_user(user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                RevisionData,
                ip=client_ip,
                titchg=titchg,
                bodchg=bodchg)
            messages.success(
                    request,
                    ('You have successfully submitted debate '
                     + debate.question))
            return redirect(debate)
    else:
        tname = request.GET.get('topic', '')
        question = request.GET.get('question', '')
        description = request.GET.get('description', '')
        data = {
            'topic_name': tname,
            'question': question,
            'description': description,
        }

        form = DebateForm(initial=data, user=user, edit=0)
    context = {
        'form': form,
    }
    return render(request, 'debates/submit_debate.html', context)


@login_required
def editdebate(request, tname, did, ds=None):
    debate = get_object_or_404(Debate, id=did)
    oquestion = debate.question
    odescription = debate.description
    topic = get_object_or_404(Topic, name=tname)
    if debate.topic != topic or ds != debate.slugify():
        return redirect(debate.get_edit_url())
    user = request.user

    if request.method == 'POST':
        if user.ismodof(topic):
            form = DebateForm(request.POST, instance=debate, user=user, edit=2)
        else:
            form = DebateForm(request.POST, instance=debate, user=user, edit=1)
        if form.is_valid():
            with reversion.create_revision():
                titchg = htmldiffs(
                                   oquestion,
                                   form.cleaned_data['question'])
                bodchg = htmldiffs(
                                   odescription,
                                   form.cleaned_data['description'])
                debate = form.save()
                reversion.set_user(request.user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                    RevisionData,
                    ip=client_ip,
                    titchg=titchg,
                    bodchg=bodchg)
                messages.success(
                    request,
                    ('You have successfully edited debate '
                     + debate.question))
            return redirect(debate)
    else:
        if user.ismodof(topic):
            form = DebateForm(instance=debate, user=user, edit=2)
        else:
            form = DebateForm(instance=debate, user=user, edit=1)
    context = {
        'form': form,
        'debate': debate,
    }
    return render(request, 'debates/edit_debate.html', context)


@login_required
def submitargument(request):
    user = request.user
    if request.method == 'POST':
        form = ArgumentForm(request.POST, user=user, edit=0)
        if form.is_valid():

            with reversion.create_revision():
                titchg = htmldiffs(
                                   '',
                                   form.cleaned_data['title'])
                bodchg = htmldiffs(
                                   '',
                                   form.cleaned_data['body'])
                argument = form.save()
                reversion.set_user(user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                    RevisionData,
                    ip=client_ip,
                    titchg=titchg,
                    bodchg=bodchg)
            messages.success(
                request,
                ('You have successfully submitted argument '
                     + argument.title))
            return redirect(argument)

    else:
        did = request.GET.get('debate', '')
        title = request.GET.get('title', '')
        body = request.GET.get('body', '')
        data = {
            'debate_id': did,
            'title': title,
            'body': body,
        }

        form = ArgumentForm(initial=data, user=user, edit=0)
    context = {
        'form': form,
    }
    return render(request, 'debates/submit_argument.html', context)


@login_required
def editargument(request, tname, did, aid, ds=None, ars=None):
    argument = get_object_or_404(Argument, id=aid)
    debate = get_object_or_404(Debate, id=did)
    otitle = argument.title
    obody = argument.body
    topic = get_object_or_404(Topic, name=tname)
    user = request.user

    if argument.debate != debate or argument.topic != topic or (
        debate.slugify() != ds or argument.slugify() != ars):
        return redirect(argument.get_edit_url())

    if request.method == 'POST':
        if user.ismodof(topic):
            form = ArgumentForm(
                request.POST,
                instance=argument,
                user=user,
                edit=2)
        else:
            form = ArgumentForm(
                request.POST,
                instance=argument,
                user=user,
                edit=1)
        if form.is_valid():

            with reversion.create_revision():
                titchg = htmldiffs(
                                   otitle,
                                   form.cleaned_data['title'])
                bodchg = htmldiffs(
                                   obody,
                                   form.cleaned_data['body'])
                argument = form.save()
                reversion.set_user(request.user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                    RevisionData,
                    ip=client_ip,
                    titchg=titchg,
                    bodchg=bodchg)
                messages.success(
                    request,
                    'You have successfully edited argument ' + argument.title)
            return redirect(argument)

    else:
        if user.ismodof(topic):
            form = ArgumentForm(instance=argument, user=user, edit=2)
        else:
            form = ArgumentForm(instance=argument, user=user, edit=1)
    context = {
        'form': form,
        'argument': argument,
    }
    return render(request, 'debates/edit_argument.html', context)


def debateedits(request, tname, did, ds=None):
    topic = get_object_or_404(Topic, name=tname)
    debate = get_object_or_404(Debate, id=did)
    user = request.user
    if debate.topic != topic or ds != debate.slugify():
        return redirect(debate.get_edits_url())
    versionslist = Version.objects.get_for_object(debate)
    page = request.GET.get('page', 1)

    versions = getpage(page, versionslist, 40)
    if user.is_authenticated:
        isadmin = user.isadmin()
    else:
        isadmin = False

    context = {
        'debate': debate,
        'topic': topic,
        'versions': versions,
        'isadmin': isadmin,
    }
    return render(request, 'debates/debateedits.html', context)


def argumentedits(request, tname, did, aid, ds=None, ars=None):
    topic = get_object_or_404(Topic, name=tname)
    debate = get_object_or_404(Debate, id=did)
    argument = get_object_or_404(Argument, id=aid)
    if argument.debate != debate or argument.topic != topic or (
        debate.slugify() != ds or argument.slugify() != ars):
        return redirect(argument.get_edits_url())
    user = request.user
    versionslist = Version.objects.get_for_object(argument)
    page = request.GET.get('page', 1)

    versions = getpage(page, versionslist, 40)
    if user.is_authenticated:
        isadmin = user.isadmin()
    else:
        isadmin = False

    context = {
        'debate': debate,
        'argument': argument,
        'topic': topic,
        'versions': versions,
        'isadmin': isadmin,
    }
    return render(request, 'debates/argumentedits.html', context)


@login_required
def submittopic(request):
    user = request.user
    if request.method == 'POST':
        form = TopicForm(request.POST, user=user, edit=0)
        if form.is_valid():
            with reversion.create_revision():
                titchg = htmldiffs(
                    '',
                    form.cleaned_data['title'])
                bodchg = htmldiffs(
                    '',
                    form.cleaned_data['description'])
                topic = form.save(commit=False)
                topic.moderators.set(form.modsl)
                topic.save()
                reversion.set_user(user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                    RevisionData,
                    ip=client_ip,
                    titchg=titchg,
                    bodchg=bodchg)
                messages.success(
                    request,
                    ('You have successfully submitted topic '
                     + topic.name))
            return redirect(topic)

    else:
        name = request.GET.get('name', '')
        title = request.GET.get('title', '')
        description = request.GET.get('description', '')
        data = {
            'name': name,
            'title': title,
            'description': description,
        }

        form = TopicForm(initial=data, user=user, edit=0)
    context = {
        'form': form,
    }
    return render(request, 'debates/submit_topic.html', context)


@login_required
def edittopic(request, tname):
    topic = get_object_or_404(Topic, name=tname)
    otitle = topic.title
    obody = topic.description
    user = request.user

    if request.method == 'POST':
        isowner = user.isowner(topic)
        if isowner:
            form = TopicForm(request.POST, instance=topic, user=user, edit=2)
        else:
            form = TopicForm(request.POST, instance=topic, user=user, edit=1)
        if form.is_valid():
            with reversion.create_revision():
                titchg = htmldiffs(
                                   otitle,
                                   form.cleaned_data['title'])
                bodchg = htmldiffs(
                                   obody,
                                   form.cleaned_data['description'])
                topic = form.save(commit=False)
                if isowner:
                    topic.moderators.set(form.modsl)
                topic.save()
                reversion.set_user(request.user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                    RevisionData,
                    ip=client_ip,
                    titchg=titchg,
                    bodchg=bodchg)
                messages.success(
                    request,
                    'You have successfully edited topic ' + tname)
            return redirect(topic)

    elif request.method == 'GET':
        if user.isowner(topic):
            form = TopicForm(instance=topic, user=user, edit=2)
        else:
            form = TopicForm(instance=topic, user=user, edit=1)
    context = {
        'form': form,
        'topic': topic,
    }
    return render(request, 'debates/edit_topic.html', context)


def topicedits(request, tname):
    topic = get_object_or_404(Topic, name=tname)
    user = request.user
    versionslist = Version.objects.get_for_object(topic)
    page = request.GET.get('page', 1)

    versions = getpage(page, versionslist, 40)
    if user.is_authenticated:
        isadmin = user.isadmin()
    else:
        isadmin = False

    context = {
        'topic': topic,
        'versions': versions,
        'isadmin': isadmin,
    }
    return render(request, 'debates/topicedits.html', context)

@login_required
def submitreport(request):
    user = request.user
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = user
            client_ip, is_routable = get_client_ip(request)
            report.ip = client_ip
            report.content_object = form.obj
            report.save()
            messages.success(
                request,
                'You have successfully submitted a report.')
    else:
        content_type = request.GET.get('type', '')
        object_id = request.GET.get('id', '')
        data = {
            'content_type': content_type,
            'object_id': object_id,
        }
        form = ReportForm(initial=data)
    context = {
        'form': form,
    }
    return render(request, 'debates/submitreport.html', context)
'''
      AJAX VIEWS
'''
def votedebate(request):
    if request.method == 'POST':
        debate_id = int(request.POST.get('id'))
        vote = int(request.POST.get('vote'))
        user = request.user
        if not (user.is_authenticated and user.hasperm()):
            raise PermissionDenied
        debate = get_object_or_404(Debate, id=debate_id)
        if (debate.users_upvoting.filter(id=user.id).count() == 1):
            ovote = 1
        elif (debate.users_downvoting.filter(id=user.id).count() == 1):
            ovote = -1
        else:
            ovote = 0

        if (vote == 1):
            if (ovote == 1):
                return HttpResponseBadRequest('error - already upvoted')
            if (ovote == 0):
                debate.karma += 1
                debate.users_upvoting.add(user)
            if (ovote == -1):
                debate.karma += 2
                debate.users_upvoting.add(user)
                debate.users_downvoting.remove(user)
        elif (vote == 0):
            if (ovote == 1):
                debate.karma -= 1
                debate.users_upvoting.remove(user)
            if (ovote == 0):
                return HttpResponse(debate.karma)
            if (ovote == -1):
                debate.karma += 1
                debate.users_downvoting.remove(user)
        elif (vote == -1):
            if (ovote == 1):
                debate.karma -= 2
                debate.users_downvoting.add(user)
                debate.users_upvoting.remove(user)
            if (ovote == 0):
                debate.karma -= 1
                debate.users_downvoting.add(user)
            if (ovote == -1):
                return HttpResponseBadRequest('error - already downvoted')

        debate.save()
        return HttpResponse(debate.karma)
    raise Http404()

def save(request):
    if request.method == 'POST':
        pid = int(request.POST.get('id'))
        typ = int(request.POST.get('typ'))
        save = int(request.POST.get('save'))
        user = request.user
        if not user.is_authenticated:
            return HttpResponseBadRequest(
                'you must be logged in to perform that action')
        if typ == 0:
            debate = get_object_or_404(Debate, id=pid)
            if save == 0:
                if not SavedDebate.objects.filter(
                    user=user, debate=debate).exists():
                    SavedDebate.objects.create(user=user, debate=debate)
                else:
                    return HttpResponseBadRequest('error - already saved')
            else:
                SavedDebate.objects.filter(user=user, debate=debate).delete()

        else:
            argument = get_object_or_404(Argument, id=pid)
            if save == 0:
                if not SavedArgument.objects.filter(
                    user=user, argument=argument).exists():
                    SavedArgument.objects.create(user=user, argument=argument)
                else:
                    return HttpResponseBadRequest('error - already saved')
            else:
                SavedArgument.objects.filter(
                    user=user, argument=argument).delete()
        return HttpResponse('')
    raise Http404()

def closereport(request):
    if request.method == 'POST':
        rid = int(request.POST.get('id'))
        typ = int(request.POST.get('typ'))
        modnote = request.POST.get('modnote')
        user = request.user
        report = user.report(rid)
        if report.status != 0:
            return HttpResponseBadRequest('error - report already closed')
        if typ == 1 or typ == 2: #closed, action taken
            report.status = typ
        else:
            return HttpResponseBadRequest('error - invalid "typ" attribute')
        report.modnote = modnote
        report.save()
        return HttpResponse(str(typ))
    raise Http404()

'''
		MISC PAGES
'''


@login_required
def feed(request):
    user = request.user
    query = Debate.objects.none()
    topics = user.stopics.all()
    for topic in topics:
        query = query.union(
            debateslist(topic),
            all=True)
    debates_list = query.order_by('-created_on')

    page = request.GET.get('page', 1)

    debates = getpage(page, debates_list, 30)

    dupvoted = user.debates_upvoted.all()
    ddownvoted = user.debates_downvoted.all()

    context = {
        'topics': topics,
        'debates': debates,
        'dupvoted': dupvoted,
        'ddownvoted': ddownvoted,
    }
    return render(request, 'debates/feed.html', context)


def search(request):
    user = request.user
    query = request.GET.get('q', '')
    tname = request.GET.get('t', '')
    if tname != '':
        topic = get_object_or_404(Topic, name=tname)
        debates_list = SearchQuerySet().filter(content=query, topic=topic)
    else:
        debates_list = SearchQuerySet().filter(content=query)

    page = request.GET.get('page', 1)

    debatesq = getpage(page, debates_list, 30)
    debates = [d.object for d in debatesq]

    if (user.is_authenticated):
        dupvoted = user.debates_upvoted.all()
        ddownvoted = user.debates_downvoted.all()
    else:
        dupvoted = []
        ddownvoted = []
    context = {
        'debatesq': debatesq,
        'debates': debates,
        'query': query,
        'tname': tname,
        'dupvoted': dupvoted,
        'ddownvoted': ddownvoted,
    }
    return render(request, 'debates/search.html', context)


'''
		MODERATOR PAGES
'''


@gmod_required
def ban(request):
    if request.method == 'POST':
        form = BanForm(request.POST, user=request.user)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            t = form.cleaned_data['terminate']
            bannote = form.cleaned_data['bannote']
            bandate = form.cleaned_data['bandate']
            if t:
                DeleteUser(user, 3, bannote=bannote)
                ModAction.objects.create(
                    user=user, mod=request.user, action=2, modnote=bannote)
                messages.success(
                    request, 'You have successfully terminated this user.')
            else:
                user.active = 2
                user.bandate = bandate
                user.bannote = bannote
                user.save()
                ModAction.objects.create(
                    user=user,
                    mod=request.user,
                    action=0,
                    modnote=bannote,
                    until=bandate)
                messages.success(
                    request, 'You have successfully suspended this user.')
    elif request.method == 'GET':
        user = request.GET.get('user', '')
        data = {
            'username': user,
        }
        form = BanForm(initial=data, user=request.user)
    context = {
        'form': form,
    }
    return render(request, 'debates/mod/ban.html', context)


@gmod_required
def unsuspend(request):
    if request.method == 'POST':
        form = UnsuspendForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            user.active = 0
            user.save()
            ModAction.objects.create(user=user, mod=request.user, action=1)
            messages.success(
                request, 'You have successfully unsuspended this user.')
    elif request.method == 'GET':
        user = request.GET.get('user', '')
        data = {
            'username': user,
        }
        form = UnsuspendForm(initial=data)
    context = {
        'form': form,
    }
    return render(request, 'debates/mod/unsuspend.html', context)


@gmod_required
def move(request):
    if request.method == 'POST':
        form = MoveForm(request.POST)
        if form.is_valid():
            with reversion.create_revision():
                post = form.post
                pid = form.cleaned_data['fid']
                pid2 = form.cleaned_data['sid']
                post2 = form.post2
                S1 = ('You have successfully moved all arguments in the first '
                      'debate to the second debate.')
                S2 = ('You have successfully moved all debates in the first '
                      'topic to the second topic.')
                L1 = '[Moved from debate %s to debate %s.]'
                L2 = '[Moved from topic %s to topic %s.]'
                L3 = '[Moderator Action]'
                f = '<span class="text-secondary">%s</span>'

                if isinstance(post, Debate):
                    arguments = Argument.objects.filter(debate=post)
                    difft = (post.topic_id != post2.topic_id)
                    arguments.update(debate=post2)
                    for argument in arguments:
                        if difft:
                            argument.topic = post2.topic
                        argument.save()
                    action = 5
                    messages.success(request, S1)
                    L = L1
                else:
                    debates = Debate.objects.filter(topic=post)
                    debates.update(topic=post2)
                    for debate in debates:
                        debate.save()
                    arguments = Argument.objects.filter(topic=post)
                    arguments.update(topic=post2)
                    for argument in arguments:
                        argument.save()
                    action = 6
                    messages.success(request, S2)
                    L = L2
                ModAction.objects.create(
                    user=post.owner,
                    mod=request.user,
                    action=action,
                    pid=pid,
                    pid2=pid2)
                L = L % (pid, pid2)
                L = f % L
                L3 = f % L3
                reversion.set_user(request.user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                    RevisionData,
                    ip=client_ip,
                    titchg=L3,
                    bodchg=L,
                    modaction=True)
    elif request.method == 'GET':
        form = MoveForm()
    context = {
        'form': form,
    }
    return render(request, 'debates/mod/move.html', context)


@gmod_required
def delete(request):
    if request.method == 'POST':
        form = DeleteForm(request.POST)
        if form.is_valid():
            with reversion.create_revision():
                titchg = '[DELETED]'
                bodchg = '[DELETED]'
                f = '<span class="text-secondary">%s</span>'
                titchg = f % titchg
                bodchg = f % bodchg
                post = form.post
                versions = Version.objects.get_for_object(post)
                versions.delete()
                post.approvalstatus = 3
                post.modnote = "[DELETED]"
                if isinstance(post, Argument):
                    post.title = "[DELETED]"
                    post.body = "[DELETED]"
                    messages.success(
                        request, ('You have successfully deleted the selected '
                                  'argument.'))
                    action = 3
                else:
                    post.question = "[DELETED]"
                    post.description = "[DELETED]"
                    messages.success(
                        request, ('You have successfully deleted the selected '
                                  'debate.'))
                    action = 4
                ModAction.objects.create(
                    user=post.owner,
                    mod=request.user,
                    action=action,
                    pid=post.id)
                post.owner = request.user
                post.save()
                reversion.set_user(request.user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                    RevisionData,
                    ip=client_ip,
                    titchg=titchg,
                    bodchg=bodchg,
                    modaction=True)
    elif request.method == 'GET':
        form = DeleteForm()
    context = {
        'form': form,
    }
    return render(request, 'debates/mod/delete.html', context)


@gmod_required
def modlogs(request):
    username = request.GET.get('user', '')
    modname = request.GET.get('mod', '')
    modactions_list = ModAction.objects.all()
    if username != '':
        user = get_object_or_404(User, username=username)
        modactions_list = modactions_list.filter(user=user)
    if modname != '':
        mod = get_object_or_404(User, username=modname)
        modactions_list = modactions_list.filter(mod=mod)
    page = request.GET.get('page', 1)
    modactions = getpage(page, modactions_list, 50)
    context = {
        'username': username,
        'mod': modname,
        'modactions': modactions,
        'usercol': True,
    }
    return render(request, 'debates/mod/modlogs.html', context)


@gmod_required
def staff(request, **kwargs):
    typ = kwargs['typ']
    if typ == 0:
        q = ~Q(modstatus=0)
    elif typ == 1:
        q = Q(modstatus=1)
    elif typ == 2:
        q = Q(modstatus=2)
    elif typ == 3:
        q = Q(modstatus=3)
    staff_list = User.objects.filter(q)
    staff_list = staff_list.order_by('-modstatus', 'date_joined')
    page = request.GET.get('page', 1)
    staff = getpage(page, staff_list, 50)
    context = {
        'staff': staff,
        'typ': typ,
        'allcount': User.objects.filter(~Q(modstatus=0)).count(),
        'gmodcount': User.objects.filter(Q(modstatus=1)).count(),
        'admincount': User.objects.filter(Q(modstatus=2)).count(),
        'ownercount': User.objects.filter(Q(modstatus=3)).count(),
    }
    return render(request, 'debates/mod/staff.html', context)

@mod_required
def unapprovedargs(request):
    user = request.user
    unapprovedargs_list = user.unapprovedarguments()
    page = request.GET.get('page', 1)
    unapprovedargs = getpage(page, unapprovedargs_list, 25)
    context = {
        'arguments': unapprovedargs,
        'editalist': True,
        'usercol': True,
    }
    return render(request, 'debates/mod/unapprovedargs.html', context)


@mod_required
def unapproveddebs(request):
    user = request.user
    unapproveddebs_list = user.unapproveddebates()
    page = request.GET.get('page', 1)
    unapproveddebs = getpage(page, unapproveddebs_list, 30)
    context = {
        'debates': unapproveddebs,
        'editdlist': True,

    }
    return render(request, 'debates/mod/unapproveddebs.html', context)


@mod_required
def slvls(request):
    if request.method == 'POST':
        form = UpdateSlvlForm(request.POST, user=request.user)
        if form.is_valid():
            with reversion.create_revision():
                T = '[Moderator Action]'
                f = '<span class="text-secondary">%s</span>'
                L = '[Changed security level of debates in %s to %d.]'
                T = f % T
                L = L % (form.cleaned_data['tname'], form.cleaned_data['slvl'])
                L = f % L
                debates = form.topic.debates.all()
                debates.update(slvl=form.cleaned_data['slvl'])
                for debate in debates:
                    debate.save()
                messages.success(
                    request, ('You have successfully changed the security levels '
                              ' of all debates in the selected topic.'))
                reversion.set_user(request.user)
                client_ip, is_routable = get_client_ip(request)
                reversion.add_meta(
                    RevisionData,
                    ip=client_ip,
                    titchg=T,
                    bodchg=L,
                    modaction=True)
    elif request.method == 'GET':
        form = UpdateSlvlForm(user=request.user)
    context = {
        'form': form,
    }
    return render(request, 'debates/mod/slvls.html', context)

@mod_required
def argreports(request):
    user = request.user
    argreports_list = user.argreports()
    page = request.GET.get('page', 1)
    argreports = getpage(page, argreports_list, 30)
    context = {
        'reports': argreports,
        'rulecol': True,
        'usercol': True,
    }
    return render(request, 'debates/mod/argreports.html', context)

@mod_required
def debreports(request):
    user = request.user
    debreports_list = user.debreports()
    page = request.GET.get('page', 1)
    debreports = getpage(page, debreports_list, 30)
    context = {
        'reports': debreports,
        'rulecol': True,
        'usercol': True,
    }
    return render(request, 'debates/mod/debreports.html', context)

@gmod_required
def topicreports(request):
    user = request.user
    topicreports_list = user.topicreports()
    page = request.GET.get('page', 1)
    topicreports = getpage(page, topicreports_list, 30)
    context = {
        'reports': topicreports,
        'rulecol': True,
        'usercol': True,
    }
    return render(request, 'debates/mod/topicreports.html', context)

@gmod_required
def userreports(request):
    user = request.user
    userreports_list = user.userreports()
    page = request.GET.get('page', 1)
    userreports = getpage(page, userreports_list, 30)
    context = {
        'reports': userreports,
        'rulecol': True,
        'usercol': True,
    }
    return render(request, 'debates/mod/userreports.html', context)

@mod_required
def report(request, rid):
    report = request.user.report(rid)
    reported = report.content_object
    ctype = report.content_type.model


    context = {
        'report': report,
        'reported': reported,
        'ctype': ctype,
    }
    return render(request, 'debates/mod/report.html', context)
