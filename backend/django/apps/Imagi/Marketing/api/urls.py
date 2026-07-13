"""
URL patterns for the Marketing app API.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Twilio configuration
    path('projects/<int:project_id>/settings/',
         views.MarketingSettingsView.as_view(), name='api-marketing-settings'),
    path('projects/<int:project_id>/settings/verify/',
         views.VerifyConnectionView.as_view(), name='api-marketing-verify'),

    # Dashboard
    path('projects/<int:project_id>/overview/',
         views.OverviewView.as_view(), name='api-marketing-overview'),

    # Audience
    path('projects/<int:project_id>/contacts/',
         views.ContactListCreateView.as_view(), name='api-marketing-contacts'),
    path('projects/<int:project_id>/contacts/import/',
         views.ContactImportView.as_view(), name='api-marketing-contacts-import'),
    path('projects/<int:project_id>/contacts/<int:pk>/',
         views.ContactDetailView.as_view(), name='api-marketing-contact-detail'),
    path('projects/<int:project_id>/contacts/<int:pk>/messages/',
         views.ContactMessagesView.as_view(), name='api-marketing-contact-messages'),
    path('projects/<int:project_id>/tags/',
         views.TagListView.as_view(), name='api-marketing-tags'),

    # Campaigns
    path('projects/<int:project_id>/campaigns/',
         views.CampaignListCreateView.as_view(), name='api-marketing-campaigns'),
    path('projects/<int:project_id>/campaigns/<int:pk>/',
         views.CampaignDetailView.as_view(), name='api-marketing-campaign-detail'),
    path('projects/<int:project_id>/campaigns/<int:pk>/recipients/',
         views.CampaignRecipientsPreviewView.as_view(), name='api-marketing-campaign-recipients'),
    path('projects/<int:project_id>/campaigns/<int:pk>/send/',
         views.CampaignSendView.as_view(), name='api-marketing-campaign-send'),
    path('projects/<int:project_id>/campaigns/<int:pk>/cancel/',
         views.CampaignCancelView.as_view(), name='api-marketing-campaign-cancel'),
    path('projects/<int:project_id>/campaigns/<int:pk>/sync/',
         views.CampaignSyncView.as_view(), name='api-marketing-campaign-sync'),

    # Inbox
    path('projects/<int:project_id>/conversations/',
         views.ConversationListView.as_view(), name='api-marketing-conversations'),

    # Ads (Google Ads / Meta Ads)
    path('projects/<int:project_id>/ads/connections/',
         views.AdConnectionListView.as_view(), name='api-marketing-ad-connections'),
    path('projects/<int:project_id>/ads/connections/<str:provider>/',
         views.AdConnectionDetailView.as_view(), name='api-marketing-ad-connection-detail'),
    path('projects/<int:project_id>/ads/connections/<str:provider>/verify/',
         views.AdConnectionVerifyView.as_view(), name='api-marketing-ad-connection-verify'),
    path('projects/<int:project_id>/ads/campaigns/',
         views.AdCampaignListView.as_view(), name='api-marketing-ad-campaigns'),
    path('projects/<int:project_id>/ads/campaigns/<int:pk>/status/',
         views.AdCampaignStatusView.as_view(), name='api-marketing-ad-campaign-status'),
    path('projects/<int:project_id>/ads/sync/',
         views.AdsSyncView.as_view(), name='api-marketing-ads-sync'),

    # Twilio callbacks (signature-authenticated, no user session)
    path('webhooks/<int:project_id>/status/',
         views.TwilioStatusWebhookView.as_view(), name='api-marketing-webhook-status'),
    path('webhooks/<int:project_id>/inbound/',
         views.TwilioInboundWebhookView.as_view(), name='api-marketing-webhook-inbound'),
]
