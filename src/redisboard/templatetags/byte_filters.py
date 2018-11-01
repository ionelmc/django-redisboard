from django import template

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

register = template.Library()


@register.filter
def url_encode(value):
    return quote(value)


@register.filter
def try_decode(value):
    if isinstance(value, bytes):
        try:
            return value.decode('utf8')
        except UnicodeDecodeError:
            return value
    else:
        return value
