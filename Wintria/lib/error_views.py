from wintria.wintria.views import render_with_context

def custom_404(request):
    return render_with_context(request, '404.html')

def custom_500(request):
    return render_with_context(request, '500.html')