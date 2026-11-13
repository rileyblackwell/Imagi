import SwiftUI

struct SignInView: View {
    var onRegister: () -> Void

    @Environment(SessionStore.self) private var session
    @State private var username = ""
    @State private var password = ""
    @State private var error: String?
    @State private var working = false
    @FocusState private var focus: Field?

    private enum Field { case username, password }

    var body: some View {
        AuthScaffold(title: "Welcome back", lede: "Sign in to pick up where you left off.") {
            FieldBox(label: "Username", focused: focus == .username) {
                TextField("", text: $username, prompt: Text("Your username").foregroundStyle(Color.slPlaceholder))
                    .textContentType(.username)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .submitLabel(.next)
                    .focused($focus, equals: .username)
                    .onSubmit { focus = .password }
            }
            FieldBox(label: "Password", focused: focus == .password) {
                SecureField("", text: $password, prompt: Text("Your password").foregroundStyle(Color.slPlaceholder))
                    .textContentType(.password)
                    .submitLabel(.go)
                    .focused($focus, equals: .password)
                    .onSubmit(submit)
            }
            if let error { ProblemNote(text: error) }
            Button(action: submit) {
                if working { ProgressView().tint(.slOnAccent) } else { Text("Sign in") }
            }
            .buttonStyle(LitButtonStyle())
            .disabled(working)
            .padding(.top, 4)
            Button("New to Imagi? Create an account", action: onRegister)
                .font(.app(14.5, .medium))
                .foregroundStyle(Color.slMuted)
                .frame(maxWidth: .infinity)
        }
        .onAppear { focus = .username }
    }

    private func submit() {
        let name = username.trimmingCharacters(in: .whitespaces)
        guard !name.isEmpty, !password.isEmpty else {
            error = "Enter your username and password."
            return
        }
        working = true
        error = nil
        Task {
            defer { working = false }
            do {
                try await session.signIn(username: name, password: password)
            } catch {
                self.error = error.localizedDescription
            }
        }
    }
}

/// The shared layout of the sign-in and sign-up screens: a centred card on the stage.
struct AuthScaffold<Content: View>: View {
    let title: String
    let lede: String
    @ViewBuilder var content: Content

    var body: some View {
        ZStack {
            SpotlightBackground()
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(title)
                            .font(.display(36, relativeTo: .largeTitle))
                            .tracking(-1)
                            .foregroundStyle(Color.slText)
                        Text(lede)
                            .font(.app(16))
                            .foregroundStyle(Color.slMuted)
                    }
                    .padding(.bottom, 6)
                    content
                }
                .imagiCard(padding: 22)
                .padding(.horizontal, 16)
                .padding(.top, 24)
                .padding(.bottom, 32)
            }
            .scrollDismissesKeyboard(.interactively)
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar(.visible, for: .navigationBar)
        .toolbar {
            ToolbarItem(placement: .principal) { Wordmark(size: 20) }
        }
    }
}
