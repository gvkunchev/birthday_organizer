from django import template
from django.conf import settings

register = template.Library()


@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    """Usage example {{ your_dict|get_value_from_dict:your_key }}"""
    if key:
        return dict_data.get(key)


# Project version appended to static files to force browser reload
@register.simple_tag
def version_variable(prefix='?'):
    version_to_str = "_".join(map(str, settings.VERSION))
    return f"{prefix}version={version_to_str}"
