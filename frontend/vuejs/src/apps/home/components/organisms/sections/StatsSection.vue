<!-- Stats Section - warm porcelain editorial design -->
<template>
  <section id="why-imagi" class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 scroll-mt-14 transition-colors duration-500">

    <!-- Cool baby-blue wash behind the section -->
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <div class="section-wash-cool absolute -top-20 right-[-15%] w-[760px] h-[560px]"></div>
    </div>

    <div class="relative max-w-6xl mx-auto">

      <!-- Hairline divider -->
      <div class="section-divider mb-20 md:mb-24" aria-hidden="true"></div>

      <!-- Editorial header: headline left, supporting copy right -->
      <div v-reveal class="md:flex md:items-end md:justify-between gap-12 mb-14 md:mb-16">
        <div class="max-w-xl">
          <SectionLabel label="Why Imagi" tone="orange" class="mb-6" />
          <h2 class="font-display text-4xl sm:text-5xl md:text-[3.4rem] font-semibold text-blue-950 dark:text-white tracking-[-0.015em] leading-[1.08] text-balance transition-colors duration-300">
            Everything your business needs, <em class="section-accent not-italic">in one place</em>
          </h2>
        </div>
        <p class="mt-6 md:mt-0 md:max-w-sm md:pb-2 text-lg text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
          Your practical partner for building and running a business. We handle the technical complexity while you focus on your customers.
        </p>
      </div>

      <!-- Stat band: spec-sheet panel with hairline dividers -->
      <div v-reveal="{ delay: 90 }" class="crisp-card relative rounded-2xl bg-white/85 dark:bg-white/[0.045] border border-blue-950/[0.08] dark:border-white/[0.1] backdrop-blur-sm mb-6 overflow-hidden">
        <div class="grid grid-cols-1 sm:grid-cols-2">
          <div
            v-for="(stat, index) in stats"
            :key="index"
            class="relative px-8 py-10 md:px-12"
            :class="index > 0 ? 'border-t sm:border-t-0 sm:border-l border-blue-950/[0.07] dark:border-white/[0.08]' : ''"
          >
            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700 dark:text-blue-300/70 mb-3 transition-colors duration-300">{{ stat.label }}</p>
            <div class="font-display text-5xl md:text-6xl font-semibold tracking-tight tabular-nums text-blue-950 dark:text-white transition-colors duration-300">
              {{ stat.value }}<span v-if="stat.unit" class="text-3xl text-blue-950/60 dark:text-blue-100/60 ml-1.5 font-medium">{{ stat.unit }}</span>
            </div>
            <p v-if="stat.caption" class="mt-3 text-sm text-blue-950/70 dark:text-blue-100/55 transition-colors duration-300">{{ stat.caption }}</p>
          </div>
        </div>
      </div>

      <!-- Audience cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          v-for="(metric, index) in metrics"
          :key="index"
          v-reveal="{ delay: 140 + index * 90 }"
          class="lift-card group relative h-full p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] border backdrop-blur-sm transition-all duration-300"
          :class="index % 2 === 1 ? 'border-orange-200/70 dark:border-orange-300/[0.14]' : 'border-blue-200/70 dark:border-blue-300/[0.14]'"
        >
          <!-- Icon -->
          <div
            class="icon-tile relative flex items-center justify-center w-12 h-12 rounded-xl mb-6 ring-1 transition-all duration-300"
            :class="index % 2 === 1 ? 'bg-orange-100 dark:bg-orange-400/[0.14] ring-orange-900/[0.08] dark:ring-orange-300/[0.18]' : 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-blue-900/[0.08] dark:ring-blue-300/[0.18]'"
          >
            <HomeCardIcon :name="metric.icon" :class="index % 2 === 1 ? 'text-orange-600 dark:text-orange-300' : 'text-blue-600 dark:text-blue-300'" />
          </div>

          <!-- Title -->
          <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-3">
            {{ metric.title }}
          </h3>

          <!-- Description -->
          <p class="relative text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
            {{ metric.description }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import { SectionLabel, HomeCardIcon } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'StatsSection',
  components: { SectionLabel, HomeCardIcon },
  directives: { reveal },
  props: {
    stats: {
      type: Array,
      default: () => [
        {
          value: 'Free',
          unit: '',
          label: 'Plans Starting At',
          caption: 'Start free, then upgrade as you grow. Usage refreshes on a rolling 5-hour session and a weekly limit—cancel anytime.'
        },
        {
          value: '30',
          unit: 'min',
          label: 'Typical Build Time',
          caption: 'From first prompt to a working app you can share.'
        }
      ]
    },
    metrics: {
      type: Array,
      default: () => [
        {
          icon: 'founders',
          title: 'Ideal for Founders',
          description: 'Go from idea to a running business without a technical co-founder. Build your app, then find customers and grow revenue—all in one platform.'
        },
        {
          icon: 'business',
          title: 'Ideal for Small Businesses',
          description: 'Get your business online and manage marketing, sales, and finances in one place—no need to stitch together a dozen separate tools.'
        },
        {
          icon: 'teams',
          title: 'Ideal for Teams',
          description: 'Give your whole team the tools to launch products and run operations quickly, without waiting on engineering resources.'
        }
      ]
    }
  }
})
</script>

<style scoped>
/* Hairline gradient divider that fades at the edges */
.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(23, 37, 84, 0.12), transparent);
}

.dark .section-divider {
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}

/* Soft cool wash */
.section-wash-cool {
  background: radial-gradient(closest-side, rgba(158, 205, 243, 0.2), rgba(158, 205, 243, 0.06) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .section-wash-cool {
  background: radial-gradient(closest-side, rgba(96, 165, 250, 0.08), rgba(96, 165, 250, 0.02) 55%, transparent 75%);
}

/* Italic serif accent in blue ink */
.section-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #1d4ed8 5%, #2563eb 55%, #0284c7 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.05em;
}

.dark .section-accent {
  background: linear-gradient(115deg, #93c5fd 5%, #60a5fa 60%, #7dd3fc 95%);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Crisp, sharply-defined cards: hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

/* Cards that lift gently on hover */
.lift-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.lift-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.04),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 10px 20px -4px rgba(15, 23, 42, 0.1),
    0 24px 44px -12px rgba(15, 23, 42, 0.14);
}

.dark .lift-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

.dark .lift-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.06),
    0 2px 4px rgba(0, 0, 0, 0.5),
    0 12px 24px -4px rgba(0, 0, 0, 0.5),
    0 28px 48px -12px rgba(0, 0, 0, 0.6);
}

/* Icon tile nudge on card hover */
.lift-card:hover .icon-tile {
  transform: scale(1.06) rotate(-3deg);
}
</style>
