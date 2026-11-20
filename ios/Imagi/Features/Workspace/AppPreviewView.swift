import Observation
import SwiftUI
import WebKit

/// The App tab: the project's app itself, running live, in a plain browser frame.
struct AppPreviewView: View {
    let model: WorkspaceModel
    @State private var browser = PreviewBrowser()

    var body: some View {
        VStack(spacing: 0) {
            addressBar
            ZStack {
                Color.slBgDeep
                if let url = model.previewURL {
                    PreviewWebView(url: url, browser: browser)
                        .opacity(browser.hasLoaded ? 1 : 0)
                    if !browser.hasLoaded {
                        notice
                    }
                } else {
                    notice
                }
            }
            controls
        }
        .background(Color.slBg)
    }

    // MARK: Chrome

    private var addressBar: some View {
        HStack(spacing: 8) {
            Image(systemName: "lock.fill")
                .font(.system(size: 10, weight: .semibold))
                .foregroundStyle(Color.slFaint)
            Text(browser.path)
                .font(.app(13.5, .medium))
                .foregroundStyle(Color.slText)
                .lineLimit(1)
                .truncationMode(.middle)
            Spacer(minLength: 4)
            statusPill
        }
        .padding(.horizontal, 14)
        .frame(height: 36)
        .background(Capsule().fill(Color.slSurface2))
        .overlay(Capsule().strokeBorder(Color.slLine, lineWidth: 1))
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
    }

    private var statusPill: some View {
        let (word, color): (String, Color) = {
            if model.previewError != nil { return ("Stopped", .slBad) }
            if model.previewStarting || model.previewURL == nil { return ("Starting", .slWork) }
            if browser.isLoading { return ("Loading", .slWork) }
            return ("Live", .slOk)
        }()
        return HStack(spacing: 5) {
            Circle().fill(color).frame(width: 6, height: 6)
            Text(word.uppercased())
                .font(.app(10.5, .semibold))
                .tracking(1)
                .foregroundStyle(color)
        }
    }

    private var controls: some View {
        HStack {
            Button { browser.webView?.goBack() } label: { Image(systemName: "chevron.left") }
                .disabled(!browser.canGoBack)
                .accessibilityLabel("Back")
            Spacer()
            Button { browser.webView?.goForward() } label: { Image(systemName: "chevron.right") }
                .disabled(!browser.canGoForward)
                .accessibilityLabel("Forward")
            Spacer()
            Button {
                if model.previewURL == nil || model.previewError != nil {
                    model.startPreview()
                } else {
                    browser.webView?.reload()
                }
            } label: { Image(systemName: "arrow.clockwise") }
                .accessibilityLabel("Reload")
            Spacer()
            Button {
                if let url = model.previewURL { browser.webView?.load(URLRequest(url: url)) }
            } label: { Image(systemName: "house") }
                .disabled(model.previewURL == nil)
                .accessibilityLabel("Home page")
        }
        .font(.system(size: 17, weight: .medium))
        .foregroundStyle(Color.slText)
        .padding(.horizontal, 28)
        .frame(height: 46)
        .background(Color.slBg)
        .overlay(alignment: .top) { Rectangle().fill(Color.slLine).frame(height: 1) }
    }

    // MARK: Notice

    private var notice: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let error = model.previewError {
                Eyebrow("Preview stopped", color: .slBad)
                Text(error)
                    .font(.app(15))
                    .foregroundStyle(Color.slText)
                Button("Start it again") { model.startPreview() }
                    .buttonStyle(LitButtonStyle(fullWidth: false))
            } else {
                HStack(spacing: 8) {
                    WorkingIndicator(size: 7)
                    Eyebrow(model.buildingFirstVersion ? "Building your home page" : "Starting your app", color: .slWork)
                }
                Text(model.buildingFirstVersion
                     ? "Imagi is writing your app's first page. It opens here the moment it's ready."
                     : "Your app's servers are starting. This takes a few seconds the first time.")
                    .font(.app(15))
                    .foregroundStyle(Color.slMuted)
                    .fixedSize(horizontal: false, vertical: true)
                if !model.previewStages.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(model.previewStages, id: \.self) { stage in
                            HStack(spacing: 10) {
                                stageMark(stage.state)
                                Text(stage.label ?? "")
                                    .font(.app(14))
                                    .foregroundStyle(stage.state == "done" ? Color.slMuted : Color.slText)
                            }
                        }
                    }
                    .padding(.top, 4)
                }
            }
        }
        .padding(20)
        .frame(maxWidth: 340, alignment: .leading)
        .imagiCard(padding: 4)
        .padding(24)
    }

    @ViewBuilder
    private func stageMark(_ state: String?) -> some View {
        switch state {
        case "done":
            Image(systemName: "checkmark").font(.system(size: 11, weight: .bold)).foregroundStyle(Color.slOk).frame(width: 16)
        case "running":
            WorkingIndicator(size: 5).frame(width: 16)
        case "failed":
            Image(systemName: "xmark").font(.system(size: 11, weight: .bold)).foregroundStyle(Color.slBad).frame(width: 16)
        default:
            Circle().strokeBorder(Color.slLineStrong, lineWidth: 1.5).frame(width: 9, height: 9).frame(width: 16)
        }
    }
}

/// The preview browser's state, read from its WKWebView.
@Observable
@MainActor
final class PreviewBrowser {
    weak var webView: WKWebView?
    var path = "/"
    var canGoBack = false
    var canGoForward = false
    var isLoading = false
    var hasLoaded = false

    /// The app's own path, without the preview's private /s/<token> prefix.
    nonisolated static func appPath(of url: URL?) -> String {
        guard let url else { return "/" }
        var path = url.path
        if let range = path.range(of: #"^/s/[^/]+"#, options: .regularExpression) {
            path.removeSubrange(range)
        }
        if path.isEmpty { path = "/" }
        if let query = url.query, !query.isEmpty { path += "?" + query }
        return path
    }
}

struct PreviewWebView: UIViewRepresentable {
    let url: URL
    let browser: PreviewBrowser

    func makeCoordinator() -> Coordinator { Coordinator(browser: browser) }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.allowsBackForwardNavigationGestures = true
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.navigationDelegate = context.coordinator
        context.coordinator.observe(webView)
        browser.webView = webView
        webView.load(URLRequest(url: url))
        context.coordinator.loadedURL = url
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        // A restarted preview comes back on a new address.
        if context.coordinator.loadedURL != url {
            context.coordinator.loadedURL = url
            webView.load(URLRequest(url: url))
        }
    }

    @MainActor
    final class Coordinator: NSObject, WKNavigationDelegate {
        let browser: PreviewBrowser
        var loadedURL: URL?
        private var observations: [NSKeyValueObservation] = []

        init(browser: PreviewBrowser) {
            self.browser = browser
        }

        func observe(_ webView: WKWebView) {
            observations = [
                webView.observe(\.url, options: [.initial, .new]) { [weak self] view, _ in
                    MainActor.assumeIsolated { self?.browser.path = PreviewBrowser.appPath(of: view.url) }
                },
                webView.observe(\.canGoBack, options: [.initial, .new]) { [weak self] view, _ in
                    MainActor.assumeIsolated { self?.browser.canGoBack = view.canGoBack }
                },
                webView.observe(\.canGoForward, options: [.initial, .new]) { [weak self] view, _ in
                    MainActor.assumeIsolated { self?.browser.canGoForward = view.canGoForward }
                },
                webView.observe(\.isLoading, options: [.initial, .new]) { [weak self] view, _ in
                    MainActor.assumeIsolated { self?.browser.isLoading = view.isLoading }
                },
            ]
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            browser.hasLoaded = true
        }

        /// Links that leave the app open in Safari rather than inside the preview.
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction) async -> WKNavigationActionPolicy {
            if action.navigationType == .linkActivated,
               let target = action.request.url,
               let host = target.host, host != loadedURL?.host,
               action.targetFrame?.isMainFrame ?? true {
                _ = await UIApplication.shared.open(target)
                return .cancel
            }
            return .allow
        }
    }
}
