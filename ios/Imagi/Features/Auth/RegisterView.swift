import SwiftUI

struct RegisterView: View {
    var onSignIn: () -> Void

    @Environment(SessionStore.self) private var session
    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @State private var confirmation = ""
    @State private var fieldErrors: [String: String] = [:]
    @State private var error: String?
    @State private var working = false
    @FocusState private var focus: Field?

    private enum Field { case username, email, password, confirmation }

    var body: some View {
        AuthScaffold(title: "Create your account", lede: "Free to use. No card needed.") {
            FieldBox(label: "Username", error: fieldErrors["username"], focused: focus == .username) {
                TextField("", text: $username, prompt: Text("Pick a username").foregroundStyle(Color.slPlaceholder))
                    .textContentType(.username)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .submitLabel(.next)
                    .focused($focus, equals: .username)
                    .onSubmit { focus = .email }
            }
            FieldBox(label: "Email", error: fieldErrors["email"], focused: focus == .email) {
                TextField("", text: $email, prompt: Text("you@example.com").foregroundStyle(Color.slPlaceholder))
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .textInputAutocapitalization(.never)
                    .autocorrectionDisabled()
                    .submitLabel(.next)
                    .focused($focus, equals: .email)
                    .onSubmit { focus = .password }
            }
            FieldBox(label: "Password", error: fieldErrors["password"], focused: focus == .password) {
                SecureField("", text: $password, prompt: Text("At least 8 characters").foregroundStyle(Color.slPlaceholder))
                    .textContentType(.newPassword)
                    .submitLabel(.next)
                    .focused($focus, equals: .password)
                    .onSubmit { focus = .confirmation }
            }
            FieldBox(label: "Confirm password", error: fieldErrors["password_confirmation"], focused: focus == .confirmation) {
                SecureField("", text: $confirmation, prompt: Text("Type it again").foregroundStyle(Color.slPlaceholder))
                    .textContentType(.newPassword)
                    .submitLabel(.go)
                    .focused($focus, equals: .confirmation)
                    .onSubmit(submit)
            }
            if let error { ProblemNote(text: error) }
            Button(action: submit) {
                if working { ProgressView().tint(.slOnAccent) } else { Text("Create account") }
            }
            .buttonStyle(LitButtonStyle())
            .disabled(working)
            .padding(.top, 4)
            Text(Self.consent)
                .font(.app(13))
                .foregroundStyle(Color.slMuted)
                .tint(.slText)
            Button("Already have an account? Sign in", action: onSignIn)
                .font(.app(14.5, .medium))
                .foregroundStyle(Color.slMuted)
                .frame(maxWidth: .infinity)
        }
        .onAppear { focus = .username }
    }

    private static let consent: AttributedString = {
        let text = "By creating an account you agree to the [Terms](\(AppConfig.termsURL.absoluteString)) and [Privacy Policy](\(AppConfig.privacyURL.absoluteString))."
        return (try? AttributedString(markdown: text)) ?? AttributedString(text)
    }()

    private func submit() {
        var problems: [String: String] = [:]
        let name = username.trimmingCharacters(in: .whitespaces)
        let mail = email.trimmingCharacters(in: .whitespaces)
        if name.isEmpty { problems["username"] = "Pick a username." }
        if !mail.contains("@") { problems["email"] = "Enter your email address." }
        if password.count < 8 { problems["password"] = "Use at least 8 characters." }
        if confirmation != password { problems["password_confirmation"] = "The passwords don't match." }
        fieldErrors = problems
        error = problems.isEmpty ? nil : "Your account can't be created yet. Check the fields above."
        guard problems.isEmpty else { return }

        working = true
        Task {
            defer { working = false }
            do {
                try await session.register(username: name, email: mail, password: password, confirmation: confirmation)
            } catch let apiError as APIError {
                fieldErrors = apiError.fields.filter { ["username", "email", "password", "password_confirmation"].contains($0.key) }
                error = fieldErrors.isEmpty ? apiError.message : "Your account can't be created yet. Check the fields above."
            } catch {
                self.error = error.localizedDescription
            }
        }
    }
}
