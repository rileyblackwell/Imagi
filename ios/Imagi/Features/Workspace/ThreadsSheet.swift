import SwiftUI

/// Every thread in the project, grouped by where it stands, and each thread's chat.
struct ThreadsSheet: View {
    let model: WorkspaceModel
    @Binding var path: [Int]
    @Environment(\.dismiss) private var dismiss

    private let order: [ThreadState] = [.waiting, .working, .scheduled, .stopped, .finished]

    var body: some View {
        NavigationStack(path: $path) {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    if model.threads.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("No threads yet")
                                .font(.display(22, bold: true))
                                .foregroundStyle(Color.slText)
                            Text("When the coordinator hands work to a thread, it shows up here. Threads work in parallel, each on its own part of your app.")
                                .font(.app(15))
                                .foregroundStyle(Color.slMuted)
                        }
                        .padding(.top, 8)
                    }
                    ForEach(order, id: \.self) { state in
                        let group = model.threads.filter { model.state(of: $0) == state }
                        if !group.isEmpty {
                            VStack(alignment: .leading, spacing: 10) {
                                Eyebrow("\(state.label) · \(group.count)", color: state == .waiting ? .slWait : .slMuted)
                                ForEach(group) { thread in
                                    NavigationLink(value: thread.id) {
                                        ThreadRow(thread: thread, state: state)
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                    }
                }
                .padding(16)
            }
            .background(Color.slBg)
            .navigationTitle("Threads")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }.foregroundStyle(Color.slText)
                }
            }
            .navigationDestination(for: Int.self) { id in
                ThreadDetailView(model: model, threadId: id)
            }
        }
        .presentationDragIndicator(.visible)
    }
}

struct ThreadRow: View {
    let thread: Conversation
    let state: ThreadState

    private var subtitle: String {
        let options = state == .finished
            ? [thread.lastAssistantSummary, thread.overview, thread.lastMessagePreview]
            : [thread.overview, thread.lastMessagePreview]
        return options.compactMap { $0 }.first { !$0.isEmpty } ?? ""
    }

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            StatusDot(state: state).padding(.top, 2)
            VStack(alignment: .leading, spacing: 4) {
                Text(thread.displayTitle)
                    .font(.app(16, .semibold))
                    .foregroundStyle(Color.slText)
                    .lineLimit(2)
                    .multilineTextAlignment(.leading)
                if !subtitle.isEmpty {
                    Text(subtitle)
                        .font(.app(13.5))
                        .foregroundStyle(Color.slMuted)
                        .lineLimit(2)
                        .multilineTextAlignment(.leading)
                }
                if let updated = thread.updatedAt, updated > .distantPast {
                    Text(updated.imagiRelative)
                        .font(.app(12))
                        .foregroundStyle(Color.slFaint)
                }
            }
            Spacer(minLength: 0)
            Image(systemName: "chevron.right")
                .font(.system(size: 12, weight: .semibold))
                .foregroundStyle(Color.slFaint)
                .padding(.top, 4)
        }
        .imagiCard(edge: state == .waiting ? .slWait : .slLine, padding: 14)
        .contentShape(Rectangle())
    }
}

/// One thread's chat: the job it was given, what it did, and a box to steer it.
struct ThreadDetailView: View {
    let model: WorkspaceModel
    let threadId: Int
    @State private var draft = ""
    @State private var confirmingDiscard = false
    @Environment(\.dismiss) private var dismiss

    private var thread: Conversation? { model.conversation(threadId) }
    private var state: ThreadState { thread.map { model.state(of: $0) } ?? .working }

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    header.padding(.bottom, 18)
                    if let problem = model.problem {
                        ProblemNote(text: problem)
                            .padding(.bottom, 16)
                            .onTapGesture { model.problem = nil }
                    }
                    if model.transcripts[threadId] == nil {
                        ProgressView().frame(maxWidth: .infinity).padding(.top, 30)
                    }
                    TranscriptView(
                        model: model,
                        conversationId: threadId,
                        isThread: true,
                        onOpenThread: { _ in },
                        onAnswer: { answer in Task { await model.sendToThread(threadId, answer) } }
                    )
                    if state == .stopped {
                        stoppedActions
                    }
                    Color.clear.frame(height: 1).id("bottom")
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
            }
            .defaultScrollAnchor(.bottom)
            .scrollDismissesKeyboard(.interactively)
            .onChange(of: scrollKey) {
                withAnimation(.imagi) { proxy.scrollTo("bottom", anchor: .bottom) }
            }
        }
        .background(Color.slBg)
        .safeAreaInset(edge: .bottom) {
            Composer(
                text: $draft,
                placeholder: "Steer this thread…",
                busy: model.isBusy(threadId),
                onSend: { text in Task { await model.sendToThread(threadId, text) } },
                onStop: { model.stop(threadId) }
            )
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Color.slBg.opacity(0.96).ignoresSafeArea())
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .principal) {
                HStack(spacing: 6) {
                    StatusDot(state: state)
                    Text(state.label)
                        .font(.app(14, .semibold))
                        .foregroundStyle(state.color)
                }
            }
        }
        .task { await model.openThread(threadId) }
        .onDisappear { model.closeThread(threadId) }
        .onChange(of: model.returnedDraft) {
            if let returned = model.returnedDraft, returned.conversationId == threadId {
                if draft.isEmpty { draft = returned.text }
                model.returnedDraft = nil
            }
        }
        .confirmationDialog("Discard this thread?", isPresented: $confirmingDiscard, titleVisibility: .visible) {
            Button("Discard", role: .destructive) {
                Task {
                    await model.discard(threadId)
                    dismiss()
                }
            }
        } message: {
            Text("Its changes are taken back out of your app.")
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Eyebrow("Thread")
            Text(thread?.displayTitle ?? "Thread")
                .font(.display(24, bold: true, relativeTo: .title))
                .tracking(-0.4)
                .foregroundStyle(Color.slText)
                .fixedSize(horizontal: false, vertical: true)
            if let overview = thread?.overview, !overview.isEmpty, state != .finished {
                Text(overview)
                    .font(.app(14.5))
                    .foregroundStyle(Color.slMuted)
            }
        }
    }

    private var stoppedActions: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("This thread stopped before it finished.")
                .font(.app(14))
                .foregroundStyle(Color.slMuted)
            HStack(spacing: 10) {
                Button("Try again") { Task { await model.retry(threadId) } }
                    .buttonStyle(LitButtonStyle(fullWidth: false))
                Button("Discard") { confirmingDiscard = true }
                    .buttonStyle(QuietButtonStyle())
            }
        }
        .padding(.bottom, 18)
    }

    private var scrollKey: String {
        let live = model.live[threadId]
        return "\(model.transcripts[threadId]?.count ?? 0)-\(live?.text.count ?? -1)-\(live?.steps.count ?? 0)"
    }
}
