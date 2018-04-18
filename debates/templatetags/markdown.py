from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from debates.utils import clean
import markdown

register = template.Library()


@register.filter
@stringfilter
def markdownf(value, arg="0"):
    typ = int(arg)
    result = clean(markdown.markdown(
                   clean(value, typ=2),
                   extensions=['markdown.extensions.tables']),
                   typ=typ).replace('<table>', '<table class="table">')
    return mark_safe(result)
