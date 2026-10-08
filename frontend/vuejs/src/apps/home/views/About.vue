<!--
  About page — on the home page's Spotlight stage.

  The same lit stage as Home: an opener under the spotlight, centered section
  headers, cards for the points, and the closing prompt. Light and dark come
  from shared/styles/spotlight.css, which follows the site theme.
-->
<template>
  <div class="spotlight about-page">
    <DefaultLayout>
      <!-- Opening statement -->
      <section class="sl-opener">
        <div class="sl-spot" aria-hidden="true"></div>
        <div class="sl-dots" aria-hidden="true"></div>

        <div class="sl-wrap sl-opener__inner">
          <p class="about-rise sl-eyebrow sl-pill">
            <span class="sl-pip" aria-hidden="true"></span>
            <span>About Imagi</span>
          </p>
          <h1 class="about-rise sl-display sl-h1 about-title" style="animation-delay: 60ms">
            Build and <em class="sl-run">run</em> a business
          </h1>
          <p class="about-rise sl-lede" style="animation-delay: 120ms">
            One platform for the whole thing: make the product with AI, then market it,
            sell it and keep the books &mdash; without a technical team behind you.
          </p>
        </div>
      </section>

      <!-- Mission -->
      <section class="sl-sec about-step">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow"><span class="sl-grad-text about-num">01</span><span>Our mission</span></p>
            <h2 class="sl-display sl-h2">Entrepreneurship, without the gatekeeping</h2>
            <p class="sl-lede">
              Starting a business shouldn't require a co-founder who codes. We give you the
              tools to build the product and the tools to run the company behind it.
            </p>
          </div>

          <div class="sl-cards">
            <article
              v-for="(card, index) in missionCards"
              :key="card.title"
              v-reveal="{ delay: 80 + index * 80 }"
              class="sl-card"
            >
              <h3 class="sl-card__title">{{ card.title }}</h3>
              <p class="sl-card__body">{{ card.description }}</p>
            </article>
          </div>
        </div>
      </section>

      <div class="sl-divider" aria-hidden="true"></div>

      <!-- What we do -->
      <section class="sl-sec about-step">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow"><span class="sl-grad-text about-num">02</span><span>What we do</span></p>
            <h2 class="sl-display sl-h2">One platform, not a dozen subscriptions</h2>
            <p class="sl-lede">
              AI-built web apps and the everyday operating tools in the same project, so the
              two halves of a business actually know about each other.
            </p>
          </div>

          <div class="sl-cards">
            <article
              v-for="(feature, index) in features"
              :key="feature.title"
              v-reveal="{ delay: 80 + index * 80 }"
              class="sl-card"
            >
              <span class="sl-card__icon"><LineIcon :name="feature.icon" /></span>
              <h3 class="sl-card__title">{{ feature.title }}</h3>
              <p class="sl-card__body">{{ feature.description }}</p>
            </article>
          </div>
        </div>
      </section>

      <div class="sl-divider" aria-hidden="true"></div>

      <!-- Who we serve -->
      <section class="sl-sec about-step">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow"><span class="sl-grad-text about-num">03</span><span>Who we serve</span></p>
            <h2 class="sl-display sl-h2">Anyone with an idea and no engineering queue</h2>
            <p class="sl-lede">
              Founders, small businesses, teams and side projects &mdash; the common thread is
              wanting to ship without waiting on someone else to write it.
            </p>
          </div>

          <div class="sl-cards sl-cards--2">
            <article
              v-for="(userType, index) in userTypes"
              :key="userType.title"
              v-reveal="{ delay: 80 + index * 80 }"
              class="sl-card"
            >
              <h3 class="sl-card__title">{{ userType.title }}</h3>
              <p class="sl-card__body">{{ userType.description }}</p>
            </article>
          </div>
        </div>
      </section>

      <ClosingSection
        title="Ready to start?"
        description="Describe what you want to build, and have a working web app the same afternoon — with the tools to market, sell and run it waiting in the same project."
        primary-button-text="Start building"
        secondary-button-text="Read the docs"
        secondary-button-to="/docs"
      />
    </DefaultLayout>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { ClosingSection } from '@/apps/home/components/organisms/sections'
import { LineIcon } from '@/shared/components'
import reveal from '@/apps/home/directives/reveal'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout,
    ClosingSection,
    LineIcon
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
        description: 'Uptime, speed and visitors for the app on one side; revenue, expenses and profit on the other, all against the same project.',
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

<style scoped>
/* Staggered entrance on load, as on the home hero */
.about-rise {
  animation: about-rise 0.85s var(--app-ease) both;
}

@keyframes about-rise {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

/* "Build and run a business" is one word longer than the home headline, so it
   gets a little more measure and a step down in size. */
.sl-opener .about-title {
  max-width: 12ch;
  margin-top: 6px;
  font-size: clamp(46px, 8.4vw, 112px);
}

.about-num {
  font-weight: 700;
}

/* A softer pool of light at the top of each section, as on Home's steps */
.about-step {
  isolation: isolate;
  overflow: hidden;
}

.about-step::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  z-index: -1;
  width: min(1100px, 140vw);
  height: 560px;
  transform: translateX(-50%);
  pointer-events: none;
  background: radial-gradient(ellipse 50% 60% at 50% 0%, var(--sl-section-glow), transparent 70%);
}

@media (prefers-reduced-motion: reduce) {
  .about-rise {
    animation: none;
  }
}
</style>
