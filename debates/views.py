from django.shortcuts import render
from django.http import HttpResponse, Http404
from .models import Topic

# Create your views here.
def index(request):
	context = {
		'nbar': 'home',
	}
	return render(request, 'debates/topic.html', context)

def topic(request, tname):
	try:
		topic = Topic.objects.get(name=tname)
	except Topic.DoesNotExist:
		raise Http404("Topic does not exist.")

	debates = topic.debates.all()
	context = {
		'topic': topic,
		'debates': debates,
	}
	return render(request, 'debates/topic.html', context)
