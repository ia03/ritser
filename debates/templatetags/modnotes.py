from django import template

register = template.Library()

@register.inclusion_tag('modnotes.html')
def modnotes(modnotes):
    return {'modnotes': modnotes,}