from django import template

register = template.Library()

@register.filter
def last_segment(path):
    """Returns the last segment of a URL path."""
    return path.rstrip('/').split('/')[-1]
