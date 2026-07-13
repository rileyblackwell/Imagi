from django.contrib import admin

from .models import AdCampaign, AdConnection, Campaign, Contact, MarketingSettings, Message


@admin.register(AdConnection)
class AdConnectionAdmin(admin.ModelAdmin):
    list_display = ('project', 'provider', 'account_id', 'account_name', 'last_synced_at')
    list_filter = ('provider',)
    search_fields = ('project__name', 'account_id', 'account_name')
    readonly_fields = ('credentials_encrypted', 'created_at', 'updated_at')


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'provider', 'status', 'spend', 'clicks', 'last_synced_at')
    list_filter = ('provider', 'status')
    search_fields = ('name', 'external_id', 'project__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MarketingSettings)
class MarketingSettingsAdmin(admin.ModelAdmin):
    list_display = ('project', 'twilio_account_sid', 'twilio_phone_number', 'last_verified_at')
    search_fields = ('project__name', 'twilio_account_sid', 'twilio_phone_number')
    readonly_fields = ('twilio_auth_token_encrypted', 'created_at', 'updated_at')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'phone_number', 'project', 'consent', 'source', 'created_at')
    list_filter = ('consent', 'source')
    search_fields = ('first_name', 'last_name', 'phone_number', 'email', 'project__name')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'channel', 'status', 'scheduled_at', 'created_at')
    list_filter = ('channel', 'status')
    search_fields = ('name', 'project__name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('direction', 'channel', 'to_number', 'status', 'campaign', 'created_at')
    list_filter = ('direction', 'channel', 'status')
    search_fields = ('to_number', 'from_number', 'twilio_sid', 'body')
    readonly_fields = ('created_at', 'updated_at')
