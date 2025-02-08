from django.urls import path
from . import views

urlpatterns = [
    # Frontend redirects
    path('', views.landing_page, name='landing'),
    path('about/', views.about_page, name='about'),
    path('privacy/', views.privacy_page, name='privacy'),
    path('terms/', views.terms_page, name='terms'),
    path('contact/', views.contact_page, name='contact'),
    path('cookie-policy/', views.cookie_policy, name='cookie_policy'),
]

