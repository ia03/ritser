from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Topic, Debate, Argument, RevisionData
from .forms import DebateForm, ArgumentForm
from .utils import getpage, newdiff
from ipware import get_client_ip
from .templatetags.markdown import markdownf
import reversion, bleach
from reversion.models import Version

dmp = newdiff()

# Create your views here.
def index(request):
	context = {
		'nbar': 'home',
	}
	return render(request, 'debates/index.html', context)

def about(request):
	context = {
		'nbar': 'about',
	}
	return render(request, 'debates/about.html', context)

def privacy(request):
	return render(request, 'debates/privacy.html')

def terms(request):
	return render(request, 'debates/terms.html')

def topic(request, tname):

	topic = get_object_or_404(Topic, name=tname)
	mods = topic.moderators.all()
	user = request.user
	fmods = mods[:10] #first 10 mods
	sortc = request.COOKIES.get('dsort')
	sorta = request.GET.get('sort', '')
	query = topic.debates.filter(Q(approvalstatus=0) | Q(approvalstatus=1)) if (topic.slvl == 0) or (topic.slvl == 1) else topic.debates.filter(approvalstatus=0)

	if (sorta == 'top'):
		debates_list = query.order_by('-karma') #default
		sortb = "&sort=top"
	elif (sorta == 'lowest'):
		debates_list = query.order_by('karma')
		sortb = "&sort=lowest"
	elif (sorta == 'new'):
		debates_list = query.order_by('-approved_on')
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
		debates_list = query.order_by('-approved_on')
		sortb = "&sort=new"
	elif (sortc == 'random'):
		debates_list = query.order_by('?')
		sortb = "&sort=random"
	else:
		debates_list = query.order_by('-karma') #default
		sortb = "&sort=top"

	if (sorta == ''):
		sorta = sortb
	else:
		sorta = ''

	page = request.GET.get('page', 1)

	debates = getpage(page, debates_list, 30)

	if (user.is_authenticated):
		if ((topic.slvl == 1 or topic.slvl == 2) and (user.approvedargs < 10 and not user.ismod(topic))) or ((topic.slvl == 3) and not user.ismod(topic)):
			ats = False
		else:
			ats = True
		dupvoted = user.debates_upvoted.all()
		ddownvoted = user.debates_downvoted.all()
	else:
		dupvoted = []
		ddownvoted = []
		ats = False


	context = {
		'fmods': fmods,
		'minjq': True,
		'ats': ats,
		'mods': mods,
		'topic': topic,
		'ctopicn': topic.name.capitalize(),
		'debates': debates,
		'request': request,
		'sorta': sorta,
		'dupvoted': dupvoted,
		'ddownvoted': ddownvoted,
	}
	return render(request, 'debates/topic.html', context)

def votedebate(request):
	debate_id = int(request.POST.get('id'))
	vote = int(request.POST.get('vote'))
	if (not request.user.is_authenticated):
		return HttpResponse('error - not authenticated')
	debate = get_object_or_404(Debate, id=debate_id)
	user = request.user
	if (debate.users_upvoting.filter(id=user.id).count() == 1):
		ovote = 1
	elif (debate.users_downvoting.filter(id=user.id).count() == 1):
		ovote = -1
	else:
		ovote = 0

	if (vote == 1):
		if (ovote == 1):
			return HttpResponse('error - already upvoted')
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
			return HttpResponse('error - already downvoted')

	debate.save()
	return HttpResponse(debate.karma)

def topicinfo(request, tname):

	topic = get_object_or_404(Topic, name=tname)
	mods = topic.moderators.all()

	debates = topic.debates.all()
	context = {
		'mods': mods,
		'topic': topic,
		'ctopicn': topic.name.capitalize(),
		'debates': debates,
	}
	return render(request, 'debates/topicinfo.html', context)


def debate(request, tname, did, **kwargs): #use same template for different approval statuses, but change int that says what type it is
	topic = get_object_or_404(Topic, name=tname)
	debate = get_object_or_404(Debate, topic=topic, id=did)
	user = request.user

	if (kwargs['apprs'] == -1):
		if (debate.slvl == 0):
			cquery = Q(approvalstatus=0) | Q(approvalstatus=1) | Q(approvalstatus=2)
		elif (debate.slvl == 1 or debate.slvl == 2):
			cquery = Q(approvalstatus=0) | Q(approvalstatus=1)
		else:
			cquery = Q(approvalstatus=0)
	elif (kwargs['apprs'] == 0):
		cquery = Q(approvalstatus=0)
	elif (kwargs['apprs'] == 1):
		cquery = Q(approvalstatus=1)
	elif (kwargs['apprs'] == 2):
		cquery = Q(approvalstatus=2)
	querysetf = debate.arguments.filter(Q(side=0) & cquery)
	queryseta = debate.arguments.filter(Q(side=1) & cquery)

	if (kwargs['apprs'] == -1):
		argumentslistf = querysetf.order_by('approvalstatus', 'order', '-owner__approvedargs')  # filter by no. of approved arguments by user and approvalstatus
	else:
		argumentslistf = querysetf.order_by('order', '-owner__approvedargs') # filter by no. of approved arguments by user

	pagef = request.GET.get('pagef', 1)

	argumentsf = getpage(pagef, argumentslistf, 10)

	if (kwargs['apprs'] == -1):
		argumentslista = queryseta.order_by('approvalstatus', 'order', '-owner__approvedargs')  # filter by no. of approved arguments by user and approvalstatus
	else:
		argumentslista = queryseta.order_by('order', '-owner__approvedargs') # filter by no. of approved arguments by user

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
		'request': request,
		'minjq': True,
		'topic': topic,
		'argumentsf': argumentsf,
		'argumentsa': argumentsa,
		'pagef': pagef,
		'pagea': pagea,
		'apprs': kwargs['apprs'],
		'vote': vote,
	}
	return render(request, 'debates/debate.html', context)


def argument(request, tname, did, aid):

	topic = get_object_or_404(Topic, name=tname)
	debate = get_object_or_404(Debate, id=did)
	argument = get_object_or_404(Argument, id=aid)

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
				obj = form.save(commit=False)
				obj.karma = 1
				obj.save()
				obj.users_upvoting.add(user)
				reversion.set_user(user)
				client_ip, is_routable = get_client_ip(request)
				reversion.add_meta(RevisionData, ip=client_ip)
			return HttpResponseRedirect(reverse('debate', args=[form.cleaned_data['topic_name'], obj.id]))
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
def editdebate(request, tname, did):
	debate = get_object_or_404(Debate, id=did)
	oquestion = debate.question
	odescription = debate.description
	topic = get_object_or_404(Topic, name=tname)
	user = request.user

	if request.method == 'POST':
		if user.ismod(topic):
			form = DebateForm(request.POST, instance=debate, user=user, edit=2)
		else:
			form = DebateForm(request.POST, instance=debate, user=user, edit=1)
		if form.is_valid():
			with reversion.create_revision():
				diffs = dmp.diff_main(bleach.clean(oquestion), bleach.clean(form.cleaned_data['question']))
				dmp.diff_cleanupSemantic(diffs)
				titchg = dmp.diff_prettyHtml(diffs)
				diffs2 = dmp.diff_main(markdownf(odescription), markdownf(form.cleaned_data['description']))
				dmp.diff_cleanupSemantic(diffs2)
				bodchg = dmp.diff_prettyHtml(diffs2)
				debate = form.save()
				reversion.set_user(request.user)
				client_ip, is_routable = get_client_ip(request)
				reversion.add_meta(RevisionData, ip=client_ip, titchg=titchg, bodchg=bodchg)
			return HttpResponseRedirect(reverse('debate', args=[tname, did]))
	else:
		if user.ismod(topic):
			form = DebateForm(instance=debate, user=user, edit=2)
		else:
			form = DebateForm(instance=debate, user=user, edit=1)
	context = {
		'form': form,
		'debate': debate,
	}
	return render(request, 'debates/edit_debate.html', context)

@login_required()
def submitargument(request):
	user = request.user
	if request.method == 'POST':
		form = ArgumentForm(request.POST, user=user, edit=0)
		if form.is_valid():
			
			with reversion.create_revision():
				obj = form.save()
				reversion.set_user(user)
				client_ip, is_routable = get_client_ip(request)
				reversion.add_meta(RevisionData, ip=client_ip)
			return HttpResponseRedirect(reverse('argument', args=[obj.topic.name, obj.debate.id, obj.id]))
			
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
def editargument(request, tname, did, aid):
	argument = get_object_or_404(Argument, id=aid)
	otitle = argument.title
	obody = argument.body
	topic = get_object_or_404(Topic, name=tname)
	user = request.user

	if request.method == 'POST':
		if user.ismod(topic):
			form = ArgumentForm(request.POST, instance=argument, user=user, edit=2)
		else:
			form = ArgumentForm(request.POST, instance=argument, user=user, edit=1)
		if form.is_valid():
			
		
			with reversion.create_revision():
				diffs = dmp.diff_main(bleach.clean(otitle), bleach.clean(form.cleaned_data['title']))
				dmp.diff_cleanupSemantic(diffs)
				titchg = dmp.diff_prettyHtml(diffs)
				diffs2 = dmp.diff_main(markdownf(obody), markdownf(form.cleaned_data['body']))
				dmp.diff_cleanupSemantic(diffs2)
				bodchg = dmp.diff_prettyHtml(diffs2)
				argument = form.save()
				reversion.set_user(request.user)
				client_ip, is_routable = get_client_ip(request)
				reversion.add_meta(RevisionData, ip=client_ip, titchg=titchg, bodchg=bodchg)
			return HttpResponseRedirect(reverse('argument', args=[tname, did, aid]))
		
	else:
		if user.ismod(topic):
			form = ArgumentForm(instance=argument, user=user, edit=2)
		else:
			form = ArgumentForm(instance=argument, user=user, edit=1)
	context = {
		'form': form,
		'argument': argument,
	}
	return render(request, 'debates/edit_argument.html', context)
	
def debateedits(request, tname, did): #use same template for different approval statuses, but change int that says what type it is
	topic = get_object_or_404(Topic, name=tname)
	debate = get_object_or_404(Debate, id=did, topic=topic)
	user = request.user
	versionslist = Version.objects.get_for_object(debate)
	page = request.GET.get('page', 1)

	versions = getpage(page, versionslist, 40)
	if user.is_authenticated:
		isadmin = user.isadmin()
	else:
		isadmin = False
	print (isadmin)

	context = {
		'debate': debate,
		'user': user,
		'topic': topic,
		'request': request,
		'versions': versions,
		'isadmin': isadmin,
	}
	return render(request, 'debates/debateedits.html', context)
	
def argumentedits(request, tname, did, aid):
	topic = get_object_or_404(Topic, name=tname)
	debate = get_object_or_404(Debate, id=did, topic=topic)
	argument = get_object_or_404(Argument, id=aid, debate=debate, topic=topic)
	
	user = request.user
	versionslist = Version.objects.get_for_object(argument)
	page = request.GET.get('page', 1)

	versions = getpage(page, versionslist, 40)
	if user.is_authenticated:
		isadmin = user.isadmin()
	else:
		isadmin = False
	print (isadmin)

	context = {
		'debate': debate,
		'user': user,
		'argument': argument,
		'topic': topic,
		'request': request,
		'versions': versions,
		'isadmin': isadmin,
	}
	return render(request, 'debates/argumentedits.html', context)