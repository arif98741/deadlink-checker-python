import os
import re
import csv
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse
from .models import LinkResult

def generate_report(results: list[LinkResult]) -> str:
    """Generate a formatted report of all link check results."""
    if not results: return "No links were found to check."

    dead_links = [r for r in results if r.is_dead]
    alive_links = [r for r in results if not r.is_dead]
    internal_links = [r for r in results if not r.is_external]
    external_links = [r for r in results if r.is_external]
    dead_internal = [r for r in dead_links if not r.is_external]
    dead_external = [r for r in dead_links if r.is_external]
    pages_crawled = set(r.found_on for r in results)

    by_type = defaultdict(list)
    for r in results: by_type[r.link_type].append(r)

    by_status = defaultdict(list)
    for r in results: by_status[r.status_text].append(r)

    report = []
    report.append("=" * 80)
    report.append("                        DEAD LINK CHECKER REPORT")
    report.append("=" * 80)
    report.append("")
    report.append("📊 SUMMARY")
    report.append("-" * 40)
    report.append(f"  Pages crawled:       {len(pages_crawled)}")
    report.append(f"  Total items checked: {len(results)}")
    report.append(f"  ✅ Working items:    {len(alive_links)}")
    report.append(f"  ❌ Dead items:       {len(dead_links)}")
    report.append(f"  Success rate:        {len(alive_links)/len(results)*100:.1f}%" if results else "  Success rate:        0%")
    report.append("")
    report.append("📦 ASSET TYPE BREAKDOWN")
    report.append("-" * 40)
    for ltype, items in sorted(by_type.items(), key=lambda x: -len(x[1])):
        report.append(f"  {ltype}: {len(items)}")
    report.append("")
    report.append("🔗 LINK LOCATION BREAKDOWN")
    report.append("-" * 40)
    report.append(f"  🏠 Internal:   {len(internal_links)}")
    report.append(f"  🌐 External:   {len(external_links)}")
    report.append("")
    report.append("📈 STATUS BREAKDOWN")
    report.append("-" * 40)
    for status, links in sorted(by_status.items(), key=lambda x: -len(x[1])):
        report.append(f"  {status}: {len(links)}")
    report.append("")

    if dead_internal:
        report.append("❌ DEAD INTERNAL ASSETS (Need Attention)")
        report.append("-" * 40)
        for i, link in enumerate(dead_internal, 1):
            report.append(f"  {i}. [{link.link_type}] {link.url}")
            report.append(f"     Status: {link.status_text}")
            report.append(f"     Found on: {link.found_on}")
            report.append("")

    if dead_external:
        report.append("❌ DEAD EXTERNAL ASSETS")
        report.append("-" * 40)
        for i, link in enumerate(dead_external, 1):
            report.append(f"  {i}. [{link.link_type}] {link.url}")
            report.append(f"     Status: {link.status_text}")
            report.append(f"     Found on: {link.found_on}")
            report.append("")

    if alive_links:
        report.append("✅ WORKING ASSETS (Verified)")
        report.append("-" * 40)
        for i, link in enumerate(alive_links, 1):
            report.append(f"  {i}. [{link.link_type}] {link.url}")
            report.append(f"     Status: {link.status_text}")
            report.append("")

    report.append("")
    report.append("=" * 80)
    report.append("                           END OF REPORT")
    report.append("=" * 80)
    return "\n".join(report)

def get_report_filename(target_url: str, extension: str = "txt", reports_dir: str = None, session_folder: str = None) -> str:
    """Generate a meaningful filename with domain and datetime."""
    domain = urlparse(target_url).netloc.lower().replace('www.', '')
    domain_clean = re.sub(r'[^\w\-]', '_', domain)
    timestamp = datetime.now().strftime('%H%M%S')

    if reports_dir is None:
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
    
    final_dir = os.path.join(reports_dir, session_folder) if session_folder else reports_dir
    os.makedirs(final_dir, exist_ok=True)
    return os.path.join(final_dir, f"{domain_clean}_{timestamp}.{extension}")

def save_report(report: str, filename: str = "link_report.txt"):
    """Save the report to a file."""
    os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 Report saved to: {filename}")

def generate_csv_report(results: list[LinkResult], filename: str, target_url: str):
    """Generate a CSV report of all link check results."""
    if not results: return
    os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
    dead_links = [r for r in results if r.is_dead]
    alive_links = [r for r in results if not r.is_dead]
    pages_crawled = set(r.found_on for r in results)
    success_rate = len(alive_links) / len(results) * 100 if results else 0
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Dead Link Checker Report'])
        writer.writerow(['Target URL', target_url])
        writer.writerow(['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['Pages Crawled', len(pages_crawled)])
        writer.writerow(['Total Links Checked', len(results)])
        writer.writerow(['Working Links', len(alive_links)])
        writer.writerow(['Broken Links', len(dead_links)])
        writer.writerow(['Success Rate', f'{success_rate:.1f}%'])
        writer.writerow([])
        writer.writerow(['URL', 'Asset Type', 'Status Code', 'Status Text', 'Response Time (s)', 'Location', 'Found On Page', 'Is Dead', 'Is External'])
        for r in results:
            writer.writerow([r.url, r.link_type, r.status_code or 'N/A', r.status_text, r.response_time or 'N/A', 'External' if r.is_external else 'Internal', r.found_on, 'Yes' if r.is_dead else 'No', 'Yes' if r.is_external else 'No'])
    print(f"\n💾 CSV report saved to: {filename}")

def generate_pdf_report(results: list[LinkResult], filename: str, target_url: str):
    """Generate a professional PDF report with tabular format."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, HRFlowable)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    if not results: return
    dead_links = [r for r in results if r.is_dead]
    alive_links = [r for r in results if not r.is_dead]
    internal_links = [r for r in results if not r.is_external]
    external_links = [r for r in results if r.is_external]
    dead_internal = [r for r in dead_links if not r.is_external]
    dead_external = [r for r in dead_links if r.is_external]
    pages_crawled = set(r.found_on for r in results)
    success_rate = len(alive_links) / len(results) * 100 if results else 0

    PRIMARY_COLOR = colors.HexColor('#1a5276')
    SECONDARY_COLOR = colors.HexColor('#2980b9')
    SUCCESS_COLOR = colors.HexColor('#27ae60')
    DANGER_COLOR = colors.HexColor('#c0392b')
    WARNING_COLOR = colors.HexColor('#f39c12')
    LIGHT_BG = colors.HexColor('#f8f9fa')
    DARK_TEXT = colors.HexColor('#2c3e50')
    LIGHT_TEXT = colors.HexColor('#7f8c8d')

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(LIGHT_TEXT)
        page_num = canvas.getPageNumber()
        canvas.drawRightString(landscape(A4)[0] - 40, 25, f"Page {page_num}")
        canvas.drawString(40, 25, f"Dead Link Checker Report - {urlparse(target_url).netloc}")
        canvas.setStrokeColor(PRIMARY_COLOR)
        canvas.setLineWidth(2)
        canvas.line(40, landscape(A4)[1] - 35, landscape(A4)[0] - 40, landscape(A4)[1] - 35)
        canvas.setLineWidth(0.5)
        canvas.line(40, 40, landscape(A4)[0] - 40, 40)
        canvas.restoreState()

    doc = SimpleDocTemplate(filename, pagesize=landscape(A4), rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=28, alignment=TA_CENTER, spaceAfter=5, textColor=PRIMARY_COLOR, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, spaceAfter=20, textColor=LIGHT_TEXT)
    section_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=16, spaceBefore=25, spaceAfter=12, textColor=PRIMARY_COLOR, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=10, textColor=DARK_TEXT, spaceAfter=8)

    elements.append(Paragraph("DEAD LINK CHECKER", title_style))
    elements.append(Paragraph("Website Analysis Report", subtitle_style))
    
    info_data = [["Target Website", urlparse(target_url).netloc], ["Full URL", target_url[:70] + "..." if len(target_url) > 70 else target_url], ["Report Generated", datetime.now().strftime('%B %d, %Y at %H:%M:%S')], ["Analysis Depth", f"{len(pages_crawled)} page(s) crawled"]]
    info_table = Table(info_data, colWidths=[2*inch, 5*inch])
    info_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (0, -1), PRIMARY_COLOR), ('TEXTCOLOR', (0, 0), (0, -1), colors.white), ('BACKGROUND', (1, 0), (1, -1), LIGHT_BG), ('TEXTCOLOR', (1, 0), (1, -1), DARK_TEXT), ('ALIGN', (0, 0), (0, -1), 'RIGHT'), ('ALIGN', (1, 0), (1, -1), 'LEFT'), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6'))]))
    elements.append(info_table)
    elements.append(Spacer(1, 25))

    elements.append(Paragraph("Executive Summary", section_style))
    sum_data = [[Paragraph(f"<font size='24'><b>{len(results)}</b></font>", ParagraphStyle('c', alignment=TA_CENTER, textColor=PRIMARY_COLOR)), Paragraph(f"<font size='24'><b>{len(alive_links)}</b></font>", ParagraphStyle('c', alignment=TA_CENTER, textColor=SUCCESS_COLOR)), Paragraph(f"<font size='24'><b>{len(dead_links)}</b></font>", ParagraphStyle('c', alignment=TA_CENTER, textColor=DANGER_COLOR)), Paragraph(f"<font size='24'><b>{success_rate:.1f}%</b></font>", ParagraphStyle('c', alignment=TA_CENTER, textColor=SUCCESS_COLOR if success_rate >= 90 else WARNING_COLOR))], [Paragraph("Total Links", ParagraphStyle('l', alignment=TA_CENTER)), Paragraph("Working", ParagraphStyle('l', alignment=TA_CENTER)), Paragraph("Broken", ParagraphStyle('l', alignment=TA_CENTER)), Paragraph("Success Rate", ParagraphStyle('l', alignment=TA_CENTER))]]
    sum_table = Table(sum_data, colWidths=[2*inch]*4)
    sum_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6'))]))
    elements.append(sum_table)

    if dead_links:
        elements.append(PageBreak())
        elements.append(Paragraph("Broken Links - Action Required", section_style))
        if dead_internal:
            elements.append(Paragraph(f"Internal Broken Links ({len(dead_internal)})", body_style))
            d_data = [["#", "URL", "Type", "Status", "Found On"]]
            for i, l in enumerate(dead_internal, 1): 
                d_data.append([str(i), Paragraph(l.url, body_style), l.link_type, l.status_text, Paragraph(l.found_on, body_style)])
            dt = Table(d_data, colWidths=[0.4*inch, 3.5*inch, 1*inch, 1.2*inch, 2.5*inch])
            dt.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), DANGER_COLOR), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
            elements.append(dt)
            elements.append(Spacer(1, 15))

        if dead_external:
            elements.append(Paragraph(f"External Broken Links ({len(dead_external)})", body_style))
            e_data = [["#", "URL", "Type", "Status", "Found On"]]
            for i, l in enumerate(dead_external, 1): 
                e_data.append([str(i), Paragraph(l.url, body_style), l.link_type, l.status_text, Paragraph(l.found_on, body_style)])
            et = Table(e_data, colWidths=[0.4*inch, 3.5*inch, 1*inch, 1.2*inch, 2.5*inch])
            et.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e22')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
            elements.append(et)
            elements.append(Spacer(1, 15))

    if alive_links:
        elements.append(PageBreak())
        elements.append(Paragraph("Verified Working Links", section_style))
        w_data = [["#", "URL", "Type", "Status", "Time"]]
        for i, l in enumerate(alive_links, 1):
            w_data.append([str(i), Paragraph(l.url, body_style), l.link_type, l.status_text, f"{l.response_time}s"])
        wt = Table(w_data, colWidths=[0.4*inch, 4.5*inch, 1*inch, 1.2*inch, 1*inch])
        wt.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), SUCCESS_COLOR), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
        elements.append(wt)

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"📄 PDF Report saved to: {filename}")
