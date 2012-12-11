# -*- coding: utf-8 -*-
"""
    djlime.forms.utils
    ~~~~~~~~~~~~~~~~~~

    Utilities for forms.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""
from django.utils import simplejson


def _errors_to_dict(form):
    return dict([(k, v[0]) for k, v in form.errors.items()])


def form_errors_to_json(form):
    if hasattr(form, '__iter__'):
        rv = {'success': False, 'errors': []}
        for f in form:
            rv['errors'].append(_errors_to_dict(f))
    else:
        rv = {'success': False, 'errors': _errors_to_dict(form)}
    return simplejson.dumps(rv)
