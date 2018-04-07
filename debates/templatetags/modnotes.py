from django import template

register = template.Library()

@register.inclusion_tag('modnotes.html')
def modnotes(modnotes, index=0):
    return {'modnotes': modnotes,
        'index': index,
    }