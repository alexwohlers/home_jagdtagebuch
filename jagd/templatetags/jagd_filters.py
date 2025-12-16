from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Holt einen Wert aus einem Dictionary"""
    if dictionary:
        return dictionary.get(key, key)
    return key
