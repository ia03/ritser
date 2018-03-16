from django import template

register = template.Library()

@register.inclusion_tag('paginator.html')
def paginator(obj, request):
    return {'obj': obj, 'request': request,}