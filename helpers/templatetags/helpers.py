from django import template
from django.conf import settings

register = template.Library()


@register.filter
def key(d, key_name):
    try:
        if isinstance(d, list) or isinstance(d, tuple):
            key_name = int(key_name)
        value = d[key_name]
    except (KeyError, IndexError):
        value = settings.TEMPLATE_STRING_IF_INVALID

    return value
