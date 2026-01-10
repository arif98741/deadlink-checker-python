import sys
import io
from urllib.parse import urlparse

def setup_windows_encoding():
    """Fix Windows console encoding for Unicode."""
    if sys.platform == 'win32':
        if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and sys.stderr.buffer is not None:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def is_external_url(url: str, base_url: str) -> bool:
    """Check if a URL is external (different domain) compared to the base URL."""
    base_domain = urlparse(base_url).netloc.lower()
    link_domain = urlparse(url).netloc.lower()

    # Remove 'www.' prefix for comparison
    base_domain = base_domain.replace('www.', '')
    link_domain = link_domain.replace('www.', '')

    return base_domain != link_domain

def get_status_text(status_code: int) -> str:
    """Get human-readable status text for HTTP status codes."""
    status_map = {
        200: "200 OK",
        201: "201 Created",
        202: "202 Accepted",
        204: "204 No Content",
        301: "301 Moved Permanently",
        302: "302 Found",
        307: "307 Temporary Redirect",
        308: "308 Permanent Redirect",
        400: "400 Bad Request",
        401: "401 Unauthorized",
        403: "403 Forbidden",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
        408: "408 Request Timeout",
        410: "410 Gone",
        429: "429 Too Many Requests",
        500: "500 Internal Server Error",
        502: "502 Bad Gateway",
        503: "503 Service Unavailable",
        504: "504 Gateway Timeout"
    }
    return status_map.get(status_code, f"{status_code} Unknown")

def normalize_url(url: str) -> str:
    """Normalize URL by removing fragments and trailing slashes."""
    parsed = urlparse(url)
    # Remove fragments
    url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
        url += f"?{parsed.query}"
    # Remove trailing slash for consistency (except for root domain)
    if url.endswith('/') and len(parsed.path) > 1:
        url = url[:-1]
    return url
