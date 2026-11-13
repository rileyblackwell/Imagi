import SwiftUI

/// A conversation's messages and its run in progress: the coordinator's chat
/// or a thread's.
struct TranscriptView: View {
    let model: WorkspaceModel
    let conversationId: Int
    var isThread = false
    var onOpenThread: (Int) -> Void
    var onAnswer: (String) -> Void

    private var messages: [ChatMessage] { model.transcripts[conversationId] ?? [] }

    var body: some View {
        LazyVStack(alignment: .leading, spacing: 0) {
            ForEach(Array(messages.enumerated()), id: \.element.id) { index, message in
                row(message, index: index)
            }
            if let run = model.live[conversationId] {
                LiveRunView(run: run) { task in AnyView(card(for: task.conversationId, fallbackTitle: task.goal.isEmpty ? task.title : task.goal)) }
            }
        }
    }

    @ViewBuilder
    private func row(_ message: ChatMessage, index: Int) -> some View {
        if message.metadata?.appError == true {
            AppErrorNotice(text: message.content)
        } else if message.isUser {
            if isThread && index == 0 {
                BriefCard(text: message.content)
            } else {
                UserBubble(text: message.content)
            }
        } else if message.role == "assistant" {
            RailRow(node: .slOk) {
                StepsSummary(steps: message.steps)
                if !message.content.isEmpty {
                    AgentText(text: message.content)
                }
                ForEach(message.metadata?.dispatchedTasks ?? [], id: \.self) { ref in
                    if let id = ref.conversationId {
                        card(for: id, fallbackTitle: ref.title ?? "Thread")
                    }
                }
                if index == messages.count - 1, model.live[conversationId] == nil,
                   let options = message.metadata?.question?.options, !options.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(options, id: \.self) { option in
                            Button(option) { onAnswer(option) }
                                .buttonStyle(QuietButtonStyle(tint: .slText))
                        }
                    }
                }
            }
        }
    }

    private func card(for id: Int, fallbackTitle: String) -> some View {
        let thread = model.threads.first { $0.id == id }
        let state = thread.map { model.state(of: $0) } ?? .working
        let summary: String = {
            guard let thread else { return "" }
            if state == .finished, let done = thread.lastAssistantSummary, !done.isEmpty { return done }
            return thread.overview ?? ""
        }()
        return ThreadCard(
            title: thread?.displayTitle ?? fallbackTitle,
            state: state,
            summary: summary,
            onOpen: { onOpenThread(id) }
        )
    }
}

/// A thread's opening message: the job the coordinator handed it.
struct BriefCard: View {
    let text: String
    @State private var open = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Eyebrow("From the coordinator")
            Text(text)
                .font(.app(14.5))
                .foregroundStyle(Color.slText)
                .lineLimit(open ? nil : 5)
            Button(open ? "Show less" : "Show all") { withAnimation(.imagi) { open.toggle() } }
                .font(.app(13, .medium))
                .foregroundStyle(Color.slMuted)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .imagiCard(padding: 14)
        .padding(.bottom, 18)
    }
}
