import CoreText
import SwiftUI
import UIKit

// The Imagi design system (Spotlight) for the phone. Values come from the
// Design System artifact's tokens.json, which mirrors
// frontend/vuejs/src/shared/styles/spotlight.css.

extension UIColor {
    convenience init(hex: UInt32, alpha: CGFloat = 1) {
        self.init(
            red: CGFloat((hex >> 16) & 0xff) / 255,
            green: CGFloat((hex >> 8) & 0xff) / 255,
            blue: CGFloat(hex & 0xff) / 255,
            alpha: alpha
        )
    }
}

extension Color {
    /// A colour that follows light and dark mode.
    static func themed(_ light: UIColor, _ dark: UIColor) -> Color {
        Color(UIColor { $0.userInterfaceStyle == .dark ? dark : light })
    }

    static func themed(_ light: UInt32, _ dark: UInt32) -> Color {
        themed(UIColor(hex: light), UIColor(hex: dark))
    }

    // Stage and surfaces
    static let slBg = themed(0xf8f7f4, 0x0b0c11)
    static let slBgDeep = themed(0xf0eee9, 0x08090d)
    static let slSurface = themed(0xffffff, 0x14161f)
    static let slSurface2 = themed(0xffffff, 0x1a1d28)
    static let slLine = themed(UIColor(hex: 0x14151e, alpha: 0.09), UIColor(white: 1, alpha: 0.08))
    static let slLineStrong = themed(UIColor(hex: 0x14151e, alpha: 0.15), UIColor(white: 1, alpha: 0.14))
    static let slChip = themed(UIColor(hex: 0x14151e, alpha: 0.035), UIColor(white: 1, alpha: 0.04))
    static let slChipHover = themed(UIColor(hex: 0x14151e, alpha: 0.065), UIColor(white: 1, alpha: 0.07))

    // Ink
    static let slText = themed(0x14151c, 0xeef0f6)
    static let slMuted = themed(0x5c6172, 0x9aa0b4)
    static let slFaint = themed(0x8a8fa0, 0x6b7186)
    static let slPlaceholder = themed(0x6b7080, 0xc9cddb)

    // The light
    static let slCoral = themed(0xec4a33, 0xff6b5a)
    static let slAmber = themed(0xee8c10, 0xffb547)
    static let slOnAccent = themed(0x1a0e08, 0x1a0e08)
    static let slGlow = themed(UIColor(red: 1, green: 120 / 255, blue: 80 / 255, alpha: 0.2), UIColor(red: 1, green: 120 / 255, blue: 80 / 255, alpha: 0.22))
    static let slSpotCore = themed(UIColor(red: 1, green: 170 / 255, blue: 110 / 255, alpha: 0.38), UIColor(red: 1, green: 170 / 255, blue: 110 / 255, alpha: 0.3))
    static let slSpotMid = themed(UIColor(red: 1, green: 140 / 255, blue: 90 / 255, alpha: 0.14), UIColor(red: 1, green: 120 / 255, blue: 80 / 255, alpha: 0.12))
    static let slWarmLine = themed(UIColor(red: 236 / 255, green: 120 / 255, blue: 50 / 255, alpha: 0.26), UIColor(red: 1, green: 150 / 255, blue: 100 / 255, alpha: 0.18))
    static let slCool = themed(0x3a5fd0, 0xa9c4ff)

    // Status
    static let slOk = themed(0x139a55, 0x4fd18b)
    static let slBad = themed(0xd7334a, 0xff6b80)
    static let slWait = themed(0xc46f00, 0xffb547)
    static let slWork = themed(0x3a5fd0, 0xa9c4ff)
}

extension ShapeStyle where Self == LinearGradient {
    /// The light: coral to amber.
    static var slLight: LinearGradient {
        LinearGradient(colors: [.slCoral, .slAmber], startPoint: .leading, endPoint: .trailing)
    }
}

// MARK: Type

enum ImagiFonts {
    static let files = [
        "BricolageGrotesque-ExtraBold", "BricolageGrotesque-Bold",
        "InstrumentSans-Regular", "InstrumentSans-Medium",
        "InstrumentSans-SemiBold", "InstrumentSans-Bold",
    ]

    /// Bundled fonts are registered at launch, so there is no Info.plist list to keep in step.
    static func register() {
        for name in files {
            guard let url = Bundle.main.url(forResource: name, withExtension: "ttf") else { continue }
            CTFontManagerRegisterFontsForURL(url as CFURL, .process, nil)
        }
    }
}

extension Font {
    /// Bricolage Grotesque, the display face (headlines, the wordmark).
    static func display(_ size: CGFloat, bold: Bool = false, relativeTo style: Font.TextStyle = .title) -> Font {
        .custom(bold ? "BricolageGrotesque-Bold" : "BricolageGrotesque-ExtraBold", size: size, relativeTo: style)
    }

    /// Instrument Sans, the signed-in app's text face.
    static func app(_ size: CGFloat, _ weight: Font.Weight = .regular, relativeTo style: Font.TextStyle = .body) -> Font {
        let name: String
        switch weight {
        case .medium: name = "InstrumentSans-Medium"
        case .semibold: name = "InstrumentSans-SemiBold"
        case .bold, .heavy, .black: name = "InstrumentSans-Bold"
        default: name = "InstrumentSans-Regular"
        }
        return .custom(name, size: size, relativeTo: style)
    }
}

enum Radius {
    static let tile: CGFloat = 12
    static let callout: CGFloat = 16
    static let card: CGFloat = 18
}

/// One curve everywhere: leave at once, spend the time settling.
extension Animation {
    static let imagi = Animation.timingCurve(0.22, 1, 0.36, 1, duration: 0.2)
    static let imagiEntrance = Animation.timingCurve(0.22, 1, 0.36, 1, duration: 0.7)
}
