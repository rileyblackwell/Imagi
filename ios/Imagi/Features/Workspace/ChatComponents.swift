import MarkdownUI
import SwiftUI

// The pieces of a coordinator or thread chat. The agent's side hangs on a rail
// with a node per reply; the person's messages are bubbles on the right.

/// The agent's words, rendered as Markdown in the app's text face.
struct AgentText: View {
    let text: String

    var body: some View {
        Markdown(text)
            .markdownTheme(.basic)
            .markdownTextStyle(\.text) {
                FontFamily(.custom("Instrument Sans"))
                FontSize(15.5)
                ForegroundColor(.slText)
            }
            .markdownTextStyle(\.code) {
                FontFamilyVariant(.monospaced)
                FontSize(.em(0.88))
                BackgroundColor(.slChipHover)
            }
            .markdownTextStyle(\.link) {
                ForegroundColor(.slCoral)
            }
            .textSelection(.enabled)
    }
}

/// One step of the agent's side, hung on the rail.
struct RailRow<Content: View>: View {
    var node: Color = .slOk
    var working = false
    var showsLine = true
    @ViewBuilder var content: Content

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            VStack(spacing: 4) {
                Group {
                    if working {
                        WorkingIndicator(size: 7)
                    } else {
                        Circle()
                            .fill(node)
                            .frame(width: 8, height: 8)
                            .frame(width: 17, height: 17)
                    }
                }
                if showsLine {
                    Rectangle().fill(Color.slLine).frame(width: 1.5)
                }
            }
            .frame(width: 17)
            VStack(alignment: .leading, spacing: 10) {
                content
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.bottom, 18)
        }
    }
}

struct UserBubble: View {
    let text: String

    var body: some View {
        HStack {
            Spacer(minLength: 48)
            Text(text)
                .font(.app(15.5))
                .foregroundStyle(Color.slText)
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background(RoundedRectangle(cornerRadius: 18, style: .continuous).fill(Color.slChipHover))
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).strokeBorder(Color.slLine, lineWidth: 1))
                .textSelection(.enabled)
        }
        .padding(.bottom, 18)
    }
}

/// The plain-language steps a reply took, folded to one line.
struct StepsSummary: View {
    let steps: [String]
    @State private var open = false

    var body: some View {
        if !steps.isEmpty {
            VStack(alignment: .leading, spacing: 6) {
                Button {
                    withAnimation(.imagi) { open.toggle() }
                } label: {
                    HStack(spacing: 6) {
                        Text(steps.count == 1 ? steps[0] : "\(steps.last ?? "") and \(steps.count - 1) more step\(steps.count == 2 ? "" : "s")")
                            .lineLimit(1)
                        if steps.count > 1 {
                            Image(systemName: "chevron.down")
                                .font(.system(size: 10, weight: .semibold))
                                .rotationEffect(.degrees(open ? 180 : 0))
                        }
                    }
                    .font(.app(13))
                    .foregroundStyle(Color.slMuted)
                }
                .buttonStyle(.plain)
                .disabled(steps.count < 2)
                if open {
                    VStack(alignment: .leading, spacing: 4) {
                        ForEach(Array(steps.enumerated()), id: \.offset) { _, step in
                            HStack(alignment: .firstTextBaseline, spacing: 8) {
                                Rectangle().fill(Color.slFaint).frame(width: 4, height: 4).rotationEffect(.degrees(45))
                                Text(step)
                            }
                        }
                    }
                    .font(.app(13))
                    .foregroundStyle(Color.slMuted)
                    .padding(.leading, 2)
                }
            }
        }
    }
}

/// A thread the coordinator started, as a card in its chat.
struct ThreadCard: View {
    let title: String
    let state: ThreadState
    let summary: String
    var onOpen: () -> Void

    var body: some View {
        Button(action: onOpen) {
            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 7) {
                    StatusDot(state: state)
                    Text(state.label.uppercased())
                        .font(.app(11, .semibold))
                        .tracking(1.6)
                        .foregroundStyle(state.color)
                }
                Text(title)
                    .font(.display(18, bold: true, relativeTo: .headline))
                    .tracking(-0.2)
                    .foregroundStyle(Color.slText)
                    .multilineTextAlignment(.leading)
                    .fixedSize(horizontal: false, vertical: true)
                if !summary.isEmpty {
                    Text(summary)
                        .font(.app(14))
                        .foregroundStyle(Color.slMuted)
                        .lineLimit(3)
                        .multilineTextAlignment(.leading)
                }
                if state == .waiting {
                    Text("It has a question for you.")
                        .font(.app(13, .medium))
                        .foregroundStyle(Color.slWait)
                }
                HStack(spacing: 6) {
                    Text("Go to thread")
                    Image(systemName: "arrow.right")
                        .foregroundStyle(.slLight)
                }
                .font(.app(14, .semibold))
                .foregroundStyle(Color.slText)
                .padding(.top, 2)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .imagiCard(edge: state == .waiting ? .slWait : .slLine, padding: 14)
        }
        .buttonStyle(.plain)
    }
}

/// A run in progress: what it's doing now and what it has said so far.
struct LiveRunView: View {
    let run: LiveRun
    var cards: (DispatchedTask) -> AnyView

    var body: some View {
        RailRow(working: true, showsLine: false) {
            Text(run.steps.last ?? (run.text.isEmpty ? "Thinking" : "Writing"))
                .font(.app(13, .medium))
                .foregroundStyle(Color.slWork)
                .padding(.top, 1)
            if !run.text.isEmpty {
                AgentText(text: run.text)
            }
            ForEach(run.dispatched, id: \.conversationId) { task in
                cards(task)
            }
        }
    }
}

/// The message box: grows with the text; the button sends, or stops a run.
struct Composer: View {
    @Binding var text: String
    let placeholder: String
    var busy: Bool
    var canSend = true
    var onSend: (String) -> Void
    var onStop: (() -> Void)?
    @FocusState private var focused: Bool

    var body: some View {
        HStack(alignment: .bottom, spacing: 10) {
            TextField("", text: $text, prompt: Text(placeholder).foregroundStyle(Color.slPlaceholder), axis: .vertical)
                .lineLimit(1...6)
                .font(.app(16))
                .foregroundStyle(Color.slText)
                .tint(.slCoral)
                .focused($focused)
                .padding(.vertical, 11)
                .padding(.leading, 16)
            if busy, let onStop {
                Button(action: onStop) {
                    Image(systemName: "stop.fill")
                        .font(.system(size: 13, weight: .bold))
                        .foregroundStyle(Color.slText)
                        .frame(width: 36, height: 36)
                        .background(Circle().fill(Color.slChipHover))
                        .overlay(Circle().strokeBorder(Color.slLineStrong, lineWidth: 1))
                }
                .accessibilityLabel("Stop")
                .padding(5)
            } else {
                Button {
                    let message = text.trimmingCharacters(in: .whitespacesAndNewlines)
                    guard !message.isEmpty else { return }
                    text = ""
                    onSend(message)
                } label: {
                    Image(systemName: "arrow.up")
                        .font(.system(size: 15, weight: .bold))
                        .foregroundStyle(Color.slOnAccent)
                        .frame(width: 36, height: 36)
                        .background(Circle().fill(.slLight))
                }
                .accessibilityLabel("Send")
                .disabled(!canSend || text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                .opacity(text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? 0.45 : 1)
                .padding(5)
            }
        }
        .background(RoundedRectangle(cornerRadius: 23, style: .continuous).fill(Color.slSurface2))
        .overlay(
            RoundedRectangle(cornerRadius: 23, style: .continuous)
                .strokeBorder(focused ? AnyShapeStyle(LinearGradient.slLight) : AnyShapeStyle(Color.slLineStrong), lineWidth: 1)
        )
        .shadow(color: focused ? .slGlow : .clear, radius: 12, y: 4)
    }
}

/// A thread's question, in the queue above the coordinator's composer.
struct QuestionCard: View {
    let checkIn: CheckIn
    let count: Int
    var onAnswer: (String) -> Void
    var onLater: () -> Void
    var onOpenThread: () -> Void
    @State private var answer = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(count > 1 ? "WAITING ON YOU · \(count)" : "WAITING ON YOU")
                    .font(.app(11, .semibold))
                    .tracking(1.6)
                    .foregroundStyle(Color.slWait)
                Spacer()
                if count > 1 {
                    Button("Later", action: onLater)
                        .font(.app(13, .medium))
                        .foregroundStyle(Color.slMuted)
                }
            }
            Text(checkIn.task.goal?.isEmpty == false ? checkIn.task.goal! : (checkIn.task.title ?? "A thread"))
                .font(.app(13, .medium))
                .foregroundStyle(Color.slMuted)
                .lineLimit(1)
            ScrollView {
                Text(checkIn.body)
                    .font(.app(15))
                    .foregroundStyle(Color.slText)
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(maxHeight: 120)
            .fixedSize(horizontal: false, vertical: true)
            if let options = checkIn.options, !options.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(options, id: \.self) { option in
                            Button(option) { onAnswer(option) }
                                .buttonStyle(QuietButtonStyle(tint: .slText))
                        }
                    }
                }
            }
            HStack(spacing: 8) {
                TextField("", text: $answer, prompt: Text("Answer in your own words").foregroundStyle(Color.slPlaceholder))
                    .font(.app(15))
                    .submitLabel(.send)
                    .onSubmit(send)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 9)
                    .background(Capsule().fill(Color.slSurface2))
                    .overlay(Capsule().strokeBorder(Color.slLineStrong, lineWidth: 1))
                Button("Go to thread", action: onOpenThread)
                    .font(.app(13.5, .semibold))
                    .foregroundStyle(Color.slText)
            }
        }
        .imagiCard(edge: .slWait, padding: 14)
    }

    private func send() {
        let text = answer.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        answer = ""
        onAnswer(text)
    }
}

/// A notice on the rail: the app's own errors, which the server sent to the coordinator.
struct AppErrorNotice: View {
    let text: String
    @State private var open = false

    var body: some View {
        RailRow(node: .slBad) {
            VStack(alignment: .leading, spacing: 6) {
                Text("YOUR APP HIT AN ERROR")
                    .font(.app(11, .semibold))
                    .tracking(1.6)
                    .foregroundStyle(Color.slBad)
                Text("Imagi sent it to the coordinator to fix.")
                    .font(.app(14))
                    .foregroundStyle(Color.slMuted)
                Button(open ? "Hide the error" : "Show the error") {
                    withAnimation(.imagi) { open.toggle() }
                }
                .font(.app(13, .medium))
                .foregroundStyle(Color.slText)
                if open {
                    Text(text)
                        .font(.system(size: 12, design: .monospaced))
                        .foregroundStyle(Color.slMuted)
                        .textSelection(.enabled)
                }
            }
        }
    }
}
