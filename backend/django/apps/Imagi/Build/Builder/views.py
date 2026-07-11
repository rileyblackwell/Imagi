"""
This file contains all the views for the Builder app. 
The views are separated into two categories: API and non-API views.
All API endpoints are handled in the api/ directory.
"""
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

@method_decorator(csrf_protect, name='dispatch')
class BuilderView(View):
    """
    Base view class for Builder app views.
    Provides common functionality and middleware for Builder views.
    """
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
