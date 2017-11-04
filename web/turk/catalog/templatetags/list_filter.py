from django import template

register = template.Library()
@register.filter()
def list_index(value, arg):
    return value[arg]

@register.filter()
def list_index1(value, arg):
    return value[arg + 30]