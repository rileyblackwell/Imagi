import SwiftUI

/// The create form, laid out for a phone: the app's name as the headline,
/// then three steps on a lit rail, and Create app pinned at the bottom.
struct CreateAppView: View {
    var onCreated: (Project) -> Void

    @Environment(\.dismiss) private var dismiss
    @State private var name = ""
    @State private var description = ""
    @State private var details = ""
    @State private var style: String?
    @State private var scheme: String?
    @State private var brandColor = Color(hex: 0x4F46E5)
    @State private var notes = ""
    @State private var showNotes = false
    @State private var pressed = false
    @State private var serverErrors: [Field: String] = [:]
    @State private var formError: String?
    @State private var working = false
    @FocusState private var focus: Field?

    private static let minLength = 20

    enum Field: Hashable { case name, description, details }

    var body: some View {
        NavigationStack {
            ScrollViewReader { scroller in
                ScrollView {
                    VStack(alignment: .leading, spacing: 0) {
                        nameBlock.id(Field.name)
                        step(1, "What is your app?", hint: "What it does and who it's for.", done: descriptionDone) {
                            promptField(text: $description, field: .description,
                                        placeholder: "A booking app for my dog-walking business, so clients can pick a time and pay ahead.")
                        }
                        .id(Field.description)
                        step(2, "How does it work?", hint: "What people can do in it and what it keeps track of.", done: detailsDone) {
                            promptField(text: $details, field: .details,
                                        placeholder: "Clients sign up, see open walk times, book one and get a reminder. I see the week's bookings.")
                        }
                        .id(Field.details)
                        step(3, "Set the look", hint: "Optional. Imagi picks the look if you skip it.", done: style != nil || scheme != nil, last: true) {
                            lookPicker
                        }
                    }
                    .padding(.horizontal, 16)
                    .padding(.bottom, 24)
                }
                .scrollDismissesKeyboard(.interactively)
                .background(SpotlightBackground())
                .safeAreaInset(edge: .bottom) { footer(scroller) }
            }
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                        .foregroundStyle(Color.slText)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
        }
        .onChange(of: name) { serverErrors[.name] = nil }
        .onChange(of: description) { serverErrors[.description] = nil }
        .onChange(of: details) { serverErrors[.details] = nil }
        .interactiveDismissDisabled(working)
    }

    // MARK: Pieces

    private var nameBlock: some View {
        VStack(alignment: .leading, spacing: 10) {
            Marquee(text: "New app")
            TextField("", text: $name, prompt: Text("Name your app").foregroundStyle(Color.slFaint), axis: .vertical)
                .font(.display(38, relativeTo: .largeTitle))
                .tracking(-1)
                .foregroundStyle(Color.slText)
                .focused($focus, equals: .name)
                .submitLabel(.next)
                .onSubmit { focus = .description }
            Rectangle()
                .fill(nameTrimmed.isEmpty ? AnyShapeStyle(Color.slLineStrong) : AnyShapeStyle(.slLight))
                .frame(height: nameTrimmed.isEmpty ? 1 : 2)
            if let error = errorFor(.name) {
                Text(error).font(.app(13.5)).foregroundStyle(Color.slBad)
            } else {
                Text("The name of your app. You can change it later.")
                    .font(.app(13.5))
                    .foregroundStyle(Color.slMuted)
            }
        }
        .padding(.top, 8)
        .padding(.bottom, 28)
    }

    private func step<Content: View>(_ number: Int, _ title: String, hint: String, done: Bool, last: Bool = false, @ViewBuilder content: () -> Content) -> some View {
        HStack(alignment: .top, spacing: 14) {
            VStack(spacing: 0) {
                ZStack {
                    if done {
                        Circle().fill(.slLight)
                        Image(systemName: "checkmark")
                            .font(.system(size: 13, weight: .bold))
                            .foregroundStyle(Color.slOnAccent)
                    } else {
                        Circle().fill(Color.slBg)
                        Circle().strokeBorder(Color.slLineStrong, lineWidth: 1.5)
                        Text(String(format: "%02d", number))
                            .font(.system(size: 12, weight: .medium, design: .monospaced))
                            .foregroundStyle(Color.slMuted)
                    }
                }
                .frame(width: 34, height: 34)
                if !last {
                    Rectangle()
                        .fill(done ? AnyShapeStyle(LinearGradient(colors: [.slCoral, .slAmber], startPoint: .top, endPoint: .bottom)) : AnyShapeStyle(Color.slLineStrong))
                        .frame(width: 2)
                        .padding(.vertical, 6)
                }
            }
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.display(22, bold: true, relativeTo: .title2))
                    .tracking(-0.3)
                    .foregroundStyle(Color.slText)
                    .padding(.top, 3)
                Text(hint)
                    .font(.app(14.5))
                    .foregroundStyle(Color.slMuted)
                    .padding(.bottom, 10)
                content()
            }
            .padding(.bottom, last ? 0 : 26)
        }
    }

    private func promptField(text: Binding<String>, field: Field, placeholder: String) -> some View {
        let length = text.wrappedValue.trimmingCharacters(in: .whitespacesAndNewlines).count
        let error = errorFor(field)
        return VStack(alignment: .leading, spacing: 8) {
            TextField("", text: text, prompt: Text(placeholder).foregroundStyle(Color.slPlaceholder), axis: .vertical)
                .lineLimit(4...12)
                .font(.app(16))
                .foregroundStyle(Color.slText)
                .focused($focus, equals: field)
                .padding(14)
                .background(RoundedRectangle(cornerRadius: Radius.callout, style: .continuous).fill(Color.slSurface2))
                .overlay(
                    RoundedRectangle(cornerRadius: Radius.callout, style: .continuous)
                        .strokeBorder(error != nil ? AnyShapeStyle(Color.slBad) : (focus == field ? AnyShapeStyle(.slLight) : AnyShapeStyle(Color.slLineStrong)), lineWidth: 1)
                )
                .shadow(color: focus == field ? .slGlow : .clear, radius: 14, y: 4)
            HStack(spacing: 6) {
                if length >= Self.minLength {
                    Image(systemName: "checkmark").font(.system(size: 11, weight: .bold))
                    Text("Enough to start")
                } else if length == 0 {
                    Text("At least \(Self.minLength) characters")
                } else {
                    let left = Self.minLength - length
                    Text("\(left) more character\(left == 1 ? "" : "s")")
                }
            }
            .font(.app(12.5, length >= Self.minLength ? .semibold : .regular))
            .foregroundStyle(length >= Self.minLength ? Color.slOk : Color.slMuted)
            if let error {
                Text(error).font(.app(13.5)).foregroundStyle(Color.slBad)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
    }

    private var lookPicker: some View {
        VStack(alignment: .leading, spacing: 16) {
            Eyebrow("Style")
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(StarterDesign.styles) { option in
                        Button {
                            withAnimation(.imagi) { style = style == option.id ? nil : option.id }
                        } label: {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(option.label)
                                    .font(.app(15, .semibold))
                                    .foregroundStyle(Color.slText)
                                Text(option.line)
                                    .font(.app(12.5))
                                    .foregroundStyle(Color.slMuted)
                                    .lineLimit(2)
                                    .multilineTextAlignment(.leading)
                            }
                            .frame(width: 138, height: 70, alignment: .topLeading)
                            .padding(12)
                            .background(RoundedRectangle(cornerRadius: Radius.tile, style: .continuous).fill(style == option.id ? Color.slChipHover : Color.slSurface))
                            .overlay(
                                RoundedRectangle(cornerRadius: Radius.tile, style: .continuous)
                                    .strokeBorder(style == option.id ? AnyShapeStyle(.slLight) : AnyShapeStyle(Color.slLine), lineWidth: style == option.id ? 1.5 : 1)
                            )
                        }
                        .buttonStyle(.plain)
                        .accessibilityAddTraits(style == option.id ? .isSelected : [])
                    }
                }
                .padding(.vertical, 2)
            }
            Eyebrow("Colours")
            LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 10), count: 3), spacing: 10) {
                ForEach(StarterDesign.schemes) { option in
                    schemeTile(id: option.id, label: option.label, colours: [option.background, option.primary, option.accent])
                }
                customTile
            }
            if showNotes {
                FieldBox(label: "Note") {
                    TextField("", text: $notes, prompt: Text("Anything else about the look").foregroundStyle(Color.slPlaceholder), axis: .vertical)
                        .lineLimit(2...5)
                }
            } else {
                Button("Add a note") { withAnimation(.imagi) { showNotes = true } }
                    .buttonStyle(QuietButtonStyle())
            }
        }
    }

    private func schemeTile(id: String, label: String, colours: [UInt32]) -> some View {
        Button {
            withAnimation(.imagi) { scheme = scheme == id ? nil : id }
        } label: {
            VStack(spacing: 8) {
                HStack(spacing: 0) {
                    ForEach(Array(colours.enumerated()), id: \.offset) { _, colour in
                        Rectangle().fill(Color(hex: colour))
                    }
                }
                .frame(height: 30)
                .clipShape(RoundedRectangle(cornerRadius: 8, style: .continuous))
                Text(label)
                    .font(.app(13, .medium))
                    .foregroundStyle(Color.slText)
            }
            .padding(8)
            .background(RoundedRectangle(cornerRadius: Radius.tile, style: .continuous).fill(Color.slSurface))
            .overlay(
                RoundedRectangle(cornerRadius: Radius.tile, style: .continuous)
                    .strokeBorder(scheme == id ? AnyShapeStyle(.slLight) : AnyShapeStyle(Color.slLine), lineWidth: scheme == id ? 1.5 : 1)
            )
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(scheme == id ? .isSelected : [])
    }

    private var customTile: some View {
        VStack(spacing: 8) {
            ColorPicker("Your colour", selection: Binding(
                get: { brandColor },
                set: { brandColor = $0; scheme = "custom" }
            ), supportsOpacity: false)
            .labelsHidden()
            .frame(height: 30)
            Text("Your colour")
                .font(.app(13, .medium))
                .foregroundStyle(Color.slText)
        }
        .frame(maxWidth: .infinity)
        .padding(8)
        .background(RoundedRectangle(cornerRadius: Radius.tile, style: .continuous).fill(Color.slSurface))
        .overlay(
            RoundedRectangle(cornerRadius: Radius.tile, style: .continuous)
                .strokeBorder(scheme == "custom" ? AnyShapeStyle(.slLight) : AnyShapeStyle(Color.slLine), lineWidth: scheme == "custom" ? 1.5 : 1)
        )
        .onTapGesture { scheme = "custom" }
    }

    private func footer(_ scroller: ScrollViewProxy) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            if let formError {
                ProblemNote(text: formError)
            } else if pressed && !missing.isEmpty {
                ProblemNote(text: "Your app can't be created yet. Check: " + missing.map(label).joined(separator: ", ") + ".")
            }
            Button {
                submit(scroller)
            } label: {
                if working {
                    HStack(spacing: 10) { ProgressView().tint(.slOnAccent); Text("Creating your app") }
                } else {
                    Text("Create app")
                }
            }
            .buttonStyle(LitButtonStyle())
            .disabled(working)
            Text("You can change everything later in the workspace.")
                .font(.app(12.5))
                .foregroundStyle(Color.slFaint)
                .frame(maxWidth: .infinity)
        }
        .padding(.horizontal, 16)
        .padding(.top, 12)
        .padding(.bottom, 6)
        .background(Color.slBg.opacity(0.94).ignoresSafeArea())
        .overlay(alignment: .top) { Rectangle().fill(Color.slLine).frame(height: 1) }
    }

    // MARK: Validation and submit

    private var nameTrimmed: String { name.trimmingCharacters(in: .whitespacesAndNewlines) }
    private var descriptionDone: Bool { description.trimmingCharacters(in: .whitespacesAndNewlines).count >= Self.minLength }
    private var detailsDone: Bool { details.trimmingCharacters(in: .whitespacesAndNewlines).count >= Self.minLength }

    private var missing: [Field] {
        var fields: [Field] = []
        if nameTrimmed.isEmpty { fields.append(.name) }
        if !descriptionDone { fields.append(.description) }
        if !detailsDone { fields.append(.details) }
        return fields
    }

    private func label(_ field: Field) -> String {
        switch field {
        case .name: return "App name"
        case .description: return "What is your app?"
        case .details: return "How does it work?"
        }
    }

    private func errorFor(_ field: Field) -> String? {
        if let server = serverErrors[field] { return server }
        guard pressed, missing.contains(field) else { return nil }
        switch field {
        case .name: return "Give your app a name."
        case .description:
            let length = description.trimmingCharacters(in: .whitespacesAndNewlines).count
            return length == 0
                ? "Say what your app is and who it's for. Imagi uses this to build the first version."
                : "Add a little more (at least \(Self.minLength) characters, \(Self.minLength - length) to go)."
        case .details:
            let length = details.trimmingCharacters(in: .whitespacesAndNewlines).count
            return length == 0
                ? "Say how your app works: what people can do on it and what it keeps track of."
                : "Add a little more (at least \(Self.minLength) characters, \(Self.minLength - length) to go)."
        }
    }

    private func submit(_ scroller: ScrollViewProxy) {
        pressed = true
        formError = nil
        if let first = missing.first {
            withAnimation(.imagi) { scroller.scrollTo(first, anchor: .top) }
            focus = first
            return
        }
        working = true
        let preferences = StarterDesign.preferences(
            style: style, scheme: scheme,
            brandColor: scheme == "custom" ? brandColor.hexValue : nil,
            notes: notes
        )
        Task {
            defer { working = false }
            do {
                let project = try await APIClient.shared.createProject(
                    name: nameTrimmed,
                    description: description.trimmingCharacters(in: .whitespacesAndNewlines),
                    appDetails: details.trimmingCharacters(in: .whitespacesAndNewlines),
                    designPreferences: preferences
                )
                onCreated(project)
            } catch let error as APIError {
                var fields: [Field: String] = [:]
                if let text = error.fields["name"] { fields[.name] = text }
                if let text = error.fields["description"] { fields[.description] = text }
                if let text = error.fields["app_details"] { fields[.details] = text }
                serverErrors = fields
                formError = fields.isEmpty ? error.message : nil
            } catch {
                formError = error.localizedDescription
            }
        }
    }
}
