import Foundation
import Observation

/// Who is signed in. The token is kept in the Keychain; the user's name in UserDefaults.
@Observable
@MainActor
final class SessionStore {
    private(set) var user: User?
    private(set) var isSignedIn = false

    private let api = APIClient.shared
    private static let userKey = "imagi.user"

    init() {
        let token = Keychain.get("token")
        api.token = token
        isSignedIn = token != nil
        if let data = UserDefaults.standard.data(forKey: Self.userKey) {
            user = try? JSONDecoder().decode(User.self, from: data)
        }
        api.onUnauthorized = { [weak self] in self?.forget() }
    }

    func signIn(username: String, password: String) async throws {
        adopt(try await api.signIn(username: username, password: password))
    }

    func register(username: String, email: String, password: String, confirmation: String) async throws {
        adopt(try await api.register(username: username, email: email, password: password, confirmation: confirmation))
    }

    func signOut() async {
        await api.signOut()
        forget()
    }

    func deleteAccount(password: String) async throws {
        try await api.deleteAccount(password: password)
        forget()
    }

    private func adopt(_ auth: AuthResponse) {
        Keychain.set(auth.token, for: "token")
        api.token = auth.token
        user = auth.user
        UserDefaults.standard.set(try? JSONEncoder().encode(auth.user), forKey: Self.userKey)
        // The website's session cookie isn't needed: the app signs every
        // request with its token.
        for cookie in HTTPCookieStorage.shared.cookies(for: AppConfig.siteURL) ?? [] where cookie.name == "sessionid" {
            HTTPCookieStorage.shared.deleteCookie(cookie)
        }
        isSignedIn = true
        Task { await api.prewarmPreviews() }
    }

    private func forget() {
        Keychain.set(nil, for: "token")
        api.token = nil
        user = nil
        UserDefaults.standard.removeObject(forKey: Self.userKey)
        isSignedIn = false
    }
}
