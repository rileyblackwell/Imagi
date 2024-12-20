from django.shortcuts import render

# Create your views here.
def landing_page(request):
    context = {
        'page_type': 'feature'  # For landing pages with feature sections
    }
    return render(request, 'home/home_landing_page.html', context)

def about_page(request):
    context = {
        'page_type': 'feature'  # About page has feature cards
    }
    return render(request, 'home/about.html', context)

def privacy_page(request):
    context = {
        'page_type': 'content'  # For text-heavy policy pages
    }
    return render(request, 'home/privacy.html', context)

def terms_page(request):
    context = {
        'page_type': 'content'  # For text-heavy policy pages
    }
    return render(request, 'home/terms.html', context)

def contact_page(request):
    context = {
        'page_type': 'feature'  # Contact has special form layout
    }
    return render(request, 'home/contact.html', context)

def cookie_policy(request):
    context = {
        'page_type': 'content'  # For text-heavy policy pages
    }
    return render(request, 'home/cookie_policy.html', context)

