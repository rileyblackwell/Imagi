import Foundation

/// A refused request, with the server's own words when it gave any.
struct APIError: LocalizedError {
    let status: Int
    let message: String
    /// Per-field messages from a form the server refused (name, email, …).
    let fields: [String: String]
    /// The server's machine-readable reason, when it gave one ("agent_busy").
    let code: String?

    var errorDescription: String? { message }

    static func from(status: Int, data: Data) -> APIError {
        var fields: [String: String] = [:]
        var message: String?
        var code: String?
        if let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
            for (key, value) in object {
                if let text = value as? String {
                    fields[key] = text
                } else if let list = value as? [Any], let first = list.first {
                    fields[key] = "\(first)"
                }
            }
            let detail = object["detail"] as? String
            let error = object["error"] as? String
            code = detail ?? error
            message = friendly(detail) ?? friendly(error)
                ?? fields["non_field_errors"]
                ?? fields.values.sorted().first
        }
        if status == 0 {
            message = message ?? "Imagi can't be reached. Check your connection and try again."
        }
        return APIError(
            status: status,
            message: message ?? "Something went wrong (\(status)). Try again.",
            fields: fields,
            code: code
        )
    }

    /// Codes the server sends as a word rather than a sentence.
    private static func friendly(_ text: String?) -> String? {
        guard let text, !text.isEmpty else { return nil }
        switch text {
        case "agent_busy": return "The coordinator is still working on your last message."
        case "too_many_concurrent_runs": return "You have the most runs going at once. Try again when one finishes."
        default: return text.contains(" ") ? text : nil
        }
    }
}

/// Talks to Imagi's Django API with the account's token.
final class APIClient {
    static let shared = APIClient()

    var token: String?
    /// Called when the server no longer accepts the token.
    var onUnauthorized: (@MainActor () -> Void)?

    private let session: URLSession
    private let streamSession: URLSession

    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 60
        session = URLSession(configuration: config)

        // Runs can stay quiet for a while between events; the server sends
        // keep-alives, so a generous idle timeout is enough.
        let streamConfig = URLSessionConfiguration.default
        streamConfig.timeoutIntervalForRequest = 300
        streamConfig.timeoutIntervalForResource = 60 * 60 * 6
        streamSession = URLSession(configuration: streamConfig)
    }

    // MARK: Requests

    func makeRequest(_ method: String, _ path: String, query: [String: String] = [:], json: [String: Any]? = nil) -> URLRequest {
        var components = URLComponents(url: AppConfig.apiBase.appendingPathComponent(path), resolvingAgainstBaseURL: false)!
        // appendingPathComponent drops a trailing slash, which Django needs.
        if path.hasSuffix("/"), !(components.path.hasSuffix("/")) { components.path += "/" }
        if !query.isEmpty {
            components.queryItems = query.map { URLQueryItem(name: $0.key, value: $0.value) }
        }
        var request = URLRequest(url: components.url!)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if let token {
            request.setValue("Token \(token)", forHTTPHeaderField: "Authorization")
        }
        if let json {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try? JSONSerialization.data(withJSONObject: json)
        }
        return request
    }

    @discardableResult
    func data(_ request: URLRequest) async throws -> Data {
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch let error as URLError where error.code == .cancelled {
            throw CancellationError()
        } catch {
            throw APIError.from(status: 0, data: Data())
        }
        let status = (response as? HTTPURLResponse)?.statusCode ?? 0
        guard (200..<300).contains(status) else {
            if status == 401, request.value(forHTTPHeaderField: "Authorization") != nil {
                let handler = self.onUnauthorized
                await MainActor.run { handler?() }
            }
            throw APIError.from(status: status, data: data)
        }
        return data
    }

    func get<T: Decodable>(_ path: String, query: [String: String] = [:]) async throws -> T {
        let body = try await self.data(makeRequest("GET", path, query: query))
        return try JSONDecoder.imagi.decode(T.self, from: body)
    }

    func send<T: Decodable>(_ method: String, _ path: String, json: [String: Any]? = nil) async throws -> T {
        let body = try await self.data(makeRequest(method, path, json: json ?? [:]))
        return try JSONDecoder.imagi.decode(T.self, from: body)
    }

    func sendIgnoringBody(_ method: String, _ path: String, json: [String: Any]? = nil) async throws {
        try await data(makeRequest(method, path, json: json ?? [:]))
    }

    /// Sign-in and sign-up are CSRF-protected for the website's sake, so a
    /// native client fetches the csrftoken cookie first and echoes it back.
    func csrfRequest(_ path: String, json: [String: Any]) async throws -> URLRequest {
        try await data(makeRequest("GET", "auth/csrf/"))
        var request = makeRequest("POST", path, json: json)
        let cookies = HTTPCookieStorage.shared.cookies(for: AppConfig.siteURL) ?? []
        if let csrf = cookies.first(where: { $0.name == "csrftoken" })?.value {
            request.setValue(csrf, forHTTPHeaderField: "X-CSRFToken")
        }
        request.setValue(AppConfig.siteURL.absoluteString + "/", forHTTPHeaderField: "Referer")
        request.setValue(AppConfig.siteURL.absoluteString, forHTTPHeaderField: "Origin")
        return request
    }

    // MARK: Event streams

    /// Read a run's Server-Sent Events until the server closes the stream.
    func events(_ request: URLRequest) -> AsyncThrowingStream<AgentEvent, Error> {
        var request = request
        request.setValue("text/event-stream", forHTTPHeaderField: "Accept")
        let session = streamSession
        return AsyncThrowingStream { continuation in
            let task = Task {
                do {
                    let (bytes, response) = try await session.bytes(for: request)
                    let status = (response as? HTTPURLResponse)?.statusCode ?? 0
                    guard (200..<300).contains(status) else {
                        var body = Data()
                        for try await byte in bytes { body.append(byte) }
                        throw APIError.from(status: status, data: body)
                    }
                    for try await line in bytes.lines {
                        if let event = AgentEvent.parse(line: line) {
                            continuation.yield(event)
                        }
                    }
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
            continuation.onTermination = { _ in task.cancel() }
        }
    }
}
