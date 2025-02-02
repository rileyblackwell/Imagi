from django.shortcuts import redirect
from django.conf import settings

# Create your views here.
def landing_page(request):
    return redirect(f"{settings.FRONTEND_URL}/")

def about_page(request):
    return redirect(f"{settings.FRONTEND_URL}/about")

def privacy_page(request):
    return redirect(f"{settings.FRONTEND_URL}/privacy")

def terms_page(request):
    return redirect(f"{settings.FRONTEND_URL}/terms")

def contact_page(request):
    return redirect(f"{settings.FRONTEND_URL}/contact")

def cookie_policy(request):
    return redirect(f"{settings.FRONTEND_URL}/cookie-policy")

