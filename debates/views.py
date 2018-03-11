from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Topic, Debate

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
	isint = True
	try:
		count = int(request.GET.get('count', ''))
	except:
		isint = False
	dsize = topic.debates.count()
	if (isint and count > -1 and count < dsize): #check if count is an int that is a valid element id
		s = count
		e = min(count+30, dsize)
	else: #if count is not an int that is a valid element id (or does not exist)
		s = 0
		e = min(30, dsize)


	if (sorta == 'top'):
		debates = topic.debates.order_by('-karma') #default
	elif (sorta == 'lowest'):
		debates = topic.debates.order_by('karma')
	elif (sorta == 'new'):
		debates = topic.debates.order_by('-approved_on')
	elif (sorta == 'random'):
		debates = topic.debates.order_by('?')
	elif (sortc == 'top'):
		debates = topic.debates.order_by('-karma')
	elif (sortc == 'lowest'):
		debates = topic.debates.order_by('karma')
	elif (sortc == 'new'):
		debates = topic.debates.order_by('-approved_on')
	elif (sortc == 'random'):
		debates = topic.debates.order_by('?')
	else:
		debates = topic.debates.order_by('-karma') #default

	debates = debates[s:e]
	prevb = False
	nextb = False
	if(s+30 < dsize):
		nextb = True
	if(s-30 > -1):
		prevb = True

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
		'count': s,
		'prevb': prevb,
		'nextb': nextb,
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


def debate(request, tname, did): #use same template for different approval statuses, but change int that says what type it is
	topic = get_object_or_404(Topic, name=tname)
	debate = get_object_or_404(Debate, topic=topic, id=did)

	isint = True
	try:
		count = int(request.GET.get('count', ''))
	except:
		isint = False
	asize = debate.arguments.count()
	if (isint and count > -1 and count < asize): #check if count is an int that is a valid element id
		s = count
		e = min(count+10, asize)
	else: #if count is not an int that is a valid element id (or does not exist)
		s = 0
		e = min(10, asize)

		arguments = debate.arguments.order_by('-owner__approvedargs')[s:e] # filter by no. of approved arguments by user
		prevb = False
		nextb = False
		if(s+10 < asize):
			nextb = True
		if(s-10 > -1):
			prevb = True


	if (request.user.is_authenticated):
		if (debate.users_upvoting.filter(id=request.user.id).count() == 1):
			vote = 1
		elif (debate.users_downvoting.filter(id=request.user.id).count() == 1):
			vote = -1
		else:
			vote = 0

	context = {
		'debate': debate,
		'minjq': True,
		'count': s,
		'topic': topic,
		'arguments': arguments,
		'vote': vote,
	}
	return render(request, 'debates/debate.html', context)
