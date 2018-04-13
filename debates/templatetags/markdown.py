from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from debates.utils import clean
import markdown
import bleach

register = template.Library()


@register.filter
@stringfilter
def markdownf(value, arg="0"):
    typ = int(arg)
    result = clean(markdown.markdown(
                   value,
                   extensions=['markdown.extensions.tables']), typ=typ)
    return mark_safe(result)
