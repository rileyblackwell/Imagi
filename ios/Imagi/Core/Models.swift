import Foundation

// The shapes Imagi's API returns. Every field the server might leave out is
// optional, so an older or newer server never breaks decoding.

struct User: Codable, Equatable {
    let id: Int
    let username: String
    let email: String?
    let name: String?
}

struct AuthResponse: Decodable {
    let token: String
    let user: User
}

struct Project: Codable, Identifiable, Hashable {
    let id: Int
    let name: String
    let slug: String?
    let description: String?
    let appDetails: String?
    let createdAt: Date?
    let updatedAt: Date?

    /// The first sentence of what the app is, for a list row.
    var summary: String {
        let text = (description ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return "" }
        if let end = text.firstIndex(where: { ".!?".contains($0) }) {
            return String(text[...end])
        }
        return text
    }
}

/// A list endpoint answers either with a bare array or with DRF's page.
struct ListResponse<T: Decodable>: Decodable {
    let items: [T]

    private struct Page: Decodable { let results: [T] }

    init(from decoder: Decoder) throws {
        if let array = try? [T](from: decoder) {
            items = array
        } else {
            items = try Page(from: decoder).results
        }
    }
}

struct ThreadSchedule: Decodable, Hashable {
    let status: String?
    let reason: String?
}

/// One agent conversation: the coordinator (kind "lead") or a thread ("task").
struct Conversation: Decodable, Identifiable, Hashable {
    let id: Int
    let title: String?
    let modelName: String?
    let reasoningEffort: String?
    let serviceTier: String?
    let projectId: Int?
    let kind: String?
    let parent: Int?
    let reviewStatus: String?
    let archivedAt: Date?
    let createdAt: Date?
    let updatedAt: Date?
    let lastMessagePreview: String?
    let lastAssistantSummary: String?
    let brief: String?
    let overview: String?
    let isRunning: Bool?
    let queuedPrompt: String?
    let schedule: ThreadSchedule?

    var isCoordinator: Bool { kind == "lead" }
    var isThread: Bool { kind == "task" }
    var running: Bool { isRunning ?? false }
    var hasQueuedWork: Bool { !(queuedPrompt ?? "").trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }

    /// What the thread is doing, in the person's words.
    var displayTitle: String {
        for candidate in [brief, title] {
            let text = (candidate ?? "").trimmingCharacters(in: .whitespacesAndNewlines)
            if !text.isEmpty { return text }
        }
        return "Thread"
    }
}

struct TaskRef: Decodable, Hashable {
    let conversationId: Int?
    let title: String?
}

struct ToolCallRecord: Decodable {
    let name: String
    let args: [String: LooseString]?
}

struct QuestionInfo: Decodable, Hashable {
    let options: [String]?
}

struct MessageMetadata: Decodable {
    let toolCalls: [ToolCallRecord]?
    let dispatchedTasks: [TaskRef]?
    let question: QuestionInfo?
    let appError: Bool?
    let filesChanged: [String]?
    let taskReport: Bool?
}

struct ChatMessage: Decodable, Identifiable {
    let id: Int
    let role: String
    let content: String
    let timestamp: Date?
    let metadata: MessageMetadata?

    init(id: Int, role: String, content: String, timestamp: Date? = Date(), metadata: MessageMetadata? = nil) {
        self.id = id
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.metadata = metadata
    }

    private enum CodingKeys: String, CodingKey { case id, role, content, timestamp, metadata }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(Int.self, forKey: .id)
        role = (try? c.decode(String.self, forKey: .role)) ?? "assistant"
        content = (try? c.decode(String.self, forKey: .content)) ?? ""
        timestamp = try? c.decode(Date.self, forKey: .timestamp)
        // Metadata is free-form on the server; a field we don't expect must
        // never cost the whole transcript.
        metadata = try? c.decode(MessageMetadata.self, forKey: .metadata)
    }

    var isUser: Bool { role == "user" }

    /// Plain-language steps the agent took, as the web workspace words them.
    var steps: [String] {
        (metadata?.toolCalls ?? []).map { ToolLabels.label(for: $0.name, args: $0.args?.mapValues(\.value)) }
    }
}

struct CheckInTask: Decodable, Hashable {
    let id: Int
    let title: String?
    let goal: String?
    let reviewStatus: String?
    let isRunning: Bool?
}

/// Something a thread put in front of the person: a question, a finish, an error.
struct CheckIn: Decodable, Identifiable, Hashable {
    let id: Int
    let kind: String
    let body: String
    let options: [String]?
    let status: String?
    let task: CheckInTask

    var isQuestion: Bool { kind == "question" || kind == "ready" }
}

struct PreviewStart: Decodable {
    let running: Bool?
    let url: String?
    let error: String?
    let cold: Bool?
}

struct PreviewStage: Decodable, Hashable {
    let key: String?
    let label: String?
    let state: String?
}

struct PreviewProgress: Decodable {
    let stages: [PreviewStage]?
}

struct ServerStatus: Decodable {
    let state: String?
}

struct PreviewStatus: Decodable {
    let running: Bool?
    let frontend: ServerStatus?
    let backend: ServerStatus?
    let progress: PreviewProgress?
}

/// A JSON value read as text whatever its type (string, number or bool).
struct LooseString: Decodable, Hashable {
    let value: String

    init(from decoder: Decoder) throws {
        let c = try decoder.singleValueContainer()
        if let s = try? c.decode(String.self) { value = s }
        else if let i = try? c.decode(Int.self) { value = String(i) }
        else if let d = try? c.decode(Double.self) { value = String(d) }
        else if let b = try? c.decode(Bool.self) { value = String(b) }
        else { value = "" }
    }
}

extension JSONDecoder {
    /// Snake-case keys and Django's ISO 8601 dates (with or without
    /// microseconds). A date that can't be read becomes nil-like distantPast
    /// rather than failing the response.
    static let imagi: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .custom { decoder in
            let c = try decoder.singleValueContainer()
            let text = try c.decode(String.self)
            return ISODate.parse(text) ?? .distantPast
        }
        return decoder
    }()
}

enum ISODate {
    static func parse(_ text: String) -> Date? {
        let withFraction = ISO8601DateFormatter()
        withFraction.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = withFraction.date(from: text) { return date }
        let plain = ISO8601DateFormatter()
        plain.formatOptions = [.withInternetDateTime]
        if let date = plain.date(from: text) { return date }
        // Microseconds: drop the fraction and try again.
        if let range = text.range(of: #"\.\d+"#, options: .regularExpression) {
            var trimmed = text
            trimmed.removeSubrange(range)
            return plain.date(from: trimmed)
        }
        return nil
    }
}
