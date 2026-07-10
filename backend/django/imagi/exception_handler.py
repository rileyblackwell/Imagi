"""
Project-wide DRF exception handling.

DRF's default handler renders APIExceptions (400/401/403/404/...) as JSON but
lets any *other* exception fall through to Django, which — outside DEBUG —
returns an opaque HTML 500 with no JSON body the SPA can parse.

`api_exception_handler` keeps DRF's behavior for APIExceptions and, for
genuinely unexpected errors, logs the full traceback server-side and returns a
safe, generic JSON 500. This lets views stop wrapping every call in a broad
`except Exception` that both fabricates the 500 and leaks `str(exc)` (which can
expose filesystem paths, SQL, etc.) to the client.
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    """Return DRF's response for handled exceptions; a safe 500 otherwise."""
    response = drf_exception_handler(exc, context)
    if response is not None:
        # A recognised APIException (validation, auth, permission, not-found,
        # ...). DRF already produced the correct status and body.
        return response

    # Anything else is an unexpected server-side failure. Log it with the full
    # traceback for debugging, but never surface the raw error to the client.
    view = context.get('view')
    view_name = view.__class__.__name__ if view is not None else 'unknown view'
    logger.exception('Unhandled exception in %s', view_name)

    return Response(
        {'error': 'A server error occurred. Please try again later.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
