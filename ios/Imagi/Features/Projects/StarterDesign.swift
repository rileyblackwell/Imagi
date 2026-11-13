import SwiftUI

/// The create form's "Set the look": a style and a colour scheme, sent to the
/// build as plain text in `design_preferences`. Mirrors the web form's
/// projectBrief.ts so both clients ask for the same looks in the same words.
struct DesignStyle: Identifiable, Hashable {
    let id: String
    let label: String
    let line: String
    let brief: String
    let fonts: String
}

struct ColourScheme: Identifiable, Hashable {
    let id: String
    let label: String
    var dark = false
    let background: UInt32
    let surface: UInt32
    let text: UInt32
    let primary: UInt32
    let accent: UInt32
}

enum StarterDesign {
    static let styles: [DesignStyle] = [
        DesignStyle(id: "professional", label: "Professional", line: "Clear, calm and trustworthy",
                    brief: "clear structure, calm colour, businesslike and trustworthy, softly rounded corners",
                    fonts: "a clean modern sans-serif throughout (such as Inter or Hanken Grotesk)"),
        DesignStyle(id: "minimal", label: "Minimal", line: "Lots of space, very little decoration",
                    brief: "lots of white space, restrained colour, thin rules instead of boxes, nearly square corners",
                    fonts: "a light, neutral sans-serif (such as Instrument Sans or Inter)"),
        DesignStyle(id: "friendly", label: "Friendly", line: "Soft, rounded and welcoming",
                    brief: "soft rounded corners, pill buttons, gentle shadows, centred welcoming headings",
                    fonts: "a rounded sans-serif (such as Nunito or Quicksand)"),
        DesignStyle(id: "bold", label: "Bold", line: "Big type and strong contrast",
                    brief: "big heavy headings, strong contrast, blocks of solid colour, sharp corners",
                    fonts: "a heavy display sans-serif for headings (such as Bricolage Grotesque or Archivo Black) with a plain sans-serif for body text"),
        DesignStyle(id: "elegant", label: "Elegant", line: "Refined, quiet and premium",
                    brief: "refined and understated, generous spacing, hairline borders, square corners, small letter-spaced labels",
                    fonts: "serif headings (such as Fraunces or Playfair Display) with a clean sans-serif for body text"),
        DesignStyle(id: "playful", label: "Playful", line: "Bright shapes and a sense of fun",
                    brief: "bright colour, very rounded shapes, pill buttons, cards in tinted colours, a little fun in the details",
                    fonts: "a friendly rounded display font for headings (such as Fredoka) with a rounded sans-serif for body text (such as Nunito)"),
        DesignStyle(id: "colourful", label: "Colourful", line: "Rich colour from edge to edge",
                    brief: "rich colour, a gradient hero from the primary to the accent colour, pill buttons, confident and lively",
                    fonts: "a bold modern sans-serif for headings (such as Bricolage Grotesque or Plus Jakarta Sans) with a plain sans-serif for body text"),
        DesignStyle(id: "retro", label: "Retro", line: "Thick outlines and a vintage feel",
                    brief: "a vintage feel, thick dark outlines with hard offset shadows on cards and buttons",
                    fonts: "a classic display serif for headings (such as DM Serif Display) with a monospace or typewriter face for body text (such as Space Mono)"),
        DesignStyle(id: "techy", label: "Techy", line: "Sharp, precise and modern",
                    brief: "sharp and precise, a faint grid in the background, small monospace labels, crisp thin borders",
                    fonts: "a geometric sans-serif (such as Sora or Geist) with a monospace face for small labels (such as JetBrains Mono)"),
    ]

    static let schemes: [ColourScheme] = [
        ColourScheme(id: "ocean", label: "Ocean", background: 0xF3F6FA, surface: 0xFFFFFF, text: 0x0F1B33, primary: 0x1E4FD8, accent: 0x38BDF8),
        ColourScheme(id: "forest", label: "Forest", background: 0xF4F1E8, surface: 0xFBFAF5, text: 0x1B2A22, primary: 0x1F5A40, accent: 0x8DBF96),
        ColourScheme(id: "sunset", label: "Sunset", background: 0xFFF6EE, surface: 0xFFFFFF, text: 0x2A1712, primary: 0xE1462F, accent: 0xF5A524),
        ColourScheme(id: "berry", label: "Berry", background: 0xFCF2F7, surface: 0xFFFFFF, text: 0x2B0F1E, primary: 0xA3195B, accent: 0xC084FC),
        ColourScheme(id: "earth", label: "Earth", background: 0xF4EDE4, surface: 0xFBF7F1, text: 0x2E1F16, primary: 0x9A4A2C, accent: 0xC9A66B),
        ColourScheme(id: "mono", label: "Mono", background: 0xF6F6F5, surface: 0xFFFFFF, text: 0x111111, primary: 0x111111, accent: 0xA3A3A3),
        ColourScheme(id: "midnight", label: "Midnight", dark: true, background: 0x0D1220, surface: 0x151C2E, text: 0xEAF0FF, primary: 0x6EA8FF, accent: 0x7FE0D4),
        ColourScheme(id: "ember", label: "Ember", dark: true, background: 0x15110F, surface: 0x201A17, text: 0xF6EEE8, primary: 0xF2A541, accent: 0xE8644A),
    ]

    static func hex(_ value: UInt32) -> String { String(format: "#%06X", value) }

    /// The look as the text the build reads, one line per answer; empty when
    /// nothing was picked, so the build chooses a look itself.
    static func preferences(style: String?, scheme: String?, brandColor: UInt32?, notes: String) -> String {
        var lines: [String] = []
        if let style = styles.first(where: { $0.id == style }) {
            lines.append("Style: \(style.label) (\(style.brief)).")
            lines.append("Fonts: \(style.fonts).")
        }
        if scheme == "custom", let brandColor {
            lines.append("Colours: build the palette around the brand colour \(hex(brandColor)).")
        } else if let scheme = schemes.first(where: { $0.id == scheme }) {
            lines.append("Colours: \(scheme.label) scheme, primary \(hex(scheme.primary)), accent \(hex(scheme.accent)), background \(hex(scheme.background)), text \(hex(scheme.text)).")
            lines.append("Theme: \(scheme.dark ? "dark" : "light") mode.")
        }
        let note = notes.trimmingCharacters(in: .whitespacesAndNewlines)
        if !note.isEmpty { lines.append(lines.isEmpty ? note : "Also: \(note)") }
        return lines.joined(separator: "\n")
    }
}

extension Color {
    init(hex: UInt32) { self.init(UIColor(hex: hex)) }

    /// The colour as #RRGGBB.
    var hexValue: UInt32 {
        var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0, a: CGFloat = 0
        UIColor(self).getRed(&r, green: &g, blue: &b, alpha: &a)
        let clamp = { (v: CGFloat) -> UInt32 in UInt32(max(0, min(255, (v * 255).rounded()))) }
        return (clamp(r) << 16) | (clamp(g) << 8) | clamp(b)
    }
}
