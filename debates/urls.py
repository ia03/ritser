from django.urls import path, re_path
from django.contrib.sitemaps.views import sitemap
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
    path('cookies/', views.cookies, name='cookies'),
    #Static pages above listed in sitemap
    path('feed/', views.feed, name='feed'),
    path('t/<slug:tname>/', views.topic, name='topic'),
    path('t/<slug:tname>/info', views.topicinfo, name='topicinfo'),
    path('t/<slug:tname>/edit', views.edittopic, name='edittopic'),
    path('t/<slug:tname>/edits', views.topicedits, name='topicedits'),
    path('t/<slug:tname>/<int:did>,<slug:ds>/', views.debate,
         name='debate'),
    path('t/<slug:tname>/<int:did>,<slug:ds>/edit/', views.editdebate,
         name='editdebate'),
    path(
        't/<slug:tname>/<int:did>,<slug:ds>/edits/',
        views.debateedits,
        name='debateedits'),
    path(
        't/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>,<slug:ars>/',
        views.argument,
        name='argument'),
    path('t/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>,<slug:ars>/edit/',
         views.editargument, name='editargument'),
    path('t/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>,<slug:ars>/edits/',
         views.argumentedits, name='argumentedits'),
    # TODO: add reports link to base.html moderate link
    path('mod/ban/', views.ban, name='ban'),
    path('mod/unsuspend/', views.unsuspend, name='unsuspend'),
    path('mod/move/', views.move, name='move'),
    path('mod/delete/', views.delete, name='delete'),
    path('mod/logs/', views.modlogs, name='modlogs'),
    path('mod/staff/', views.staff,
         {'typ': 0}, name='staff'),
    path('mod/staff/gmods/', views.staff,
         {'typ': 1}, name='staffgmods'),
    path('mod/staff/admins/', views.staff,
         {'typ': 2}, name='staffadmins'),
    path('mod/staff/owners/', views.staff,
         {'typ': 3}, name='staffowners'),
    path(
        'mod/unapproved/arguments/',
        views.unapprovedargs,
        name='unapprovedargs'),
    path(
        'mod/unapproved/debates/',
        views.unapproveddebs,
        name='unapproveddebs'),
    path('mod/slvls/', views.slvls, name='slvls'),
    path('search/', views.search, name='search'),
    path('submit_argument/', views.submitargument, name='submitargument'),
    path('submit_debate/', views.submitdebate, name='submitdebate'),
    path('submit_topic/', views.submittopic, name='submittopic'),
    path('ajax/votedebate', views.votedebate, name='votedebate'),
    
    
    
    
    
    # These URLs will redirect as they are not pretty
    # Ugly debate URLs
    path('t/<slug:tname>/<int:did>,/', views.debate,
         name='debate'),
    path('t/<slug:tname>/<int:did>/', views.debate,
         name='debate'),
    path('t/<slug:tname>/<int:did>,/edit/', views.editdebate,
         name='editdebate'),
    path('t/<slug:tname>/<int:did>/edit/', views.editdebate,
         name='editdebate'),
    path(
        't/<slug:tname>/<int:did>,/edits/',
        views.debateedits,
        name='debateedits'),
    path(
        't/<slug:tname>/<int:did>/edits/',
        views.debateedits,
        name='debateedits'),
    # Ugly argument URLs
    path(
        't/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>,/',
        views.argument,
        name='argument'),
    path(
        't/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>/',
        views.argument,
        name='argument'),
    
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>,<slug:ars>/',
        views.argument,
        name='argument'),
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>,/',
        views.argument,
        name='argument'),
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>/',
        views.argument,
        name='argument'),
    
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>,<slug:ars>/',
        views.argument,
        name='argument'),
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>/',
        views.argument,
        name='argument'),
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>,/',
        views.argument,
        name='argument'),
        
    
    
    path(
        't/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>,/edit/',
        views.editargument,
        name='editargument'),
    path(
        't/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>/edit/',
        views.editargument,
        name='editargument'),
    
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>,<slug:ars>/edit/',
        views.editargument,
        name='editargument'),
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>,/edit/',
        views.editargument,
        name='editargument'),
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>/edit/',
        views.editargument,
        name='editargument'),
    
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>,<slug:ars>/edit/',
        views.editargument,
        name='editargument'),
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>/edit/',
        views.editargument,
        name='editargument'),
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>,/edit/',
        views.editargument,
        name='editargument'),
        
    
    
    path(
        't/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>,/edits/',
        views.editargument,
        name='argumentedits'),
    path(
        't/<slug:tname>/<int:did>,<slug:ds>/argument/<int:aid>/edits/',
        views.editargument,
        name='argumentedits'),
    
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>,<slug:ars>/edits/',
        views.editargument,
        name='argumentedits'),
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>,/edits/',
        views.editargument,
        name='argumentedits'),
    path(
        't/<slug:tname>/<int:did>,/argument/<int:aid>/edits/',
        views.editargument,
        name='argumentedits'),
    
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>,<slug:ars>/edits/',
        views.editargument,
        name='argumentedits'),
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>/edits/',
        views.editargument,
        name='argumentedits'),
    path(
        't/<slug:tname>/<int:did>/argument/<int:aid>,/edits/',
        views.editargument,
        name='editargument'),
    
]
