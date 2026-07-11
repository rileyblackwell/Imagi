from django.urls import include, path

urlpatterns = [
    path('home/', include('apps.Home.api.urls')),
    path('auth/', include('apps.Auth.api.urls')),
    path('payments/', include('apps.Payments.api.urls')),
    path('marketing/', include('apps.Imagi.Marketing.api.urls')),
    path('sell/', include('apps.Imagi.Sell.api.urls')),
    path('operate/', include('apps.Imagi.Operate.api.urls')),
    path('project-manager/', include('apps.Imagi.Build.ProjectManager.api.urls')),
    path('builder/', include('apps.Imagi.Build.Builder.api.urls')),
    path('agents/', include('apps.Imagi.Build.Agents.api.urls')),
]
