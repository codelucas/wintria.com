__author__ = 'louyang'

from django.forms import ModelForm
from WintriaUser.models import WintriaUser


class FeedbackForm(ModelForm):
    class Meta:
        model = WintriaUser
        fields = ['email', 'favorite_news', 'feedback']
