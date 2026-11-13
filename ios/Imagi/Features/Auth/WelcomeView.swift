import SwiftUI

/// The signed-out opener: what Imagi is, and the two ways in.
struct WelcomeView: View {
    private enum Route: Hashable { case signIn, register }
    @State private var path: [Route] = []

    var body: some View {
        NavigationStack(path: $path) {
            ZStack {
                SpotlightBackground()
                VStack(alignment: .leading, spacing: 0) {
                    Wordmark(size: 26)
                        .padding(.top, 12)
                    Spacer(minLength: 24)
                    Marquee(text: "Build your app")
                        .padding(.bottom, 18)
                    headline
                        .padding(.bottom, 16)
                    Text("Describe the app you want. Imagi's agent builds it while you watch, and you keep shaping it by talking to it.")
                        .font(.app(17, relativeTo: .body))
                        .lineSpacing(5)
                        .foregroundStyle(Color.slMuted)
                        .fixedSize(horizontal: false, vertical: true)
                    Spacer(minLength: 32)
                    VStack(spacing: 12) {
                        Button("Start building") { path.append(.register) }
                            .buttonStyle(LitButtonStyle())
                        Button("Sign in") { path.append(.signIn) }
                            .buttonStyle(InkButtonStyle())
                    }
                    legal
                        .padding(.top, 18)
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 12)
            }
            .navigationDestination(for: Route.self) { route in
                switch route {
                case .signIn: SignInView(onRegister: { path = [.register] })
                case .register: RegisterView(onSignIn: { path = [.signIn] })
                }
            }
            .toolbar(.hidden, for: .navigationBar)
        }
    }

    private var headline: some View {
        (Text("Build and ") + Text("run").foregroundStyle(.slLight) + Text(" your business"))
            .font(.display(52, relativeTo: .largeTitle))
            .tracking(-1.6)
            .lineSpacing(-6)
            .foregroundStyle(Color.slText)
            .fixedSize(horizontal: false, vertical: true)
    }

    private var legal: some View {
        HStack(spacing: 6) {
            Text("Free to use.")
            Link("Terms", destination: AppConfig.termsURL)
            Text("·")
            Link("Privacy", destination: AppConfig.privacyURL)
        }
        .font(.app(13, relativeTo: .footnote))
        .foregroundStyle(Color.slMuted)
        .tint(.slMuted)
        .frame(maxWidth: .infinity)
    }
}
