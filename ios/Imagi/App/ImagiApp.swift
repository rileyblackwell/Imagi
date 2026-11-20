import SwiftUI

@main
struct ImagiApp: App {
    @State private var session: SessionStore

    init() {
        ImagiFonts.register()
        _session = State(initialValue: SessionStore())
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(session)
                .tint(.slCoral)
        }
    }
}

struct RootView: View {
    @Environment(SessionStore.self) private var session

    var body: some View {
        Group {
            if session.isSignedIn {
                ProjectsView()
            } else {
                WelcomeView()
            }
        }
        .animation(.imagi, value: session.isSignedIn)
    }
}
