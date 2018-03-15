from django.urls import path, re_path
from . import views


urlpatterns = [
	path('', views.index, name='index'),
	path('privacy', views.privacy, name='privacy'),
	path('terms', views.terms, name='terms'),
	path('about', views.about, name='about'),
	path('t/<slug:tname>/', views.topic, name='topic'),
	path('t/<slug:tname>/info', views.topicinfo, name='topicinfo'),
	path('t/<slug:tname>/<int:did>/', views.debate, {'apprs': -1}, name='debate'),
	path('t/<slug:tname>/<int:did>/edit', views.editdebate, name='editdebate'),
	path('t/<slug:tname>/<int:did>/approved', views.debate, {'apprs': 0}, name='debateapproved'),
	path('t/<slug:tname>/<int:did>/unapproved', views.debate, {'apprs': 1}, name='debateunapproved'),
	path('t/<slug:tname>/<int:did>/denied', views.debate, {'apprs': 2}, name='debatedenied'),
	path('t/<slug:tname>/<int:did>/argument/<int:aid>', views.argument, name='argument'),
	path('t/<slug:tname>/<int:did>/argument/<int:aid>/edit', views.editargument, name='editargument'),
	path('submit_argument', views.submitargument, name='submitargument'),
	path('submit_debate', views.submitdebate, name='submitdebate'),
	path('ajax/votedebate', views.votedebate, name='votedebate'),
]
