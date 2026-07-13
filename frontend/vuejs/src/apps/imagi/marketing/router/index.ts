import type { RouteRecordRaw } from 'vue-router'
import MarketingWorkspace from '../views/MarketingWorkspace.vue'
import MarketingOverview from '../views/MarketingOverview.vue'
import MarketingCampaigns from '../views/MarketingCampaigns.vue'
import MarketingCampaignDetail from '../views/MarketingCampaignDetail.vue'
import MarketingAudience from '../views/MarketingAudience.vue'
import MarketingAds from '../views/MarketingAds.vue'
import MarketingInbox from '../views/MarketingInbox.vue'
import MarketingSettings from '../views/MarketingSettings.vue'

/**
 * Marketing workspace routes, nested under a project. The static `marketing`
 * segment takes precedence over the generic `:category` coming-soon route.
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/imagi/project/:projectName/marketing',
    component: MarketingWorkspace,
    props: route => ({
      projectName: String(route.params.projectName)
    }),
    meta: {
      requiresAuth: true,
      title: 'Marketing'
    },
    children: [
      {
        path: '',
        name: 'marketing-overview',
        component: MarketingOverview,
        meta: { requiresAuth: true, title: 'Marketing Overview' }
      },
      {
        path: 'campaigns',
        name: 'marketing-campaigns',
        component: MarketingCampaigns,
        meta: { requiresAuth: true, title: 'Campaigns' }
      },
      {
        path: 'campaigns/:campaignId',
        name: 'marketing-campaign-detail',
        component: MarketingCampaignDetail,
        meta: { requiresAuth: true, title: 'Campaign' }
      },
      {
        path: 'audience',
        name: 'marketing-audience',
        component: MarketingAudience,
        meta: { requiresAuth: true, title: 'Audience' }
      },
      {
        path: 'ads',
        name: 'marketing-ads',
        component: MarketingAds,
        meta: { requiresAuth: true, title: 'Ads' }
      },
      {
        path: 'inbox',
        name: 'marketing-inbox',
        component: MarketingInbox,
        meta: { requiresAuth: true, title: 'Inbox' }
      },
      {
        path: 'settings',
        name: 'marketing-settings',
        component: MarketingSettings,
        meta: { requiresAuth: true, title: 'Marketing Settings' }
      }
    ]
  }
]

export default routes
