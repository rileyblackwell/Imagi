import Foundation

/// Where the app finds Imagi.
///
/// Production by default. For a local backend in the simulator, set the
/// `IMAGI_SITE_URL` environment variable in the scheme (Product > Scheme >
/// Edit Scheme > Run > Arguments), e.g. `http://localhost:8000`.
enum AppConfig {
    static let siteURL: URL = {
        if let override = ProcessInfo.processInfo.environment["IMAGI_SITE_URL"],
           let url = URL(string: override), url.scheme != nil {
            return url
        }
        return URL(string: "https://imagi.up.railway.app")!
    }()

    static var apiBase: URL { siteURL.appendingPathComponent("api/v1") }
    static var privacyURL: URL { siteURL.appendingPathComponent("privacy") }
    static var termsURL: URL { siteURL.appendingPathComponent("terms") }
}
