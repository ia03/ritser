from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from debates.utils import clean
import markdown

register = template.Library()


@register.filter
@stringfilter
def markdownf(value, arg=0):
    typ = arg
    result = clean(markdown.markdown(
                   clean(value, typ=2).replace('&gt;', '>'),
                   extensions=[
                       'markdown.extensions.tables',
                       'markdown.extensions.fenced_code',
                       'pymdownx.betterem',
                       'pymdownx.tilde',
                       'pymdownx.caret']),
                   typ=typ).replace(
                       '<table>',
                       '<table class="table">').replace(
                           '<blockquote>',
                           '<blockquote class="blockquote"')
    return mark_safe(result)
