import Foundation

/// A thread the coordinator handed work to, as a run announces it.
struct DispatchedTask: Hashable {
    let conversationId: Int
    let title: String
    let goal: String
}

/// One event from an agent run's stream (a fresh run or a watch of one).
struct AgentEvent {
    enum Kind {
        case start(conversationId: Int?)
        case delta(String)
        case toolCall(name: String, args: [String: String])
        case taskDispatch([DispatchedTask])
        case title(String)
        case done(filesChanged: Int)
        case error(message: String, code: String?)
        case other
    }

    let kind: Kind
    /// The event's number in the run's log, for resuming a dropped watch.
    let seq: Int?

    /// Read one line of a Server-Sent Events stream. Only `data:` lines carry
    /// events; keep-alive comments and blank lines give nil.
    static func parse(line: String) -> AgentEvent? {
        guard line.hasPrefix("data:") else { return nil }
        let payload = line.dropFirst(5).trimmingCharacters(in: .whitespaces)
        guard let data = payload.data(using: .utf8),
              let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let type = object["type"] as? String else { return nil }
        let seq = object["seq"] as? Int

        let kind: Kind
        switch type {
        case "start":
            kind = .start(conversationId: object["conversation_id"] as? Int)
        case "delta":
            kind = .delta(object["text"] as? String ?? "")
        case "tool_call":
            var args: [String: String] = [:]
            for (key, value) in object["args"] as? [String: Any] ?? [:] {
                args[key] = "\(value)"
            }
            kind = .toolCall(name: object["name"] as? String ?? "", args: args)
        case "task_dispatch":
            let tasks = (object["tasks"] as? [[String: Any]] ?? []).compactMap { task -> DispatchedTask? in
                guard let id = task["conversation_id"] as? Int else { return nil }
                return DispatchedTask(
                    conversationId: id,
                    title: task["title"] as? String ?? "",
                    goal: task["goal"] as? String ?? ""
                )
            }
            kind = .taskDispatch(tasks)
        case "title":
            kind = .title(object["title"] as? String ?? "")
        case "done":
            kind = .done(filesChanged: (object["files_changed"] as? [Any])?.count ?? 0)
        case "error":
            kind = .error(message: object["error"] as? String ?? "The run stopped.", code: object["code"] as? String)
        default:
            kind = .other
        }
        return AgentEvent(kind: kind, seq: seq)
    }
}

/// What a tool call is called in front of the person whose app it is. Mirrors
/// labelForTool in the web workspace (agentService.ts): what changed about
/// their app, never a file path.
enum ToolLabels {
    private static let lookActions: Set<String> = [
        "screenshot", "zoom", "read_page", "find", "get_page_text", "read_console", "wait",
    ]

    static func page(from args: [String: String]?) -> String? {
        let path = args?["path"] ?? args?["file_path"] ?? ""
        let file = path.split(separator: "/").last.map(String.init) ?? ""
        guard file.hasSuffix(".vue") else { return nil }
        var stem = String(file.dropLast(4))
        let named = stem.hasSuffix("View") && stem.count > 4
        if named { stem = String(stem.dropLast(4)) }
        guard named || path.contains("/views/"), let first = stem.first, first.isLetter else { return nil }
        var words = ""
        for (index, char) in stem.enumerated() {
            if index > 0, char.isUppercase { words.append(" ") }
            words.append(char)
        }
        return "your \(words.lowercased()) page"
    }

    static func label(for name: String, args: [String: String]?) -> String {
        if name == "browser" {
            let steps = (args?["actions"] ?? "")
                .split(separator: ",")
                .map { $0.trimmingCharacters(in: .whitespaces) }
                .filter { !$0.isEmpty }
            if !steps.isEmpty, steps.allSatisfy({ $0 == "navigate" }) { return "Opened a page in the preview" }
            if steps.isEmpty || steps.allSatisfy({ $0 == "navigate" || lookActions.contains($0) }) {
                return "Looked at your app in the preview"
            }
            return "Tried out your app in the preview"
        }
        let page = page(from: args)
        switch name {
        case "read_file": return page.map { "Looked at \($0)" } ?? "Looked at your project"
        case "edit_file", "update_file": return page.map { "Updated \($0)" } ?? "Updated your app"
        case "create_file": return page.map { "Built \($0)" } ?? "Added something new to your app"
        case "delete_file": return "Removed something from your app"
        case "grep_files", "glob_files", "get_project_tree", "list_project_files", "explore_project":
            return "Looked through your project"
        case "update_plan": return "Planned out the work"
        case "web_search", "web_search_call": return "Looked something up online"
        case "create_app": return "Set up a new part of your app"
        case "check_backend": return "Checked your app's backend"
        case "create_directory", "delete_directory": return "Tidied up your project"
        case "dispatch_task": return "Started a thread"
        case "ask_user": return "Asked you a question"
        default: return "Worked on your app"
        }
    }
}
