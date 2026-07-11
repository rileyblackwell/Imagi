/**
 * Marketing Service — communication with the Marketing app API
 * (/api/v1/marketing/projects/:projectId/...).
 */

import api from '@/shared/services/api'
import type {
  Campaign,
  CampaignPayload,
  Contact,
  ContactPayload,
  Conversation,
  ImportResult,
  ImportRow,
  MarketingSettings,
  MarketingSettingsPayload,
  Message,
  OverviewPayload,
  TagCount,
  VerifyResult,
} from '../types'

const base = (projectId: number) => `/v1/marketing/projects/${projectId}`

/** Pull a readable message out of an axios/DRF error. */
export function extractError(error: unknown, fallback = 'Something went wrong'): string {
  const data = (error as { response?: { data?: unknown } })?.response?.data
  if (typeof data === 'string') return fallback
  if (data && typeof data === 'object') {
    const payload = data as Record<string, unknown>
    if (typeof payload.error === 'string') return payload.error
    if (typeof payload.detail === 'string') return payload.detail
    // DRF field errors: {"field": ["message", ...]}
    for (const [field, value] of Object.entries(payload)) {
      const first = Array.isArray(value) ? value[0] : value
      if (typeof first === 'string') {
        return field === 'non_field_errors' ? first : `${field.replace(/_/g, ' ')}: ${first}`
      }
    }
  }
  const message = (error as { message?: string })?.message
  return message || fallback
}

export const MarketingService = {
  // -- Settings -------------------------------------------------------------
  async getSettings(projectId: number): Promise<MarketingSettings> {
    const { data } = await api.get(`${base(projectId)}/settings/`)
    return data.settings
  },

  async saveSettings(projectId: number, payload: MarketingSettingsPayload): Promise<MarketingSettings> {
    const { data } = await api.put(`${base(projectId)}/settings/`, payload)
    return data.settings
  },

  async verifyConnection(projectId: number): Promise<VerifyResult> {
    const { data } = await api.post(`${base(projectId)}/settings/verify/`)
    return data
  },

  // -- Overview -------------------------------------------------------------
  async getOverview(projectId: number): Promise<OverviewPayload> {
    const { data } = await api.get(`${base(projectId)}/overview/`)
    return data
  },

  // -- Contacts -------------------------------------------------------------
  async listContacts(
    projectId: number,
    params: { search?: string; tag?: string; consent?: string; limit?: number; offset?: number } = {}
  ): Promise<{ contacts: Contact[]; total: number }> {
    const { data } = await api.get(`${base(projectId)}/contacts/`, { params })
    return data
  },

  async createContact(projectId: number, payload: ContactPayload): Promise<Contact> {
    const { data } = await api.post(`${base(projectId)}/contacts/`, payload)
    return data.contact
  },

  async updateContact(projectId: number, contactId: number, payload: ContactPayload): Promise<Contact> {
    const { data } = await api.patch(`${base(projectId)}/contacts/${contactId}/`, payload)
    return data.contact
  },

  async deleteContact(projectId: number, contactId: number): Promise<void> {
    await api.delete(`${base(projectId)}/contacts/${contactId}/`)
  },

  async importContacts(projectId: number, rows: ImportRow[]): Promise<ImportResult> {
    const { data } = await api.post(`${base(projectId)}/contacts/import/`, { contacts: rows })
    return data
  },

  async listTags(projectId: number): Promise<TagCount[]> {
    const { data } = await api.get(`${base(projectId)}/tags/`)
    return data.tags
  },

  // -- Campaigns ------------------------------------------------------------
  async listCampaigns(
    projectId: number,
    params: { status?: string; limit?: number; offset?: number } = {}
  ): Promise<{ campaigns: Campaign[]; total: number }> {
    const { data } = await api.get(`${base(projectId)}/campaigns/`, { params })
    return data
  },

  async createCampaign(projectId: number, payload: CampaignPayload): Promise<Campaign> {
    const { data } = await api.post(`${base(projectId)}/campaigns/`, payload)
    return data.campaign
  },

  async getCampaign(projectId: number, campaignId: number): Promise<{ campaign: Campaign; messages: Message[] }> {
    const { data } = await api.get(`${base(projectId)}/campaigns/${campaignId}/`)
    return data
  },

  async updateCampaign(projectId: number, campaignId: number, payload: CampaignPayload): Promise<Campaign> {
    const { data } = await api.patch(`${base(projectId)}/campaigns/${campaignId}/`, payload)
    return data.campaign
  },

  async deleteCampaign(projectId: number, campaignId: number): Promise<void> {
    await api.delete(`${base(projectId)}/campaigns/${campaignId}/`)
  },

  async previewRecipients(projectId: number, campaignId: number): Promise<number> {
    const { data } = await api.get(`${base(projectId)}/campaigns/${campaignId}/recipients/`)
    return data.recipients
  },

  async sendCampaign(
    projectId: number,
    campaignId: number,
    sendAt?: string
  ): Promise<{ dispatched: number; failed: number; campaign: Campaign }> {
    const payload = sendAt ? { send_at: sendAt } : {}
    const { data } = await api.post(`${base(projectId)}/campaigns/${campaignId}/send/`, payload)
    return data
  },

  async cancelCampaign(projectId: number, campaignId: number): Promise<{ canceled: number; campaign: Campaign }> {
    const { data } = await api.post(`${base(projectId)}/campaigns/${campaignId}/cancel/`)
    return data
  },

  async syncCampaign(projectId: number, campaignId: number): Promise<{ updated: number; campaign: Campaign }> {
    const { data } = await api.post(`${base(projectId)}/campaigns/${campaignId}/sync/`)
    return data
  },

  // -- Inbox ----------------------------------------------------------------
  async listConversations(projectId: number): Promise<{ conversations: Conversation[]; total: number }> {
    const { data } = await api.get(`${base(projectId)}/conversations/`)
    return data
  },

  async getThread(projectId: number, contactId: number): Promise<{ contact: Contact; messages: Message[] }> {
    const { data } = await api.get(`${base(projectId)}/contacts/${contactId}/messages/`)
    return data
  },

  async sendDirectMessage(projectId: number, contactId: number, body: string): Promise<Message> {
    const { data } = await api.post(`${base(projectId)}/contacts/${contactId}/messages/`, { body })
    return data.message
  },
}

export default MarketingService
