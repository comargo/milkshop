from django import template, get_version
from django.conf import settings
from pkg_resources import parse_version

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


if parse_version(get_version()) < parse_version("2.1"):
    @register.filter(is_safe=True)
    def json_script(value, element_id):
        _json_script_escapes = {
            ord('>'): '\\u003E',
            ord('<'): '\\u003C',
            ord('&'): '\\u0026',
        }

        def _json_script(value, element_id):
            """
            Escape all the HTML/XML special characters with their unicode escapes, so
            value is safe to be output anywhere except for inside a tag attribute. Wrap
            the escaped JSON in a script tag.
            """
            from django.core.serializers.json import DjangoJSONEncoder
            import json
            from django.utils.html import format_html
            from django.utils.safestring import mark_safe

            json_str = json.dumps(value, cls=DjangoJSONEncoder).translate(_json_script_escapes)
            return format_html(
                '<script id="{}" type="application/json">{}</script>',
                element_id, mark_safe(json_str)
            )

        """
        Output value JSON-encoded, wrapped in a <script type="application/json">
        tag.
        """
        return _json_script(value, element_id)
