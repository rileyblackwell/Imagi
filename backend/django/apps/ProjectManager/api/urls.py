from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'projectmanager'

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
] 