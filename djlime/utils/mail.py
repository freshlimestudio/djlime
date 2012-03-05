# -*- coding: utf-8 -*-
"""
    djlime.utils.mail
    ~~~~~~~~~~~~~~

    Utilities for mail sending.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives


def send_mail(recipients, subject_template, html_template, text_template,
              context):
    subject = render_to_string(subject_template, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    html_msg = render_to_string(html_template, context)
    text_msg = render_to_string(text_template, context)
    if not isinstance(recipients, list):
        recipients = [recipients]
    msg = EmailMultiAlternatives(subject, text_msg,
                                 settings.DEFAULT_FROM_EMAIL, recipients)
    msg.attach_alternative(html_msg, "text/html")
    msg.send()
