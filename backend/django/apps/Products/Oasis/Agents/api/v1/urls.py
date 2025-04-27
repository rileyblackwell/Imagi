from django.urls import path
from .views import ModelDefinitionsView

urlpatterns = [
    path('models/', ModelDefinitionsView.as_view(), name='model-definitions'),
] 