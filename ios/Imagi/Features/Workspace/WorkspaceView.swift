import SwiftUI

/// A project's build workspace on a phone: two full-screen tabs, the
/// coordinator's Chat and the running App, with the threads one tap away.
struct WorkspaceView: View {
    let project: Project

    @State private var model: WorkspaceModel
    @State private var tab: Tab = .chat
    @State private var showingThreads = false
    @State private var threadPath: [Int] = []

    enum Tab { case chat, app }

    init(project: Project) {
        self.project = project
        _model = State(initialValue: WorkspaceModel(project: project))
    }

    var body: some View {
        ZStack {
            Color.slBg.ignoresSafeArea()
            CoordinatorChatView(model: model, onOpenThread: openThread)
                .opacity(tab == .chat ? 1 : 0)
                .allowsHitTesting(tab == .chat)
                .accessibilityHidden(tab != .chat)
            // Kept alive behind the chat so the app doesn't reload on every switch.
            AppPreviewView(model: model)
                .opacity(tab == .app ? 1 : 0)
                .allowsHitTesting(tab == .app)
                .accessibilityHidden(tab != .app)
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbarBackground(Color.slBg, for: .navigationBar)
        .toolbar {
            ToolbarItem(placement: .principal) {
                TabSwitch(tab: $tab, appHasNews: model.appHasNews)
            }
            ToolbarItem(placement: .topBarTrailing) {
                ThreadsButton(waiting: model.waitingCount, working: model.workingCount) {
                    threadPath = []
                    showingThreads = true
                }
            }
        }
        .sheet(isPresented: $showingThreads) {
            ThreadsSheet(model: model, path: $threadPath)
        }
        .task { await model.open() }
        .onDisappear { model.close() }
        .onChange(of: tab) {
            model.previewVisible = tab == .app
            if tab == .app { model.appHasNews = false }
        }
    }

    private func openThread(_ id: Int) {
        threadPath = [id]
        showingThreads = true
    }
}

/// Chat | App, a segmented pill in the bar. A dot on App says work landed.
struct TabSwitch: View {
    @Binding var tab: WorkspaceView.Tab
    var appHasNews: Bool
    @Namespace private var pill

    var body: some View {
        HStack(spacing: 2) {
            segment("Chat", .chat)
            segment("App", .app)
                .overlay(alignment: .topTrailing) {
                    if appHasNews && tab != .app {
                        Circle().fill(.slLight).frame(width: 7, height: 7).offset(x: -6, y: 5)
                    }
                }
        }
        .padding(3)
        .background(Capsule().fill(Color.slChip))
        .overlay(Capsule().strokeBorder(Color.slLine, lineWidth: 1))
    }

    private func segment(_ title: String, _ value: WorkspaceView.Tab) -> some View {
        Button {
            withAnimation(.imagi) { tab = value }
        } label: {
            Text(title)
                .font(.app(14, tab == value ? .semibold : .medium))
                .foregroundStyle(tab == value ? Color.slText : Color.slMuted)
                .frame(width: 66, height: 30)
                .background {
                    if tab == value {
                        Capsule().fill(Color.slSurface2)
                            .shadow(color: .black.opacity(0.08), radius: 2, y: 1)
                            .matchedGeometryEffect(id: "pill", in: pill)
                    }
                }
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(tab == value ? .isSelected : [])
    }
}

struct ThreadsButton: View {
    let waiting: Int
    let working: Int
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 5) {
                Image(systemName: "square.stack")
                    .font(.system(size: 16, weight: .regular))
                    .foregroundStyle(Color.slText)
                if waiting > 0 {
                    Text("\(waiting)")
                        .font(.app(12, .bold))
                        .foregroundStyle(Color.slOnAccent)
                        .padding(.horizontal, 6)
                        .frame(minWidth: 18, minHeight: 18)
                        .background(Capsule().fill(Color.slWait))
                } else if working > 0 {
                    Text("\(working)")
                        .font(.app(12, .semibold))
                        .foregroundStyle(Color.slWork)
                }
            }
        }
        .accessibilityLabel(waiting > 0 ? "Threads, \(waiting) waiting on you" : "Threads")
    }
}

/// The coordinator's chat, with the questions queue above its composer.
struct CoordinatorChatView: View {
    let model: WorkspaceModel
    var onOpenThread: (Int) -> Void
    @State private var draft = ""

    private var coordinatorId: Int? { model.coordinator?.id }

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    if let problem = model.problem {
                        ProblemNote(text: problem)
                            .padding(.bottom, 16)
                            .onTapGesture { model.problem = nil }
                    }
                    if let id = coordinatorId {
                        if (model.transcripts[id] ?? []).isEmpty && model.live[id] == nil && !model.loading {
                            intro
                        }
                        TranscriptView(model: model, conversationId: id, onOpenThread: onOpenThread) { answer in
                            model.sendToCoordinator(answer)
                        }
                    } else if model.loading {
                        ProgressView().frame(maxWidth: .infinity).padding(.top, 60)
                    }
                    Color.clear.frame(height: 1).id("bottom")
                }
                .padding(.horizontal, 16)
                .padding(.top, 14)
            }
            .defaultScrollAnchor(.bottom)
            .scrollDismissesKeyboard(.interactively)
            .onChange(of: scrollKey) {
                withAnimation(.imagi) { proxy.scrollTo("bottom", anchor: .bottom) }
            }
        }
        .safeAreaInset(edge: .bottom) {
            VStack(spacing: 10) {
                if let question = model.questions.first {
                    QuestionCard(
                        checkIn: question,
                        count: model.questions.count,
                        onAnswer: { answer in Task { await model.sendToThread(question.task.id, answer) } },
                        onLater: { model.later(question) },
                        onOpenThread: { onOpenThread(question.task.id) }
                    )
                    .transition(.move(edge: .bottom).combined(with: .opacity))
                }
                Composer(
                    text: $draft,
                    placeholder: "Ask for a change",
                    busy: coordinatorId.map { model.isBusy($0) } ?? false,
                    canSend: model.coordinator != nil,
                    onSend: { model.sendToCoordinator($0) },
                    onStop: { if let id = coordinatorId { model.stop(id) } }
                )
            }
            .padding(.horizontal, 12)
            .padding(.top, 8)
            .padding(.bottom, 6)
            .background(Color.slBg.opacity(0.96).ignoresSafeArea())
            .animation(.imagi, value: model.questions.first?.id)
        }
        .onChange(of: model.returnedDraft) {
            if let returned = model.returnedDraft, returned.conversationId == coordinatorId {
                if draft.isEmpty { draft = returned.text }
                model.returnedDraft = nil
            }
        }
    }

    private var scrollKey: String {
        guard let id = coordinatorId else { return "" }
        let live = model.live[id]
        return "\(model.transcripts[id]?.count ?? 0)-\(live?.text.count ?? -1)-\(live?.steps.count ?? 0)-\(live?.dispatched.count ?? 0)"
    }

    private var intro: some View {
        VStack(alignment: .leading, spacing: 10) {
            Eyebrow("Coordinator")
            Text("Tell Imagi what to change")
                .font(.display(26, bold: true))
                .foregroundStyle(Color.slText)
            Text("Describe a change in your own words. The coordinator answers simple questions itself and hands real work to threads, which you'll see here as they start and finish.")
                .font(.app(15))
                .lineSpacing(3)
                .foregroundStyle(Color.slMuted)
        }
        .padding(.top, 20)
        .padding(.bottom, 28)
    }
}
