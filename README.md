# Dead Link Checker

A Python tool to crawl websites and check for broken/dead links with detailed reporting in both text and PDF formats.

## Features

- Scrapes all links from a given webpage
- Recursive crawling with configurable depth
- Concurrent link checking for fast performance
- Identifies internal vs external links
- Detects dead links (4xx, 5xx errors, timeouts, connection errors)
- Auto-generates reports with meaningful filenames
- Saves all reports in `reports/` directory
- Generates text and PDF reports with tabular format
- Shows response times for each link

## Installation

### Prerequisites

- Python 3.10 or higher

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Command

```bash
python deadlink_checker.py <URL> [OPTIONS]
```

### Options

| Flag | Long Option | Type | Default | Description |
|------|-------------|------|---------|-------------|
| `-w` | `--workers` | int | 10 | Number of concurrent threads for checking links |
| `-t` | `--timeout` | int | 10 | Timeout in seconds for each HTTP request |
| `-o` | `--output` | str | auto | Custom output path for text report |
| `-d` | `--depth` | int | 1 | Crawl depth level |
| | `--pdf` | flag | - | Generate PDF report |
| | `--no-txt` | flag | - | Skip generating text report |

### Report Files

Reports are automatically saved in the `reports/` directory with meaningful names:

```
reports/
  example_com_20240115_143022.txt
  example_com_20240115_143022.pdf
  database_com_20240115_150530.txt
```

**Filename format:** `{domain}_{YYYYMMDD}_{HHMMSS}.{ext}`

### Depth Levels Explained

| Depth | Behavior |
|-------|----------|
| 1 | Check links on the homepage only (default) |
| 2 | Check homepage + follow all internal links and check those pages |
| 3+ | Continue crawling deeper into the site |

**Note:** Higher depth values will take significantly longer and check many more pages.

## Examples

### 1. Basic Usage - Check Homepage Only

```bash
python deadlink_checker.py https://example.com
```
Output: `reports/example_com_20240115_143022.txt`

### 2. Check with More Workers (Faster)

```bash
python deadlink_checker.py https://example.com -w 20
```

### 3. Increase Timeout for Slow Sites

```bash
python deadlink_checker.py https://example.com -t 30
```

### 4. Crawl Internal Pages (Depth 2)

```bash
python deadlink_checker.py https://example.com -d 2
```

### 5. Generate PDF Report

```bash
python deadlink_checker.py https://example.com --pdf
```
Output:
- `reports/example_com_20240115_143022.txt`
- `reports/example_com_20240115_143022.pdf`

### 6. Generate Only PDF (No Text Report)

```bash
python deadlink_checker.py https://example.com --pdf --no-txt
```
Output: `reports/example_com_20240115_143022.pdf`

### 7. Custom Output Path

```bash
python deadlink_checker.py https://example.com -o my_custom_report.txt
```

### 8. Full Example with All Options

```bash
python deadlink_checker.py https://example.com -w 20 -t 15 -d 2 --pdf
```
Output:
- `reports/example_com_20240115_143022.txt`
- `reports/example_com_20240115_143022.pdf`

## Output

### Console Output

During execution, you'll see real-time progress:

```
[1/120] OK (Internal): https://example.com/page1
[2/120] OK (External): https://github.com/user
[3/120] Not Found (Internal): https://example.com/broken-link
```

**Status Codes:**
- `OK` - Link is working (200 status)
- `Not Found` - 404 error
- `Forbidden` - 403 error
- `Timeout` - Request timed out
- `Connection Error` - Could not connect

**Link Types:**
- `Internal` - Same domain as target URL
- `External` - Different domain

### Text Report

The text report includes:

1. **Summary** - Total links, working/dead counts, success rate
2. **Link Type Breakdown** - Internal vs external link counts
3. **Status Breakdown** - Count of each HTTP status
4. **Dead Internal Links** - Broken links on your site (priority)
5. **Dead External Links** - Broken third-party links
6. **Working Internal Links** - All working internal links
7. **Working External Links** - All working external links

### PDF Report

The PDF report includes formatted tables with:

- Summary statistics table
- Dead links table (red highlighted) with URL, status, type, source page
- Working links table (green highlighted) with URL, status, type, response time

## Understanding Results

### Common Status Codes

| Code | Meaning | Is Dead? |
|------|---------|----------|
| 200 | OK | No |
| 301 | Moved Permanently | No |
| 302 | Redirect | No |
| 400 | Bad Request | Yes |
| 401 | Unauthorized | Yes |
| 403 | Forbidden | Yes |
| 404 | Not Found | Yes |
| 500 | Internal Server Error | Yes |
| 503 | Service Unavailable | Yes |

### Notes on External Links

Some external sites (LinkedIn, Facebook, Medium) block automated requests and may show as "dead" even though they work in a browser. This is normal bot-blocking behavior.

## Performance Tips

1. **Increase workers** (`-w 30`) for faster checking on sites with many links
2. **Reduce timeout** (`-t 5`) if you want faster results and don't mind missing slow sites
3. **Start with depth 1** to get a quick overview before deep crawling
4. **Use depth 2** for comprehensive site audits including all internal pages

## Directory Structure

```
deadlinkchecker/
  deadlink_checker.py    # Main script
  requirements.txt       # Dependencies
  README.md              # Documentation
  reports/               # Auto-created directory for reports
    example_com_20240115_143022.txt
    example_com_20240115_143022.pdf
```

## Example Output

```
================================================================================
                        DEAD LINK CHECKER REPORT
================================================================================

SUMMARY
----------------------------------------
  Pages crawled:       1
  Total links checked: 120
  Working links:       117
  Dead links:          3
  Success rate:        97.5%

LINK TYPE BREAKDOWN
----------------------------------------
  Internal links:      115
  External links:      5

DEAD EXTERNAL LINKS
----------------------------------------
  1. https://linkedin.com/in/username
     Status: HTTP 999
     Found on: https://example.com

WORKING INTERNAL LINKS
----------------------------------------
  1. [200] https://example.com/about (0.5s)
  2. [200] https://example.com/contact (0.3s)
  ...
================================================================================

Report saved to: reports/example_com_20240115_143022.txt
PDF Report saved to: reports/example_com_20240115_143022.pdf
```

## License

MIT License
