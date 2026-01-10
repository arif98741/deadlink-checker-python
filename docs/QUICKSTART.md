# Quick Start Guide - Dead Link Checker Desktop App

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
**Option A - Using Python:**
```bash
python deadlink_gui.py
```

**Option B - Using Batch File (Windows):**
```bash
run_gui.bat
```

**Option C - Build Executable:**
```bash
.\build.ps1
# Then run: dist\DeadLinkChecker.exe
```

### Step 3: Analyze a Website
1. Enter URL (e.g., `https://example.com`)
2. Adjust settings if needed:
   - Crawl Depth: 1-5 (1 = homepage only)
   - Workers: 5-50 (higher = faster)
   - Timeout: 5-30 seconds
3. Select report formats (TXT and/or PDF)
4. Click "▶ Start Analysis"
5. View results in real-time
6. Access reports in the `reports` folder

## 📊 Understanding Results

### Status Codes
- **✅ 200-299**: Success (link is working)
- **❌ 400-499**: Client errors (404 Not Found, 403 Forbidden, etc.)
- **❌ 500-599**: Server errors (500 Internal Server Error, 503 Service Unavailable, etc.)
- **❌ Timeout**: Server didn't respond in time
- **❌ Connection Error**: Cannot connect to server
- **❌ SSL Error**: Certificate or encryption issue

### Link Types
- **🏠 Internal**: Links to the same domain
- **🌐 External**: Links to other domains

## ⚙️ Recommended Settings

### For Small Websites (< 100 pages)
- Crawl Depth: 2-3
- Workers: 10-20
- Timeout: 10s

### For Large Websites (> 100 pages)
- Crawl Depth: 1-2
- Workers: 30-50
- Timeout: 15s

### For Slow Servers
- Crawl Depth: 1
- Workers: 5-10
- Timeout: 20-30s

## 🔧 Troubleshooting

### Application won't start
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### "Module not found" error
```bash
# Install missing module
pip install customtkinter pillow reportlab
```

### Build fails
```bash
# Clean and rebuild
pyinstaller --clean --onefile deadlink_gui.spec
```

### Reports not saving
- Check if `reports` folder exists (created automatically)
- Ensure write permissions in the application directory

## 💡 Tips

1. **Start Small**: Test with depth=1 first to see how many links exist
2. **Monitor Resources**: High worker count uses more CPU/memory
3. **External Links**: May give false positives if they block automated requests
4. **Save Reports**: Reports are timestamped, so you can track changes over time
5. **Batch Processing**: Use the CLI version for automated/scheduled scans

## 📝 Example Workflow

```
1. Open application
2. Enter: https://mywebsite.com
3. Set depth to 2
4. Set workers to 20
5. Enable both TXT and PDF reports
6. Click "Start Analysis"
7. Wait for completion (watch progress bar)
8. Click "Open Reports Folder"
9. Review the generated reports
10. Fix broken links on your website
11. Re-run analysis to verify fixes
```

## 🎯 Common Use Cases

### Website Maintenance
- Run weekly scans to catch new broken links
- Generate PDF reports for stakeholders
- Track link health over time

### SEO Optimization
- Identify and fix 404 errors
- Check external link validity
- Improve site crawlability

### Pre-Launch Testing
- Scan staging sites before going live
- Verify all internal navigation works
- Check third-party integrations

### Content Auditing
- Find outdated external references
- Identify pages with many broken links
- Prioritize content updates

## 📞 Need Help?

- Check the full README.md for detailed documentation
- Review the example reports in the `reports` folder
- Open an issue on GitHub with error details

---

**Happy Link Checking! 🔗✨**
