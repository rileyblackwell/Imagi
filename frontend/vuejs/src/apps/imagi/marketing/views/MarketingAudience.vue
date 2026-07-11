<!--
  MarketingAudience.vue - The project's contact list: search/filter, add,
  edit, delete, and bulk import. Consent is front and center — campaigns only
  reach subscribed contacts.
-->
<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-col lg:flex-row lg:items-center gap-3 mb-6">
      <div class="relative flex-1">
        <i class="fas fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-xs text-blue-950/40 dark:text-white/30"></i>
        <input
          v-model="search"
          type="search"
          placeholder="Search by name, phone, or email"
          class="pl-9"
          :class="ui.input"
          @input="debouncedLoad"
        />
      </div>
      <div class="flex items-center gap-3">
        <select v-model="consentFilter" :class="ui.input" class="w-auto" @change="load">
          <option value="">All contacts</option>
          <option value="subscribed">Subscribed</option>
          <option value="unsubscribed">Unsubscribed</option>
        </select>
        <select v-model="tagFilter" :class="ui.input" class="w-auto" @change="load">
          <option value="">All tags</option>
          <option v-for="tag in store.tags" :key="tag.tag" :value="tag.tag">{{ tag.tag }} ({{ tag.count }})</option>
        </select>
        <button type="button" :class="ui.secondaryBtn" @click="showImport = true">
          <i class="fas fa-file-import text-xs"></i>
          Import
        </button>
        <button type="button" :class="ui.primaryBtn" @click="openCreate">
          <i class="fas fa-user-plus text-xs"></i>
          Add contact
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.contactsLoading && !store.contacts.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-violet-200 dark:border-violet-300/30 border-t-violet-600 dark:border-t-violet-300 rounded-full animate-spin"></div>
    </div>

    <!-- Table -->
    <section v-else-if="store.contacts.length" class="overflow-hidden" :class="ui.card">
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[720px]">
          <thead>
            <tr class="text-left text-xs font-semibold uppercase tracking-[0.12em] text-blue-950/50 dark:text-blue-100/50 border-b border-blue-200/60 dark:border-white/[0.08]">
              <th class="px-5 py-3.5 font-semibold">Name</th>
              <th class="px-5 py-3.5 font-semibold">Phone</th>
              <th class="px-5 py-3.5 font-semibold">Tags</th>
              <th class="px-5 py-3.5 font-semibold">Status</th>
              <th class="px-5 py-3.5 font-semibold">Added</th>
              <th class="px-5 py-3.5"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="contact in store.contacts"
              :key="contact.id"
              class="border-b border-blue-200/40 dark:border-white/[0.05] last:border-b-0 hover:bg-violet-50/40 dark:hover:bg-violet-400/[0.05] transition-colors duration-150"
            >
              <td class="px-5 py-3.5">
                <p class="font-medium text-blue-950 dark:text-white">{{ contact.display_name }}</p>
                <p v-if="contact.email" class="text-xs text-blue-950/50 dark:text-blue-100/50">{{ contact.email }}</p>
              </td>
              <td class="px-5 py-3.5 font-mono text-xs text-blue-950/70 dark:text-blue-100/70">{{ contact.phone_number }}</td>
              <td class="px-5 py-3.5">
                <div class="flex flex-wrap gap-1.5">
                  <span
                    v-for="tag in contact.tags"
                    :key="tag"
                    class="px-2 py-0.5 rounded-full border border-violet-200/70 dark:border-violet-400/25 bg-violet-50/80 dark:bg-violet-400/10 text-[11px] font-medium text-violet-700 dark:text-violet-300"
                  >
                    {{ tag }}
                  </span>
                  <span v-if="!contact.tags.length" class="text-xs text-blue-950/40 dark:text-white/30">—</span>
                </div>
              </td>
              <td class="px-5 py-3.5"><StatusBadge :status="contact.consent" /></td>
              <td class="px-5 py-3.5 text-xs text-blue-950/60 dark:text-blue-100/60 whitespace-nowrap">{{ formatDateTime(contact.created_at) }}</td>
              <td class="px-5 py-3.5">
                <div class="flex items-center justify-end gap-1">
                  <router-link
                    v-if="contact.consent === 'subscribed'"
                    :to="{ name: 'marketing-inbox', params: { projectName: route.params.projectName }, query: { contact: contact.id } }"
                    class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-white/50 hover:text-violet-700 dark:hover:text-violet-300 hover:bg-violet-50 dark:hover:bg-violet-400/10 transition-colors duration-150"
                    title="Send a message"
                  >
                    <i class="fas fa-paper-plane text-xs"></i>
                  </router-link>
                  <button
                    type="button"
                    class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-white/50 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-150"
                    title="Edit contact"
                    @click="openEdit(contact)"
                  >
                    <i class="fas fa-pen text-xs"></i>
                  </button>
                  <button
                    type="button"
                    class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-white/50 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors duration-150"
                    title="Delete contact"
                    @click="removeContact(contact)"
                  >
                    <i class="fas fa-trash-can text-xs"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="px-5 py-3 border-t border-blue-200/60 dark:border-white/[0.08] text-xs text-blue-950/50 dark:text-blue-100/50">
        {{ store.contacts.length }} of {{ store.contactsTotal }} contact{{ store.contactsTotal === 1 ? '' : 's' }}
      </div>
    </section>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-center">
      <div class="w-16 h-16 text-2xl mb-5" :class="ui.iconTile">
        <i class="fas fa-address-book"></i>
      </div>
      <h2 class="text-xl font-semibold text-blue-950 dark:text-white mb-2">
        {{ hasFilters ? 'No contacts match' : 'Build your audience' }}
      </h2>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 max-w-md mb-6">
        {{ hasFilters
          ? 'Try a different search or filter.'
          : 'Add the customers you have permission to text. Tag them to send targeted campaigns later.' }}
      </p>
      <div v-if="!hasFilters" class="flex items-center gap-3">
        <button type="button" :class="ui.primaryBtn" @click="openCreate">
          <i class="fas fa-user-plus text-xs"></i>
          Add a contact
        </button>
        <button type="button" :class="ui.secondaryBtn" @click="showImport = true">
          <i class="fas fa-file-import text-xs"></i>
          Import a list
        </button>
      </div>
    </div>

    <div v-if="loadError" class="mt-4" :class="ui.errorBox">{{ loadError }}</div>

    <!-- Add / edit modal -->
    <MarketingModal v-if="showForm" :title="editingContact ? 'Edit contact' : 'Add contact'" @close="closeForm">
      <form class="space-y-4" @submit.prevent="saveContact">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label :class="ui.label" for="contact-first">First name</label>
            <input id="contact-first" v-model="form.first_name" type="text" maxlength="100" :class="ui.input" />
          </div>
          <div>
            <label :class="ui.label" for="contact-last">Last name</label>
            <input id="contact-last" v-model="form.last_name" type="text" maxlength="100" :class="ui.input" />
          </div>
        </div>
        <div>
          <label :class="ui.label" for="contact-phone">Phone number</label>
          <input
            id="contact-phone"
            v-model="form.phone_number"
            type="tel"
            required
            placeholder="+15551234567"
            :class="ui.input"
          />
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">International format with country code (E.164).</p>
        </div>
        <div>
          <label :class="ui.label" for="contact-email">Email <span class="normal-case tracking-normal font-normal">(optional)</span></label>
          <input id="contact-email" v-model="form.email" type="email" :class="ui.input" />
        </div>
        <div>
          <label :class="ui.label" for="contact-tags">Tags <span class="normal-case tracking-normal font-normal">(comma-separated)</span></label>
          <input id="contact-tags" v-model="form.tagsText" type="text" placeholder="vip, newsletter" :class="ui.input" />
        </div>
        <div v-if="editingContact">
          <label class="flex items-center gap-2.5 text-sm text-blue-950 dark:text-white cursor-pointer">
            <input v-model="form.subscribed" type="checkbox" class="accent-violet-600" />
            Subscribed to messages
          </label>
        </div>
        <div v-else :class="ui.infoBox">
          Only add people who have agreed to receive messages from your business — carriers require it, and Twilio enforces STOP requests automatically.
        </div>

        <div v-if="formError" :class="ui.errorBox">{{ formError }}</div>

        <div class="flex items-center justify-end gap-3 pt-1">
          <button type="button" :class="ui.secondaryBtn" @click="closeForm">Cancel</button>
          <button type="submit" :class="ui.primaryBtn" :disabled="formBusy || !form.phone_number.trim()">
            <i v-if="formBusy" class="fas fa-circle-notch animate-spin"></i>
            {{ editingContact ? 'Save changes' : 'Add contact' }}
          </button>
        </div>
      </form>
    </MarketingModal>

    <!-- Import modal -->
    <MarketingModal v-if="showImport" title="Import contacts" wide @close="closeImport">
      <div class="space-y-4">
        <p class="text-sm text-blue-950/70 dark:text-blue-100/70">
          Paste one contact per line:
          <code class="font-mono text-xs px-1.5 py-0.5 rounded bg-blue-950/[0.05] dark:bg-white/[0.08]">phone, first name, last name, email, tag1; tag2</code>
          — only the phone number is required.
        </p>
        <textarea
          v-model="importText"
          rows="8"
          placeholder="+15551234567, Ada, Lovelace, ada@example.com, vip; early
+15559876543, Grace"
          class="font-mono text-xs"
          :class="ui.input"
        ></textarea>
        <p class="text-xs text-blue-950/50 dark:text-blue-100/50">
          {{ parsedImportRows.length }} contact{{ parsedImportRows.length === 1 ? '' : 's' }} ready to import.
          Duplicates and invalid numbers are skipped automatically.
        </p>

        <div v-if="importError" :class="ui.errorBox">{{ importError }}</div>

        <div v-if="importResult" :class="ui.successBox">
          <p class="font-medium">Imported {{ importResult.created }} contact{{ importResult.created === 1 ? '' : 's' }}.</p>
          <ul v-if="importResult.skipped.length" class="mt-2 space-y-0.5 text-xs opacity-90">
            <li v-for="(row, i) in importResult.skipped.slice(0, 8)" :key="i">
              Line {{ row.index + 1 }}{{ row.phone_number ? ` (${row.phone_number})` : '' }}: {{ row.reason }}
            </li>
            <li v-if="importResult.skipped.length > 8">…and {{ importResult.skipped.length - 8 }} more skipped.</li>
          </ul>
        </div>

        <div class="flex items-center justify-end gap-3">
          <button type="button" :class="ui.secondaryBtn" @click="closeImport">
            {{ importResult ? 'Done' : 'Cancel' }}
          </button>
          <button
            v-if="!importResult"
            type="button"
            :class="ui.primaryBtn"
            :disabled="importBusy || !parsedImportRows.length"
            @click="runImport"
          >
            <i v-if="importBusy" class="fas fa-circle-notch animate-spin"></i>
            Import {{ parsedImportRows.length || '' }} contact{{ parsedImportRows.length === 1 ? '' : 's' }}
          </button>
        </div>
      </div>
    </MarketingModal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { debounce } from 'lodash-es'
import MarketingModal from '../components/MarketingModal.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { Contact, ImportResult, ImportRow } from '../types'
import { formatDateTime, ui } from '../utils/ui'

const route = useRoute()
const store = useMarketingStore()

const search = ref('')
const consentFilter = ref('')
const tagFilter = ref('')
const loadError = ref('')

const showForm = ref(false)
const editingContact = ref<Contact | null>(null)
const formBusy = ref(false)
const formError = ref('')
const form = reactive({
  first_name: '',
  last_name: '',
  phone_number: '',
  email: '',
  tagsText: '',
  subscribed: true,
})

const showImport = ref(false)
const importText = ref('')
const importBusy = ref(false)
const importError = ref('')
const importResult = ref<ImportResult | null>(null)

const hasFilters = computed(() => Boolean(search.value || consentFilter.value || tagFilter.value))

async function load() {
  loadError.value = ''
  try {
    await store.fetchContacts({
      search: search.value || undefined,
      consent: consentFilter.value || undefined,
      tag: tagFilter.value || undefined,
    })
  } catch (error) {
    loadError.value = extractError(error, 'Could not load contacts.')
  }
}

const debouncedLoad = debounce(load, 300)

function openCreate() {
  editingContact.value = null
  Object.assign(form, {
    first_name: '', last_name: '', phone_number: '', email: '', tagsText: '', subscribed: true,
  })
  formError.value = ''
  showForm.value = true
}

function openEdit(contact: Contact) {
  editingContact.value = contact
  Object.assign(form, {
    first_name: contact.first_name,
    last_name: contact.last_name,
    phone_number: contact.phone_number,
    email: contact.email,
    tagsText: contact.tags.join(', '),
    subscribed: contact.consent === 'subscribed',
  })
  formError.value = ''
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingContact.value = null
}

async function saveContact() {
  formBusy.value = true
  formError.value = ''
  const payload = {
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    phone_number: form.phone_number.trim().replace(/[\s()-]/g, ''),
    email: form.email.trim(),
    tags: form.tagsText.split(',').map(tag => tag.trim()).filter(Boolean),
  }
  try {
    if (editingContact.value) {
      await store.updateContact(editingContact.value.id, {
        ...payload,
        consent: form.subscribed ? 'subscribed' : 'unsubscribed',
      })
    } else {
      await store.createContact(payload)
    }
    showForm.value = false
    await Promise.all([load(), store.fetchTags().catch(() => {})])
  } catch (error) {
    formError.value = extractError(error, 'Could not save the contact.')
  } finally {
    formBusy.value = false
  }
}

async function removeContact(contact: Contact) {
  if (!window.confirm(`Remove ${contact.display_name} from your audience? Their message history stays in the inbox.`)) return
  try {
    await store.deleteContact(contact.id)
  } catch (error) {
    loadError.value = extractError(error, 'Could not delete the contact.')
  }
}

const parsedImportRows = computed<ImportRow[]>(() => {
  return importText.value
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean)
    .map(line => {
      const [phone = '', first = '', last = '', email = '', tags = ''] = line.split(',').map(part => part.trim())
      return {
        phone_number: phone.replace(/[\s()-]/g, ''),
        first_name: first,
        last_name: last,
        email,
        tags: tags.split(';').map(tag => tag.trim()).filter(Boolean),
      }
    })
    .filter(row => row.phone_number.length > 0)
})

async function runImport() {
  importBusy.value = true
  importError.value = ''
  try {
    importResult.value = await store.importContacts(parsedImportRows.value)
    await Promise.all([load(), store.fetchTags().catch(() => {})])
  } catch (error) {
    importError.value = extractError(error, 'Import failed.')
  } finally {
    importBusy.value = false
  }
}

function closeImport() {
  showImport.value = false
  importText.value = ''
  importError.value = ''
  importResult.value = null
}

onMounted(async () => {
  await load()
  try {
    await store.fetchTags()
  } catch {
    // Tag filter just stays empty.
  }
})
</script>
