__author__ = 'janglapuk'

from django import forms
from .models import Pembayaran


class PembayaranForm(forms.Form):
    buktitrf = forms.FileField()
