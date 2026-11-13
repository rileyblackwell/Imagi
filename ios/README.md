# Imagi for iPhone

A native SwiftUI app for Imagi. It talks to the same Django API as the website
(`https://imagi.up.railway.app/api/v1`, token auth) and covers the build half:

- **Sign in and create an account**, plus **Delete account** (Apple requires
  in-app deletion for any app with sign-up; backed by
  `POST /api/v1/auth/account/delete/`).
- **Projects**: your apps, newest first; long-press to delete.
- **Create app**: the web form's Studio steps on one scrolling page (name,
  What is your app?, How does it work?, Set the look) with Create app pinned at
  the bottom.
- **Workspace**, two full-screen tabs switched at the top:
  - **Chat**: the coordinator on the rail, thread cards that open the thread,
    the questions queue above the composer, and Stop while a run works.
  - **App**: the live preview (preview v2) in a WKWebView, with the app's
    path, a one-word status, and back / forward / reload / home.
  - **Threads** (the stack button, with a count of what is waiting on you):
    every thread grouped Waiting on you, Working, Scheduled, Stopped, Finished;
    each opens its own chat with "Steer this thread…", and a stopped thread
    offers Try again and Discard.

Runs happen on the server, so they keep going when the phone locks or the app
closes; the app only watches them (Server-Sent Events, resumed after a drop).

No purchases are in the app. Imagi is Free-only for now, and selling plans in
an iOS app would have to go through Apple's in-app purchase.

## Layout

```
ios/
  Imagi.xcodeproj         Xcode project (folders are synced: new files are picked up automatically)
  Imagi/
    App/                  entry point and root view
    Core/                 API client, models, event stream parsing, Keychain, session
    Design/               the Spotlight design system for SwiftUI (tokens, type, buttons, status)
    Features/             Auth, Projects (+ create form), Workspace, Account
    Resources/            bundled fonts (OFL) and the privacy manifest
    Assets.xcassets       app icon and accent colour
  ImagiTests/             unit tests (event parsing, labels, decoding, the create form's look text)
```

One package dependency, [MarkdownUI](https://github.com/gonzalezreal/swift-markdown-ui),
renders the agent's Markdown. Xcode fetches it on first open.

## Run it on your Mac

You need Xcode 16 or later (from the Mac App Store).

1. Open `ios/Imagi.xcodeproj` in Xcode. Wait for "Resolving packages" to finish
   in the top bar.
2. Pick an iPhone simulator in the bar at the top (for example "iPhone 16").
3. Press **⌘R**. The simulator starts and opens Imagi on production.

From Terminal instead:

```bash
cd ios
xcodebuild -scheme Imagi -destination 'platform=iOS Simulator,name=iPhone 16' build
xcodebuild -scheme Imagi -destination 'platform=iOS Simulator,name=iPhone 16' test
```

To point the app at a local backend, edit the scheme (Product > Scheme > Edit
Scheme > Run > Arguments) and add the environment variable `IMAGI_SITE_URL`,
for example `http://localhost:8000`.

## Run it on your own iPhone

1. In Xcode, open **Settings > Accounts** and sign in with your Apple ID.
2. Select the **Imagi** project in the left sidebar, then the **Imagi** target,
   then **Signing & Capabilities**. Under **Team**, pick your team.
3. Plug in your iPhone, pick it in the device menu at the top, and press **⌘R**.
   The first time, the iPhone asks you to trust the developer under
   Settings > General > VPN & Device Management, and to turn on Developer Mode
   under Settings > Privacy & Security.

The bundle identifier is `com.rileyblackwell.imagi`. Change it under Signing &
Capabilities if you want a different one; it can't change once the app is on
the App Store.

## Ship it to the App Store

This needs a paid Apple Developer Program membership.

1. In [App Store Connect](https://appstoreconnect.apple.com), choose **Apps > +
   > New App**: platform iOS, name "Imagi", the bundle identifier above, and a
   SKU such as `imagi-ios`.
2. In Xcode, pick **Any iOS Device (arm64)** as the destination, then
   **Product > Archive**. When the Organizer opens, choose **Distribute App >
   App Store Connect > Upload**.
3. The build shows up under **TestFlight** after processing (usually 10 to 30
   minutes). Install it on your phone with the TestFlight app to try it.
4. To submit for review, fill in the App Store listing (description,
   screenshots, support URL, privacy policy URL
   `https://imagi.up.railway.app/privacy`), answer the privacy questions
   (the app collects an email address, a username and the text you type, all
   linked to your account and used only to run the app; no tracking), add the
   build, and give App Review a test account to sign in with.
