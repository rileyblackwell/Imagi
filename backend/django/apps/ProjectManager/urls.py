from django.urls import path, include

app_name = 'projectmanager'

urlpatterns = [
    path('api/', include('apps.ProjectManager.api.urls', namespace='api')),
]