/**
 * Pinia store for the Marketing workspace.
 *
 * Holds the state shared across the marketing tabs (settings, audience,
 * campaigns, inbox, overview) for the currently open project. The workspace
 * shell calls `setProject()` once the project is resolved from the URL slug;
 * every view then reads `projectId` from here.
 */

import { defineStore } from 'pinia'
import MarketingService from '../services/marketingService'
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

interface MarketingState {
  projectId: number | null
  settings: MarketingSettings | null
  settingsLoading: boolean
  overview: OverviewPayload | null
  overviewLoading: boolean
  contacts: Contact[]
  contactsTotal: number
  contactsLoading: boolean
  tags: TagCount[]
  campaigns: Campaign[]
  campaignsTotal: number
  campaignsLoading: boolean
  conversations: Conversation[]
  conversationsLoading: boolean
}

export const useMarketingStore = defineStore('marketing', {
  state: (): MarketingState => ({
    projectId: null,
    settings: null,
    settingsLoading: false,
    overview: null,
    overviewLoading: false,
    contacts: [],
    contactsTotal: 0,
    contactsLoading: false,
    tags: [],
    campaigns: [],
    campaignsTotal: 0,
    campaignsLoading: false,
    conversations: [],
    conversationsLoading: false,
  }),

  getters: {
    isConfigured: (state) => Boolean(state.settings?.is_configured),
  },

  actions: {
    /** Point the store at a project; clears data when switching projects. */
    setProject(projectId: number) {
      if (this.projectId !== projectId) {
        this.$reset()
        this.projectId = projectId
      }
    },

    requireProject(): number {
      if (this.projectId === null) {
        throw new Error('Marketing store has no active project')
      }
      return this.projectId
    },

    // -- Settings -----------------------------------------------------------
    async fetchSettings(): Promise<MarketingSettings> {
      const projectId = this.requireProject()
      this.settingsLoading = true
      try {
        this.settings = await MarketingService.getSettings(projectId)
        return this.settings
      } finally {
        this.settingsLoading = false
      }
    },

    async saveSettings(payload: MarketingSettingsPayload): Promise<MarketingSettings> {
      const projectId = this.requireProject()
      this.settings = await MarketingService.saveSettings(projectId, payload)
      return this.settings
    },

    async verifyConnection(): Promise<VerifyResult> {
      const projectId = this.requireProject()
      const result = await MarketingService.verifyConnection(projectId)
      this.settings = result.settings
      return result
    },

    // -- Overview -----------------------------------------------------------
    async fetchOverview(): Promise<OverviewPayload> {
      const projectId = this.requireProject()
      this.overviewLoading = true
      try {
        this.overview = await MarketingService.getOverview(projectId)
        return this.overview
      } finally {
        this.overviewLoading = false
      }
    },

    // -- Contacts -----------------------------------------------------------
    async fetchContacts(params: { search?: string; tag?: string; consent?: string; limit?: number; offset?: number } = {}) {
      const projectId = this.requireProject()
      this.contactsLoading = true
      try {
        const { contacts, total } = await MarketingService.listContacts(projectId, params)
        this.contacts = contacts
        this.contactsTotal = total
      } finally {
        this.contactsLoading = false
      }
    },

    async createContact(payload: ContactPayload): Promise<Contact> {
      const contact = await MarketingService.createContact(this.requireProject(), payload)
      return contact
    },

    async updateContact(contactId: number, payload: ContactPayload): Promise<Contact> {
      const contact = await MarketingService.updateContact(this.requireProject(), contactId, payload)
      const index = this.contacts.findIndex(c => c.id === contactId)
      if (index !== -1) this.contacts[index] = contact
      return contact
    },

    async deleteContact(contactId: number): Promise<void> {
      await MarketingService.deleteContact(this.requireProject(), contactId)
      this.contacts = this.contacts.filter(c => c.id !== contactId)
      this.contactsTotal = Math.max(this.contactsTotal - 1, 0)
    },

    async importContacts(rows: ImportRow[]): Promise<ImportResult> {
      return MarketingService.importContacts(this.requireProject(), rows)
    },

    async fetchTags() {
      this.tags = await MarketingService.listTags(this.requireProject())
    },

    // -- Campaigns ----------------------------------------------------------
    async fetchCampaigns(params: { status?: string; limit?: number; offset?: number } = {}) {
      const projectId = this.requireProject()
      this.campaignsLoading = true
      try {
        const { campaigns, total } = await MarketingService.listCampaigns(projectId, params)
        this.campaigns = campaigns
        this.campaignsTotal = total
      } finally {
        this.campaignsLoading = false
      }
    },

    async createCampaign(payload: CampaignPayload): Promise<Campaign> {
      return MarketingService.createCampaign(this.requireProject(), payload)
    },

    async getCampaign(campaignId: number): Promise<{ campaign: Campaign; messages: Message[] }> {
      return MarketingService.getCampaign(this.requireProject(), campaignId)
    },

    async updateCampaign(campaignId: number, payload: CampaignPayload): Promise<Campaign> {
      return MarketingService.updateCampaign(this.requireProject(), campaignId, payload)
    },

    async deleteCampaign(campaignId: number): Promise<void> {
      await MarketingService.deleteCampaign(this.requireProject(), campaignId)
      this.campaigns = this.campaigns.filter(c => c.id !== campaignId)
      this.campaignsTotal = Math.max(this.campaignsTotal - 1, 0)
    },

    async previewRecipients(campaignId: number): Promise<number> {
      return MarketingService.previewRecipients(this.requireProject(), campaignId)
    },

    async sendCampaign(campaignId: number, sendAt?: string) {
      return MarketingService.sendCampaign(this.requireProject(), campaignId, sendAt)
    },

    async cancelCampaign(campaignId: number) {
      return MarketingService.cancelCampaign(this.requireProject(), campaignId)
    },

    async syncCampaign(campaignId: number) {
      return MarketingService.syncCampaign(this.requireProject(), campaignId)
    },

    // -- Inbox ----------------------------------------------------------------
    async fetchConversations() {
      const projectId = this.requireProject()
      this.conversationsLoading = true
      try {
        const { conversations } = await MarketingService.listConversations(projectId)
        this.conversations = conversations
      } finally {
        this.conversationsLoading = false
      }
    },

    async getThread(contactId: number) {
      return MarketingService.getThread(this.requireProject(), contactId)
    },

    async sendDirectMessage(contactId: number, body: string): Promise<Message> {
      return MarketingService.sendDirectMessage(this.requireProject(), contactId, body)
    },
  },
})
