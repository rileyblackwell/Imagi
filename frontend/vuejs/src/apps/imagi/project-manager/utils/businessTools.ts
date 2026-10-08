/**
 * businessTools.ts - Configuration for the Imagi business workspace.
 *
 * Imagi lets users BUILD a business (create a web app with AI agents) and RUN
 * that business (tools for selling, marketing, and operations). This file is the
 * single source of truth for the categories shown on a project's hub page.
 *
 * To add or change a workspace tool, edit the `businessTools` array below. The
 * hub cards, the coming-soon template pages, and routing all read from here.
 *
 * This file is domain configuration — names, taglines, icons, routes. The class
 * strings that dress a tool's accent live in `@/shared/styles/accents`, where
 * each workspace reads the same definition its hub card does.
 */

import { type ToolAccent } from '@/shared/styles'

export type { ToolAccent }
export type ToolStatus = 'available' | 'coming-soon'

/** A single capability listed on a tool category's page. */
export interface ToolFeature {
  /** Font Awesome icon class, e.g. "fa-cart-shopping". */
  icon: string
  name: string
  description: string
}

/** A workspace category shown on the project hub. */
export interface BusinessTool {
  /** Stable identifier. */
  id: string
  /**
   * URL segment used for coming-soon tools, e.g. /project/:name/sales.
   * `null` for tools that route to a dedicated view instead (e.g. Build).
   */
  slug: string | null
  /** Short label, e.g. "Build". */
  name: string
  /** One-line summary shown under the name. */
  tagline: string
  /** Longer description shown on the tool's own page. */
  description: string
  /** Font Awesome icon class, e.g. "fa-wand-magic-sparkles". */
  icon: string
  /**
   * The thin-stroke mark the hub draws, keyed to shared LineIcon's set. These
   * are the same marks the home page uses to describe the same four modules, so
   * a visitor meets Sell as the handshake on the way in and finds the handshake
   * again on the hub.
   */
  lineIcon: string
  accent: ToolAccent
  status: ToolStatus
  /**
   * Named route to navigate to when the card is clicked. Available tools point
   * at a real view; coming-soon tools reuse the generic 'project-tool' route.
   */
  routeName: string
  /** Planned capabilities, rendered as a preview on the tool's page. */
  features: ToolFeature[]
}

/**
 * The four pillars of the Imagi workspace, all live today: "Build" (the AI
 * app builder), "Sell" (Stripe-powered products, checkout, orders, and
 * customers), "Market" (Twilio-powered campaigns, inbox, and audience), and
 * "Operate" (a dashboard for the live app and the business's money).
 */
export const businessTools: BusinessTool[] = [
  {
    id: 'build',
    slug: null,
    name: 'Build',
    tagline: 'Create your product with AI',
    description:
      'Design and build your web application with AI agents. Describe what you want in plain language and Imagi generates the pages, styling, and logic for your product.',
    icon: 'fa-wand-magic-sparkles',
    lineIcon: 'design',
    accent: 'blue',
    status: 'available',
    routeName: 'builder-workspace',
    features: [
      { icon: 'fa-comments', name: 'AI agents', description: 'Chat with agents that build and edit your app.' },
      { icon: 'fa-code', name: 'Live workspace', description: 'Generate and refine pages in real time.' },
      { icon: 'fa-eye', name: 'Instant preview', description: 'See your product update as you build.' },
    ],
  },
  {
    id: 'sell',
    slug: 'sales',
    name: 'Sell',
    tagline: 'Turn visitors into customers',
    description:
      'Everything you need to sell your product or service — storefronts, checkout, orders, and customer relationships, all connected to the app you build.',
    icon: 'fa-hand-holding-dollar',
    lineIcon: 'sales',
    accent: 'emerald',
    status: 'available',
    routeName: 'sell-overview',
    features: [
      { icon: 'fa-cart-shopping', name: 'Storefront & checkout', description: 'Sell products and take payments with Stripe.' },
      { icon: 'fa-receipt', name: 'Orders', description: 'Track and fulfill customer orders.' },
      { icon: 'fa-address-book', name: 'CRM', description: 'Manage leads and customer relationships.' },
    ],
  },
  {
    id: 'market',
    slug: 'marketing',
    name: 'Market',
    tagline: 'Run campaigns',
    description:
      'Run campaigns that reach your customers: texts to your contacts through Twilio, and search ads on Google, with every campaign and its results in one place.',
    icon: 'fa-bullhorn',
    lineIcon: 'marketing',
    accent: 'violet',
    status: 'available',
    routeName: 'marketing-overview',
    features: [
      { icon: 'fa-comment-sms', name: 'Text campaigns', description: 'Text your contacts, now or scheduled, through Twilio.' },
      { icon: 'fa-magnifying-glass', name: 'Google search ads', description: 'Plan an ad, its keywords and a daily budget.' },
      { icon: 'fa-inbox', name: 'Two-way inbox', description: 'Read and reply to customer texts in one thread.' },
    ],
  },
  {
    id: 'operate',
    slug: 'operations',
    name: 'Operate',
    tagline: 'Run the business',
    description:
      'One dashboard for running the business: whether your app is up and fast, who is visiting, and your revenue, expenses and profit.',
    icon: 'fa-briefcase',
    lineIcon: 'finance',
    accent: 'amber',
    status: 'available',
    routeName: 'operate-dashboard',
    features: [
      { icon: 'fa-signal', name: 'Your app', description: 'Uptime, response time, and visitors to your live app.' },
      { icon: 'fa-sack-dollar', name: 'Your business', description: 'Revenue, expenses, and profit, month by month.' },
    ],
  },
]

/** Look up a tool by its URL slug (for coming-soon routes). */
export function getToolBySlug(slug: string): BusinessTool | undefined {
  return businessTools.find(tool => tool.slug === slug)
}
