/**
 * Types for the Marketing module — mirrors the Django Marketing app API
 * (backend/django/apps/Marketing).
 */

export interface MarketingSettings {
  twilio_account_sid: string
  /** True when an auth token is stored server-side (the token itself is never returned). */
  twilio_auth_token_set: boolean
  twilio_phone_number: string
  twilio_messaging_service_sid: string
  voice: string
  account_friendly_name: string
  last_verified_at: string | null
  is_configured: boolean
  /** Twilio webhook URLs; empty when the backend has no public base URL configured. */
  status_callback_url: string
  inbound_webhook_url: string
}

export interface MarketingSettingsPayload {
  twilio_account_sid?: string
  /** Write-only; omit or send '' to keep the stored token. */
  twilio_auth_token?: string
  twilio_phone_number?: string
  twilio_messaging_service_sid?: string
  voice?: string
}

export interface TwilioPhoneNumber {
  phone_number: string
  friendly_name: string
}

export interface VerifyResult {
  verified: boolean
  account_name: string
  account_status: string
  phone_numbers: TwilioPhoneNumber[]
  settings: MarketingSettings
}

export type ConsentStatus = 'subscribed' | 'unsubscribed'

export interface Contact {
  id: number
  first_name: string
  last_name: string
  display_name: string
  phone_number: string
  email: string
  tags: string[]
  consent: ConsentStatus
  source: 'manual' | 'import' | 'inbound'
  notes: string
  created_at: string
  updated_at: string
}

export interface ContactPayload {
  first_name?: string
  last_name?: string
  phone_number?: string
  email?: string
  tags?: string[]
  consent?: ConsentStatus
  notes?: string
}

export interface ImportRow {
  first_name?: string
  last_name?: string
  phone_number: string
  email?: string
  tags?: string[]
}

export interface ImportResult {
  created: number
  skipped: { index: number; phone_number?: string; reason: string }[]
}

export interface TagCount {
  tag: string
  count: number
}

export type CampaignChannel = 'sms' | 'voice'
export type CampaignStatus = 'draft' | 'scheduled' | 'sending' | 'sent' | 'failed' | 'canceled'
export type AudienceType = 'all' | 'tags'

export interface CampaignStats {
  recipients: number
  delivered: number
  failed: number
  pending: number
}

export interface Campaign {
  id: number
  name: string
  channel: CampaignChannel
  body: string
  audience_type: AudienceType
  audience_tags: string[]
  status: CampaignStatus
  scheduled_at: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
  stats: CampaignStats
}

export interface CampaignPayload {
  name?: string
  channel?: CampaignChannel
  body?: string
  audience_type?: AudienceType
  audience_tags?: string[]
}

export type MessageDirection = 'outbound' | 'inbound'

export interface Message {
  id: number
  direction: MessageDirection
  channel: CampaignChannel
  body: string
  from_number: string
  to_number: string
  status: string
  error_code: string
  error_message: string
  contact_id: number | null
  contact_name: string
  campaign_id: number | null
  created_at: string
}

export interface Conversation {
  id: number
  display_name: string
  phone_number: string
  consent: ConsentStatus
  last_message_body: string
  last_message_direction: MessageDirection
  last_message_at: string
  message_count: number
}

export interface OverviewStats {
  configured: boolean
  contacts_total: number
  contacts_subscribed: number
  campaigns_total: number
  campaigns_active: number
  messages_sent_30d: number
  messages_delivered_30d: number
  messages_failed_30d: number
  replies_30d: number
}

export interface OverviewPayload {
  stats: OverviewStats
  ads: AdsSummary
  recent_campaigns: Campaign[]
  recent_inbound: Message[]
}

// -- Ads (Google Ads / Meta Ads) ---------------------------------------------

export type AdProvider = 'google' | 'meta'
export type AdCampaignStatus = 'active' | 'paused' | 'ended' | 'other'

export interface AdConnection {
  provider: AdProvider
  account_id: string
  account_name: string
  currency: string
  /** Names of the credential keys stored server-side (values never leave the server). */
  credentials_set: string[]
  is_configured: boolean
  last_verified_at: string | null
  last_synced_at: string | null
}

/** Write-only credential payload; blank fields keep the stored values. */
export interface AdConnectionPayload {
  account_id?: string
  // Meta
  access_token?: string
  // Google
  developer_token?: string
  client_id?: string
  client_secret?: string
  refresh_token?: string
  login_customer_id?: string
}

export interface AdCampaign {
  id: number
  provider: AdProvider
  external_id: string
  name: string
  status: AdCampaignStatus
  provider_status: string
  objective: string
  daily_budget: string | null
  currency: string
  impressions: number
  clicks: number
  spend: string
  conversions: string | null
  /** Click-through rate in percent; null without impressions. */
  ctr: number | null
  /** Average cost per click; null without clicks. */
  cpc: number | null
  manager_url: string
  last_synced_at: string | null
}

export interface AdsSummary {
  connected_providers: AdProvider[]
  campaigns_total: number
  campaigns_active: number
  impressions: number
  clicks: number
  spend: string
  /** Shared account currency, or '' when connected accounts differ. */
  currency: string
  last_synced_at: string | null
}

export interface AdsSyncResult {
  results: Partial<Record<AdProvider, { synced: number; removed: number }>>
  errors: Partial<Record<AdProvider, string>>
  campaigns: AdCampaign[]
  summary: AdsSummary
}
