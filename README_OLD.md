# Website Documentation Scraper System

A comprehensive solution for converting entire websites into structured markdown documentation using Google's Gemini 2.5 Flash model.

## 🎯 Features

- **Complete Website Crawling** - Discovers and processes all pages on a website
- **AI-Powered Content Extraction** - Uses Gemini 2.5 Flash to intelligently extract content
- **Markdown Generation** - Converts content to clean, structured markdown files
- **Smart State Management** - Resume interrupted crawls automatically
- **GUI Interface** - User-friendly desktop application
- **REST API Backend** - Server-based processing with web interface
- **Progress Tracking** - Real-time monitoring of scraping progress
- **Error Handling** - Graceful failure handling and recovery
- **Cross-Platform** - Works on Windows, macOS, and Linux

## 📦 Components

### 1. Core Scraper (`website_doc_scraper.py`)
The main scraping engine that handles:
- Website discovery and link crawling
- Content extraction using Gemini 2.5 Flash
- Markdown file generation
- State persistence and recovery

### 2. GUI Application (`scraper_gui.py`)
Desktop application with:
- Easy-to-use interface
- Real-time progress monitoring
- Configurable settings
- Output folder management

### 3. Backend Server (`scraper_backend.py`)
REST API server providing:
- Job management endpoints
- Web-based interface
- File serving and downloads
- Multi-job processing

### 4. GitHub Repository Crawler (`complete_github_crawler.py`)
Specialized crawler for GitHub repositories with:
- Repository metadata extraction
- Batch processing capabilities
- CSV/JSON export functionality

## 🚀 Quick Start

### Prerequisites
```bash
pip install scrapegraphai beautifulsoup4 requests flask flask-cors
```

### Set up Gemini API Key
```bash
# On Windows (PowerShell)
$env:GOOGLE_APIKEY = "your_gemini_api_key_here"

# On macOS/Linux
export GOOGLE_APIKEY="your_gemini_api_key_here"
```

### Basic Usage

#### 1. Command Line Interface
```python
from website_doc_scraper import WebsiteDocumentationScraper

scraper = WebsiteDocumentationScraper(
    base_url="https://example.com",
    output_dir="docs",
    max_depth=3,
    delay=2.0,
    max_pages=100
)

summary = scraper.crawl_website()
scraper.generate_index()
```

#### 2. GUI Application
```bash
python scraper_gui.py
```

#### 3. Backend Server
```bash
python scraper_backend.py
```
Then open http://localhost:5000 in your browser.

## ⚙️ Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `base_url` | Starting URL to crawl | Required |
| `output_dir` | Directory for markdown files | "docs" |
| `max_depth` | Maximum crawl depth | 3 |
| `delay` | Delay between requests (seconds) | 2.0 |
| `max_pages` | Maximum pages to process | 100 |

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/jobs` | POST | Create new scraping job |
| `/api/jobs/<id>/start` | POST | Start a job |
| `/api/jobs/<id>/stop` | POST | Stop a job |
| `/api/jobs/<id>/status` | GET | Get job status |
| `/api/jobs/<id>/files` | GET | List generated files |
| `/api/jobs/<id>/download` | GET | Download files as ZIP |

## 🔧 Advanced Features

### Smart State Management
- Automatically saves progress every 10 pages
- Resume interrupted crawls seamlessly
- Handles network failures gracefully

### Content Intelligence
- Extracts main content while filtering navigation
- Preserves code blocks and formatting
- Generates meaningful filenames
- Creates comprehensive index files

### Cross-Platform Compatibility
- Native file system integration
- Platform-specific optimizations
- Consistent behavior across operating systems

## 📝 Example Use Cases

### 1. Documentation Migration
```python
# Convert existing documentation site to markdown
scraper = WebsiteDocumentationScraper(
    base_url="https://old-docs.company.com",
    output_dir="new_docs",
    max_depth=5,
    max_pages=500
)
```

### 2. Knowledge Base Creation
```python
# Extract knowledge from support sites
scraper = WebsiteDocumentationScraper(
    base_url="https://support.example.com",
    output_dir="kb",
    max_depth=3,
    max_pages=200
)
```

### 3. API Documentation
```python
# Extract API documentation
scraper = WebsiteDocumentationScraper(
    base_url="https://api-docs.example.com",
    output_dir="api_docs",
    max_depth=4,
    max_pages=100
)
```

## 🛠️ File Structure

```
docs/
├── index.md                 # Main index file
├── page1.md                 # Individual page content
├── page2.md                 # Individual page content
├── ...
└── scraper_state.json       # State persistence file
```

## 📋 Generated Markdown Format

Each markdown file includes:
- Page title and description
- Source URL and generation timestamp
- Clean, structured content
- Proper markdown formatting
- Relevant tags and metadata

## 🔍 Error Handling

The system handles various error conditions:
- Network timeouts and failures
- Invalid URLs and redirects
- Content extraction errors
- File system permissions
- API rate limits

## 🚦 Best Practices

1. **Respectful Crawling**: Use appropriate delays (1-2 seconds minimum)
2. **Depth Limits**: Start with max_depth=2-3 for testing
3. **Page Limits**: Set reasonable max_pages to avoid overwhelming sites
4. **State Management**: Always enable resume functionality
5. **Error Monitoring**: Check logs for failed URLs

## 🧪 Testing

The project includes comprehensive test scripts:

```bash
# Basic functionality test
python test_scraper.py

# GitHub repository scraping test
python test_github_scraper.py

# HTTPBin API documentation test
python test_httpbin.py

# Batch testing multiple sites
python test_multiple_sites.py

# GitHub crawler testing
python test_batch_crawler.py
```

**Note:** Test outputs are saved to separate directories and are not tracked in version control. This allows you to test the scraper without cluttering the repository.

## 📈 Performance

- **Speed**: ~0.5-2 pages per second (depending on delay)
- **Memory**: Efficient with minimal memory usage
- **Storage**: Compressed markdown files (~10-50KB per page)
- **Scalability**: Handles 1000+ pages efficiently

## 🔒 Security

- No sensitive data stored in files
- API keys handled securely
- Rate limiting to prevent abuse
- Input validation for all parameters

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini 2.5 Flash for AI-powered content extraction
- ScrapeGraph AI for the underlying scraping framework
- BeautifulSoup for HTML parsing
- Flask for the web interface

---

**Ready to convert any website into structured documentation!** 🚀
