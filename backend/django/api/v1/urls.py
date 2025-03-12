from django.urls import path, include

urlpatterns = [
    # Auth endpoints
    path('auth/', include('apps.Auth.api.urls')),
    
    # Builder endpoints
    path('builder/', include('apps.Builder.api.urls')),
    
    # Project Manager endpoints
    path('project-manager/', include('apps.Products.Oasis.ProjectManager.api.urls')),
    
    # Payments endpoints
    path('payments/', include('apps.Payments.api.urls')),
    
    # Agents endpoints
    path('agents/', include('apps.Agents.api.urls')),
]
