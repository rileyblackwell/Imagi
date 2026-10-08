import type { RouteRecordRaw } from 'vue-router'
import OperateWorkspace from '../views/OperateWorkspace.vue'
import OperateDashboard from '../views/OperateDashboard.vue'
import OperateFinance from '../views/OperateFinance.vue'

/**
 * Operate workspace routes, nested under a project. The static `operations`
 * segment takes precedence over the generic `:category` coming-soon route.
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/imagi/project/:projectName/operations',
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
        meta: { requiresAuth: true, title: 'Operate' }
      },
      {
        path: 'finance',
        name: 'operate-finance',
        component: OperateFinance,
        meta: { requiresAuth: true, title: 'Ledger' }
      },
      // Invoices and tasks were folded out when Operate became a dashboard;
      // old links land on it instead of a dead page.
      { path: 'invoices', redirect: { name: 'operate-dashboard' } },
      { path: 'tasks', redirect: { name: 'operate-dashboard' } },
    ]
  }
]

export default routes
