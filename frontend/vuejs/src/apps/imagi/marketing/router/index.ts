import type { RouteRecordRaw } from 'vue-router'
import MarketingWorkspace from '../views/MarketingWorkspace.vue'
import MarketingOverview from '../views/MarketingOverview.vue'
import MarketingCampaignDetail from '../views/MarketingCampaignDetail.vue'
import MarketingAdBuilder from '../views/MarketingAdBuilder.vue'
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
        // The Campaigns home: start a text or a Google ad, and every campaign.
        path: '',
        name: 'marketing-overview',
        component: MarketingOverview,
        meta: { requiresAuth: true, title: 'Campaigns' }
      },
      {
        // The old campaign list now lives on the home page; keep its links
        // (and ?new=1, which opens the text composer) working.
        path: 'campaigns',
        name: 'marketing-campaigns',
        redirect: to => ({ name: 'marketing-overview', params: to.params, query: to.query })
      },
      {
        path: 'campaigns/google/new',
        name: 'marketing-ad-new',
        component: MarketingAdBuilder,
        meta: { requiresAuth: true, title: 'New Google ad' }
      },
      {
        path: 'campaigns/google/:draftId(\\d+)',
        name: 'marketing-ad-draft',
        component: MarketingAdBuilder,
        meta: { requiresAuth: true, title: 'Google ad' }
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
        meta: { requiresAuth: true, title: 'Ad results' }
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
        meta: { requiresAuth: true, title: 'Channels' }
      }
    ]
  }
]

export default routes
