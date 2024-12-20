from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.UserProfileView.as_view(), name='user-profile'),
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('contact/', views.ContactView.as_view(), name='contact'),
] 