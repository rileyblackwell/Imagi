import SwiftUI

// Shared pieces of the Spotlight look, sized for a phone.

/// The lowercase wordmark: type, not an image, with the last dot lit.
struct Wordmark: View {
    var size: CGFloat = 24

    var body: some View {
        HStack(alignment: .firstTextBaseline, spacing: 0) {
            Text("imag")
            Text("\u{0131}")
                .overlay(alignment: .top) {
                    Circle()
                        .fill(.slLight)
                        .frame(width: size * 0.22, height: size * 0.22)
                        .offset(y: size * 0.1)
                }
        }
        .font(.display(size, relativeTo: .headline))
        .tracking(-size * 0.04)
        .foregroundStyle(Color.slText)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Imagi")
    }
}

/// A tracked uppercase label in `muted`.
struct Eyebrow: View {
    let text: String
    var color: Color = .slMuted

    init(_ text: String, color: Color = .slMuted) {
        self.text = text
        self.color = color
    }

    var body: some View {
        Text(text.uppercased())
            .font(.app(11.5, .semibold, relativeTo: .caption))
            .tracking(1.8)
            .foregroundStyle(color)
    }
}

/// The page-opening label between a coral and an amber hairline.
struct Marquee: View {
    let text: String

    var body: some View {
        HStack(spacing: 12) {
            LinearGradient(colors: [.clear, .slCoral], startPoint: .leading, endPoint: .trailing)
                .frame(width: 28, height: 1)
            Text(text.uppercased())
                .font(.app(11.5, .semibold, relativeTo: .caption))
                .tracking(2.6)
                .foregroundStyle(Color.slMuted)
            LinearGradient(colors: [.slAmber, .clear], startPoint: .leading, endPoint: .trailing)
                .frame(width: 28, height: 1)
        }
    }
}

/// The overhead spotlight pool a page opener carries.
struct SpotlightBackground: View {
    var body: some View {
        ZStack {
            Color.slBg
            GeometryReader { proxy in
                RadialGradient(
                    colors: [.slSpotCore, .slSpotMid, .clear],
                    center: UnitPoint(x: 0.5, y: -0.08),
                    startRadius: 0,
                    endRadius: max(proxy.size.width, 320) * 0.95
                )
                .frame(height: proxy.size.height * 0.75)
            }
        }
        .ignoresSafeArea()
    }
}

// MARK: Buttons

/// The lit primary pill. One per screen.
struct LitButtonStyle: ButtonStyle {
    var fullWidth = true
    @Environment(\.isEnabled) private var isEnabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.app(16, .semibold, relativeTo: .headline))
            .foregroundStyle(Color.slOnAccent)
            .frame(maxWidth: fullWidth ? .infinity : nil, minHeight: 50)
            .padding(.horizontal, 22)
            .background(Capsule().fill(.slLight))
            .overlay(Capsule().strokeBorder(Color.white.opacity(0.3), lineWidth: 0.5).blendMode(.overlay))
            .shadow(color: .slGlow, radius: configuration.isPressed ? 8 : 14, y: 6)
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .opacity(isEnabled ? 1 : 0.5)
            .animation(.imagi, value: configuration.isPressed)
    }
}

/// The ink pill: `text` fill, `bg` label.
struct InkButtonStyle: ButtonStyle {
    var fullWidth = true

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.app(16, .semibold, relativeTo: .headline))
            .foregroundStyle(Color.slBg)
            .frame(maxWidth: fullWidth ? .infinity : nil, minHeight: 50)
            .padding(.horizontal, 22)
            .background(Capsule().fill(Color.slText))
            .opacity(configuration.isPressed ? 0.85 : 1)
    }
}

/// An outline pill on `chip-bg`.
struct QuietButtonStyle: ButtonStyle {
    var fullWidth = false
    var tint: Color = .slText

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.app(14.5, .medium, relativeTo: .subheadline))
            .foregroundStyle(tint)
            .frame(maxWidth: fullWidth ? .infinity : nil, minHeight: 38)
            .padding(.horizontal, 16)
            .background(Capsule().fill(configuration.isPressed ? Color.slChipHover : Color.slChip))
            .overlay(Capsule().strokeBorder(Color.slLineStrong, lineWidth: 1))
    }
}

// MARK: Cards and fields

struct CardBackground: ViewModifier {
    var edge: Color = .slLine
    var padding: CGFloat = 18

    func body(content: Content) -> some View {
        content
            .padding(padding)
            .background(RoundedRectangle(cornerRadius: Radius.card, style: .continuous).fill(Color.slSurface))
            .overlay(RoundedRectangle(cornerRadius: Radius.card, style: .continuous).strokeBorder(edge, lineWidth: 1))
    }
}

extension View {
    func imagiCard(edge: Color = .slLine, padding: CGFloat = 18) -> some View {
        modifier(CardBackground(edge: edge, padding: padding))
    }
}

/// A text field: one border that deepens on focus and turns `bad` on a problem.
struct FieldBox<Content: View>: View {
    let label: String
    var error: String?
    var focused = false
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Eyebrow(label)
            content
                .font(.app(16, relativeTo: .body))
                .foregroundStyle(Color.slText)
                .tint(.slCoral)
                .padding(.horizontal, 14)
                .padding(.vertical, 13)
                .background(RoundedRectangle(cornerRadius: Radius.tile, style: .continuous).fill(Color.slSurface))
                .overlay(
                    RoundedRectangle(cornerRadius: Radius.tile, style: .continuous)
                        .strokeBorder(error != nil ? Color.slBad : (focused ? Color.slText.opacity(0.35) : Color.slLineStrong), lineWidth: 1)
                )
            if let error {
                Text(error)
                    .font(.app(13.5, relativeTo: .footnote))
                    .foregroundStyle(Color.slBad)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }
}

/// A form-level problem under a button, on a `bad` left rule.
struct ProblemNote: View {
    let text: String

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Rectangle().fill(Color.slBad).frame(width: 2)
            Text(text)
                .font(.app(14, relativeTo: .footnote))
                .foregroundStyle(Color.slText)
                .fixedSize(horizontal: false, vertical: true)
        }
        .fixedSize(horizontal: false, vertical: true)
    }
}

// MARK: Status

/// The workspace's one working sign: a steady `work` dot with a breathing halo.
struct WorkingIndicator: View {
    var size: CGFloat = 8
    @State private var breathe = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ZStack {
            Circle()
                .fill(Color.slWork.opacity(0.28))
                .frame(width: size * 2.4, height: size * 2.4)
                .scaleEffect(breathe ? 1 : 0.55)
                .opacity(breathe ? 0.15 : 0.7)
            Circle().fill(Color.slWork).frame(width: size, height: size)
        }
        .frame(width: size * 2.4, height: size * 2.4)
        .onAppear {
            guard !reduceMotion else { return }
            withAnimation(.easeInOut(duration: 1.4).repeatForever(autoreverses: true)) { breathe = true }
        }
        .accessibilityLabel("Working")
    }
}

/// Where a thread stands, in the workspace's four status colours.
enum ThreadState: Int, Comparable {
    case waiting, working, scheduled, finished, stopped

    static func < (a: ThreadState, b: ThreadState) -> Bool { a.rawValue < b.rawValue }

    var color: Color {
        switch self {
        case .waiting: return .slWait
        case .working, .scheduled: return .slWork
        case .finished: return .slOk
        case .stopped: return .slBad
        }
    }

    var label: String {
        switch self {
        case .waiting: return "Waiting on you"
        case .working: return "Working"
        case .scheduled: return "Scheduled"
        case .finished: return "Finished"
        case .stopped: return "Stopped"
        }
    }
}

struct StatusDot: View {
    let state: ThreadState

    var body: some View {
        if state == .working {
            WorkingIndicator(size: 7)
        } else {
            Circle()
                .strokeBorder(state.color, style: StrokeStyle(lineWidth: 1.5, dash: state == .scheduled ? [2, 2] : []))
                .background(Circle().fill(state == .scheduled ? Color.clear : state.color))
                .frame(width: 9, height: 9)
                .frame(width: 17, height: 17)
        }
    }
}

extension Date {
    /// "just now", "5 min ago", "Yesterday", or a date.
    var imagiRelative: String {
        let seconds = Date().timeIntervalSince(self)
        if seconds < 60 { return "just now" }
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .short
        return formatter.localizedString(for: self, relativeTo: Date())
    }
}
