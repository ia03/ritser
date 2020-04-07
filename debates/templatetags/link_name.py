from django import template
import re

register = template.Library()


@register.filter(name='link_name')
def link_name(path, page_number):
    output = re.search('(page=\d+)', path)
    if output is not None:
        # print(str(output.group(1)))
        return path.replace(str(output.group(1)), "page={page_number}")
    if re.search('(page=\d+)', path):
        path.replace()
    page_number = str(page_number)
    if '?' in path:
        return path + "&page=" + page_number
    return path + "?page=" + page_number


@register.filter(name='link_namef')
def link_namef(path, page_number):
    output = re.search('(pagef=\d+)', path)
    if output is not None:
        # print(str(output.group(1)))
        return path.replace(str(output.group(1)), "pagef={page_number}")
    if re.search('(pagef=\d+)', path):
        path.replace()
    page_number = str(page_number)
    if '?' in path:
        return path + "&pagef=" + page_number
    return path + "?pagef=" + page_number


@register.filter(name='link_namea')
def link_namea(path, page_number):
    output = re.search('(pagea=\d+)', path)
    if output is not None:
        # print(str(output.group(1)))
        return path.replace(str(output.group(1)), "pagea={page_number}")
    if re.search('(pagea=\d+)', path):
        path.replace()
    page_number = str(page_number)
    if '?' in path:
        return path + "&pagea=" + page_number
    return path + "?pagea=" + page_number
