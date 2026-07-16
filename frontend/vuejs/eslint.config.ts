import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import pluginOxlint from 'eslint-plugin-oxlint'
import skipFormatting from 'eslint-config-prettier'

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**', '**/node_modules/**']),

  pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,

  // Rules covered by oxlint (which runs first in `npm run lint`) are
  // disabled here so the two linters don't double-report.
  ...pluginOxlint.configs['flat/recommended'],
  skipFormatting,

  {
    name: 'app/rule-overrides',
    rules: {
      // `any` is used deliberately at API boundaries throughout this codebase.
      '@typescript-eslint/no-explicit-any': 'off',
      // Multi-word names are a convention we don't follow for view components
      // (e.g. Login.vue, Register.vue routed views).
      'vue/multi-word-component-names': 'off',
      // Many older components still use plain <script>; don't force a mass
      // TypeScript conversion.
      'vue/block-lang': ['error', { script: { lang: 'ts', allowNoLang: true } }],
      // Existing debt: surfaced without failing the build. New unused vars
      // still show up in lint output.
      '@typescript-eslint/no-unused-vars': 'warn',
    },
  },
)
