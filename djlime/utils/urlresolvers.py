# -*- coding: utf-8 -*-
"""
    djlime.utils.urlresolvers
    ~~~~~~~~~~~~~~

    Utilities for urls.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""
from django.core.urlresolvers import reverse
from django.utils.functional import lazy


reverse_lazy = lazy(reverse, str)

