from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ProjectManager.views import ProjectViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    # ... existing urls ...
    path('api/', include(router.urls)),
]