from django.shortcuts import render, get_object_or_404
#from django.http import HttpResponse, Http404
from .models import Topic

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
	count = request.GET.get('count', '')
	debatesq = topic.debates.all()
	if (isinstance(count, int) and count > -1 and count < len(debatesq)): #check if count is an int that is a valid element id
		s = count
		e = min(count+30, len(debatesq))
	else: #if count is not an int that is a valid element id (or does not exist)
		s = 0
		e = min(30, len(debatesq))


	if (sorta == 'top'):
		debates = topic.debates.order_by('-karma') #default
	elif (sorta == 'new'):
		debates = topic.debates.order_by('-approved_on')
	elif (sorta == 'random'):
		debates = topic.debates.order_by('?')
	elif (sortc == 'top'):
		debates = topic.debates.order_by('-karma')
	elif (sortc == 'new'):
		debates = topic.debates.order_by('-approved_on')
	elif (sortc == 'random'):
		debates = topic.debates.order_by('?')
	else:
		debates = topic.debates.order_by('-karma') #default

	debates = debates[s:e]

	context = {
		'fmods': fmods,
		'mods': mods,
		'topic': topic,
		'ctopicn': topic.name.capitalize(),
		'debates': debates,
	}
	return render(request, 'debates/topic.html', context)

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
