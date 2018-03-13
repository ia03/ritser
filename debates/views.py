from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Topic, Debate, Argument

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
	fmods = mods[:10] #first 10 mods
	sortc = request.COOKIES.get('dsort')
	sorta = request.GET.get('sort', '')

	if (sorta == 'top'):
		debates_list = topic.debates.order_by('-karma') #default
		sortb = "&sort=top"
	elif (sorta == 'lowest'):
		debates_list = topic.debates.order_by('karma')
		sortb = "&sort=lowest"
	elif (sorta == 'new'):
		debates_list = topic.debates.order_by('-approved_on')
		sortb = "&sort=new"
	elif (sorta == 'random'):
		debates_list = topic.debates.order_by('?')
		sortb = "&sort=random"
	elif (sortc == 'top'):
		debates_list = topic.debates.order_by('-karma')
		sortb = "&sort=top"
	elif (sortc == 'lowest'):
		debates_list = topic.debates.order_by('karma')
		sortb = "&sort=lowest"
	elif (sortc == 'new'):
		debates_list = topic.debates.order_by('-approved_on')
		sortb = "&sort=new"
	elif (sortc == 'random'):
		debates_list = topic.debates.order_by('?')
		sortb = "&sort=random"
	else:
		debates_list = topic.debates.order_by('-karma') #default
		sortb = "&sort=top"

	if (sorta == ''):
		sorta = sortb
	else:
		sorta = ''

	page = request.GET.get('page', 1)

	paginator = Paginator(debates_list, 30)

	try:
		debates = paginator.page(page)
	except (EmptyPage, PageNotAnInteger):
		debates = paginator.page(1)


	if (request.user.is_authenticated):
		dupvoted = request.user.debates_upvoted.all()
		ddownvoted = request.user.debates_downvoted.all()
	else:
		dupvoted = []
		ddownvoted = []



	context = {
		'fmods': fmods,
		'minjq': True,
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

	if (debate.users_upvoting.filter(id=request.user.id).count() == 1):
		ovote = 1
	elif (debate.users_downvoting.filter(id=request.user.id).count() == 1):
		ovote = -1
	else:
		ovote = 0

	if (vote == 1):
		if (ovote == 1):
			return HttpResponse('error - already upvoted')
		if (ovote == 0):
			debate.karma += 1
			debate.users_upvoting.add(request.user)
		if (ovote == -1):
			debate.karma += 2
			debate.users_upvoting.add(request.user)
			debate.users_downvoting.remove(request.user)
	elif (vote == 0):
		if (ovote == 1):
			debate.karma -= 1
			debate.users_upvoting.remove(request.user)
		if (ovote == 0):
			return HttpResponse(debate.karma)
		if (ovote == -1):
			debate.karma += 1
			debate.users_downvoting.remove(request.user)
	elif (vote == -1):
		if (ovote == 1):
			debate.karma -= 2
			debate.users_downvoting.add(request.user)
			debate.users_upvoting.remove(request.user)
		if (ovote == 0):
			debate.karma -= 1
			debate.users_downvoting.add(request.user)
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


	if (kwargs['apprs'] == -1):
		if (debate.slvl == 0):
			cquery = Q(approvedstatus=0) | Q(approvedstatus=1) | Q(approvedstatus=2)
		elif (debate.slvl == 1 or debate.slvl == 2):
			cquery = Q(approvedstatus=0) | Q(approvedstatus=1)
		else:
			cquery = Q(approvedstatus=0)
	elif (kwargs['apprs'] == 0):
		cquery = Q(approvedstatus=0)
	elif (kwargs['apprs'] == 1):
		cquery = Q(approvedstatus=1)
	elif (kwargs['apprs'] == 2):
		cquery = Q(approvedstatus=2)
	querysetf = debate.arguments.filter(Q(side=0) & cquery)
	queryseta = debate.arguments.filter(Q(side=1) & cquery)

	if (kwargs['apprs'] == -1):
		argumentslistf = querysetf.order_by('approvedstatus', 'order', '-owner__approvedargs')  # filter by no. of approved arguments by user and approvedstatus
	else:
		argumentslistf = querysetf.order_by('order', '-owner__approvedargs') # filter by no. of approved arguments by user

	pagef = request.GET.get('pagef', 1)

	paginatorf = Paginator(argumentslistf, 10)
	try:
		argumentsf = paginatorf.page(pagef)
	except (EmptyPage, PageNotAnInteger):
		argumentsf = paginatorf.page(1)




	if (kwargs['apprs'] == -1):
		argumentslista = queryseta.order_by('approvedstatus', 'order', '-owner__approvedargs')  # filter by no. of approved arguments by user and approvedstatus
	else:
		argumentslista = queryseta.order_by('order', '-owner__approvedargs') # filter by no. of approved arguments by user

	pagea = request.GET.get('pagea', 1)

	paginatora = Paginator(argumentslista, 10)
	try:
		argumentsa = paginatora.page(pagea)
	except (EmptyPage, PageNotAnInteger):
		argumentsa = paginatora.page(1)

	if (request.user.is_authenticated):
		if (debate.users_upvoting.filter(id=request.user.id).count() == 1):
			vote = 1
		elif (debate.users_downvoting.filter(id=request.user.id).count() == 1):
			vote = -1
		else:
			vote = 0
	else:
		vote = 0

	context = {
		'debate': debate,
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
		'argument': argument
	}
	return render(request, 'debates/argument.html', context)
