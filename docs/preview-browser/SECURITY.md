# Security

The preview runs code an AI agent wrote, from a user's prompt, in that
user's browser and on Imagi's server. The questions are who can reach a
preview, what it can do to the workspace around it, and what it can do to
other previews.

## Reaching a preview

- **Capability URL.** `/s/<token>/` with 32 random bytes
  (`secrets.token_urlsafe(32)`). Only the project's owner gets it, from an
  authenticated API call. A new token is minted whenever the servers start;
  stopping, idling out or restarting deletes the route file, after which the
  edge answers 404.
- **No guessing, no listing.** Unknown tokens and paths outside a session get
  a 404 with no detail. Tokens are validated against `^[A-Za-z0-9_-]{32,64}$`
  before any file lookup, so a token cannot name a path.
- **No leaking.** `Referrer-Policy: same-origin` keeps the token out of
  requests to other sites. Pages carry `X-Robots-Tag: noindex, nofollow`.
- **Only Imagi can frame it.** `Content-Security-Policy: frame-ancestors`
  lists `PREVIEW_PARENT_ORIGINS`; the app's own `X-Frame-Options` is dropped
  so this one rule decides.

## The frame and the workspace

- The iframe is cross-origin from the workspace, so the app cannot read the
  workspace's DOM, storage or Imagi auth token.
- `sandbox="allow-scripts allow-forms allow-same-origin allow-popups
  allow-popups-to-escape-sandbox allow-modals allow-downloads"`: no
  `allow-top-navigation`, so the app cannot navigate the workspace away.
  `allow-same-origin` is safe here only because the origin differs from the
  workspace's; it lets the app use its own storage and cookies.
- **postMessage both ways is origin-checked.** The workspace accepts messages
  only from the preview origin *and* from that iframe's window, then validates
  each message's shape and clips its text (`parseBridgeMessage`). The bridge
  talks only to a parent matching `PREVIEW_PARENT_ORIGINS`, and only after it
  says hello. The commands it accepts are fixed (back, forward, reload,
  navigate to an in-app path, start or cancel the picker).
- Console text from the app reaches an agent as fenced diagnostic data,
  marked never to be followed as instructions (existing app-error routing).

## Shared origin

All previews share one origin (DECISIONS.md, 2). Consequences:

- Previews open in **one person's browser** share `localStorage`,
  `sessionStorage` and cookies. Project A's code could read project B's
  stored token if both are open in the same browser. Both belong to the same
  person, and both are development data, so the exposure is to themselves.
  Different users' browsers never share anything.
- A preview could fetch another session's pages only by knowing its token.
- Cookies are rewritten `SameSite=None; Secure; Partitioned`, so they live in
  a jar keyed to the Imagi workspace and are never sent when the preview is
  visited directly from elsewhere. Cookies with a `Domain` are dropped, so a
  preview cannot plant one on `up.railway.app`.

Moving to a subdomain per preview (custom domain with a wildcard) removes all
of this; the routing already supports it.

## The server

- The edge proxies only to `127.0.0.1` ports named in route files Imagi
  writes (directory mode 0700). Request bodies it buffers for retries are
  capped at 10 MB.
- `X-Forwarded-Proto` is set by the edge, never trusted from the client.
- Server actions are owner-only and fixed (`ACTIONS`); `reset_database` only
  deletes the project's own `*.sqlite3`.
- **Before cutover for everyone:** dev servers run as the container user. Run
  them as an unprivileged user with CPU, memory and file limits, so a hostile
  app cannot read other projects' files or the container's environment. Until
  then, keep `PREVIEW_V2` to trusted accounts.
