"""
Custom content negotiation for streaming responses.
"""

from rest_framework.negotiation import DefaultContentNegotiation

class StreamingContentNegotiation(DefaultContentNegotiation):
    """
    Custom content negotiation class that handles streaming content types.
    This allows text/event-stream to be returned regardless of Accept header.
    """
    def select_renderer(self, request, renderers, format_suffix=None):
        # Check if this is a streaming request (path + sse)
        if request.path.endswith('/chat/') and getattr(request, '_streaming', False):
            # Force streaming content type
            request.accepted_renderer = None
            request.accepted_media_type = 'text/event-stream'
            return None, 'text/event-stream'
        
        # Otherwise use default content negotiation
        return super().select_renderer(request, renderers, format_suffix) 