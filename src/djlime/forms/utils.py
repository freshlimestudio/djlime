# -*- coding: utf-8 -*-
"""
    djlime.forms.utils
    ~~~~~~~~~~~~~~~~~~

    Utilities for forms.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""
import simplejson
from django.utils.encoding import force_text


def form_errors_to_json(form):
    errors = dict([(k, force_text(v[0])) for k, v in form.errors.items()])
    return simplejson.dumps({'success': False, 'errors': errors})
