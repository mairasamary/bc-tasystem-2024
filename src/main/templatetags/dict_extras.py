from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Allow dict[key] lookups in templates: {{ my_dict|get_item:key }}"""
    if not isinstance(dictionary, dict):
        return ''
    return dictionary.get(key, '')
