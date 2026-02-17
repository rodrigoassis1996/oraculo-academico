# services/google_docs/exceptions.py

class GoogleDocsError(Exception):
    """Base exception for Google Docs module."""
    pass

class AuthenticationError(GoogleDocsError):
    """Raised when authentication fails."""
    pass

class DocumentNotFoundError(GoogleDocsError):
    """Raised when a document is not found."""
    pass

class APIError(GoogleDocsError):
    """Raised when the Google API returns an error."""
    pass

class RateLimitError(APIError):
    """Raised when the API rate limit is exceeded."""
    pass
