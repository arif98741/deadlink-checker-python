#!/usr/bin/env python3
"""
Dead Link Checker - Legacy Wrapper
Now imports from the modular deadlink package.
"""

import sys
import argparse
from deadlink import (
    setup_windows_encoding,
    check_all_links,
    generate_report,
    get_report_filename,
    save_report,
    generate_csv_report,
    generate_pdf_report
)

def main():
    setup_windows_encoding()
    
    parser = argparse.ArgumentParser(description='Check a website for dead links.')
    parser.add_argument('url', help='The URL of the website to check')
    parser.add_argument('--workers', type=int, default=10, help='Number of concurrent workers (default: 10)')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds for each request (default: 10)')
    parser.add_argument('--depth', type=int, default=1, help='Crawl depth (1=page only, 2+=recursive) (default: 1)')
    parser.add_argument('--pdf', action='store_true', help='Generate a PDF report')
    parser.add_argument('--csv', action='store_true', help='Generate a CSV report')
    parser.add_argument('--output-dir', help='Custom directory for reports')
    
    args = parser.parse_args()
    
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    try:
        results = check_all_links(url, args.workers, args.timeout, args.depth)
        
        report = generate_report(results)
        print("\n" + report)
        
        # Always save TXT report
        reports_dir = args.output_dir
        txt_filename = get_report_filename(url, "txt", reports_dir)
        save_report(report, txt_filename)
        
        if args.pdf:
            pdf_filename = get_report_filename(url, "pdf", reports_dir)
            generate_pdf_report(results, pdf_filename, url)
            
        if args.csv:
            csv_filename = get_report_filename(url, "csv", reports_dir)
            generate_csv_report(results, csv_filename, url)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
