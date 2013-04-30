# -*- coding: utf-8 -*-
"""
    djlime.views.robots
    ~~~~~~~~~~~~~~

    robots.txt view.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""
from django.views.generic import TemplateView


class RobotsView(TemplateView):
    """
    Serves /robots.txt without Apache configuration modification.
    """
    template_name = 'robots.txt'

    def render_to_response(self, context, **kwargs):
        return super(TemplateView, self).render_to_response(
            context, content_type='text/plain',**kwargs)
