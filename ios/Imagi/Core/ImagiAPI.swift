import Foundation

/// Imagi's endpoints, as the app uses them.
extension APIClient {
    // MARK: Account

    func signIn(username: String, password: String) async throws -> AuthResponse {
        let request = try await csrfRequest("auth/signin/", json: ["username": username, "password": password])
        return try JSONDecoder.imagi.decode(AuthResponse.self, from: try await data(request))
    }

    func register(username: String, email: String, password: String, confirmation: String) async throws -> AuthResponse {
        let request = try await csrfRequest("auth/register/", json: [
            "username": username,
            "email": email,
            "password": password,
            "password_confirmation": confirmation,
        ])
        return try JSONDecoder.imagi.decode(AuthResponse.self, from: try await data(request))
    }

    func signOut() async {
        try? await sendIgnoringBody("POST", "auth/logout/")
    }

    func deleteAccount(password: String) async throws {
        try await sendIgnoringBody("POST", "auth/account/delete/", json: ["password": password])
    }

    // MARK: Projects

    func projects() async throws -> [Project] {
        let list: ListResponse<Project> = try await get("project-manager/projects/")
        return list.items
    }

    func createProject(name: String, description: String, appDetails: String, designPreferences: String) async throws -> Project {
        try await send("POST", "project-manager/projects/create/", json: [
            "name": name,
            "description": description,
            "app_details": appDetails,
            "design_preferences": designPreferences,
        ])
    }

    func deleteProject(_ id: Int) async throws {
        try await sendIgnoringBody("DELETE", "project-manager/projects/\(id)/delete/")
    }

    /// Warm the previews of the most recently opened projects (sign-in hook).
    func prewarmPreviews() async {
        try? await sendIgnoringBody("POST", "builder/preview/prewarm/")
    }

    // MARK: Coordinator and threads

    func conversations(projectId: Int) async throws -> [Conversation] {
        let list: ListResponse<Conversation> = try await get("agents/conversations/", query: ["project_id": String(projectId)])
        return list.items
    }

    func conversation(_ id: Int) async throws -> Conversation {
        try await get("agents/conversations/\(id)/")
    }

    /// The project's coordinator; the server returns the existing one if there is one.
    func coordinator(projectId: Int) async throws -> Conversation {
        try await send("POST", "agents/conversations/", json: ["project_id": projectId, "kind": "lead"])
    }

    func messages(conversationId: Int) async throws -> [ChatMessage] {
        let list: ListResponse<ChatMessage> = try await get("agents/conversations/\(conversationId)/messages/")
        return list.items.filter { $0.metadata?.taskReport != true }
    }

    func checkIns(projectId: Int) async throws -> [CheckIn] {
        let list: ListResponse<CheckIn> = try await get("agents/checkins/", query: ["project_id": String(projectId)])
        return list.items
    }

    func resolveCheckIn(_ id: Int) async {
        try? await sendIgnoringBody("POST", "agents/checkins/\(id)/resolve/")
    }

    /// Send the coordinator a message and follow the run it starts.
    func runCoordinator(conversation: Conversation, projectId: Int, message: String) -> AsyncThrowingStream<AgentEvent, Error> {
        var body: [String: Any] = [
            "message": message,
            "project_id": String(projectId),
            "conversation_id": conversation.id,
            "model": conversation.modelName ?? "claude-opus-5-5",
        ]
        if let effort = conversation.reasoningEffort { body["reasoning_effort"] = effort }
        if let tier = conversation.serviceTier { body["service_tier"] = tier }
        return events(makeRequest("POST", "agents/agent/stream/", json: body))
    }

    /// Follow a conversation's current (or next) run; `after` resumes a dropped watch.
    func watch(conversationId: Int, after: Int? = nil) -> AsyncThrowingStream<AgentEvent, Error> {
        var query: [String: String] = [:]
        if let after { query["after"] = String(after) }
        return events(makeRequest("GET", "agents/conversations/\(conversationId)/events/", query: query))
    }

    /// Give a thread its next message (or, with none, start work already staged).
    func sendToThread(_ id: Int, message: String) async throws {
        try await sendIgnoringBody("POST", "agents/conversations/\(id)/send/", json: ["message": message])
    }

    func cancelRun(_ id: Int) async {
        try? await sendIgnoringBody("POST", "agents/conversations/\(id)/cancel/", json: ["reason": "Stopped from the iOS app"])
    }

    func dismissThread(_ id: Int) async throws {
        try await sendIgnoringBody("POST", "agents/conversations/\(id)/dismiss/")
    }

    // MARK: Preview

    func startPreview(projectId: Int) async throws -> PreviewStart {
        var request = makeRequest("POST", "builder/\(projectId)/preview/", json: [:])
        // A cold start installs and boots the app's servers.
        request.timeoutInterval = 600
        let body = try await data(request)
        return try JSONDecoder.imagi.decode(PreviewStart.self, from: body)
    }

    /// Health poll, and the heartbeat that keeps the preview warm while watched.
    func previewStatus(projectId: Int, visible: Bool) async throws -> PreviewStatus {
        try await send("POST", "builder/\(projectId)/preview/status/", json: ["console_errors": [], "visible": visible])
    }
}
