from django import template

register = template.Library()
@register.filter()
def list_index(value, arg):
    return value[arg]