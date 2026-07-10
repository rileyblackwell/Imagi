import type { RouteRecordRaw } from 'vue-router'
import OperateWorkspace from '../views/OperateWorkspace.vue'
import OperateDashboard from '../views/OperateDashboard.vue'
import OperateFinance from '../views/OperateFinance.vue'
import OperateInvoices from '../views/OperateInvoices.vue'
import OperateTasks from '../views/OperateTasks.vue'

/**
 * Operate workspace routes, nested under a project. The static `operations`
 * segment takes precedence over the generic `:category` coming-soon route.
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/products/imagi/project/:projectName/operations',
    component: OperateWorkspace,
    props: route => ({
      projectName: String(route.params.projectName)
    }),
    meta: {
      requiresAuth: true,
      title: 'Operate'
    },
    children: [
      {
        path: '',
        name: 'operate-dashboard',
        component: OperateDashboard,
        meta: { requiresAuth: true, title: 'Operate Dashboard' }
      },
      {
        path: 'finance',
        name: 'operate-finance',
        component: OperateFinance,
        meta: { requiresAuth: true, title: 'Finance' }
      },
      {
        path: 'invoices',
        name: 'operate-invoices',
        component: OperateInvoices,
        meta: { requiresAuth: true, title: 'Invoices' }
      },
      {
        path: 'tasks',
        name: 'operate-tasks',
        component: OperateTasks,
        meta: { requiresAuth: true, title: 'Tasks' }
      }
    ]
  }
]

export default routes
