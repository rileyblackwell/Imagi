import SwiftUI

/// The signed-in home: your apps, newest first, and Create app.
struct ProjectsView: View {
    @State private var projects: [Project] = []
    @State private var loaded = false
    @State private var error: String?
    @State private var path: [Project] = []
    @State private var creating = false
    @State private var showingAccount = false
    @State private var pendingDelete: Project?

    private let api = APIClient.shared

    var body: some View {
        NavigationStack(path: $path) {
            ScrollView {
                VStack(alignment: .leading, spacing: 14) {
                    header
                    if let error {
                        ProblemNote(text: error)
                    }
                    if loaded && projects.isEmpty && error == nil {
                        emptyState
                    }
                    ForEach(projects) { project in
                        NavigationLink(value: project) {
                            ProjectRow(project: project)
                        }
                        .buttonStyle(.plain)
                        .contextMenu {
                            Button(role: .destructive) { pendingDelete = project } label: {
                                Label("Delete app", systemImage: "trash")
                            }
                        }
                    }
                    if !loaded {
                        ProgressView().frame(maxWidth: .infinity).padding(.top, 40)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 110)
            }
            .background(SpotlightBackground())
            .refreshable { await load() }
            .safeAreaInset(edge: .bottom) {
                if !projects.isEmpty {
                    Button { creating = true } label: {
                        Label("Create app", systemImage: "plus")
                    }
                    .buttonStyle(LitButtonStyle())
                    .padding(.horizontal, 16)
                    .padding(.bottom, 8)
                }
            }
            .toolbar {
                ToolbarItem(placement: .principal) { Wordmark(size: 21) }
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showingAccount = true } label: {
                        Image(systemName: "person.crop.circle")
                            .font(.system(size: 19, weight: .regular))
                            .foregroundStyle(Color.slText)
                    }
                    .accessibilityLabel("Account")
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .navigationDestination(for: Project.self) { project in
                WorkspaceView(project: project)
            }
        }
        .task { if !loaded { await load() } }
        .fullScreenCover(isPresented: $creating) {
            CreateAppView { project in
                projects.insert(project, at: 0)
                creating = false
                path = [project]
            }
        }
        .sheet(isPresented: $showingAccount) { AccountView() }
        .confirmationDialog(
            "Delete \(pendingDelete?.name ?? "this app")?",
            isPresented: Binding(get: { pendingDelete != nil }, set: { if !$0 { pendingDelete = nil } }),
            titleVisibility: .visible
        ) {
            Button("Delete app", role: .destructive) {
                if let project = pendingDelete { delete(project) }
            }
        } message: {
            Text("Its code, threads and preview are removed for good.")
        }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Eyebrow("Your apps")
            Text("Projects")
                .font(.display(40, relativeTo: .largeTitle))
                .tracking(-1.2)
                .foregroundStyle(Color.slText)
        }
        .padding(.top, 12)
        .padding(.bottom, 4)
    }

    private var emptyState: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("No apps yet")
                .font(.display(24, bold: true))
                .foregroundStyle(Color.slText)
            Text("Name your app and say what it does. Imagi builds the first version and opens it right here.")
                .font(.app(15.5))
                .lineSpacing(3)
                .foregroundStyle(Color.slMuted)
            Button("Create app") { creating = true }
                .buttonStyle(LitButtonStyle())
                .padding(.top, 4)
        }
        .imagiCard(padding: 22)
        .padding(.top, 8)
    }

    private func load() async {
        do {
            projects = try await api.projects()
                .sorted { ($0.updatedAt ?? .distantPast) > ($1.updatedAt ?? .distantPast) }
            error = nil
        } catch is CancellationError {
            return
        } catch {
            self.error = error.localizedDescription
        }
        loaded = true
    }

    private func delete(_ project: Project) {
        pendingDelete = nil
        withAnimation(.imagi) { projects.removeAll { $0.id == project.id } }
        Task {
            do {
                try await api.deleteProject(project.id)
            } catch {
                self.error = "\(project.name) couldn't be deleted. \(error.localizedDescription)"
                await load()
            }
        }
    }
}

struct ProjectRow: View {
    let project: Project

    var body: some View {
        HStack(alignment: .top, spacing: 14) {
            Text(String(project.name.prefix(1)).uppercased())
                .font(.display(20, bold: true))
                .foregroundStyle(Color.slText)
                .frame(width: 44, height: 44)
                .background(RoundedRectangle(cornerRadius: Radius.tile, style: .continuous).fill(Color.slChip))
                .overlay(RoundedRectangle(cornerRadius: Radius.tile, style: .continuous).strokeBorder(Color.slLineStrong, lineWidth: 1))
            VStack(alignment: .leading, spacing: 5) {
                Text(project.name)
                    .font(.app(17, .semibold, relativeTo: .headline))
                    .foregroundStyle(Color.slText)
                    .lineLimit(1)
                if !project.summary.isEmpty {
                    Text(project.summary)
                        .font(.app(14.5))
                        .foregroundStyle(Color.slMuted)
                        .lineLimit(2)
                }
                if let updated = project.updatedAt, updated > .distantPast {
                    Text("Updated \(updated.imagiRelative)")
                        .font(.app(12.5))
                        .foregroundStyle(Color.slFaint)
                }
            }
            Spacer(minLength: 0)
            Image(systemName: "chevron.right")
                .font(.system(size: 13, weight: .semibold))
                .foregroundStyle(Color.slFaint)
                .padding(.top, 14)
        }
        .imagiCard(padding: 16)
        .contentShape(Rectangle())
    }
}
