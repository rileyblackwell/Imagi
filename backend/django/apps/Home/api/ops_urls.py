"""Ops/diagnostic routes mounted at /api/v1/ops/.

The web and workspace tiers run the same Django image, so the same view is
exposed under two prefixes that the nginx $api_upstream map routes to the two
different tiers. Hitting both and comparing the reported `commit` confirms the
tiers deployed from the same push are on the same code. See
apps.Home.api.views.version_info and frontend/vuejs/nginx.conf.
"""
from django.urls import path

from . import views

app_name = 'home_ops'

urlpatterns = [
    # Routed to the web (backend) tier by nginx (the map's default).
    path('web/version/', views.version_info, name='version_web'),
    # Routed to the workspace tier by nginx's ~^/api/v1/ops/workspace/ entry.
    path('workspace/version/', views.version_info, name='version_workspace'),
]
