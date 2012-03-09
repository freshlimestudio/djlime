# -*- coding: utf-8 -*-
"""
    djlime.utils.pagination
    ~~~~~~~~~~~~~~

    Utilities for pagination.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginator_factory(request, objects, num_pages, page='page'):

    paginator = Paginator(objects, num_pages)
    page = request.GET.get(page, '1')

    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    return objects
