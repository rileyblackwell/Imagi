from django.urls import include, path

urlpatterns = [
    path('home/', include('apps.Home.api.urls')),
    path('auth/', include('apps.Auth.api.urls')),
    path('payments/', include('apps.Payments.api.urls')),
    path('project-manager/', include('apps.Products.Imagi.ProjectManager.api.urls')),
    path('builder/', include('apps.Products.Imagi.Builder.api.urls')),
    path('agents/', include('apps.Products.Imagi.Agents.api.urls')),
]
