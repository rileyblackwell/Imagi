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
 * NOTE: Accent color classes are written as full, static Tailwind strings inside
 * `accentClasses` so the Tailwind JIT compiler can see them. Do not build these
 * class names dynamically or they will be purged from the production build.
 */

export type ToolAccent = 'blue' | 'emerald' | 'violet' | 'amber'
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
 * The four pillars of the Imagi workspace. "Build" is live today (the AI app
 * builder); the rest are general templates that will be filled in later.
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
    accent: 'emerald',
    status: 'coming-soon',
    routeName: 'project-tool',
    features: [
      { icon: 'fa-cart-shopping', name: 'Storefront & checkout', description: 'Sell products and take payments.' },
      { icon: 'fa-receipt', name: 'Orders', description: 'Track and fulfill customer orders.' },
      { icon: 'fa-address-book', name: 'CRM', description: 'Manage leads and customer relationships.' },
    ],
  },
  {
    id: 'market',
    slug: 'marketing',
    name: 'Market',
    tagline: 'Grow your audience',
    description:
      'Reach and engage your customers with campaigns, email, social, and content tools — plus the analytics to see what is working.',
    icon: 'fa-bullhorn',
    accent: 'violet',
    status: 'coming-soon',
    routeName: 'project-tool',
    features: [
      { icon: 'fa-envelope-open-text', name: 'Email campaigns', description: 'Design and send email to your audience.' },
      { icon: 'fa-hashtag', name: 'Social & content', description: 'Plan and publish across channels.' },
      { icon: 'fa-chart-line', name: 'Marketing analytics', description: 'Measure reach, traffic, and conversion.' },
    ],
  },
  {
    id: 'operate',
    slug: 'operations',
    name: 'Operate',
    tagline: 'Run the business',
    description:
      'Manage the day-to-day of your business — finance, invoicing, and operations — with dashboards that give you a clear view of how things are going.',
    icon: 'fa-briefcase',
    accent: 'amber',
    status: 'coming-soon',
    routeName: 'project-tool',
    features: [
      { icon: 'fa-file-invoice-dollar', name: 'Finance & invoicing', description: 'Track revenue, expenses, and invoices.' },
      { icon: 'fa-gauge-high', name: 'Operations dashboard', description: 'Monitor the health of your business.' },
      { icon: 'fa-users-gear', name: 'Team & workflows', description: 'Organize people and recurring work.' },
    ],
  },
]

/** Look up a tool by its URL slug (for coming-soon routes). */
export function getToolBySlug(slug: string): BusinessTool | undefined {
  return businessTools.find(tool => tool.slug === slug)
}

/** Look up a tool by its id. */
export function getToolById(id: string): BusinessTool | undefined {
  return businessTools.find(tool => tool.id === id)
}

/**
 * Full, static Tailwind class strings per accent. Keep these literal so the JIT
 * compiler keeps them in the build. Each entry styles the icon tile, badges,
 * borders, and hover affordances used by the hub card and tool pages.
 */
export const accentClasses: Record<ToolAccent, {
  cardBorder: string
  iconWrap: string
  iconText: string
  badge: string
  link: string
  glow: string
}> = {
  blue: {
    cardBorder: 'border-blue-200/70 dark:border-blue-300/[0.16] hover:border-blue-300 dark:hover:border-blue-300/40',
    iconWrap: 'bg-blue-50 dark:bg-blue-400/10 border-blue-200/60 dark:border-blue-400/25',
    iconText: 'text-blue-600 dark:text-blue-300',
    badge: 'border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-blue-700 dark:text-blue-300',
    link: 'text-blue-700 dark:text-blue-300 group-hover:text-blue-800 dark:group-hover:text-blue-200',
    glow: 'from-blue-400/20',
  },
  emerald: {
    cardBorder: 'border-emerald-200/70 dark:border-emerald-300/[0.16] hover:border-emerald-300 dark:hover:border-emerald-300/40',
    iconWrap: 'bg-emerald-50 dark:bg-emerald-400/10 border-emerald-200/60 dark:border-emerald-400/25',
    iconText: 'text-emerald-600 dark:text-emerald-300',
    badge: 'border-emerald-200/70 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-400/10 text-emerald-700 dark:text-emerald-300',
    link: 'text-emerald-700 dark:text-emerald-300 group-hover:text-emerald-800 dark:group-hover:text-emerald-200',
    glow: 'from-emerald-400/20',
  },
  violet: {
    cardBorder: 'border-violet-200/70 dark:border-violet-300/[0.16] hover:border-violet-300 dark:hover:border-violet-300/40',
    iconWrap: 'bg-violet-50 dark:bg-violet-400/10 border-violet-200/60 dark:border-violet-400/25',
    iconText: 'text-violet-600 dark:text-violet-300',
    badge: 'border-violet-200/70 dark:border-violet-400/25 bg-violet-50/80 dark:bg-violet-400/10 text-violet-700 dark:text-violet-300',
    link: 'text-violet-700 dark:text-violet-300 group-hover:text-violet-800 dark:group-hover:text-violet-200',
    glow: 'from-violet-400/20',
  },
  amber: {
    cardBorder: 'border-amber-200/70 dark:border-amber-300/[0.16] hover:border-amber-300 dark:hover:border-amber-300/40',
    iconWrap: 'bg-amber-50 dark:bg-amber-400/10 border-amber-200/60 dark:border-amber-400/25',
    iconText: 'text-amber-600 dark:text-amber-300',
    badge: 'border-amber-200/70 dark:border-amber-400/25 bg-amber-50/80 dark:bg-amber-400/10 text-amber-700 dark:text-amber-300',
    link: 'text-amber-700 dark:text-amber-300 group-hover:text-amber-800 dark:group-hover:text-amber-200',
    glow: 'from-amber-400/20',
  },
}
