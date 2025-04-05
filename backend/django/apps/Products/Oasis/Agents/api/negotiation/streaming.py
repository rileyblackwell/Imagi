"""
Streaming content negotiation for Django REST Framework.

This module provides content negotiation classes that support streaming
responses, which are essential for real-time AI agent communication.
"""

from rest_framework.negotiation import DefaultContentNegotiation


class StreamingContentNegotiation(DefaultContentNegotiation):
    """
    Content negotiation class that supports streaming responses.
    
    This class extends the default content negotiation to better handle
    streaming responses needed for real-time AI generated content.
    """
    
    def select_renderer(self, request, renderers, format_suffix=None):
        """
        Select an appropriate renderer for the request.
        
        For streaming responses, we prioritize renderers that support streaming.
        
        Args:
            request: The request object
            renderers: List of available renderers
            format_suffix: Optional format suffix from the URL
            
        Returns:
            tuple: (renderer, media_type)
        """
        # Get the normal selected renderer
        renderer, media_type = super().select_renderer(
            request, renderers, format_suffix
        )
        
        # Check if this is a streaming request
        is_streaming = getattr(request, 'streaming', False)
        
        if is_streaming:
            # For streaming requests, prefer streaming-capable renderers
            streaming_renderers = [r for r in renderers if getattr(r, 'supports_streaming', False)]
            if streaming_renderers:
                # Use the first streaming-capable renderer
                streaming_renderer = streaming_renderers[0]
                return streaming_renderer, streaming_renderer.media_type
        
        return renderer, media_type 