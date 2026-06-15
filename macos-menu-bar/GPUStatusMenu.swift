import AppKit
import WebKit

private func applicationSupportDirectory() -> String {
    let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
        ?? FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Library/Application Support")
    let url = base.appendingPathComponent("GPU Monitor", isDirectory: true)
    try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
    return url.path
}

private func logsDirectory() -> String {
    let base = FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask).first
        ?? FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Library")
    let url = base.appendingPathComponent("Logs/GPU Monitor", isDirectory: true)
    try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
    return url.path
}

private func resourceRoot() -> String {
    let resources = Bundle.main.resourceURL?.path ?? FileManager.default.currentDirectoryPath
    if FileManager.default.fileExists(atPath: "\(resources)/local-resource-monitor-backend/resource_monitor_backend") {
        return resources
    }
    return FileManager.default.currentDirectoryPath
}

private func firstExecutable(_ candidates: [String]) -> String {
    for candidate in candidates where FileManager.default.isExecutableFile(atPath: candidate) {
        return candidate
    }
    return candidates.first ?? "/usr/bin/false"
}

private let projectRoot = resourceRoot()
private let backendDir = "\(projectRoot)/local-resource-monitor-backend"
private let frontendDir = "\(projectRoot)/gpu-monitor-frontend-inspect"
private let supportDir = applicationSupportDirectory()
private let logDir = logsDirectory()
private let backendPort = 8765
private let frontendPort = 8000
private let appURL = URL(string: "http://127.0.0.1:\(frontendPort)/Resource%20Monitor.live.html?embed=1&v=dashboard3")!
private let browserURL = URL(string: "http://127.0.0.1:\(frontendPort)/Resource%20Monitor.live.html")!
private let gpuGuideURL = Bundle.main.url(forResource: "README", withExtension: "md") ?? URL(fileURLWithPath: "\(projectRoot)/README.md")
private let appLogFile = "\(logDir)/menu-app.log"
private let dbPath = "\(supportDir)/resource_monitor.sqlite3"
private let pythonExecutable = firstExecutable([
    "\(backendDir)/.venv/bin/python",
    "/usr/bin/python3",
    "/opt/homebrew/bin/python3",
    "/usr/local/bin/python3",
])
private let updateCheckInterval: TimeInterval = 6 * 60 * 60

private struct UpdateInfo: Decodable {
    let version: String?
    let tag_name: String?
    let download_url: String?
    let html_url: String?
    let release_url: String?
    let notes: String?

    var resolvedVersion: String? {
        version ?? tag_name
    }

    var resolvedURL: URL? {
        [download_url, html_url, release_url]
            .compactMap { $0 }
            .compactMap { URL(string: $0) }
            .first
    }
}

private func appendAppLog(_ message: String) {
    try? FileManager.default.createDirectory(atPath: logDir, withIntermediateDirectories: true)
    let timestamp = ISO8601DateFormatter().string(from: Date())
    let line = "[\(timestamp)] \(message)\n"
    if !FileManager.default.fileExists(atPath: appLogFile) {
        FileManager.default.createFile(atPath: appLogFile, contents: nil)
    }
    guard let handle = try? FileHandle(forWritingTo: URL(fileURLWithPath: appLogFile)) else { return }
    defer { try? handle.close() }
    _ = try? handle.seekToEnd()
    if let data = line.data(using: .utf8) {
        try? handle.write(contentsOf: data)
    }
}

private func currentAppVersion() -> String {
    Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "0.0.0"
}

private func configuredUpdateFeedURL() -> URL? {
    guard let raw = Bundle.main.object(forInfoDictionaryKey: "GPMUpdateFeedURL") as? String else { return nil }
    let value = raw.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !value.isEmpty, !value.contains("<"), !value.contains("YOUR_") else { return nil }
    return URL(string: value)
}

private func normalizedVersion(_ version: String) -> [Int] {
    let cleaned = version.trimmingCharacters(in: CharacterSet(charactersIn: "vV "))
    var parts = cleaned.split(separator: ".").map { Int($0) ?? 0 }
    while parts.count < 3 { parts.append(0) }
    return parts
}

private func isVersion(_ candidate: String, newerThan current: String) -> Bool {
    let left = normalizedVersion(candidate)
    let right = normalizedVersion(current)
    let count = max(left.count, right.count)
    for index in 0..<count {
        let l = index < left.count ? left[index] : 0
        let r = index < right.count ? right[index] : 0
        if l != r { return l > r }
    }
    return false
}

final class MonitorViewController: NSViewController, WKNavigationDelegate, WKUIDelegate {
    private let webView = WKWebView()
    private let statusView = NSView()
    private let statusLabel = NSTextField(labelWithString: "正在启动 GPU Monitor...")
    private var hasLoaded = false

    override func loadView() {
        view = NSView(frame: NSRect(x: 0, y: 0, width: 460, height: 720))
        webView.translatesAutoresizingMaskIntoConstraints = false
        webView.allowsMagnification = false
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.setValue(false, forKey: "drawsBackground")
        view.addSubview(webView)

        statusView.translatesAutoresizingMaskIntoConstraints = false
        statusView.wantsLayer = true
        statusView.layer?.backgroundColor = NSColor(calibratedRed: 0.047, green: 0.063, blue: 0.083, alpha: 1).cgColor
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        statusLabel.alignment = .center
        statusLabel.lineBreakMode = .byWordWrapping
        statusLabel.maximumNumberOfLines = 0
        statusLabel.textColor = NSColor(calibratedWhite: 0.88, alpha: 1)
        statusLabel.font = NSFont.systemFont(ofSize: 13, weight: .medium)
        statusView.addSubview(statusLabel)
        view.addSubview(statusView)

        NSLayoutConstraint.activate([
            webView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            webView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            webView.topAnchor.constraint(equalTo: view.topAnchor),
            webView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            statusView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            statusView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            statusView.topAnchor.constraint(equalTo: view.topAnchor),
            statusView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            statusLabel.centerXAnchor.constraint(equalTo: statusView.centerXAnchor),
            statusLabel.centerYAnchor.constraint(equalTo: statusView.centerYAnchor),
            statusLabel.leadingAnchor.constraint(greaterThanOrEqualTo: statusView.leadingAnchor, constant: 42),
            statusLabel.trailingAnchor.constraint(lessThanOrEqualTo: statusView.trailingAnchor, constant: -42),
        ])
    }

    override func viewDidAppear() {
        super.viewDidAppear()
        if !hasLoaded {
            waitForFrontendAndLoad()
        } else {
            webView.reload()
        }
    }

    private func waitForFrontendAndLoad(attempt: Int = 1) {
        updateStatus("正在连接本地监控服务...\n第 \(attempt)/40 次尝试")
        appendAppLog("checking frontend attempt=\(attempt)")

        var request = URLRequest(url: appURL)
        request.cachePolicy = .reloadIgnoringLocalCacheData
        request.timeoutInterval = 1.5

        URLSession.shared.dataTask(with: request) { [weak self] _, response, error in
            DispatchQueue.main.async {
                guard let self else { return }
                if let http = response as? HTTPURLResponse, (200..<400).contains(http.statusCode) {
                    appendAppLog("frontend ready status=\(http.statusCode)")
                    self.updateStatus("正在加载监控面板...")
                    self.webView.load(URLRequest(url: appURL, cachePolicy: .reloadIgnoringLocalCacheData))
                    return
                }

                if attempt < 40 {
                    let reason = error?.localizedDescription ?? "HTTP \(String(describing: (response as? HTTPURLResponse)?.statusCode))"
                    appendAppLog("frontend not ready attempt=\(attempt) reason=\(reason)")
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.35) {
                        self.waitForFrontendAndLoad(attempt: attempt + 1)
                    }
                } else {
                    let reason = error?.localizedDescription ?? "服务没有返回可用页面"
                    appendAppLog("frontend failed reason=\(reason)")
                    self.updateStatus("无法加载监控面板\n请确认本地服务已启动\n\(reason)")
                }
            }
        }.resume()
    }

    private func updateStatus(_ text: String) {
        statusLabel.stringValue = text
        statusView.isHidden = false
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        hasLoaded = true
        statusView.isHidden = true
        appendAppLog("webview didFinish")
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        appendAppLog("webview didFail \(error.localizedDescription)")
        updateStatus("监控面板加载失败\n\(error.localizedDescription)")
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        appendAppLog("webview didFailProvisional \(error.localizedDescription)")
        updateStatus("监控面板加载失败\n\(error.localizedDescription)")
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let url = navigationAction.request.url, shouldOpenExternally(url) {
            NSWorkspace.shared.open(url)
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration, for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = navigationAction.request.url {
            NSWorkspace.shared.open(url)
        }
        return nil
    }

    private func shouldOpenExternally(_ url: URL) -> Bool {
        guard let scheme = url.scheme?.lowercased(), scheme == "http" || scheme == "https" else { return false }
        let host = url.host?.lowercased()
        return host != "127.0.0.1" && host != "localhost"
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItem: NSStatusItem!
    private let popover = NSPopover()
    private var eventMonitor: Any?
    private var backendProcess: Process?
    private var frontendProcess: Process?
    private var updateTimer: Timer?
    private var lastNotifiedUpdateVersion: String?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        createLogDirectory()
        appendAppLog("applicationDidFinishLaunching")
        startServices()
        configureStatusItem()
        configurePopover()
        scheduleUpdateChecks()
    }

    func applicationWillTerminate(_ notification: Notification) {
        stopOwnedServices()
        if let eventMonitor {
            NSEvent.removeMonitor(eventMonitor)
        }
        updateTimer?.invalidate()
    }

    private func configureStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        guard let button = statusItem.button else { return }
        if let image = NSImage(systemSymbolName: "gauge.with.dots.needle.67percent", accessibilityDescription: "GPU Monitor") {
            image.isTemplate = true
            button.image = image
        } else {
            button.title = "GPU"
        }
        button.target = self
        button.action = #selector(statusItemClicked(_:))
        button.sendAction(on: [.leftMouseUp, .rightMouseUp])
    }

    private func configurePopover() {
        popover.contentSize = NSSize(width: 460, height: 720)
        popover.behavior = .transient
        popover.contentViewController = MonitorViewController()
        eventMonitor = NSEvent.addGlobalMonitorForEvents(matching: [.leftMouseDown, .rightMouseDown]) { [weak self] _ in
            self?.popover.performClose(nil)
        }
    }

    @objc private func statusItemClicked(_ sender: NSStatusBarButton) {
        guard let event = NSApp.currentEvent else {
            togglePopover(sender)
            return
        }
        if event.type == .rightMouseUp {
            showContextMenu()
        } else {
            togglePopover(sender)
        }
    }

    private func togglePopover(_ sender: NSStatusBarButton) {
        if popover.isShown {
            popover.performClose(sender)
        } else {
            popover.show(relativeTo: sender.bounds, of: sender, preferredEdge: .minY)
            popover.contentViewController?.view.window?.makeKey()
        }
    }

    private func showContextMenu() {
        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Open Dashboard", action: #selector(openDashboard), keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: "GPU Authorization Guide", action: #selector(openGPUAuthorizationGuide), keyEquivalent: ""))
        menu.addItem(NSMenuItem(title: "Check for Updates...", action: #selector(checkForUpdatesFromMenu), keyEquivalent: ""))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit GPU Monitor", action: #selector(quit), keyEquivalent: "q"))
        menu.items.forEach { $0.target = self }
        statusItem.menu = menu
        statusItem.button?.performClick(nil)
        statusItem.menu = nil
    }

    @objc private func openDashboard() {
        NSWorkspace.shared.open(browserURL)
    }

    @objc private func openGPUAuthorizationGuide() {
        NSWorkspace.shared.open(gpuGuideURL)
    }

    @objc private func checkForUpdatesFromMenu() {
        checkForUpdates(silent: false)
    }

    @objc private func quit() {
        NSApp.terminate(nil)
    }

    private func createLogDirectory() {
        try? FileManager.default.createDirectory(atPath: logDir, withIntermediateDirectories: true)
    }

    private func scheduleUpdateChecks() {
        checkForUpdates(silent: true)
        updateTimer = Timer.scheduledTimer(withTimeInterval: updateCheckInterval, repeats: true) { [weak self] _ in
            self?.checkForUpdates(silent: true)
        }
    }

    private func checkForUpdates(silent: Bool) {
        guard let feedURL = configuredUpdateFeedURL() else {
            if !silent {
                showAlert(
                    title: "Update feed is not configured",
                    message: "For public releases, set GPMUpdateFeedURL in Info.plist to a signed update feed or a GitHub release JSON endpoint."
                )
            }
            return
        }

        var request = URLRequest(url: feedURL)
        request.cachePolicy = .reloadIgnoringLocalAndRemoteCacheData
        request.timeoutInterval = 10
        URLSession.shared.dataTask(with: request) { [weak self] data, _, error in
            DispatchQueue.main.async {
                guard let self else { return }
                if let error {
                    appendAppLog("update check failed error=\(error.localizedDescription)")
                    if !silent {
                        self.showAlert(title: "Update check failed", message: error.localizedDescription)
                    }
                    return
                }

                guard let data else {
                    if !silent {
                        self.showAlert(title: "Update check failed", message: "The update feed returned no data.")
                    }
                    return
                }

                do {
                    let info = try JSONDecoder().decode(UpdateInfo.self, from: data)
                    guard let latest = info.resolvedVersion else {
                        if !silent {
                            self.showAlert(title: "Update feed error", message: "The update feed does not include a version.")
                        }
                        return
                    }
                    let current = currentAppVersion()
                    if isVersion(latest, newerThan: current) {
                        if silent && self.lastNotifiedUpdateVersion == latest { return }
                        self.lastNotifiedUpdateVersion = latest
                        self.showUpdateAvailable(version: latest, current: current, url: info.resolvedURL, notes: info.notes)
                    } else if !silent {
                        self.showAlert(title: "GPU Monitor is up to date", message: "Current version: \(current)")
                    }
                } catch {
                    appendAppLog("update decode failed error=\(error.localizedDescription)")
                    if !silent {
                        self.showAlert(title: "Update feed error", message: error.localizedDescription)
                    }
                }
            }
        }.resume()
    }

    private func showAlert(title: String, message: String) {
        NSApp.activate(ignoringOtherApps: true)
        let alert = NSAlert()
        alert.alertStyle = .informational
        alert.messageText = title
        alert.informativeText = message
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }

    private func showUpdateAvailable(version: String, current: String, url: URL?, notes: String?) {
        NSApp.activate(ignoringOtherApps: true)
        let alert = NSAlert()
        alert.alertStyle = .informational
        alert.messageText = "GPU Monitor \(version) is available"
        var details = "Current version: \(current)"
        if let notes, !notes.isEmpty {
            details += "\n\n\(notes)"
        }
        alert.informativeText = details
        alert.addButton(withTitle: url == nil ? "OK" : "Open Download")
        if url != nil {
            alert.addButton(withTitle: "Later")
        }
        let response = alert.runModal()
        if response == .alertFirstButtonReturn, let url {
            NSWorkspace.shared.open(url)
        }
    }

    private func startServices() {
        appendAppLog("startServices backendListening=\(portIsListening(backendPort)) frontendListening=\(portIsListening(frontendPort))")
        if !portIsListening(backendPort) {
            backendProcess = launch(
                executable: pythonExecutable,
                arguments: ["-m", "resource_monitor_backend", "--port", "\(backendPort)"],
                workingDirectory: backendDir,
                logFile: "\(logDir)/menu-backend.log",
                environment: [
                    "RESOURCE_MONITOR_DB_PATH": dbPath,
                    "PYTHONUNBUFFERED": "1",
                ]
            )
        }
        if !portIsListening(frontendPort) {
            frontendProcess = launch(
                executable: pythonExecutable,
                arguments: ["-m", "http.server", "\(frontendPort)", "--bind", "127.0.0.1"],
                workingDirectory: frontendDir,
                logFile: "\(logDir)/menu-frontend.log"
            )
        }
    }

    private func stopOwnedServices() {
        backendProcess?.terminate()
        frontendProcess?.terminate()
    }

    private func portIsListening(_ port: Int) -> Bool {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/sbin/lsof")
        process.arguments = ["-nP", "-iTCP:\(port)", "-sTCP:LISTEN"]
        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = Pipe()
        do {
            try process.run()
            process.waitUntilExit()
            return process.terminationStatus == 0
        } catch {
            return false
        }
    }

    private func launch(
        executable: String,
        arguments: [String],
        workingDirectory: String,
        logFile: String,
        environment: [String: String] = [:]
    ) -> Process? {
        appendAppLog("launch executable=\(executable) args=\(arguments.joined(separator: " ")) cwd=\(workingDirectory)")
        let process = Process()
        process.executableURL = URL(fileURLWithPath: executable)
        process.arguments = arguments
        process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
        process.environment = ProcessInfo.processInfo.environment.merging(environment) { _, new in new }
        let logURL = URL(fileURLWithPath: logFile)
        FileManager.default.createFile(atPath: logFile, contents: nil)
        guard let handle = try? FileHandle(forWritingTo: logURL) else { return nil }
        process.standardOutput = handle
        process.standardError = handle
        do {
            try process.run()
            appendAppLog("launch started pid=\(process.processIdentifier)")
            return process
        } catch {
            appendAppLog("launch failed executable=\(executable) error=\(error.localizedDescription)")
            return nil
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
