"""
Server-side payments helpers: report pay-as-you-go usage and check whether a
customer has an active plan. Maintained by Imagi.

These call Imagi's Sell API with the project's server key, which only this
backend holds (environment variable IMAGI_SELL_SERVER_KEY). Never call them
from the browser and never send the key to it: anyone with the key can report
usage for your customers.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid

from .config import IMAGI_API_BASE, IMAGI_PROJECT_ID

TIMEOUT_SECONDS = 10


class PaymentsError(Exception):
    """The payments API refused the request or could not be reached."""


def _base() -> str:
    api_base = os.environ.get('IMAGI_API_BASE') or IMAGI_API_BASE
    project_id = os.environ.get('IMAGI_PROJECT_ID') or IMAGI_PROJECT_ID
    return f"{api_base.rstrip('/')}/api/v1/sell/storefront/{project_id}"


def _request(method: str, path: str, body: dict | None = None) -> dict:
    key = os.environ.get('IMAGI_SELL_SERVER_KEY', '')
    if not key:
        raise PaymentsError(
            'IMAGI_SELL_SERVER_KEY is not set. Imagi sets it when it runs your '
            'app; when hosting elsewhere, copy it from Sell console > Settings.'
        )
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        _base() + path,
        data=data,
        method=method,
        headers={
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read() or b'{}')
    except urllib.error.HTTPError as exc:
        try:
            message = json.loads(exc.read() or b'{}').get('error')
        except ValueError:
            message = None
        raise PaymentsError(message or f'Payments API error ({exc.code})') from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise PaymentsError(f'Payments API unreachable: {exc}') from exc


def report_usage(email: str, quantity: int = 1, idempotency_key: str | None = None,
                 product_id: int | None = None) -> dict:
    """
    Record `quantity` units of usage for the customer with this email on
    their pay-as-you-go plan; Stripe bills it at the end of their month.

    Pass a stable `idempotency_key` (for example the id of the thing that
    used the units) so a retry is never counted twice.
    """
    body = {
        'customer_email': email,
        'quantity': int(quantity),
        'idempotency_key': idempotency_key or uuid.uuid4().hex,
    }
    if product_id is not None:
        body['product_id'] = product_id
    return _request('POST', '/usage/', body)


def active_plans(email: str) -> list:
    """The customer's active plans: [{'product_id', 'name', 'type', 'status', ...}]."""
    query = urllib.parse.urlencode({'email': email})
    return _request('GET', f'/subscriptions/?{query}').get('subscriptions', [])


def has_active_plan(email: str, product_id: int | None = None) -> bool:
    """Whether the customer has an active plan (optionally a specific one)."""
    plans = active_plans(email)
    if product_id is not None:
        plans = [p for p in plans if p.get('product_id') == product_id]
    return bool(plans)
