import Foundation
import Observation

/// What a run in progress has said so far.
struct ReturnedDraft: Equatable {
    let conversationId: Int
    let text: String
}

struct LiveRun: Equatable {
    var text = ""
    var steps: [String] = []
    var dispatched: [DispatchedTask] = []
    var lastSeq: Int?
}

/// One project's build workspace: its coordinator, its threads, the questions
/// waiting on the person, and the live preview of the app.
///
/// Runs happen on the server and keep going when the phone locks or the app
/// closes; this only watches them. A light poll keeps the list of threads and
/// questions current, and the open conversation streams its run live.
@Observable
@MainActor
final class WorkspaceModel {
    let project: Project

    private(set) var coordinator: Conversation?
    private(set) var threads: [Conversation] = []
    private(set) var checkIns: [CheckIn] = []
    /// Transcripts by conversation id (the coordinator's and open threads').
    private(set) var transcripts: [Int: [ChatMessage]] = [:]
    /// Runs being watched, by conversation id.
    private(set) var live: [Int: LiveRun] = [:]
    private(set) var loading = true
    var problem: String?
    /// A message the server refused, handed back to its conversation's composer.
    var returnedDraft: ReturnedDraft?
    /// Work landed since the person last looked at the app.
    var appHasNews = false

    // The live preview
    private(set) var previewURL: URL?
    private(set) var previewError: String?
    private(set) var previewStages: [PreviewStage] = []
    private(set) var previewStarting = false
    var previewVisible = false

    private let api = APIClient.shared
    private var watches: [Int: Task<Void, Never>] = [:]
    private var pollTask: Task<Void, Never>?
    private var previewTask: Task<Void, Never>?
    private var nextLocalId = -1

    init(project: Project) {
        self.project = project
    }

    // MARK: Lifecycle

    func open() async {
        loading = true
        do {
            apply(try await api.conversations(projectId: project.id))
            if coordinator == nil {
                coordinator = try await api.coordinator(projectId: project.id)
            }
            if let coordinator {
                transcripts[coordinator.id] = try await api.messages(conversationId: coordinator.id)
            }
            checkIns = (try? await api.checkIns(projectId: project.id)) ?? []
            problem = nil
        } catch is CancellationError {
            return
        } catch {
            problem = error.localizedDescription
        }
        loading = false
        if let coordinator, coordinator.running || coordinator.hasQueuedWork {
            follow(coordinator.id)
        }
        startPolling()
        if previewTask == nil { startPreview() }
    }

    func close() {
        pollTask?.cancel()
        pollTask = nil
        previewTask?.cancel()
        previewTask = nil
        for task in watches.values { task.cancel() }
        watches = [:]
        live = [:]
    }

    private func apply(_ all: [Conversation]) {
        if let lead = all.first(where: { $0.isCoordinator && $0.archivedAt == nil }) {
            coordinator = lead
        }
        threads = all
            .filter { $0.isThread && $0.archivedAt == nil && $0.reviewStatus != "dismissed" }
            .sorted { ($0.createdAt ?? .distantPast) > ($1.createdAt ?? .distantPast) }
    }

    private func startPolling() {
        pollTask?.cancel()
        pollTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(4))
                guard let self, !Task.isCancelled else { return }
                await self.refresh()
            }
        }
    }

    /// Catch up on threads and questions, and pick up runs nobody is watching yet.
    func refresh() async {
        guard let all = try? await api.conversations(projectId: project.id) else { return }
        let before = Dictionary(threads.map { ($0.id, $0) }, uniquingKeysWith: { a, _ in a })
        let coordinatorBefore = coordinator
        apply(all)

        for thread in threads {
            if let old = before[thread.id], old.running, !thread.running {
                appHasNews = true
                // An open thread that finished while unwatched gets its words.
                if transcripts[thread.id] != nil, watches[thread.id] == nil {
                    await reloadTranscript(thread.id)
                }
            }
            // An open thread that started (a follow-up from the coordinator).
            if transcripts[thread.id] != nil, watches[thread.id] == nil, thread.running || thread.hasQueuedWork {
                follow(thread.id)
            }
        }

        if let coordinator {
            if coordinator.running, watches[coordinator.id] == nil {
                follow(coordinator.id)
            } else if watches[coordinator.id] == nil, coordinator.updatedAt != coordinatorBefore?.updatedAt {
                await reloadTranscript(coordinator.id)
            }
        }

        if let fresh = try? await api.checkIns(projectId: project.id) {
            checkIns = fresh
        }
    }

    // MARK: Watching runs

    func isBusy(_ id: Int) -> Bool {
        live[id] != nil || conversation(id)?.running == true
    }

    func conversation(_ id: Int) -> Conversation? {
        if coordinator?.id == id { return coordinator }
        return threads.first { $0.id == id }
    }

    private func follow(_ id: Int, after: Int? = nil) {
        guard watches[id] == nil else { return }
        let stream = api.watch(conversationId: id, after: after)
        watches[id] = Task { [weak self] in
            await self?.consume(id: id, stream: stream, isNewMessage: false)
        }
    }

    /// Relay one run's events into `live`, then settle on the saved transcript.
    private func consume(id: Int, stream: AsyncThrowingStream<AgentEvent, Error>, isNewMessage: Bool, draft: String? = nil) async {
        if live[id] == nil { live[id] = LiveRun() }
        var ended = false
        var dropped = false
        do {
            for try await event in stream {
                var run = live[id] ?? LiveRun()
                if let seq = event.seq { run.lastSeq = seq }
                switch event.kind {
                case .delta(let text):
                    run.text += text
                case .toolCall(let name, let args):
                    run.steps.append(ToolLabels.label(for: name, args: args))
                case .taskDispatch(let tasks):
                    let known = Set(run.dispatched.map(\.conversationId))
                    let fresh = tasks.filter { !known.contains($0.conversationId) }
                    run.dispatched.append(contentsOf: fresh)
                    Task { await self.refresh() }
                case .done(let filesChanged):
                    ended = true
                    if filesChanged > 0 { appHasNews = true }
                case .error(let message, let code):
                    ended = true
                    if code != "not_found", code != "cancelled" { problem = message }
                default:
                    break
                }
                live[id] = run
            }
            if !ended { dropped = true }
        } catch is CancellationError {
            watches[id] = nil
            live[id] = nil
            return
        } catch let error as APIError {
            if error.status == 0 {
                dropped = true
            } else {
                problem = error.message
                if isNewMessage, let draft { returnedDraft = ReturnedDraft(conversationId: id, text: draft) }
            }
        } catch {
            dropped = true
        }

        // Stopped watching on purpose (the thread was closed): leave things be.
        if Task.isCancelled { return }

        let lastSeq = live[id]?.lastSeq
        await reloadTranscript(id)
        live[id] = nil
        watches[id] = nil

        if dropped, !Task.isCancelled {
            // The connection went away, not the run: look again shortly.
            try? await Task.sleep(for: .seconds(1.5))
            guard !Task.isCancelled else { return }
            if let fresh = try? await api.conversation(id), fresh.running || fresh.hasQueuedWork {
                follow(id, after: lastSeq)
            }
        }
    }

    private func reloadTranscript(_ id: Int) async {
        if let messages = try? await api.messages(conversationId: id) {
            transcripts[id] = messages
        }
    }

    private func appendLocal(_ text: String, to id: Int) {
        var list = transcripts[id] ?? []
        list.append(ChatMessage(id: nextLocalId, role: "user", content: text))
        nextLocalId -= 1
        transcripts[id] = list
    }

    // MARK: The coordinator

    func sendToCoordinator(_ text: String) {
        let message = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !message.isEmpty, let coordinator, watches[coordinator.id] == nil else { return }
        problem = nil
        appendLocal(message, to: coordinator.id)
        let stream = api.runCoordinator(conversation: coordinator, projectId: project.id, message: message)
        watches[coordinator.id] = Task { [weak self] in
            await self?.consume(id: coordinator.id, stream: stream, isNewMessage: true, draft: message)
        }
    }

    /// Stop a run. It is not tied to the connection, so the server is told.
    func stop(_ id: Int) {
        Task {
            await api.cancelRun(id)
            await refresh()
        }
    }

    // MARK: Threads

    func state(of thread: Conversation) -> ThreadState {
        if thread.reviewStatus == "failed" { return .stopped }
        if thread.reviewStatus == "input" || thread.reviewStatus == "ready"
            || checkIns.contains(where: { $0.task.id == thread.id && $0.isQuestion }) {
            return .waiting
        }
        if thread.running || live[thread.id] != nil { return .working }
        switch thread.schedule?.status {
        case "blocked": return .waiting
        case "waiting": return .scheduled
        default: break
        }
        if thread.hasQueuedWork { return .working }
        return .finished
    }

    var waitingCount: Int { threads.filter { state(of: $0) == .waiting }.count }
    var workingCount: Int { threads.filter { state(of: $0) == .working }.count }

    /// Questions only the person can answer, oldest first.
    var questions: [CheckIn] { checkIns.filter { $0.isQuestion && $0.status != "resolved" } }

    func openThread(_ id: Int) async {
        await reloadTranscript(id)
        if transcripts[id] == nil { transcripts[id] = [] }
        if let thread = conversation(id), thread.running || thread.hasQueuedWork {
            follow(id)
        }
    }

    func closeThread(_ id: Int) {
        watches[id]?.cancel()
        watches[id] = nil
        live[id] = nil
        transcripts[id] = nil
    }

    /// The person steering a thread, or answering its question: its next message.
    func sendToThread(_ id: Int, _ text: String) async {
        let message = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !message.isEmpty else { return }
        problem = nil
        if transcripts[id] != nil { appendLocal(message, to: id) }
        checkIns.removeAll { $0.task.id == id && $0.isQuestion }
        do {
            try await api.sendToThread(id, message: message)
        } catch {
            problem = error.localizedDescription
            returnedDraft = ReturnedDraft(conversationId: id, text: message)
            if transcripts[id] != nil { await reloadTranscript(id) }
            return
        }
        await refresh()
        if transcripts[id] != nil { follow(id) }
    }

    func retry(_ id: Int) async {
        do {
            try await api.sendToThread(id, message: "")
        } catch let error as APIError where error.code == "nothing_to_send" {
            await sendToThread(id, "Please try that again.")
            return
        } catch {
            problem = error.localizedDescription
            return
        }
        await refresh()
        if transcripts[id] != nil { follow(id) }
    }

    func discard(_ id: Int) async {
        do {
            try await api.dismissThread(id)
        } catch {
            problem = error.localizedDescription
        }
        await refresh()
    }

    func later(_ checkIn: CheckIn) {
        guard let index = checkIns.firstIndex(of: checkIn) else { return }
        checkIns.append(checkIns.remove(at: index))
    }

    func clear(_ checkIn: CheckIn) {
        checkIns.removeAll { $0.id == checkIn.id }
        Task { await api.resolveCheckIn(checkIn.id) }
    }

    // MARK: Preview

    func startPreview() {
        previewTask?.cancel()
        previewStarting = true
        previewError = nil
        previewTask = Task { [weak self] in
            guard let self else { return }
            let projectId = self.project.id
            // Stage progress for the notice while a cold start runs.
            let progress = Task { [weak self] in
                while !Task.isCancelled {
                    if let status = try? await APIClient.shared.previewStatus(projectId: projectId, visible: true) {
                        self?.previewStages = status.progress?.stages ?? []
                    }
                    try? await Task.sleep(for: .seconds(1.5))
                }
            }
            do {
                let result = try await self.api.startPreview(projectId: projectId)
                if result.running != false, let raw = result.url, let url = URL(string: raw) {
                    self.previewURL = url
                } else {
                    self.previewError = result.error ?? "Your app's preview isn't available right now."
                }
            } catch is CancellationError {
                progress.cancel()
                return
            } catch {
                self.previewError = error.localizedDescription
            }
            progress.cancel()
            self.previewStarting = false

            // The heartbeat that keeps the preview warm while the workspace is open.
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(self.previewVisible ? 10 : 30))
                guard !Task.isCancelled else { return }
                _ = try? await self.api.previewStatus(projectId: projectId, visible: self.previewVisible)
            }
        }
    }

    /// The first build is still writing the home page.
    var buildingFirstVersion: Bool {
        guard let coordinator else { return false }
        return isBusy(coordinator.id) && (transcripts[coordinator.id]?.filter { !$0.isUser }.isEmpty ?? true)
    }
}
