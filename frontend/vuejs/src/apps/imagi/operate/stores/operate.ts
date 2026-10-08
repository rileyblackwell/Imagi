/**
 * Pinia store for the Operate workspace.
 *
 * Holds the state shared across the Operate tabs (the dashboard and the
 * ledger) for the currently open project. The workspace shell
 * calls `setProject()` once the project is resolved from the URL slug;
 * every view then reads `projectId` from here.
 */

import { defineStore } from 'pinia'
import OperateService from '../services/operateService'
import type {
  AppSummary,
  DashboardPayload,
  LedgerSummary,
  Transaction,
  TransactionPayload,
} from '../types'

interface OperateState {
  projectId: number | null
  dashboard: DashboardPayload | null
  dashboardLoading: boolean
  transactions: Transaction[]
  transactionsSummary: LedgerSummary | null
  transactionsLoading: boolean
}

export const useOperateStore = defineStore('operate', {
  state: (): OperateState => ({
    projectId: null,
    dashboard: null,
    dashboardLoading: false,
    transactions: [],
    transactionsSummary: null,
    transactionsLoading: false,
  }),

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
        throw new Error('Operate store has no active project')
      }
      return this.projectId
    },

    // -- Dashboard ------------------------------------------------------------
    async fetchDashboard(): Promise<DashboardPayload> {
      const projectId = this.requireProject()
      this.dashboardLoading = true
      try {
        this.dashboard = await OperateService.getDashboard(projectId)
        return this.dashboard
      } finally {
        this.dashboardLoading = false
      }
    },

    /** Save the app's live address; the server checks it straight away. */
    async setLiveUrl(liveUrl: string): Promise<AppSummary> {
      const { app } = await OperateService.setLiveUrl(this.requireProject(), liveUrl)
      if (this.dashboard) this.dashboard.app = app
      return app
    },

    async checkApp(onlyIfStale = false): Promise<AppSummary> {
      const app = await OperateService.checkApp(this.requireProject(), onlyIfStale)
      if (this.dashboard) this.dashboard.app = app
      return app
    },

    // -- Transactions -----------------------------------------------------------
    async fetchTransactions(
      params: { kind?: string; category?: string; search?: string; limit?: number; offset?: number } = {}
    ) {
      const projectId = this.requireProject()
      this.transactionsLoading = true
      try {
        const { transactions, summary } = await OperateService.listTransactions(projectId, params)
        this.transactions = transactions
        this.transactionsSummary = summary
      } finally {
        this.transactionsLoading = false
      }
    },

    async createTransaction(payload: TransactionPayload): Promise<Transaction> {
      return OperateService.createTransaction(this.requireProject(), payload)
    },

    async updateTransaction(transactionId: number, payload: TransactionPayload): Promise<Transaction> {
      const transaction = await OperateService.updateTransaction(this.requireProject(), transactionId, payload)
      const index = this.transactions.findIndex(t => t.id === transactionId)
      if (index !== -1) this.transactions[index] = transaction
      return transaction
    },

    async deleteTransaction(transactionId: number): Promise<void> {
      await OperateService.deleteTransaction(this.requireProject(), transactionId)
      this.transactions = this.transactions.filter(t => t.id !== transactionId)
    },
  },
})
