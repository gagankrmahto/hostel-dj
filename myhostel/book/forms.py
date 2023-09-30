from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError

import re


class BookRoomForm(forms.Form):
    name = forms.CharField(max_length=200, help_text='Enter your preferred name')
    phone_number = forms.CharField(max_length=10, help_text='Enter a phone number')

    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']

        if re.search(r'\D', data):
            raise ValidationError(_('A phone number consists of only digits'), code='not digits')

        if not re.search(r'^07\d{8}', data):
            raise ValidationError(_('Please start with \'07\''), code='wrong format')

        return data
