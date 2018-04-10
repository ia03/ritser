from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
    path('cookies/', views.cookies, name='cookies'),
    path('feed/', views.feed, name='feed'),
    path('t/<slug:tname>/', views.topic, name='topic'),
    path('t/<slug:tname>/info', views.topicinfo, name='topicinfo'),
    path('t/<slug:tname>/edit', views.edittopic, name='edittopic'),
    path('t/<slug:tname>/edits', views.topicedits, name='topicedits'),
    path('t/<slug:tname>/<int:did>/', views.debate,
         {'apprs': -1}, name='debate'),
    path('t/<slug:tname>/<int:did>/approved', views.debate,
         {'apprs': 0}, name='debateapproved'),
    path('t/<slug:tname>/<int:did>/unapproved', views.debate,
         {'apprs': 1}, name='debateunapproved'),
    path('t/<slug:tname>/<int:did>/denied', views.debate,
         {'apprs': 2}, name='debatedenied'),
    path('t/<slug:tname>/<int:did>/edit', views.editdebate, name='editdebate'),
    path(
        't/<slug:tname>/<int:did>/edits',
        views.debateedits,
        name='debateedits'),
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>',
        views.argument,
        name='argument'),
    path('t/<slug:tname>/<int:did>/argument/<int:aid>/edit',
         views.editargument, name='editargument'),
    path('t/<slug:tname>/<int:did>/argument/<int:aid>/edits',
         views.argumentedits, name='argumentedits'),
    # TODO: add reports link to base.html moderate link
    path('mod/ban', views.ban, name='ban'),
    path('mod/unsuspend', views.unsuspend, name='unsuspend'),
    path('mod/delete', views.delete, name='delete'),
    path('mod/logs', views.modlogs, name='modlogs'),
    path(
        'mod/unapproved/arguments',
        views.unapprovedargs,
        name='unapprovedargs'),
    path(
        'mod/unapproved/debates',
        views.unapproveddebs,
        name='unapproveddebs'),
    path('search/', views.search, name='search'),
    path('submit_argument/', views.submitargument, name='submitargument'),
    path('submit_debate/', views.submitdebate, name='submitdebate'),
    path('submit_topic/', views.submittopic, name='submittopic'),
    path('ajax/votedebate', views.votedebate, name='votedebate'),
]
