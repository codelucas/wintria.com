"""
"""
from django.http import HttpResponseRedirect

from wintria.wintriauser.forms import FeedbackForm
from wintria.wintria.views import render_with_context
from wintria.wintria.settings import get_root_url

def send_feedback(request):
    form_args = {}

    if request.POST:
        form_args['data'] = request.POST
        feedback_form = FeedbackForm(**form_args)
        if feedback_form.is_valid():
            feedback = feedback_form.save(commit=True)
            return HttpResponseRedirect(get_root_url() +
                                        '/thanks_for_all_the_fish/')
    else:
        feedback_form = FeedbackForm(**form_args)
    return render_with_context(request, 'feedback.html',
                               kwargs={ 'feedback_form': feedback_form })

def thanks_for_all_the_fish(request):
    return render_with_context(request, 'thanks.html', kwargs={})