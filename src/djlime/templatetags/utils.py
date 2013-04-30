"""
    djlime.templatetags.utils
    ~~~~~~~~~~~~~~

    Useful templatetags.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""

import re

from django.template import Library

register = Library()


@register.simple_tag
def is_current_link(request, pattern, css_class='current'):
    """
    Searches regexp template in request.path

    :param request: request instance
    :param pattern: valid regexp string
    :param css_class: optional css class value
    :returns: css_class value
    :rtype: string
    """
    if re.search(pattern, request.path):
        return css_class
    return ''
