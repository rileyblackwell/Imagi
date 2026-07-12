from django.urls import include, path

urlpatterns = [
    path('home/', include('apps.Home.api.urls')),
    path('auth/', include('apps.Auth.api.urls')),
    path('payments/', include('apps.Payments.api.urls')),
    path('marketing/', include('apps.Imagi.Marketing.api.urls')),
    path('sell/', include('apps.Imagi.Sell.api.urls')),
    path('operate/', include('apps.Imagi.Operate.api.urls')),
    path('project-manager/', include('apps.Imagi.ProjectManager.api.urls')),
    # Build mounts both its public prefixes: builder/ and agents/
    path('', include('apps.Imagi.Build.api.urls')),
]
