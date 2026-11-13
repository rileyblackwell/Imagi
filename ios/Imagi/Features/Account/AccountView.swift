import SwiftUI

/// Who you're signed in as, the legal pages, sign out, and delete account.
struct AccountView: View {
    @Environment(SessionStore.self) private var session
    @Environment(\.dismiss) private var dismiss
    @State private var confirmingDelete = false
    @State private var password = ""
    @State private var deleteError: String?
    @State private var deleting = false

    var body: some View {
        NavigationStack {
            List {
                Section {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(session.user?.username ?? "Your account")
                            .font(.app(17, .semibold))
                            .foregroundStyle(Color.slText)
                        if let email = session.user?.email, !email.isEmpty {
                            Text(email).font(.app(14)).foregroundStyle(Color.slMuted)
                        }
                    }
                    .padding(.vertical, 4)
                    LabeledContent("Plan") {
                        Text("Free").foregroundStyle(Color.slMuted)
                    }
                    .font(.app(15))
                }
                Section {
                    Link("Terms of Service", destination: AppConfig.termsURL)
                    Link("Privacy Policy", destination: AppConfig.privacyURL)
                }
                .font(.app(15))
                .tint(.slText)
                Section {
                    Button("Sign out") {
                        Task {
                            await session.signOut()
                            dismiss()
                        }
                    }
                    .foregroundStyle(Color.slText)
                } footer: {
                    Text("Your apps keep building on Imagi while you're away.")
                }
                .font(.app(15))
                Section {
                    Button("Delete account", role: .destructive) { confirmingDelete = true }
                } footer: {
                    Text("Deletes your account, every app you've made and its code. This can't be undone.")
                }
                .font(.app(15))
            }
            .scrollContentBackground(.hidden)
            .background(Color.slBg)
            .navigationTitle("Account")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }.foregroundStyle(Color.slText)
                }
            }
            .alert("Delete your account?", isPresented: $confirmingDelete) {
                SecureField("Password", text: $password)
                Button("Delete account", role: .destructive, action: deleteAccount)
                Button("Cancel", role: .cancel) { password = "" }
            } message: {
                Text("Enter your password to delete your account and all of your apps for good.")
            }
            .alert("Account not deleted", isPresented: Binding(get: { deleteError != nil }, set: { if !$0 { deleteError = nil } })) {
                Button("OK", role: .cancel) {}
            } message: {
                Text(deleteError ?? "")
            }
            .overlay {
                if deleting { ProgressView().controlSize(.large) }
            }
        }
    }

    private func deleteAccount() {
        let typed = password
        password = ""
        deleting = true
        Task {
            defer { deleting = false }
            do {
                try await session.deleteAccount(password: typed)
                dismiss()
            } catch {
                deleteError = error.localizedDescription
            }
        }
    }
}
