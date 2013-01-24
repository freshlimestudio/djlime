# -*- coding: utf-8 -*-
"""
    djlime.forms.utils
    ~~~~~~~~~~~~~~~~~~

    Utilities for forms.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""
from django.utils import simplejson


def form_errors_to_json(form):
    errors = dict([(k, v[0]) for k, v in form.errors.items()])
    return simplejson.dumps({'success': False, 'errors': errors})
