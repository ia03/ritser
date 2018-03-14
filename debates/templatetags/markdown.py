from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
import markdown, bleach

register = template.Library()

@register.filter
@stringfilter
def markdownf(value, arg="0"):
    type = int(arg)
    if (type == 0):
        result = bleach.clean(markdown.markdown(value, extensions=['markdown.extensions.tables']), tags=['p', 'b', 'i', 'u', 'em', 'strong', 'del', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'br', 'ol', 'ul', 'li', 'code', 'table', 'th', 'tr', 'thead', 'tbody', 'td'], attributes=['href', 'title', 'style'], styles=['font-family', 'color', 'font-weight', 'text-decoration', 'font-variant'], strip=False)
    else:
        result = bleach.clean(markdown.markdown(value, extensions=['markdown.extensions.tables']), tags=['b', 'i', 'u', 'em', 'strong', 'del'], attributes=['style'], styles=['font-weight', 'text-decoration', 'color'], strip=True)
    return mark_safe(result)
