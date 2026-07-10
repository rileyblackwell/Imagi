/**
 * Pinia store for the Operate workspace.
 *
 * Holds the state shared across the Operate tabs (dashboard, finance,
 * invoices, tasks) for the currently open project. The workspace shell
 * calls `setProject()` once the project is resolved from the URL slug;
 * every view then reads `projectId` from here.
 */

import { defineStore } from 'pinia'
import OperateService from '../services/operateService'
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

interface OperateState {
  projectId: number | null
  dashboard: DashboardPayload | null
  dashboardLoading: boolean
  transactions: Transaction[]
  transactionsTotal: number
  transactionsSummary: LedgerSummary | null
  transactionsLoading: boolean
  invoices: Invoice[]
  invoicesTotal: number
  invoicesLoading: boolean
  tasks: OperationsTask[]
  taskCounts: TaskCounts | null
  tasksLoading: boolean
}

export const useOperateStore = defineStore('operate', {
  state: (): OperateState => ({
    projectId: null,
    dashboard: null,
    dashboardLoading: false,
    transactions: [],
    transactionsTotal: 0,
    transactionsSummary: null,
    transactionsLoading: false,
    invoices: [],
    invoicesTotal: 0,
    invoicesLoading: false,
    tasks: [],
    taskCounts: null,
    tasksLoading: false,
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

    // -- Transactions -----------------------------------------------------------
    async fetchTransactions(
      params: { kind?: string; category?: string; search?: string; limit?: number; offset?: number } = {}
    ) {
      const projectId = this.requireProject()
      this.transactionsLoading = true
      try {
        const { transactions, total, summary } = await OperateService.listTransactions(projectId, params)
        this.transactions = transactions
        this.transactionsTotal = total
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
      this.transactionsTotal = Math.max(this.transactionsTotal - 1, 0)
    },

    // -- Invoices ------------------------------------------------------------------
    async fetchInvoices(params: { status?: string; search?: string; limit?: number; offset?: number } = {}) {
      const projectId = this.requireProject()
      this.invoicesLoading = true
      try {
        const { invoices, total } = await OperateService.listInvoices(projectId, params)
        this.invoices = invoices
        this.invoicesTotal = total
      } finally {
        this.invoicesLoading = false
      }
    },

    async createInvoice(payload: InvoicePayload): Promise<Invoice> {
      return OperateService.createInvoice(this.requireProject(), payload)
    },

    async updateInvoice(invoiceId: number, payload: InvoicePayload): Promise<Invoice> {
      const invoice = await OperateService.updateInvoice(this.requireProject(), invoiceId, payload)
      const index = this.invoices.findIndex(i => i.id === invoiceId)
      if (index !== -1) this.invoices[index] = invoice
      return invoice
    },

    async deleteInvoice(invoiceId: number): Promise<void> {
      await OperateService.deleteInvoice(this.requireProject(), invoiceId)
      this.invoices = this.invoices.filter(i => i.id !== invoiceId)
      this.invoicesTotal = Math.max(this.invoicesTotal - 1, 0)
    },

    async setInvoiceStatus(invoiceId: number, status: InvoiceStatus): Promise<Invoice> {
      const invoice = await OperateService.setInvoiceStatus(this.requireProject(), invoiceId, status)
      const index = this.invoices.findIndex(i => i.id === invoiceId)
      if (index !== -1) this.invoices[index] = invoice
      return invoice
    },

    // -- Tasks ------------------------------------------------------------------------
    async fetchTasks(params: { status?: string; limit?: number; offset?: number } = {}) {
      const projectId = this.requireProject()
      this.tasksLoading = true
      try {
        const { tasks, counts } = await OperateService.listTasks(projectId, params)
        this.tasks = tasks
        this.taskCounts = counts
      } finally {
        this.tasksLoading = false
      }
    },

    async createTask(payload: TaskPayload): Promise<OperationsTask> {
      return OperateService.createTask(this.requireProject(), payload)
    },

    async updateTask(taskId: number, payload: TaskPayload): Promise<OperationsTask> {
      const task = await OperateService.updateTask(this.requireProject(), taskId, payload)
      const index = this.tasks.findIndex(t => t.id === taskId)
      if (index !== -1) this.tasks[index] = task
      return task
    },

    async deleteTask(taskId: number): Promise<void> {
      await OperateService.deleteTask(this.requireProject(), taskId)
      this.tasks = this.tasks.filter(t => t.id !== taskId)
    },
  },
})
