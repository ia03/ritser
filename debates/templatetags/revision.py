from django import template
from debates.models import Topic, Debate, Argument, RevisionData
from django.utils.safestring import mark_safe
from accounts.models import User

register = template.Library()


@register.filter(name='field')
def field(version, name):
    return version.field_dict[name]


@register.filter(name='moderators')
def moderators(version):
    mods = []
    for modid in version.field_dict['moderators']:
        mods.append(User.objects.get(id=modid))
    return mods


@register.filter(name='titchg')
def titchg(version):
    return mark_safe(
        '<pre><code>%s</code></pre>' % RevisionData.objects.get(
            revision=version.revision).titchg)


@register.filter(name='bodchg')
def bodchg(version):
    return mark_safe(
        '<pre><code>%s</code></pre>' % RevisionData.objects.get(
            revision=version.revision).bodchg)

@register.filter(name='modaction')
def modaction(version):
    return RevisionData.objects.get(revision=version.revision).modaction

@register.filter(name='ip')
def ip(version):
    return RevisionData.objects.get(revision=version.revision).ip


@register.filter(name='owner')
def owner(version):
    return User.objects.get(id=version.field_dict['owner_id'])


@register.filter(name='topic')
def topic(version):
    return Topic.objects.get(name=version.field_dict['topic_id'])


@register.filter(name='debate')
def debate(version):
    return Debate.objects.get(id=version.field_dict['debate_id'])


@register.filter(name='url')
def url(obj):
    return obj.get_absolute_url()


@register.filter(name='username')
def username(obj):
    return obj.get_username()


@register.filter(name='question')
def question(obj):
    return obj.question
