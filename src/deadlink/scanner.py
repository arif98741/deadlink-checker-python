import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .models import LinkResult
from .utils import get_status_text

def get_all_links(url: str, timeout: int = 10, auth: tuple = None, headers: dict = None) -> tuple[list[tuple[str, str]], str]:
    """
    Scrape all links and assets from a given webpage.

    Returns:
        Tuple of (list of (absolute URL, type) tuples, base URL)
    """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    if headers:
        default_headers.update(headers)

    try:
        response = requests.get(url, headers=default_headers, timeout=timeout, auth=auth)
        response.raise_for_status()
    except Exception as e:
        raise Exception(f"Failed to fetch {url}: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    assets = set()

    # 1. Find all anchor tags (Links)
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        absolute_url = urljoin(url, href)
        if absolute_url.startswith(('http://', 'https://')):
            assets.add((absolute_url, "Link"))

    # 2. Find all img tags (Images)
    for img in soup.find_all('img', src=True):
        src = img['src']
        absolute_url = urljoin(url, src)
        if absolute_url.startswith(('http://', 'https://')):
            assets.add((absolute_url, "Image"))

    # 3. Find all script tags (Scripts)
    for script in soup.find_all('script', src=True):
        src = script['src']
        absolute_url = urljoin(url, src)
        if absolute_url.startswith(('http://', 'https://')):
            assets.add((absolute_url, "Script"))

    # 4. Find all link tags (Stylesheets)
    for link in soup.find_all('link', href=True):
        rel = link.get('rel', [])
        if 'stylesheet' in rel or 'icon' in rel:
            href = link['href']
            absolute_url = urljoin(url, href)
            if absolute_url.startswith(('http://', 'https://')):
                assets.add((absolute_url, "Styles/Icon"))

    # 5. Find all iframe tags
    for iframe in soup.find_all('iframe', src=True):
        src = iframe['src']
        absolute_url = urljoin(url, src)
        if absolute_url.startswith(('http://', 'https://')):
            assets.add((absolute_url, "Iframe"))

    return list(assets), url

def check_link(url: str, found_on: str, timeout: int = 10, link_type: str = "Link", auth: tuple = None, headers: dict = None) -> LinkResult:
    """
    Check if a link is alive or dead.

    Returns:
        LinkResult with status information
    """
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    if headers:
        default_headers.update(headers)

    start_time = time.time()
    try:
        # Use HEAD request first for efficiency
        response = requests.head(url, headers=default_headers, timeout=timeout, allow_redirects=True, auth=auth)
        
        # Some servers block HEAD, if so, try GET
        if response.status_code in [404, 405, 403, 501]:
            response = requests.get(url, headers=default_headers, timeout=timeout, stream=True, auth=auth)
            
        status_code = response.status_code
        status_text = get_status_text(status_code)
        is_dead = status_code >= 400
        
    except requests.exceptions.RequestException as e:
        status_code = None
        status_text = f"Error: {type(e).__name__}"
        is_dead = True
        
    response_time = round(time.time() - start_time, 2)
    
    return LinkResult(
        url=url,
        status_code=status_code,
        status_text=status_text,
        response_time=response_time,
        found_on=found_on,
        is_dead=is_dead,
        is_external=False, # Will be set by crawler
        link_type=link_type
    )
