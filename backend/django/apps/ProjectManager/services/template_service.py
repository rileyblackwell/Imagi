class ViewTemplateService:
    @staticmethod
    def generate_view_code(view_name):
        """Generate code for a simple Django view"""
        return f"""
from django.shortcuts import render

def {view_name}(request):
    \"\"\"Render the {view_name} page\"\"\"
    return render(request, '{view_name}.html')
"""

    @staticmethod
    def generate_urls_code(url_patterns):
        """Generate Django URLs configuration"""
        imports = [
            "from django.urls import path",
            "from django.conf import settings",
            "from django.conf.urls.static import static",
            "from . import views",
            "\n",
            "urlpatterns = ["
        ]
        
        patterns = []
        for name in url_patterns:
            if name == 'index':
                patterns.append(f"    path('', views.{name}, name='{name}'),")
            else:
                patterns.append(f"    path('{name}/', views.{name}, name='{name}'),")
        
        patterns.append("]")
        
        # Add static/media serving for development
        patterns.extend([
            "",
            "# Serve static and media files during development",
            "if settings.DEBUG:",
            "    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)",
            "    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)"
        ])
        
        return "\n".join(imports + patterns) 