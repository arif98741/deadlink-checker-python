import concurrent.futures
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from .models import LinkResult
from .scanner import get_all_links, check_link
from .utils import normalize_url, is_external_url

def should_exclude(url: str, patterns: list[str]) -> bool:
    """Check if a URL matches any of the exclusion patterns."""
    if not patterns:
        return False
    for pattern in patterns:
        try:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        except re.error:
            if pattern.lower() in url.lower():
                return True
    return False

def crawl_website(url: str, max_workers: int = 10, timeout: int = 10, max_depth: int = 1, progress_callback=None, auth: tuple = None, headers: dict = None, exclude_patterns: list[str] = None) -> list[LinkResult]:
    """Crawl a website recursively and check all links found."""
    visited_pages = set()
    checked_links = set()
    all_results = []

    pages_to_crawl = [(url, 0)]

    msg = f"\n🕷️  Crawling website with max depth: {max_depth}"
    if progress_callback: progress_callback(msg + "\n")

    while pages_to_crawl:
        current_url, current_depth = pages_to_crawl.pop(0)
        normalized_current = normalize_url(current_url)

        if normalized_current in visited_pages: continue
        
        # Check if current page is excluded
        if should_exclude(current_url, exclude_patterns):
            msg = f"⏭️  Excluding page: {current_url}\n"
            if progress_callback: progress_callback(msg)
            continue
            
        visited_pages.add(normalized_current)

        msg = f"\n{'='*60}\n📄 Page {len(visited_pages)}: {current_url}\n   Depth: {current_depth}/{max_depth}\n{'='*60}\n"
        if progress_callback: progress_callback(msg)

        try:
            links_with_types, base_url = get_all_links(current_url, timeout, auth=auth, headers=headers)
        except Exception as e:
            msg = f"❌ Error scraping {current_url}: {e}"
            if progress_callback: progress_callback(msg + "\n")
            continue

        new_links = []
        for link, link_type in links_with_types:
            norm_link = normalize_url(link)
            if norm_link not in checked_links:
                if should_exclude(link, exclude_patterns):
                    # We still mark it as "checked" so we don't keep excluding it
                    checked_links.add(norm_link)
                    continue
                new_links.append((link, link_type))

        if not new_links:
            msg = "   No new links and assets to check on this page"
            if progress_callback: progress_callback(msg + "\n")
            continue

        msg = f"📋 Found {len(new_links)} new links and assets to check\n"
        if progress_callback: progress_callback(msg)

        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(check_link, link, current_url, timeout, link_type, auth=auth, headers=headers): link
                for link, link_type in new_links
            }

            completed = 0
            for future in concurrent.futures.as_completed(future_to_url):
                completed += 1
                result = future.result()
                
                # Check externality
                result.is_external = is_external_url(result.url, url)
                
                results.append(result)
                checked_links.add(normalize_url(result.url))

                status_icon = "❌" if result.is_dead else "✅"
                type_icons = {"Link": "🔗", "Image": "🖼️", "Script": "📜", "Stylesheet": "🎨", "Iframe": "🖼️", "Icon": "🔖"}
                link_icon = type_icons.get(result.link_type, "🔗")
                loc_icon = "🌐" if result.is_external else "🏠"
                
                msg = f"[{completed}/{len(new_links)}] {status_icon} {link_icon} {loc_icon} {result.status_text}: {result.url[:70]}{'...' if len(result.url) > 70 else ''}\n"
                if progress_callback: progress_callback(msg)

        all_results.extend(results)

        if current_depth < max_depth:
            for result in results:
                if not result.is_dead and not result.is_external:
                    normalized_link = normalize_url(result.url)
                    if normalized_link not in visited_pages:
                        path = urlparse(result.url).path.lower()
                        skip_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.zip', '.tar', '.gz', '.mp4', '.mp3', '.doc', '.docx', '.xls', '.xlsx', '.css', '.js')
                        if not path.endswith(skip_extensions):
                            pages_to_crawl.append((result.url, current_depth + 1))

    msg = f"\n{'='*60}\n🏁 Crawling complete!\n   Pages crawled: {len(visited_pages)}\n   Total links checked: {len(all_results)}\n{'='*60}\n"
    if progress_callback: progress_callback(msg)
    return all_results

def get_sitemap_urls(sitemap_url: str, timeout: int = 10, auth: tuple = None, headers: dict = None) -> list[str]:
    """Fetch and parse sitemap.xml to get all URLs."""
    default_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    if headers:
        default_headers.update(headers)
        
    response = requests.get(sitemap_url, headers=default_headers, timeout=timeout, auth=auth)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'xml')
    urls = []
    for loc in soup.find_all('loc'):
        url = loc.text.strip()
        if url.startswith(('http://', 'https://')): urls.append(url)
    sitemaps = soup.find_all('sitemap')
    if sitemaps:
        all_urls = []
        for sm in sitemaps:
            sm_url = sm.find('loc').text.strip()
            all_urls.extend(get_sitemap_urls(sm_url, timeout, auth=auth, headers=headers))
        return list(set(all_urls))
    return list(set(urls))

def crawl_sitemap(sitemap_url: str, max_workers: int = 10, timeout: int = 10, progress_callback=None, auth: tuple = None, headers: dict = None, exclude_patterns: list[str] = None) -> list[LinkResult]:
    """Crawl all pages listed in a sitemap and check their assets."""
    msg = f"\n🗺️  Parsing sitemap: {sitemap_url}"
    if progress_callback: progress_callback(msg + "\n")
    try:
        pages_to_check = get_sitemap_urls(sitemap_url, timeout, auth=auth, headers=headers)
    except Exception as e:
        msg = f"❌ Error parsing sitemap: {e}"
        if progress_callback: progress_callback(msg + "\n")
        return []
    msg = f"📋 Found {len(pages_to_check)} pages in sitemap to analyze\n"
    if progress_callback: progress_callback(msg)
    all_results = []
    checked_assets = set()
    for i, page_url in enumerate(pages_to_check, 1):
        if should_exclude(page_url, exclude_patterns):
            msg = f"⏭️  Excluding sitemap page: {page_url}\n"
            if progress_callback: progress_callback(msg)
            continue

        msg = f"\n{'='*60}\n📄 Sitemap Page {i}/{len(pages_to_check)}: {page_url}\n{'='*60}\n"
        if progress_callback: progress_callback(msg)
        try:
            links_with_types, _ = get_all_links(page_url, timeout, auth=auth, headers=headers)
            links_with_types.append((page_url, "Link"))
            new_assets = []
            for asset_url, asset_type in links_with_types:
                norm_asset = normalize_url(asset_url)
                if norm_asset not in checked_assets:
                    if should_exclude(asset_url, exclude_patterns):
                        checked_assets.add(norm_asset)
                        continue
                    new_assets.append((asset_url, asset_type))
            if not new_assets: continue
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(check_link, asset_url, page_url, timeout, asset_type, auth=auth, headers=headers): asset_url
                    for asset_url, asset_type in new_assets
                }
                completed = 0
                for future in concurrent.futures.as_completed(future_to_url):
                    completed += 1
                    result = future.result()
                    # Determine is_external
                    result.is_external = is_external_url(result.url, page_url)
                    all_results.append(result)
                    checked_assets.add(normalize_url(result.url))
                    status_icon = "❌" if result.is_dead else "✅"
                    type_icons = {"Link": "🔗", "Image": "🖼️", "Script": "📜", "Stylesheet": "🎨", "Iframe": "🖼️", "Icon": "🔖"}
                    link_icon = type_icons.get(result.link_type, "🔗")
                    loc_icon = "🌐" if result.is_external else "🏠"
                    msg = f"[{completed}/{len(new_assets)}] {status_icon} {link_icon} {loc_icon} {result.status_text}: {result.url[:70]}{'...' if len(result.url) > 70 else ''}\n"
                    if progress_callback: progress_callback(msg)
        except Exception as e:
            msg = f"❌ Error processing {page_url}: {e}\n"
            if progress_callback: progress_callback(msg)
    return all_results

def check_all_links(url: str, max_workers: int = 10, timeout: int = 10, max_depth: int = 1, progress_callback=None, auth: tuple = None, headers: dict = None, exclude_patterns: list[str] = None) -> list[LinkResult]:
    """Dispatcher for crawling/checking links."""
    if url.endswith('sitemap.xml') or 'sitemap' in url.lower():
        return crawl_sitemap(url, max_workers, timeout, progress_callback, auth=auth, headers=headers, exclude_patterns=exclude_patterns)
    if max_depth > 1:
        return crawl_website(url, max_workers, timeout, max_depth, progress_callback, auth=auth, headers=headers, exclude_patterns=exclude_patterns)
    
    msg = f"\n🔍 Scraping links and assets from: {url}"
    if progress_callback: progress_callback(msg + "\n")
    try:
        links_with_types, base_url = get_all_links(url, timeout, auth=auth, headers=headers)
    except Exception as e:
        msg = f"❌ Error scraping {url}: {e}"
        if progress_callback: progress_callback(msg + "\n")
        return []
    msg = f"📋 Found {len(links_with_types)} links and assets to check\n"
    if progress_callback: progress_callback(msg)
    if not links_with_types: return []
    results = []
    
    # Filter initial list
    filtered_links = []
    for link, ltype in links_with_types:
        if not should_exclude(link, exclude_patterns):
            filtered_links.append((link, ltype))
        else:
             msg = f"⏭️  Excluding: {link}\n"
             if progress_callback: progress_callback(msg)

    if not filtered_links:
        return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(check_link, link, base_url, timeout, link_type, auth=auth, headers=headers): link
            for link, link_type in filtered_links
        }
        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            completed += 1
            result = future.result()
            result.is_external = is_external_url(result.url, url)
            results.append(result)
            status_icon = "❌" if result.is_dead else "✅"
            type_icons = {"Link": "🔗", "Image": "🖼️", "Script": "📜", "Stylesheet": "🎨", "Iframe": "🖼️", "Icon": "🔖"}
            link_icon = type_icons.get(result.link_type, "🔗")
            loc_icon = "🌐" if result.is_external else "🏠"
            msg = f"[{completed}/{len(filtered_links)}] {status_icon} {link_icon} {loc_icon} {result.status_text}: {result.url[:70]}{'...' if len(result.url) > 70 else ''}\n"
            if progress_callback: progress_callback(msg)
            if hasattr(progress_callback, '__self__'):
                try:
                    progress_callback.__self__.progress_queue.put(('progress', completed / len(filtered_links)))
                except: pass
    return results
