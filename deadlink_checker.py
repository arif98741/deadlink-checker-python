#!/usr/bin/env python3
"""
Dead Link Checker - Scrapes a website for all links and checks their status.
"""

import sys
import io

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
from dataclasses import dataclass
from typing import Optional
import time
import argparse
from collections import defaultdict


@dataclass
class LinkResult:
    """Stores the result of checking a link."""
    url: str
    status_code: Optional[int]
    status_text: str
    response_time: Optional[float]
    found_on: str
    is_dead: bool
    is_external: bool


def is_external_url(url: str, base_url: str) -> bool:
    """Check if a URL is external (different domain) compared to the base URL."""
    base_domain = urlparse(base_url).netloc.lower()
    link_domain = urlparse(url).netloc.lower()

    # Remove 'www.' prefix for comparison
    base_domain = base_domain.replace('www.', '')
    link_domain = link_domain.replace('www.', '')

    return base_domain != link_domain


def get_all_links(url: str, timeout: int = 10) -> tuple[list[str], str]:
    """
    Scrape all links from a given webpage.

    Returns:
        Tuple of (list of absolute URLs, base URL)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()

    # Find all anchor tags with href
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        # Convert relative URLs to absolute
        absolute_url = urljoin(url, href)
        # Only include http/https links
        if absolute_url.startswith(('http://', 'https://')):
            links.add(absolute_url)

    return list(links), url


def check_link(url: str, found_on: str, timeout: int = 10) -> LinkResult:
    """
    Check if a link is alive or dead.

    Returns:
        LinkResult with status information
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    start_time = time.time()
    is_external = is_external_url(url, found_on)

    try:
        # Use HEAD request first (faster), fall back to GET if needed
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)

        # Some servers don't support HEAD, try GET
        if response.status_code == 405:
            response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)

        response_time = time.time() - start_time
        status_code = response.status_code

        # Determine if the link is dead
        is_dead = status_code >= 400

        status_text = get_status_text(status_code)

        return LinkResult(
            url=url,
            status_code=status_code,
            status_text=status_text,
            response_time=round(response_time, 2),
            found_on=found_on,
            is_dead=is_dead,
            is_external=is_external
        )

    except requests.exceptions.Timeout:
        return LinkResult(
            url=url,
            status_code=None,
            status_text="Timeout",
            response_time=None,
            found_on=found_on,
            is_dead=True,
            is_external=is_external
        )
    except requests.exceptions.ConnectionError:
        return LinkResult(
            url=url,
            status_code=None,
            status_text="Connection Error",
            response_time=None,
            found_on=found_on,
            is_dead=True,
            is_external=is_external
        )
    except requests.exceptions.SSLError:
        return LinkResult(
            url=url,
            status_code=None,
            status_text="SSL Error",
            response_time=None,
            found_on=found_on,
            is_dead=True,
            is_external=is_external
        )
    except Exception as e:
        return LinkResult(
            url=url,
            status_code=None,
            status_text=f"Error: {str(e)[:50]}",
            response_time=None,
            found_on=found_on,
            is_dead=True,
            is_external=is_external
        )


def get_status_text(status_code: int) -> str:
    """Get human-readable status text for HTTP status codes."""
    status_texts = {
        200: "OK",
        201: "Created",
        301: "Moved Permanently",
        302: "Found (Redirect)",
        304: "Not Modified",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        408: "Request Timeout",
        410: "Gone",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
    }
    return status_texts.get(status_code, f"HTTP {status_code}")


def normalize_url(url: str) -> str:
    """Normalize URL by removing fragments and trailing slashes."""
    parsed = urlparse(url)
    # Remove fragment and normalize
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    # Remove trailing slash for consistency (except for root)
    if normalized.endswith('/') and parsed.path != '/':
        normalized = normalized[:-1]
    return normalized


def crawl_website(url: str, max_workers: int = 10, timeout: int = 10, max_depth: int = 1) -> list[LinkResult]:
    """
    Crawl a website recursively and check all links found.

    Args:
        url: The starting URL to crawl
        max_workers: Number of concurrent threads for checking links
        timeout: Timeout in seconds for each request
        max_depth: Maximum depth to crawl (1 = homepage only, 2 = homepage + linked pages, etc.)

    Returns:
        List of LinkResult objects
    """
    base_domain = urlparse(url).netloc.lower().replace('www.', '')

    # Track visited pages and all found links
    visited_pages = set()
    checked_links = set()
    all_results = []

    # Queue of pages to crawl: (url, depth)
    pages_to_crawl = [(url, 0)]

    print(f"\n🕷️  Crawling website with max depth: {max_depth}", flush=True)

    while pages_to_crawl:
        current_url, current_depth = pages_to_crawl.pop(0)
        normalized_current = normalize_url(current_url)

        if normalized_current in visited_pages:
            continue

        visited_pages.add(normalized_current)

        print(f"\n{'='*60}", flush=True)
        print(f"📄 Page {len(visited_pages)}: {current_url}", flush=True)
        print(f"   Depth: {current_depth}/{max_depth}", flush=True)
        print(f"{'='*60}", flush=True)

        # Get all links from this page
        try:
            links, base_url = get_all_links(current_url, timeout)
        except Exception as e:
            print(f"❌ Error scraping {current_url}: {e}", flush=True)
            continue

        # Filter out already checked links
        new_links = [link for link in links if normalize_url(link) not in checked_links]

        if not new_links:
            print(f"   No new links to check on this page", flush=True)
            continue

        print(f"📋 Found {len(new_links)} new links to check\n", flush=True)

        # Check all new links
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(check_link, link, current_url, timeout): link
                for link in new_links
            }

            completed = 0
            for future in concurrent.futures.as_completed(future_to_url):
                completed += 1
                result = future.result()
                results.append(result)
                checked_links.add(normalize_url(result.url))

                # Progress indicator
                status_icon = "❌" if result.is_dead else "✅"
                link_type = "🌐" if result.is_external else "🏠"
                print(f"[{completed}/{len(new_links)}] {status_icon} {link_type} {result.status_text}: {result.url[:70]}{'...' if len(result.url) > 70 else ''}", flush=True)

        all_results.extend(results)

        # If we haven't reached max depth, add internal working links to crawl queue
        if current_depth < max_depth:
            for result in results:
                if not result.is_dead and not result.is_external:
                    normalized_link = normalize_url(result.url)
                    if normalized_link not in visited_pages:
                        # Check if it's an HTML page (not a file like .pdf, .jpg, etc.)
                        path = urlparse(result.url).path.lower()
                        skip_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg',
                                          '.zip', '.tar', '.gz', '.mp4', '.mp3', '.doc',
                                          '.docx', '.xls', '.xlsx', '.css', '.js')
                        if not path.endswith(skip_extensions):
                            pages_to_crawl.append((result.url, current_depth + 1))

    print(f"\n{'='*60}", flush=True)
    print(f"🏁 Crawling complete!", flush=True)
    print(f"   Pages crawled: {len(visited_pages)}", flush=True)
    print(f"   Total links checked: {len(all_results)}", flush=True)
    print(f"{'='*60}", flush=True)

    return all_results


def check_all_links(url: str, max_workers: int = 10, timeout: int = 10, max_depth: int = 1) -> list[LinkResult]:
    """
    Scrape a webpage and check all links found.

    Args:
        url: The webpage URL to scrape
        max_workers: Number of concurrent threads for checking links
        timeout: Timeout in seconds for each request
        max_depth: Maximum depth to crawl

    Returns:
        List of LinkResult objects
    """
    if max_depth > 1:
        return crawl_website(url, max_workers, timeout, max_depth)

    print(f"\n🔍 Scraping links from: {url}", flush=True)

    try:
        links, base_url = get_all_links(url, timeout)
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}", flush=True)
        return []

    print(f"📋 Found {len(links)} links to check\n", flush=True)

    if not links:
        return []

    results = []

    # Use ThreadPoolExecutor for concurrent link checking
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(check_link, link, base_url, timeout): link
            for link in links
        }

        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            completed += 1
            result = future.result()
            results.append(result)

            # Progress indicator
            status_icon = "❌" if result.is_dead else "✅"
            link_type = "🌐" if result.is_external else "🏠"
            print(f"[{completed}/{len(links)}] {status_icon} {link_type} {result.status_text}: {result.url[:70]}{'...' if len(result.url) > 70 else ''}", flush=True)

    return results


def generate_report(results: list[LinkResult]) -> str:
    """Generate a formatted report of all link check results."""

    if not results:
        return "No links were found to check."

    # Separate dead and alive links
    dead_links = [r for r in results if r.is_dead]
    alive_links = [r for r in results if not r.is_dead]

    # Separate internal and external links
    internal_links = [r for r in results if not r.is_external]
    external_links = [r for r in results if r.is_external]

    # Dead links by type
    dead_internal = [r for r in dead_links if not r.is_external]
    dead_external = [r for r in dead_links if r.is_external]

    # Count unique pages crawled
    pages_crawled = set(r.found_on for r in results)

    # Group by status
    by_status = defaultdict(list)
    for r in results:
        by_status[r.status_text].append(r)

    report = []
    report.append("=" * 80)
    report.append("                        DEAD LINK CHECKER REPORT")
    report.append("=" * 80)
    report.append("")

    # Summary
    report.append("📊 SUMMARY")
    report.append("-" * 40)
    report.append(f"  Pages crawled:       {len(pages_crawled)}")
    report.append(f"  Total links checked: {len(results)}")
    report.append(f"  ✅ Working links:    {len(alive_links)}")
    report.append(f"  ❌ Dead links:       {len(dead_links)}")
    report.append(f"  Success rate:        {len(alive_links)/len(results)*100:.1f}%")
    report.append("")

    # Internal/External breakdown
    report.append("🔗 LINK TYPE BREAKDOWN")
    report.append("-" * 40)
    report.append(f"  🏠 Internal links:   {len(internal_links)}")
    report.append(f"  🌐 External links:   {len(external_links)}")
    report.append("")

    # Status breakdown
    report.append("📈 STATUS BREAKDOWN")
    report.append("-" * 40)
    for status, links in sorted(by_status.items(), key=lambda x: -len(x[1])):
        report.append(f"  {status}: {len(links)}")
    report.append("")

    # Dead internal links
    if dead_internal:
        report.append("❌ DEAD INTERNAL LINKS (Need Attention)")
        report.append("-" * 40)
        for i, link in enumerate(dead_internal, 1):
            report.append(f"  {i}. {link.url}")
            report.append(f"     Status: {link.status_text}")
            report.append(f"     Found on: {link.found_on}")
            report.append("")

    # Dead external links
    if dead_external:
        report.append("❌ DEAD EXTERNAL LINKS")
        report.append("-" * 40)
        for i, link in enumerate(dead_external, 1):
            report.append(f"  {i}. {link.url}")
            report.append(f"     Status: {link.status_text}")
            report.append(f"     Found on: {link.found_on}")
            report.append("")

    # Working internal links
    working_internal = [r for r in alive_links if not r.is_external]
    if working_internal:
        report.append("✅ WORKING INTERNAL LINKS")
        report.append("-" * 40)
        for i, link in enumerate(working_internal, 1):
            time_str = f" ({link.response_time}s)" if link.response_time else ""
            report.append(f"  {i}. [{link.status_code}] {link.url}{time_str}")
        report.append("")

    # Working external links
    working_external = [r for r in alive_links if r.is_external]
    if working_external:
        report.append("✅ WORKING EXTERNAL LINKS")
        report.append("-" * 40)
        for i, link in enumerate(working_external, 1):
            time_str = f" ({link.response_time}s)" if link.response_time else ""
            report.append(f"  {i}. [{link.status_code}] {link.url}{time_str}")

    report.append("")
    report.append("=" * 80)
    report.append("                           END OF REPORT")
    report.append("=" * 80)

    return "\n".join(report)


def get_report_filename(target_url: str, extension: str = "txt") -> str:
    """Generate a meaningful filename with domain and datetime."""
    from datetime import datetime
    import os
    import re

    # Extract domain from URL
    domain = urlparse(target_url).netloc.lower()
    domain = domain.replace('www.', '')
    # Clean domain for filename (replace dots and special chars)
    domain_clean = re.sub(r'[^\w\-]', '_', domain)

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create reports directory if it doesn't exist
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # Generate filename
    filename = f"{domain_clean}_{timestamp}.{extension}"
    filepath = os.path.join(reports_dir, filename)

    return filepath


def save_report(report: str, filename: str = "link_report.txt"):
    """Save the report to a file."""
    import os
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 Report saved to: {filename}", flush=True)


def generate_pdf_report(results: list[LinkResult], filename: str, target_url: str):
    """Generate a professional PDF report with tabular format."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        PageBreak, HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus.tableofcontents import TableOfContents
    from datetime import datetime

    if not results:
        print("No results to generate PDF report.", flush=True)
        return

    # Calculate statistics
    dead_links = [r for r in results if r.is_dead]
    alive_links = [r for r in results if not r.is_dead]
    internal_links = [r for r in results if not r.is_external]
    external_links = [r for r in results if r.is_external]
    dead_internal = [r for r in dead_links if not r.is_external]
    dead_external = [r for r in dead_links if r.is_external]
    pages_crawled = set(r.found_on for r in results)
    success_rate = len(alive_links) / len(results) * 100

    # Color scheme
    PRIMARY_COLOR = colors.HexColor('#1a5276')
    SECONDARY_COLOR = colors.HexColor('#2980b9')
    SUCCESS_COLOR = colors.HexColor('#27ae60')
    DANGER_COLOR = colors.HexColor('#c0392b')
    WARNING_COLOR = colors.HexColor('#f39c12')
    LIGHT_BG = colors.HexColor('#f8f9fa')
    DARK_TEXT = colors.HexColor('#2c3e50')
    LIGHT_TEXT = colors.HexColor('#7f8c8d')

    # Page setup with header/footer
    def add_page_number(canvas, doc):
        canvas.saveState()
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(LIGHT_TEXT)
        page_num = canvas.getPageNumber()
        footer_text = f"Page {page_num}"
        canvas.drawRightString(landscape(A4)[0] - 40, 25, footer_text)
        canvas.drawString(40, 25, f"Dead Link Checker Report - {urlparse(target_url).netloc}")
        # Header line
        canvas.setStrokeColor(PRIMARY_COLOR)
        canvas.setLineWidth(2)
        canvas.line(40, landscape(A4)[1] - 35, landscape(A4)[0] - 40, landscape(A4)[1] - 35)
        # Footer line
        canvas.setLineWidth(0.5)
        canvas.line(40, 40, landscape(A4)[0] - 40, 40)
        canvas.restoreState()

    # Create PDF document
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=50
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        alignment=TA_CENTER,
        spaceAfter=5,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=5,
        textColor=LIGHT_TEXT
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=25,
        spaceAfter=12,
        textColor=PRIMARY_COLOR,
        fontName='Helvetica-Bold',
        borderPadding=(0, 0, 5, 0)
    )

    subsection_style = ParagraphStyle(
        'SubsectionHeader',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=8,
        textColor=SECONDARY_COLOR,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=DARK_TEXT,
        spaceAfter=8
    )

    # ==================== TITLE SECTION ====================
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("DEAD LINK CHECKER", title_style))
    elements.append(Paragraph("Website Analysis Report", subtitle_style))
    elements.append(Spacer(1, 20))

    # Target info box
    target_domain = urlparse(target_url).netloc
    report_date = datetime.now().strftime('%B %d, %Y at %H:%M:%S')

    info_data = [
        ["Target Website", target_domain],
        ["Full URL", target_url[:70] + "..." if len(target_url) > 70 else target_url],
        ["Report Generated", report_date],
        ["Analysis Depth", f"{len(pages_crawled)} page(s) crawled"]
    ]

    info_table = Table(info_data, colWidths=[2*inch, 5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('BACKGROUND', (1, 0), (1, -1), LIGHT_BG),
        ('TEXTCOLOR', (1, 0), (1, -1), DARK_TEXT),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 30))

    # ==================== EXECUTIVE SUMMARY ====================
    elements.append(Paragraph("Executive Summary", section_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=15))

    # Status indicator based on success rate
    if success_rate >= 95:
        status_color = SUCCESS_COLOR
        status_text = "EXCELLENT"
        status_desc = "Your website has very few broken links."
    elif success_rate >= 80:
        status_color = WARNING_COLOR
        status_text = "NEEDS ATTENTION"
        status_desc = "Some broken links were found that should be fixed."
    else:
        status_color = DANGER_COLOR
        status_text = "CRITICAL"
        status_desc = "Multiple broken links detected. Immediate action recommended."

    # Summary cards in a row
    summary_cards = [
        [
            Paragraph(f"<font size='24'><b>{len(results)}</b></font>", ParagraphStyle('card', alignment=TA_CENTER, textColor=PRIMARY_COLOR)),
            Paragraph(f"<font size='24'><b>{len(alive_links)}</b></font>", ParagraphStyle('card', alignment=TA_CENTER, textColor=SUCCESS_COLOR)),
            Paragraph(f"<font size='24'><b>{len(dead_links)}</b></font>", ParagraphStyle('card', alignment=TA_CENTER, textColor=DANGER_COLOR)),
            Paragraph(f"<font size='24'><b>{success_rate:.1f}%</b></font>", ParagraphStyle('card', alignment=TA_CENTER, textColor=status_color)),
        ],
        [
            Paragraph("<font size='9'>Total Links</font>", ParagraphStyle('cardlabel', alignment=TA_CENTER, textColor=LIGHT_TEXT)),
            Paragraph("<font size='9'>Working</font>", ParagraphStyle('cardlabel', alignment=TA_CENTER, textColor=LIGHT_TEXT)),
            Paragraph("<font size='9'>Broken</font>", ParagraphStyle('cardlabel', alignment=TA_CENTER, textColor=LIGHT_TEXT)),
            Paragraph("<font size='9'>Success Rate</font>", ParagraphStyle('cardlabel', alignment=TA_CENTER, textColor=LIGHT_TEXT)),
        ]
    ]

    cards_table = Table(summary_cards, colWidths=[2.2*inch, 2.2*inch, 2.2*inch, 2.2*inch])
    cards_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (0, -1), 1, colors.HexColor('#dee2e6')),
        ('BOX', (1, 0), (1, -1), 1, colors.HexColor('#dee2e6')),
        ('BOX', (2, 0), (2, -1), 1, colors.HexColor('#dee2e6')),
        ('BOX', (3, 0), (3, -1), 1, colors.HexColor('#dee2e6')),
    ]))
    elements.append(cards_table)
    elements.append(Spacer(1, 20))

    # Status badge
    status_data = [[
        Paragraph(f"<font size='11'><b>Overall Status: </b></font>", ParagraphStyle('status', textColor=DARK_TEXT)),
        Paragraph(f"<font size='11'><b>{status_text}</b></font>", ParagraphStyle('status', textColor=colors.white)),
        Paragraph(f"<font size='10'>{status_desc}</font>", ParagraphStyle('status', textColor=DARK_TEXT)),
    ]]
    status_table = Table(status_data, colWidths=[1.5*inch, 1.5*inch, 5.5*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (1, 0), status_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (1, 0), (1, 0), 10),
        ('RIGHTPADDING', (1, 0), (1, 0), 10),
    ]))
    elements.append(status_table)
    elements.append(Spacer(1, 20))

    # ==================== DETAILED BREAKDOWN ====================
    elements.append(Paragraph("Detailed Breakdown", section_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY_COLOR, spaceAfter=15))

    breakdown_data = [
        ["Category", "Count", "Percentage", "Status"],
        ["Internal Links", str(len(internal_links)), f"{len(internal_links)/len(results)*100:.1f}%", "—"],
        ["External Links", str(len(external_links)), f"{len(external_links)/len(results)*100:.1f}%", "—"],
        ["Working Links", str(len(alive_links)), f"{len(alive_links)/len(results)*100:.1f}%", "OK"],
        ["Broken Links", str(len(dead_links)), f"{len(dead_links)/len(results)*100:.1f}%", "ISSUE" if dead_links else "OK"],
        ["Dead Internal", str(len(dead_internal)), f"{len(dead_internal)/len(results)*100:.1f}%" if results else "0%", "CRITICAL" if dead_internal else "OK"],
        ["Dead External", str(len(dead_external)), f"{len(dead_external)/len(results)*100:.1f}%" if results else "0%", "WARNING" if dead_external else "OK"],
    ]

    breakdown_table = Table(breakdown_data, colWidths=[2.5*inch, 1.2*inch, 1.5*inch, 1.2*inch])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), LIGHT_BG),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        # Color code the status column
        ('TEXTCOLOR', (3, 3), (3, 3), SUCCESS_COLOR),
        ('TEXTCOLOR', (3, 5), (3, 5), DANGER_COLOR if dead_internal else SUCCESS_COLOR),
        ('TEXTCOLOR', (3, 6), (3, 6), WARNING_COLOR if dead_external else SUCCESS_COLOR),
        ('FONTNAME', (3, 1), (3, -1), 'Helvetica-Bold'),
    ]))
    elements.append(breakdown_table)

    # ==================== DEAD LINKS SECTION ====================
    if dead_links:
        elements.append(PageBreak())
        elements.append(Paragraph("Broken Links - Action Required", section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=DANGER_COLOR, spaceAfter=15))

        elements.append(Paragraph(
            f"<font color='#{DANGER_COLOR.hexval()[2:]}'><b>{len(dead_links)} broken link(s)</b></font> were detected during the scan. "
            "These links should be reviewed and fixed to improve user experience and SEO.",
            body_style
        ))
        elements.append(Spacer(1, 10))

        # Dead Internal Links
        if dead_internal:
            elements.append(Paragraph(f"Internal Broken Links ({len(dead_internal)})", subsection_style))

            dead_int_data = [["#", "URL", "Status", "Found On Page"]]
            for i, link in enumerate(dead_internal, 1):
                url_display = link.url[:55] + "..." if len(link.url) > 55 else link.url
                found_on = link.found_on[:45] + "..." if len(link.found_on) > 45 else link.found_on
                dead_int_data.append([str(i), url_display, link.status_text, found_on])

            dead_int_table = Table(dead_int_data, colWidths=[0.4*inch, 3.8*inch, 1.3*inch, 3*inch])
            dead_int_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), DANGER_COLOR),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fdf2f2')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fdf2f2'), colors.HexColor('#fef9f9')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f5c6cb')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(dead_int_table)
            elements.append(Spacer(1, 15))

        # Dead External Links
        if dead_external:
            elements.append(Paragraph(f"External Broken Links ({len(dead_external)})", subsection_style))
            elements.append(Paragraph(
                "<i>Note: Some external sites may block automated requests. Verify these manually.</i>",
                ParagraphStyle('note', fontSize=8, textColor=LIGHT_TEXT, spaceAfter=8)
            ))

            dead_ext_data = [["#", "URL", "Status", "Found On Page"]]
            for i, link in enumerate(dead_external, 1):
                url_display = link.url[:55] + "..." if len(link.url) > 55 else link.url
                found_on = link.found_on[:45] + "..." if len(link.found_on) > 45 else link.found_on
                dead_ext_data.append([str(i), url_display, link.status_text, found_on])

            dead_ext_table = Table(dead_ext_data, colWidths=[0.4*inch, 3.8*inch, 1.3*inch, 3*inch])
            dead_ext_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), WARNING_COLOR),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef9e7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fef9e7'), colors.HexColor('#fffdf5')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f9e79f')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(dead_ext_table)

    # ==================== WORKING LINKS SECTION ====================
    if alive_links:
        elements.append(PageBreak())
        elements.append(Paragraph("Working Links", section_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=SUCCESS_COLOR, spaceAfter=15))

        elements.append(Paragraph(
            f"<font color='#{SUCCESS_COLOR.hexval()[2:]}'><b>{len(alive_links)} link(s)</b></font> "
            "are working correctly and returning valid responses.",
            body_style
        ))
        elements.append(Spacer(1, 10))

        working_data = [["#", "URL", "Status", "Type", "Response"]]
        for i, link in enumerate(alive_links, 1):
            url_display = link.url[:50] + "..." if len(link.url) > 50 else link.url
            link_type = "External" if link.is_external else "Internal"
            time_str = f"{link.response_time}s" if link.response_time else "N/A"
            status = str(link.status_code) if link.status_code else "OK"
            working_data.append([str(i), url_display, status, link_type, time_str])

        working_table = Table(working_data, colWidths=[0.4*inch, 4.5*inch, 0.8*inch, 0.9*inch, 0.9*inch])
        working_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SUCCESS_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eafaf1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#eafaf1'), colors.HexColor('#f5fdf9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a9dfbf')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(working_table)

    # ==================== FOOTER ====================
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_TEXT, spaceAfter=10))
    elements.append(Paragraph(
        f"<font size='8' color='#{LIGHT_TEXT.hexval()[2:]}'>Generated by Dead Link Checker | "
        f"Report created on {report_date}</font>",
        ParagraphStyle('footer', alignment=TA_CENTER)
    ))

    # Build PDF with page numbers
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"📄 PDF Report saved to: {filename}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="Dead Link Checker - Check all links on a webpage for broken links"
    )
    parser.add_argument(
        "url",
        help="The URL of the webpage to check"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=10,
        help="Number of concurrent workers (default: 10)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=10,
        help="Timeout in seconds for each request (default: 10)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file for text report (default: auto-generated in reports/)"
    )
    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=1,
        help="Crawl depth: 1=homepage only, 2=follow internal links, 3+=deeper (default: 1)"
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Generate PDF report (saved in reports/ directory)"
    )
    parser.add_argument(
        "--no-txt",
        action="store_true",
        help="Skip generating text report"
    )

    args = parser.parse_args()

    # Ensure URL has a scheme
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    print("\n" + "=" * 60, flush=True)
    print("       🔗 DEAD LINK CHECKER", flush=True)
    print("=" * 60, flush=True)

    # Check all links
    results = check_all_links(url, args.workers, args.timeout, args.depth)

    # Generate and display report
    report = generate_report(results)
    print("\n" + report, flush=True)

    # Save text report
    if not args.no_txt:
        txt_filename = args.output if args.output else get_report_filename(url, "txt")
        save_report(report, txt_filename)

    # Generate PDF report if requested
    if args.pdf:
        pdf_filename = get_report_filename(url, "pdf")
        generate_pdf_report(results, pdf_filename, url)


if __name__ == "__main__":
    main()
