"""
    djlime.forms.widgets
    ~~~~~~~~~~~~~~

    Extended django form widgets.

    :copyright: (c) 2012 by Andrey Voronov.
    :license: BSD, see LICENSE for more details.
"""

from itertools import chain
from django.forms import widgets
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class RadioInput(widgets.RadioInput):

    def __init__(self, name, value, attrs, label_attrs, choice, index):
        self.label_attrs = label_attrs
        super(RadioInput, self).__init__(name, value, attrs, choice, index)

    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'<label %s %s>%s %s</label>' % (label_for, flatatt(self.label_attrs), self.tag(), choice_label))


class HorizontalRadioRenderer(widgets.RadioSelect.renderer):

    def __init__(self, name, value, attrs, label_attrs, choices):
        self.label_attrs = label_attrs
        super(HorizontalRadioRenderer, self).__init__(name, value, attrs, choices)

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioInput(self.name, self.value, self.attrs.copy(), self.label_attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioInput(self.name, self.value, self.attrs.copy(), self.label_attrs.copy(), choice, idx)

    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class RadioFieldRenderer(widgets.RadioFieldRenderer):

    def __init__(self, name, value, attrs, label_attrs, choices):
        self.label_attrs = label_attrs
        super(RadioFieldRenderer, self).__init__(name, value, attrs, choices)

    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield RadioInput(self.name, self.value, self.attrs.copy(), self.label_attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return RadioInput(self.name, self.value, self.attrs.copy(), self.label_attrs.copy(), choice, idx)


class RadioSelect(widgets.RadioSelect):
    """
    RadioSelect widget with support for label attributes such is class, id
    """
    renderer = RadioFieldRenderer

    def __init__(self, *args, **kwargs):
        label_attrs = kwargs.pop('label_attrs', {})
        self.label_attrs = label_attrs
        super(RadioSelect, self).__init__(*args, **kwargs)

    def get_renderer(self, name, value, attrs=None, label_attrs=None, choices=()):
        """Returns an instance of the renderer."""
        if value is None: value = ''
        str_value = force_unicode(value) # Normalize to string.
        final_attrs = self.build_attrs(attrs)
        choices = list(chain(self.choices, choices))
        return self.renderer(name, str_value, final_attrs, label_attrs, choices)

    def render(self, name, value, attrs=None, label_attrs=None, choices=()):
        return self.get_renderer(name, value, attrs, self.label_attrs, choices).render()
