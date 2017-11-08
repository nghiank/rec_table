from django import template

register = template.Library()
@register.filter()
def list_index(value, arg):
    if arg < len(value):
        return value[arg]
    return ''

@register.filter()
def list_index1(value, arg):
    if arg + 30 < len(value):
        return value[arg + 30]
    return ''