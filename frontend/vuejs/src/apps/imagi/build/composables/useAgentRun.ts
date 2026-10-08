import type { Ref } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { AgentService, STREAM_DROPPED, toolCallToActivityStep } from '../services/agentService'
import { FileService } from '../services/fileService'
import { VersionControlService } from '../services/versionControlService'
import { useAuthStore } from '@/shared/stores/auth'
import { useUsageStore, formatResetTime } from '@/shared/stores/usage'
import type { AIMessage } from '../types/index'
import type { DispatchedTaskRef } from '../types/services'

// Tools that mutate project files. Also drives the interrupted-run cleanup:
// a stopped/turn-capped run that called any of these still changed the disk.
export const FILE_EDIT_TOOLS = new Set([
  'edit_file', 'update_file', 'create_file', 'delete_file', 'create_directory', 'delete_directory'
])

/** Turn an agent tool name into a transient status line ("Editing project
 *  files…"). The per-step activity-feed labels come from labelForTool /
 *  toolCallToActivityStep in agentService, shared with metadata hydration. */
export function describeAgentTool(name: string): string {
  if (name === 'update_plan') return 'Planning…'
  if (name === 'web_search' || name === 'web_search_call') return 'Searching the web…'
  if (['get_project_tree', 'list_project_files', 'glob_files', 'grep_files', 'read_file'].includes(name)) {
    return 'Reading project files…'
  }
  if (FILE_EDIT_TOOLS.has(name)) {
    return 'Editing project files…'
  }
  return 'Working…'
}

/**
 * One agent run, from the user pressing send to the reply settling: the
 * optimistic bubbles, the stream callbacks, the post-run file refresh and
 * commit, and how each way a run can fail is shown. Lifted out of the
 * Workspace view so it can be tested without mounting the whole workspace.
 */
export function useAgentRun(projectId: Ref<string>) {
  const store = useAgentStore()

  // Create a git commit after successful code changes
  function createCommitFromPrompt(filePath: string, prompt: string) {
    if (!projectId.value || !filePath) return;
    
    // Use the version control service to handle commits in the background
    VersionControlService.commitAfterFileOperation(
      projectId.value,
      filePath,
      prompt
    );
  }

  // targetInstanceId lets a queued prompt fire on the instance it was queued
  // for, even when the user has since switched to another one.
  async function handlePrompt(promptText: string, targetInstanceId?: string) {
    if (!promptText.trim()) return

    const instance = targetInstanceId
      ? store.instances.find(i => i.id === targetInstanceId) ?? null
      : store.activeInstance
    if (!instance) return
    if (!instance.selectedModelId) return
    if (!projectId.value) return

    // Backstop for callers that don't pre-check (the chat input queues before
    // submitting): never race a second run onto a busy instance.
    if (instance.isProcessing) {
      store.queuePrompt(instance.id, promptText)
      return
    }

    const instanceId = instance.id
    const conversationIdBefore = instance.conversationId
    // Task runs edit their own git worktree, never the canonical tree — so
    // none of the canonical post-run work (file refresh, auto-commit, version
    // history) applies to them. Committing canonical here would snapshot a
    // parallel lead run's half-finished edits under this task's prompt.
    const isTaskRun = instance.kind === 'task'
    // Set when the connection closed under a run that is still going on the
    // server: the run is followed from there (the store's resync poll), so
    // this handler must not mark it finished on its way out.
    let followedOnServer = false

    try {
      const timestamp = new Date().toISOString()

      store.setInstanceProcessing(instanceId, true)

      // Registered synchronously with the processing flag — before the first
      // await. The resync poller treats "processing with no controller" as a
      // restored server-side run, so a controller registered any later would
      // leave a window where a poll tick wipes this run's transcript and flips
      // processing off mid-start. The stop button and delete guard use it too;
      // cleared when processing ends.
      const abortController = new AbortController()
      store.registerAbortController(instanceId, abortController)

      // Add the user message to this instance's conversation immediately
      const userMessageId = `user-${Date.now()}`
      store.addMessageToInstance(instanceId, {
        role: 'user',
        content: promptText,
        timestamp,
        id: userMessageId
      })

      // Auto-title from first user prompt (mirror backend behaviour for UI
      // snappiness). Not for the lead thread: it renders as "Main agent" and its
      // name is never shown, so naming it would be a write nobody reads.
      if (!instance.title && instance.kind !== 'lead') {
        const firstLine = promptText.trim().split('\n')[0] || ''
        void store.renameInstance(instanceId, firstLine.slice(0, 80))
      }

      const isUserAuthenticated = await useAuthStore().validateAuth()
      if (!isUserAuthenticated) return

      // The assistant message is created empty and filled in as chunks arrive.
      const streamingMessageId = `assistant-response-${Date.now()}`
      let streamedText = ''
      let messageStarted = false
      // Whether the run started server-side (its start event came back). A
      // task run that ends without one never consumed its brief, so a retry
      // fires the brief again rather than telling it to carry on.
      let runStarted = false
      let sawActivity = false
      let sawPlan = false
      let sawFileEdit = false
      // Subagent links accumulated across this run's dispatch events, rendered
      // as clickable cards on the reply (patchMessage replaces the field whole).
      let dispatchedRefs: DispatchedTaskRef[] = []

      // A run interrupted by Stop or the turn cap has still edited files on
      // disk (and the backend persisted its files_changed metadata) — without
      // this, those edits get no refresh, no commit, and no version-history
      // entry, then silently ride along in the next run's auto-commit.
      // Canonical-tree runs only: a task's edits live in its worktree (the
      // backend checkpoints them there) and reach the canonical tree solely
      // through accept-merge.
      const finalizeInterruptedEdits = async (suffix: string) => {
        if (isTaskRun || !sawFileEdit) return
        try {
          store.setFiles(await FileService.getProjectFiles(projectId.value))
        } catch (refreshError) {
          console.warn('Error refreshing files after interrupted run:', refreshError)
        }
        // The commit endpoint stages `git add .` itself and no-ops when
        // nothing actually changed, so this is safe even if the edit failed.
        createCommitFromPrompt('/', `${promptText} ${suffix}`)
      }

      // The message appears on the first sign of life — text OR a tool call —
      // so a tools-only turn still shows its activity feed as it happens, while
      // a run that dies instantly leaves no empty bubble behind.
      const ensureAssistantMessage = () => {
        if (messageStarted) return
        messageStarted = true
        store.addMessageToInstance(instanceId, {
          role: 'assistant',
          content: '',
          timestamp: new Date().toISOString(),
          id: streamingMessageId
        })
      }

      try {
        store.setInstanceStatus(instanceId, 'Thinking…')
        const response = await AgentService.streamAgent(
          projectId.value,
          {
            prompt: promptText,
            model: instance.selectedModelId,
            reasoningEffort: instance.selectedEffort,
            file: instance.selectedFile,
            conversationId: conversationIdBefore ?? undefined
          },
          {
            onStart: (conversationId, info) => {
              runStarted = true
              if (conversationId && !instance.conversationId) {
                store.updateInstanceConversationId(instanceId, conversationId)
              }
              // Tie the optimistic bubble to its persisted row so the inline
              // restore-checkpoint control works without a reload.
              if (info?.userMessageId || info?.checkpoint) {
                store.setMessageCheckpoint(
                  instanceId, userMessageId, info.userMessageId, info.checkpoint
                )
              }
            },
            onDelta: (text) => {
              ensureAssistantMessage()
              // The reply is streaming; the status line would just sit under it.
              store.setInstanceStatus(instanceId, '')
              streamedText += text
              store.setMessageContent(instanceId, streamingMessageId, streamedText)
            },
            onToolCall: (name, args) => {
              ensureAssistantMessage()
              sawActivity = true
              if (FILE_EDIT_TOOLS.has(name)) sawFileEdit = true
              store.appendMessageActivity(
                instanceId,
                streamingMessageId,
                toolCallToActivityStep(name, args)
              )
              store.setInstanceStatus(instanceId, describeAgentTool(name))
            },
            onPlan: (plan) => {
              ensureAssistantMessage()
              sawPlan = sawPlan || plan.length > 0
              store.setMessagePlan(instanceId, streamingMessageId, plan)
            },
            onTitle: (conversationId, title) => {
              // The backend auto-named the thread from its opening exchange;
              // reflect it in the sidebar without a reload.
              store.applyInstanceTitle(conversationId, title)
            },
            onTaskDispatch: (tasks) => {
              // The lead agent delegated work: start those background runs now,
              // in parallel, while this run keeps streaming. They edit their own
              // worktrees, so they neither block nor are blocked by this one.
              store.startDispatchedTasks(tasks)
              // Link the subagents into the reply itself, so the work is one
              // click away and the main thread stays a clean summary.
              ensureAssistantMessage()
              dispatchedRefs = [
                ...dispatchedRefs,
                ...tasks.map(t => ({ conversationId: t.conversation_id, title: t.title || '' }))
              ]
              store.patchMessage(instanceId, streamingMessageId, {
                dispatchedTasks: dispatchedRefs
              })
            },
          },
          abortController.signal
        )

        if ((response as any).conversation_id && !instance.conversationId) {
          store.updateInstanceConversationId(instanceId, (response as any).conversation_id)
        }

        // Reconcile with the run's authoritative final text: deltas can miss
        // content the model emitted without streaming it.
        if (response.response && response.response !== streamedText) {
          ensureAssistantMessage()
          store.setMessageContent(instanceId, streamingMessageId, response.response)
        }

        if (messageStarted && !streamedText && !response.response && !sawActivity && !sawPlan) {
          // The run produced nothing visible — no text, no activity, no plan.
          store.removeMessage(instanceId, streamingMessageId)
        } else if (messageStarted) {
          // Attach end-of-run telemetry to the reply itself so it survives in
          // the transcript (mirrors what the backend persists as metadata).
          const meta: {
            filesChanged?: string[]
            usage?: AIMessage['usage']
            question?: AIMessage['question']
          } = {}
          if (response.files_changed && response.files_changed.length > 0) {
            meta.filesChanged = response.files_changed
          }
          // Keep every usage field the run reported; absent usage stays absent
          // (unknown, never free/zero).
          const usage = response.usage
          if (usage) {
            const mapped: NonNullable<AIMessage['usage']> = {}
            if (typeof usage.cost_usd === 'number') mapped.costUsd = usage.cost_usd
            if (typeof usage.input_tokens === 'number') mapped.inputTokens = usage.input_tokens
            if (typeof usage.output_tokens === 'number') mapped.outputTokens = usage.output_tokens
            if (Object.keys(mapped).length > 0) meta.usage = mapped
          }
          // A question with one-tap answers or a sketch (ask_user)
          if (response.question && (response.question.options?.length || response.question.visual)) {
            meta.question = response.question
          }
          if (meta.filesChanged || meta.usage || meta.question) {
            store.setMessageMeta(instanceId, streamingMessageId, meta)
          }
        }

        // Canonical-tree runs only: a task changed its worktree, not the tree
        // this refresh/commit targets — its changes land via accept-merge
        // (handleTaskAccepted does the refresh then).
        if (!isTaskRun && response.files_changed && response.files_changed.length > 0) {
          // One refresh + one commit for the whole run: the backend stages
          // `git add .` regardless of path, so a per-file loop just produced
          // N identical fetches and N commits.
          try {
            const files = await FileService.getProjectFiles(projectId.value)
            store.setFiles(files)
          } catch (refreshError) {
            console.warn('Error refreshing files after agent edit:', refreshError)
          }
          // The commit becomes the checkpoint the next message can restore to.
          createCommitFromPrompt(response.files_changed[0] ?? '/', promptText)
        }
      } catch (agentError) {
        const errorCode = (agentError as any)?.code
        // The run reported its own ending (a cost ceiling, an empty provider
        // balance, a model error): the server has already recorded it.
        const reported = (agentError as any)?.reported === true
        if (errorCode === STREAM_DROPPED && runStarted && !abortController.signal.aborted) {
          // Only the connection ended. The run is not tied to it and keeps
          // working on the server, so keep showing it as working and pick
          // the result up from there when it finishes.
          followedOnServer = true
          store.followRunOnServer(instanceId)
          return
        }
        // A subagent run that ends without finishing is a failed subagent, and
        // is reported as one — in its card and in the main thread's queue,
        // with a retry — rather than left reading "starting" with no run behind
        // it. The two branches below that are not failures (a busy 409, a
        // refused-slot 429) are kept out of this; a task's turn cap is handled
        // server-side (it continues, or asks) so that is not one either.
        const status = (agentError as any)?.status
        const taskRunDied = isTaskRun
          && status !== 409
          && status !== 429
          && errorCode !== 'max_turns'
          && !reported
        if (taskRunDied) {
          if (!runStarted) {
            // Never reached the run: the optimistic bubble would show a message
            // the transcript does not have.
            store.removeMessage(instanceId, userMessageId)
          }
          const reason = abortController.signal.aborted
            ? 'This thread was stopped before it finished.'
            : runStarted
              ? 'The connection to this thread dropped before it finished.'
              : 'The request to start this thread did not get through' +
                (agentError instanceof Error && agentError.message ? ` (${agentError.message}).` : '.')
          await store.failTaskRun(
            instanceId,
            `${reason} Nothing it started has been added to the app. Try it again to pick the job back up.`,
            runStarted ? null : promptText
          )
        } else if (isTaskRun && reported && errorCode !== 'max_turns') {
          // The thread stopped and said why; the server parked it and queued
          // that note for the main thread. Show it here too.
          store.addMessageToInstance(instanceId, {
            role: 'assistant',
            content: agentError instanceof Error ? agentError.message : 'This thread stopped before it finished.',
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          })
          void store.loadCheckIns()
        } else if (abortController.signal.aborted) {
          // User pressed stop: the partial reply already streamed into the
          // conversation stays; an error bubble would misread the intent.
          console.debug('Agent run stopped by user')
          await finalizeInterruptedEdits('(stopped)')
        } else if ((agentError as any)?.status === 409) {
          // Another run holds this project (see agent_busy contract) — this is
          // a wait-your-turn notice, not a failure. The message never reached
          // the backend, so drop the optimistic bubble: keeping it would show
          // a transcript that silently loses the message on reload.
          store.removeMessage(instanceId, userMessageId)
          store.addMessageToInstance(instanceId, {
            role: 'assistant',
            content: 'Another agent is still working on this project — wait for it to finish or stop it.',
            timestamp: new Date().toISOString(),
            id: `system-busy-${Date.now()}`
          })
        } else if (
          (agentError as any)?.status === 429
          && ((agentError as any)?.body as any)?.error === 'too_many_concurrent_runs'
        ) {
          // Every parallel slot is taken. Nothing is wrong and nothing is lost:
          // the message never reached the backend, so the optimistic bubble goes
          // (it would silently disappear on reload otherwise). A subagent simply
          // waits its turn — its brief goes back in the queue and starts when a
          // slot frees. A thread the user typed in has to be told, because they
          // are sitting there waiting for a reply that is not coming.
          store.removeMessage(instanceId, userMessageId)
          if (isTaskRun) {
            store.requeueDispatch(instanceId, promptText)
          } else {
            store.addMessageToInstance(instanceId, {
              role: 'assistant',
              content: 'Too many agents are running at once — wait for one to finish, then send that again.',
              timestamp: new Date().toISOString(),
              id: `system-busy-${Date.now()}`
            })
          }
        } else if ((agentError as any)?.status === 429) {
          // Usage limit hit (pre-stream rejection, like the 409): the message
          // never reached the backend, so drop the optimistic bubble too.
          store.removeMessage(instanceId, userMessageId)
          const body = (agentError as any)?.body as { resets_at?: string | null } | undefined
          const resetsAt = formatResetTime(body?.resets_at)
          store.addMessageToInstance(instanceId, {
            role: 'assistant',
            content: resetsAt
              ? `Usage allowance spent — frees up ${resetsAt}. A lighter model or lower reasoning effort goes further, or upgrade your plan for more.`
              : 'Usage allowance spent — it frees up as older activity ages out of the window. A lighter model or lower reasoning effort goes further, or upgrade your plan for more.',
            timestamp: new Date().toISOString(),
            id: `system-limit-${Date.now()}`
          })
          // Show the exhausted window in the navbar card / composer dropdown.
          void useUsageStore().fetchUsage()
        } else if ((agentError as any)?.code === 'max_turns') {
          // The run hit its turn cap mid-task. Work so far is saved; a
          // follow-up prompt resumes from the same conversation.
          store.addMessageToInstance(instanceId, {
            role: 'assistant',
            content: 'This task was bigger than one run — send "Continue" to pick up where it left off.',
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          })
          await finalizeInterruptedEdits('(turn limit)')
        } else if (errorCode === 'run_limit' || errorCode === 'out_of_credit') {
          // Deliberate stops with their own plain-language explanation — the
          // spend ceiling, or a provider account with no credit left.
          store.addMessageToInstance(instanceId, {
            role: 'assistant',
            content: agentError instanceof Error ? agentError.message : 'This run stopped early.',
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          })
          await finalizeInterruptedEdits('(stopped early)')
        } else {
          console.error('Error processing agent request:', agentError)
          store.addMessageToInstance(instanceId, {
            role: 'assistant',
            content: `Error: ${agentError instanceof Error ? agentError.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          })
        }
      }

      // Refresh the usage windows after the run; the short delay lets the
      // backend's usage-event write land first.
      setTimeout(() => {
        void useUsageStore().fetchUsage()
      }, 1000)
    } catch (error) {
      console.error('Error processing prompt:', error)
      // Failures outside the agent call (store errors, setup bugs) must still
      // surface in the chat — a console-only error reads as "nothing happened".
      store.addMessageToInstance(instanceId, {
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Something went wrong processing your request.'}`,
        timestamp: new Date().toISOString(),
        id: `system-error-${Date.now()}`
      })
    } finally {
      if (!followedOnServer) {
        store.setInstanceProcessing(instanceId, false)
        // A task's run end applies its work (or parks it) server-side and grows
        // its token total — sync this instance's DTO fields now so its card in the
        // main thread flips to "complete" with its summary, and its check-in
        // reaches the queue, without waiting a poll tick. A subagent finishing is
        // news, and a beat of nothing happening reads as nothing having happened.
        const finished = store.instances.find(i => i.id === instanceId)
        if (finished?.kind === 'task') void store.refreshInstanceFromServer(instanceId)
      }
    }
  }

  return { handlePrompt }
}
