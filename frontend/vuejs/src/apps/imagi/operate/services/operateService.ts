/**
 * Operate Service — communication with the Operate app API
 * (/api/v1/operate/projects/:projectId/...): the dashboard, the app's
 * live address and uptime checks, and the ledger.
 */

import api from '@/shared/services/api'
import type {
  AppMonitor,
  AppSummary,
  DashboardPayload,
  LedgerSummary,
  Transaction,
  TransactionPayload,
} from '../types'

const base = (projectId: number) => `/v1/operate/projects/${projectId}`


const OperateService = {
  // -- Dashboard --------------------------------------------------------------
  async getDashboard(projectId: number): Promise<DashboardPayload> {
    const { data } = await api.get(`${base(projectId)}/dashboard/`)
    return data
  },

  // -- The app half -----------------------------------------------------------
  async setLiveUrl(projectId: number, liveUrl: string): Promise<{ monitor: AppMonitor; app: AppSummary }> {
    const { data } = await api.patch(`${base(projectId)}/app/`, { live_url: liveUrl })
    return data
  },

  /** Check the live address now — or, with `onlyIfStale`, only if the last check is old. */
  async checkApp(projectId: number, onlyIfStale = false): Promise<AppSummary> {
    const { data } = await api.post(`${base(projectId)}/app/check/`, { only_if_stale: onlyIfStale })
    return data.app
  },

  // -- Transactions -------------------------------------------------------------
  async listTransactions(
    projectId: number,
    params: { kind?: string; category?: string; search?: string; limit?: number; offset?: number } = {}
  ): Promise<{ transactions: Transaction[]; total: number; summary: LedgerSummary }> {
    const { data } = await api.get(`${base(projectId)}/transactions/`, { params })
    return data
  },

  async createTransaction(projectId: number, payload: TransactionPayload): Promise<Transaction> {
    const { data } = await api.post(`${base(projectId)}/transactions/`, payload)
    return data.transaction
  },

  async updateTransaction(projectId: number, transactionId: number, payload: TransactionPayload): Promise<Transaction> {
    const { data } = await api.patch(`${base(projectId)}/transactions/${transactionId}/`, payload)
    return data.transaction
  },

  async deleteTransaction(projectId: number, transactionId: number): Promise<void> {
    await api.delete(`${base(projectId)}/transactions/${transactionId}/`)
  },
}

export default OperateService

// The shared implementation; re-exported so this module stays the one place
// each tool's views import their error helper from.
export { extractError } from '@/shared/utils'
