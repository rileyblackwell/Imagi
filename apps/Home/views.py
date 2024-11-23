from django.shortcuts import render

# Create your views here.
def landing_page(request):
    return render(request, 'home/home_landing_page.html')

def about_page(request):
    return render(request, 'home/about.html')

def privacy_page(request):
    return render(request, 'home/privacy.html')

def terms_page(request):
    return render(request, 'home/terms.html')

def contact_page(request):
    return render(request, 'home/contact.html')

def cookie_policy(request):
    return render(request, 'home/cookie_policy.html')

