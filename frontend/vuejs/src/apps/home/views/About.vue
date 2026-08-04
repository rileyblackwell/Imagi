<!--
  About page.

  Same editorial surface as the home page: paper and ink, hairline rules,
  headline-left / copy-right section headers, and ruled columns in place of
  cards. Everything visual comes from shared/styles/editorial.css.
-->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="editorial relative min-h-screen font-body">
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <main class="relative z-10">

        <!-- Opening statement -->
        <section class="relative pt-32 sm:pt-40 md:pt-44 pb-4">
          <div class="section-shell">
            <div class="md:flex md:items-end md:justify-between gap-12 lg:gap-16">
              <div class="max-w-[36rem]">
                <p class="eyebrow">
                  <span class="eyebrow__rule" aria-hidden="true"></span>
                  <span>About Imagi</span>
                </p>
                <h1 class="display mt-7 text-[2.75rem] sm:text-6xl md:text-[3.9rem]">
                  Build and run a business
                </h1>
              </div>
              <p class="lede mt-7 md:mt-0 md:max-w-sm md:pb-3 text-lg">
                One platform for the whole thing: make the product with AI, then market it,
                sell it and keep the books &mdash; without a technical team behind you.
              </p>
            </div>
          </div>
        </section>

        <!-- Mission -->
        <section class="relative py-20 md:py-28">
          <div class="section-shell">
            <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>

            <div v-reveal class="md:flex md:items-end md:justify-between gap-14">
              <div class="max-w-xl">
                <p class="eyebrow">
                  <span class="eyebrow__num">01</span>
                  <span class="eyebrow__rule" aria-hidden="true"></span>
                  <span>Our mission</span>
                </p>
                <h2 class="display mt-6 text-4xl sm:text-5xl md:text-[3.2rem]">
                  Entrepreneurship, without the gatekeeping
                </h2>
              </div>
              <p class="lede mt-6 md:mt-0 md:max-w-sm md:pb-2 text-lg">
                Starting a business shouldn't require a co-founder who codes. We give you the
                tools to build the product and the tools to run the company behind it.
              </p>
            </div>

            <div class="rule-cols mt-14 md:mt-16">
              <div
                v-for="(card, index) in missionCards"
                :key="card.title"
                v-reveal="{ delay: 80 + index * 80 }"
                class="rule-col"
              >
                <h3 class="rule-col__title !mt-0">{{ card.title }}</h3>
                <p class="rule-col__body !mb-0">{{ card.description }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- What we do -->
        <section class="relative py-20 md:py-28">
          <div class="section-shell">
            <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>

            <div v-reveal class="md:flex md:items-end md:justify-between gap-14">
              <div class="max-w-xl">
                <p class="eyebrow">
                  <span class="eyebrow__num">02</span>
                  <span class="eyebrow__rule" aria-hidden="true"></span>
                  <span>What we do</span>
                </p>
                <h2 class="display mt-6 text-4xl sm:text-5xl md:text-[3.2rem]">
                  One platform, not a dozen subscriptions
                </h2>
              </div>
              <p class="lede mt-6 md:mt-0 md:max-w-sm md:pb-2 text-lg">
                AI-built web apps and the everyday operating tools in the same project, so the
                two halves of a business actually know about each other.
              </p>
            </div>

            <div class="rule-cols mt-14 md:mt-16">
              <div
                v-for="(feature, index) in features"
                :key="feature.title"
                v-reveal="{ delay: 80 + index * 80 }"
                class="rule-col"
              >
                <HomeCardIcon :name="feature.icon" class="rule-col__icon" />
                <h3 class="rule-col__title">{{ feature.title }}</h3>
                <p class="rule-col__body !mb-0">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Who we serve -->
        <section class="relative py-20 md:py-28">
          <div class="section-shell">
            <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>

            <div v-reveal class="md:flex md:items-end md:justify-between gap-14">
              <div class="max-w-xl">
                <p class="eyebrow">
                  <span class="eyebrow__num">03</span>
                  <span class="eyebrow__rule" aria-hidden="true"></span>
                  <span>Who we serve</span>
                </p>
                <h2 class="display mt-6 text-4xl sm:text-5xl md:text-[3.2rem]">
                  Anyone with an idea and no engineering queue
                </h2>
              </div>
              <p class="lede mt-6 md:mt-0 md:max-w-sm md:pb-2 text-lg">
                Founders, small businesses, teams and side projects &mdash; the common thread is
                wanting to ship without waiting on someone else to write it.
              </p>
            </div>

            <div class="rule-cols rule-cols--2 mt-14 md:mt-16">
              <div
                v-for="(userType, index) in userTypes"
                :key="userType.title"
                v-reveal="{ delay: 80 + index * 80 }"
                class="rule-col"
              >
                <h3 class="rule-col__title !mt-0">{{ userType.title }}</h3>
                <p class="rule-col__body !mb-0">{{ userType.description }}</p>
              </div>
            </div>
          </div>
        </section>

        <CTASection
          title="Ready to start?"
          description="Describe what you want to build, and have a working web app the same afternoon — with the tools to market, sell and run it waiting in the same project."
          primaryButtonText="Start building"
          secondaryButtonText="Read the docs"
          secondaryButtonTo="/docs"
        />
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { CTASection } from '@/apps/home/components/organisms/sections'
import { HomeCardIcon } from '@/apps/home/components/atoms'
import reveal from '@/apps/home/directives/reveal'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout,
    CTASection,
    HomeCardIcon
  },
  directives: { reveal },
  setup() {
    const missionCards = [
      {
        title: 'Built for founders, not programmers',
        description: 'Imagi is for people with a business to start and no technical team to start it with. The tools speak in outcomes rather than in framework names.'
      },
      {
        title: 'Build and run in one place',
        description: 'Making the product, finding customers, taking payments and tracking the money all live in the same project — not across a dozen disconnected services.'
      },
      {
        title: 'The complexity stays ours',
        description: 'Agents handle the code and the deploys; the built-in tools handle the operational grind. You stay on the vision and the customers.'
      }
    ]

    const features = [
      {
        title: 'AI app builder',
        description: 'Describe what you want in plain language, shape it visually, and deploy to a real URL in a click. Real Vue and Django underneath, not a walled garden.',
        icon: 'design'
      },
      {
        title: 'Marketing and sales',
        description: 'Campaigns, contacts and ad accounts on one side; products, checkout links and orders on the other — wired into the app you just built.',
        icon: 'marketing'
      },
      {
        title: 'Finance and operations',
        description: 'Invoices out, income and expenses tracked, and the operational work that keeps the business running, all against the same project.',
        icon: 'finance'
      }
    ]

    const userTypes = [
      {
        title: 'Startup founders',
        description: 'Go from idea to a running business without hiring first. Build the product, launch it, and start finding customers before making the big commitments.'
      },
      {
        title: 'Small business owners',
        description: 'Get online and keep marketing, sales and finances together, instead of stitching a patchwork of subscriptions into something that half works.'
      },
      {
        title: 'Business teams',
        description: 'Launch products and run operations without queueing behind engineering for every change to the website.'
      },
      {
        title: 'Creators and side projects',
        description: 'Turn a project into a real business — build the app, market it, take payments and track the money, without spending months learning to do all four.'
      }
    ]

    return { missionCards, features, userTypes }
  }
})
</script>
