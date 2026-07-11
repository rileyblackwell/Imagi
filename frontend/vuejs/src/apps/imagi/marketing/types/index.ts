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
  recent_campaigns: Campaign[]
  recent_inbound: Message[]
}
