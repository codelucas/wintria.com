from django.forms import ModelForm
from wintria.wintriauser.models import WintriaUser

class FeedbackForm(ModelForm):
    class Meta:
        model = WintriaUser
        fields = ['email', 'favorite_news', 'feedback']
