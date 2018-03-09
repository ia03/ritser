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
	fmods = topic.moderators.all()[:10] #first 10 mods
	mods = topic.moderators.all()

	debates = topic.debates.all()
	context = {
		'fmods' : fmods,
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
