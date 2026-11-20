import XCTest
@testable import Imagi

final class AgentEventTests: XCTestCase {
    func testParsesDeltaWithItsSequenceNumber() {
        let event = AgentEvent.parse(line: #"data: {"type": "delta", "text": "Hello", "seq": 4}"#)
        guard case .delta(let text) = event?.kind else { return XCTFail("expected a delta") }
        XCTAssertEqual(text, "Hello")
        XCTAssertEqual(event?.seq, 4)
    }

    func testIgnoresKeepalivesAndBlankLines() {
        XCTAssertNil(AgentEvent.parse(line: ": keepalive"))
        XCTAssertNil(AgentEvent.parse(line: ""))
        XCTAssertNil(AgentEvent.parse(line: "data: not json"))
    }

    func testReadsToolCallArgumentsOfAnyType() {
        let event = AgentEvent.parse(line: #"data: {"type": "tool_call", "name": "edit_file", "args": {"path": "src/views/HomeView.vue", "line": 3}}"#)
        guard case .toolCall(let name, let args) = event?.kind else { return XCTFail("expected a tool call") }
        XCTAssertEqual(name, "edit_file")
        XCTAssertEqual(args["path"], "src/views/HomeView.vue")
        XCTAssertEqual(args["line"], "3")
    }

    func testReadsDispatchedThreads() {
        let event = AgentEvent.parse(line: #"data: {"type": "task_dispatch", "tasks": [{"conversation_id": 12, "title": "Menu", "goal": "Build the menu page"}]}"#)
        guard case .taskDispatch(let tasks) = event?.kind else { return XCTFail("expected a dispatch") }
        XCTAssertEqual(tasks, [DispatchedTask(conversationId: 12, title: "Menu", goal: "Build the menu page")])
    }

    func testReadsDoneAndErrors() {
        guard case .done(let files) = AgentEvent.parse(line: #"data: {"type": "done", "files_changed": ["a", "b"]}"#)?.kind else {
            return XCTFail("expected done")
        }
        XCTAssertEqual(files, 2)
        guard case .error(let message, let code) = AgentEvent.parse(line: #"data: {"type": "error", "error": "Stopped", "code": "max_turns"}"#)?.kind else {
            return XCTFail("expected an error")
        }
        XCTAssertEqual(message, "Stopped")
        XCTAssertEqual(code, "max_turns")
    }
}

final class ToolLabelTests: XCTestCase {
    func testNamesPagesTheWayTheirOwnerWould() {
        XCTAssertEqual(ToolLabels.label(for: "edit_file", args: ["path": "frontend/src/views/HomeView.vue"]), "Updated your home page")
        XCTAssertEqual(ToolLabels.label(for: "create_file", args: ["path": "src/views/OrderHistoryView.vue"]), "Built your order history page")
    }

    func testNeverShowsAPath() {
        XCTAssertEqual(ToolLabels.label(for: "edit_file", args: ["path": "src/router/index.ts"]), "Updated your app")
        XCTAssertEqual(ToolLabels.label(for: "read_file", args: ["path": "src/components/Card.vue"]), "Looked at your project")
    }

    func testBrowserSteps() {
        XCTAssertEqual(ToolLabels.label(for: "browser", args: ["actions": "navigate"]), "Opened a page in the preview")
        XCTAssertEqual(ToolLabels.label(for: "browser", args: ["actions": "screenshot, read_console"]), "Looked at your app in the preview")
        XCTAssertEqual(ToolLabels.label(for: "browser", args: ["actions": "left_click, type"]), "Tried out your app in the preview")
    }
}

final class DecodingTests: XCTestCase {
    func testReadsDjangoDatesWithMicroseconds() {
        XCTAssertNotNil(ISODate.parse("2026-11-13T19:12:02.123456+00:00"))
        XCTAssertNotNil(ISODate.parse("2026-11-13T19:12:02Z"))
        XCTAssertNil(ISODate.parse("yesterday"))
    }

    func testDecodesAConversationAndAPagedList() throws {
        let json = """
        {"count": 1, "next": null, "previous": null, "results": [
          {"id": 7, "title": "", "kind": "task", "review_status": "active", "is_running": true,
           "brief": "Build the menu page", "queued_prompt": "", "archived_at": null,
           "created_at": "2026-11-13T19:12:02.123456Z", "schedule": {"status": "running", "waits_on": []}}
        ]}
        """
        let list = try JSONDecoder.imagi.decode(ListResponse<Conversation>.self, from: Data(json.utf8))
        XCTAssertEqual(list.items.count, 1)
        XCTAssertEqual(list.items[0].displayTitle, "Build the menu page")
        XCTAssertTrue(list.items[0].running)
        XCTAssertTrue(list.items[0].isThread)
    }

    func testAMessageWithUnexpectedMetadataStillDecodes() throws {
        let json = #"[{"id": 1, "role": "assistant", "content": "Done", "timestamp": "2026-11-13T19:12:02Z", "metadata": {"tool_calls": "oops"}}]"#
        let messages = try JSONDecoder.imagi.decode([ChatMessage].self, from: Data(json.utf8))
        XCTAssertEqual(messages.first?.content, "Done")
        XCTAssertNil(messages.first?.metadata)
    }

    func testAPIErrorPrefersTheServersWords() {
        let error = APIError.from(status: 400, data: Data(#"{"name": ["A project with this name already exists."]}"#.utf8))
        XCTAssertEqual(error.fields["name"], "A project with this name already exists.")
        XCTAssertEqual(error.message, "A project with this name already exists.")
        let busy = APIError.from(status: 409, data: Data(#"{"detail": "agent_busy"}"#.utf8))
        XCTAssertEqual(busy.code, "agent_busy")
        XCTAssertEqual(busy.message, "The coordinator is still working on your last message.")
    }
}

final class StarterDesignTests: XCTestCase {
    func testNothingPickedLeavesTheLookToTheBuild() {
        XCTAssertEqual(StarterDesign.preferences(style: nil, scheme: nil, brandColor: nil, notes: " "), "")
    }

    func testWritesTheLookTheWayTheWebFormDoes() {
        let text = StarterDesign.preferences(style: "minimal", scheme: "midnight", brandColor: nil, notes: "No photos")
        XCTAssertTrue(text.hasPrefix("Style: Minimal ("))
        XCTAssertTrue(text.contains("Colours: Midnight scheme, primary #6EA8FF, accent #7FE0D4, background #0D1220, text #EAF0FF."))
        XCTAssertTrue(text.contains("Theme: dark mode."))
        XCTAssertTrue(text.hasSuffix("Also: No photos"))
    }

    func testABrandColour() {
        XCTAssertEqual(
            StarterDesign.preferences(style: nil, scheme: "custom", brandColor: 0x4F46E5, notes: ""),
            "Colours: build the palette around the brand colour #4F46E5."
        )
    }
}

@MainActor
final class PreviewPathTests: XCTestCase {
    func testHidesThePreviewsPrivatePrefix() {
        XCTAssertEqual(PreviewBrowser.appPath(of: URL(string: "https://preview.example/s/abc123/menu?x=1")), "/menu?x=1")
        XCTAssertEqual(PreviewBrowser.appPath(of: URL(string: "https://preview.example/s/abc123/")), "/")
        XCTAssertEqual(PreviewBrowser.appPath(of: nil), "/")
    }
}
