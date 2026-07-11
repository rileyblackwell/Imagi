/**
 * Operate Service — communication with the Operate app API
 * (/api/v1/operate/projects/:projectId/...).
 */

import api from '@/shared/services/api'
import type {
  DashboardPayload,
  Invoice,
  InvoicePayload,
  InvoiceStatus,
  LedgerSummary,
  OperationsTask,
  TaskCounts,
  TaskPayload,
  Transaction,
  TransactionPayload,
} from '../types'

const base = (projectId: number) => `/v1/operate/projects/${projectId}`

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

export const OperateService = {
  // -- Dashboard --------------------------------------------------------------
  async getDashboard(projectId: number): Promise<DashboardPayload> {
    const { data } = await api.get(`${base(projectId)}/dashboard/`)
    return data
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

  // -- Invoices --------------------------------------------------------------------
  async listInvoices(
    projectId: number,
    params: { status?: string; search?: string; limit?: number; offset?: number } = {}
  ): Promise<{ invoices: Invoice[]; total: number }> {
    const { data } = await api.get(`${base(projectId)}/invoices/`, { params })
    return data
  },

  async createInvoice(projectId: number, payload: InvoicePayload): Promise<Invoice> {
    const { data } = await api.post(`${base(projectId)}/invoices/`, payload)
    return data.invoice
  },

  async updateInvoice(projectId: number, invoiceId: number, payload: InvoicePayload): Promise<Invoice> {
    const { data } = await api.patch(`${base(projectId)}/invoices/${invoiceId}/`, payload)
    return data.invoice
  },

  async deleteInvoice(projectId: number, invoiceId: number): Promise<void> {
    await api.delete(`${base(projectId)}/invoices/${invoiceId}/`)
  },

  async setInvoiceStatus(projectId: number, invoiceId: number, status: InvoiceStatus): Promise<Invoice> {
    const { data } = await api.post(`${base(projectId)}/invoices/${invoiceId}/status/`, { status })
    return data.invoice
  },

  // -- Tasks -----------------------------------------------------------------------
  async listTasks(
    projectId: number,
    params: { status?: string; limit?: number; offset?: number } = {}
  ): Promise<{ tasks: OperationsTask[]; total: number; counts: TaskCounts }> {
    const { data } = await api.get(`${base(projectId)}/tasks/`, { params })
    return data
  },

  async createTask(projectId: number, payload: TaskPayload): Promise<OperationsTask> {
    const { data } = await api.post(`${base(projectId)}/tasks/`, payload)
    return data.task
  },

  async updateTask(projectId: number, taskId: number, payload: TaskPayload): Promise<OperationsTask> {
    const { data } = await api.patch(`${base(projectId)}/tasks/${taskId}/`, payload)
    return data.task
  },

  async deleteTask(projectId: number, taskId: number): Promise<void> {
    await api.delete(`${base(projectId)}/tasks/${taskId}/`)
  },
}

export default OperateService
