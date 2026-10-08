"""
Where this backend's payments come from. Imagi writes this file when payments
are added from the Sell console. Nothing here is secret.

The server key that authenticates usage reports is never written into the
code: Imagi passes it to the app as the IMAGI_SELL_SERVER_KEY environment
variable when it runs the app. If you host the app yourself, copy the key from
Sell console > Settings into that variable.
"""
IMAGI_PROJECT_ID = __IMAGI_PROJECT_ID__
IMAGI_API_BASE = '__IMAGI_API_BASE__'
