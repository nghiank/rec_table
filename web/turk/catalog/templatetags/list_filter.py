from django import template
from django.core.files.storage import default_storage

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

@register.filter()
def filename_to_url(value):
    return default_storage.url(value)

@register.filter()
def file_id_to_filename(value, username):
    return username + '/' + value
