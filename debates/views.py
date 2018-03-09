from django.shortcuts import render, get_object_or_404
#from django.http import HttpResponse, Http404
from .models import Topic

# Create your views here.
def index(request):
	context = {
		'nbar': 'home',
	}
	return render(request, 'debates/index.html', context)

def topic(request, tname):

	topic = get_object_or_404(Topic, name=tname)


	debates = topic.debates.all()
	context = {
		'topic': topic,
		'debates': debates,
	}
	return render(request, 'debates/topic.html', context)

def privacy(request):
	return render(request, 'debates/privacy.html')

def terms(request):
	return render(request, 'debates/terms.html')
