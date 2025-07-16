"""
Website Documentation Scraper with Gemini 2.5 Flash
===================================================

This module provides comprehensive website scraping capabilities to convert
entire websites into structured markdown documentation.

Features:
- Site discovery and link crawling
- Content extraction and formatting
- Markdown generation
- Smart state management
- Progress tracking
- Error handling and recovery
"""

import os
import json
import time
import hashlib
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from scrapegraphai.graphs import SmartScraperGraph

# Set the Gemini API key (set this as an environment variable)
# os.environ["GOOGLE_APIKEY"] = "your_gemini_api_key_here"

class WebsiteDocumentationScraper:
    """Complete website documentation scraper with markdown generation"""
    
    def __init__(self, base_url: str, output_dir: str = "docs", max_depth: int = 3, 
                 delay: float = 2.0, max_pages: int = 100):
        """
        Initialize the website scraper
        
        Args:
            base_url: Base URL of the website to scrape
            output_dir: Directory to save markdown files
            max_depth: Maximum crawl depth
            delay: Delay between requests
            max_pages: Maximum number of pages to crawl
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.delay = delay
        self.max_pages = max_pages
        
        # State management
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.pending_urls: List[Tuple[str, int]] = [(base_url, 0)]  # (url, depth)
        self.processed_count = 0
        self.start_time = None
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        self.state_file = self.output_dir / "scraper_state.json"
        
        # Gemini configuration
        self.gemini_config = {
            "llm": {
                "api_key": os.environ["GOOGLE_APIKEY"],
                "model": "google_genai/gemini-2.5-flash",
                "temperature": 0.1,
            },
            "verbose": False,
            "headless": True,
        }
        
        # File naming and organization
        self.file_counter = 0
        self.url_to_filename = {}
        
    def save_state(self):
        """Save current scraping state"""
        state = {
            "base_url": self.base_url,
            "visited_urls": list(self.visited_urls),
            "failed_urls": list(self.failed_urls),
            "pending_urls": self.pending_urls,
            "processed_count": self.processed_count,
            "file_counter": self.file_counter,
            "url_to_filename": self.url_to_filename,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self) -> bool:
        """Load previous scraping state"""
        if not self.state_file.exists():
            return False
            
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            self.visited_urls = set(state.get("visited_urls", []))
            self.failed_urls = set(state.get("failed_urls", []))
            self.pending_urls = state.get("pending_urls", [(self.base_url, 0)])
            self.processed_count = state.get("processed_count", 0)
            self.file_counter = state.get("file_counter", 0)
            self.url_to_filename = state.get("url_to_filename", {})
            
            print(f"📁 Loaded state: {len(self.visited_urls)} visited, {len(self.pending_urls)} pending")
            return True
            
        except Exception as e:
            print(f"⚠️  Failed to load state: {e}")
            return False
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling"""
        try:
            parsed = urlparse(url)
            
            # Must be same domain
            if parsed.netloc != self.domain:
                return False
                
            # Skip common non-content URLs
            skip_extensions = {'.pdf', '.jpg', '.png', '.gif', '.zip', '.exe', '.mp4'}
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
                
            # Skip common paths
            skip_paths = {'/login', '/logout', '/admin', '/api/', '/assets/', '/static/'}
            if any(path in url.lower() for path in skip_paths):
                return False
                
            return True
            
        except Exception:
            return False
    
    def discover_links(self, url: str) -> List[str]:
        """Discover all links on a page"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Clean URL (remove fragments)
                parsed = urlparse(full_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                                     parsed.params, parsed.query, ''))
                
                if self.is_valid_url(clean_url) and clean_url not in self.visited_urls:
                    links.append(clean_url)
            
            return list(set(links))  # Remove duplicates
            
        except Exception as e:
            print(f"❌ Failed to discover links from {url}: {e}")
            return []
    
    def generate_filename(self, url: str) -> str:
        """Generate a safe filename for the URL"""
        if url in self.url_to_filename:
            return self.url_to_filename[url]
        
        # Parse URL to create meaningful filename
        parsed = urlparse(url)
        path = parsed.path.strip('/').replace('/', '_')
        
        if not path or path == '':
            filename = 'index'
        else:
            filename = path
            
        # Add query parameters if significant
        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode()).hexdigest()[:8]
            filename += f"_{query_hash}"
        
        # Ensure filename is safe
        filename = "".join(c for c in filename if c.isalnum() or c in '-_')
        filename = filename[:100]  # Limit length
        
        # Add counter to avoid duplicates
        if filename in self.url_to_filename.values():
            self.file_counter += 1
            filename = f"{filename}_{self.file_counter}"
        
        filename += '.md'
        self.url_to_filename[url] = filename
        return filename
    
    def extract_content(self, url: str) -> Dict:
        """Extract and format content from a URL using Gemini"""
        prompt = f"""
        Extract and format the main content from this webpage into a structured markdown document.
        
        Return the content in this exact JSON format:
        {{
            "title": "Page title",
            "description": "Brief description of the page content",
            "url": "{url}",
            "content": "Main content formatted as clean markdown",
            "navigation": ["breadcrumb", "navigation", "links"],
            "tags": ["relevant", "tags", "keywords"],
            "last_updated": "extraction date",
            "word_count": "approximate word count"
        }}
        
        Guidelines:
        - Convert HTML to clean markdown
        - Preserve code blocks and formatting
        - Include all text content, headings, lists, tables
        - Remove navigation menus, footers, ads
        - Focus on the main documentation/content area
        - Use proper markdown syntax (##, -, *, etc.)
        - Include links but make them relative where possible
        """
        
        try:
            graph = SmartScraperGraph(
                prompt=prompt,
                source=url,
                config=self.gemini_config
            )
            
            result = graph.run()
            content_data = result.get("content", {})
            
            # Ensure we have required fields
            if not isinstance(content_data, dict):
                content_data = {"title": "Unknown", "content": str(content_data)}
            
            content_data.update({
                "url": url,
                "extraction_date": datetime.now().isoformat(),
                "source": "gemini-2.5-flash"
            })
            
            return content_data
            
        except Exception as e:
            print(f"❌ Failed to extract content from {url}: {e}")
            return {
                "title": f"Error: {urlparse(url).path}",
                "content": f"Failed to extract content: {str(e)}",
                "url": url,
                "error": str(e)
            }
    
    def generate_markdown(self, content_data: Dict, filename: str) -> str:
        """Generate markdown file from extracted content"""
        title = content_data.get("title", "Untitled")
        description = content_data.get("description", "")
        url = content_data.get("url", "")
        content = content_data.get("content", "")
        tags = content_data.get("tags", [])
        last_updated = content_data.get("extraction_date", "")
        
        # Create markdown document
        markdown = f"""# {title}

> **Source:** {url}  
> **Generated:** {last_updated}  
> **Description:** {description}

"""
        
        # Add tags if available
        if tags:
            tag_str = " ".join(f"#{tag}" for tag in tags if tag)
            markdown += f"**Tags:** {tag_str}\n\n"
        
        # Add main content
        markdown += "---\n\n"
        markdown += content
        
        # Add footer
        markdown += f"\n\n---\n\n*This document was automatically generated from {url}*"
        
        return markdown
    
    def save_markdown(self, content_data: Dict, filename: str):
        """Save content as markdown file"""
        try:
            markdown_content = self.generate_markdown(content_data, filename)
            file_path = self.output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"📄 Saved: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save {filename}: {e}")
            return False
    
    def process_url(self, url: str, depth: int) -> bool:
        """Process a single URL"""
        print(f"🔍 Processing ({depth}): {url}")
        
        # Extract content
        content_data = self.extract_content(url)
        
        # Generate filename and save
        filename = self.generate_filename(url)
        success = self.save_markdown(content_data, filename)
        
        if success:
            self.processed_count += 1
            
            # Discover new links if within depth limit
            if depth < self.max_depth:
                new_links = self.discover_links(url)
                for link in new_links:
                    if link not in self.visited_urls and link not in self.failed_urls:
                        self.pending_urls.append((link, depth + 1))
                        
                print(f"🔗 Found {len(new_links)} new links")
        
        return success
    
    def crawl_website(self, resume: bool = True) -> Dict:
        """Main crawling function"""
        if resume:
            self.load_state()
        
        self.start_time = time.time()
        
        print(f"🚀 Starting website crawl: {self.base_url}")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"⚙️  Max depth: {self.max_depth}, Max pages: {self.max_pages}")
        print(f"⏱️  Delay: {self.delay} seconds")
        print("=" * 70)
        
        try:
            while self.pending_urls and self.processed_count < self.max_pages:
                url, depth = self.pending_urls.pop(0)
                
                if url in self.visited_urls:
                    continue
                
                self.visited_urls.add(url)
                
                # Process URL
                success = self.process_url(url, depth)
                
                if not success:
                    self.failed_urls.add(url)
                
                # Show progress
                progress = (self.processed_count / self.max_pages) * 100
                elapsed = time.time() - self.start_time
                print(f"📊 Progress: {self.processed_count}/{self.max_pages} ({progress:.1f}%) - {elapsed:.1f}s")
                
                # Save state periodically
                if self.processed_count % 10 == 0:
                    self.save_state()
                
                # Respectful delay
                time.sleep(self.delay)
                print("-" * 70)
            
            # Final save
            self.save_state()
            
            # Generate summary
            summary = self.generate_summary()
            return summary
            
        except KeyboardInterrupt:
            print("\n⏹️  Crawl interrupted by user")
            self.save_state()
            return self.generate_summary()
        
        except Exception as e:
            print(f"❌ Crawl failed: {e}")
            self.save_state()
            return self.generate_summary()
    
    def generate_summary(self) -> Dict:
        """Generate crawl summary"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        summary = {
            "base_url": self.base_url,
            "processed_count": self.processed_count,
            "visited_count": len(self.visited_urls),
            "failed_count": len(self.failed_urls),
            "pending_count": len(self.pending_urls),
            "elapsed_time": elapsed,
            "pages_per_second": self.processed_count / elapsed if elapsed > 0 else 0,
            "output_directory": str(self.output_dir),
            "completion_time": datetime.now().isoformat()
        }
        
        return summary
    
    def generate_index(self):
        """Generate index.md with all scraped pages"""
        index_content = f"""# Documentation Index

> **Website:** {self.base_url}  
> **Generated:** {datetime.now().isoformat()}  
> **Total Pages:** {self.processed_count}

## Pages

"""
        
        # List all markdown files
        for filename in sorted(self.url_to_filename.values()):
            page_title = filename.replace('.md', '').replace('_', ' ').title()
            index_content += f"- [{page_title}]({filename})\n"
        
        index_content += f"\n---\n\n*Index generated automatically from {self.base_url}*"
        
        # Save index
        with open(self.output_dir / "index.md", 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"📚 Generated index.md")

def main():
    """Main function with CLI argument parsing"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Website Documentation Scraper with Gemini 2.5 Flash',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python website_doc_scraper.py https://example.com
  python website_doc_scraper.py https://example.com --depth 3 --pages 50
  python website_doc_scraper.py https://example.com --output my_docs --delay 1.0
  python website_doc_scraper.py https://example.com --no-resume
'''
    )
    
    parser.add_argument('url', help='Website URL to scrape')
    parser.add_argument('--depth', '-d', type=int, default=3, 
                      help='Maximum crawl depth (default: 3)')
    parser.add_argument('--pages', '-p', type=int, default=100,
                      help='Maximum number of pages to process (default: 100)')
    parser.add_argument('--output', '-o', default='docs',
                      help='Output directory for markdown files (default: docs)')
    parser.add_argument('--delay', type=float, default=2.0,
                      help='Delay between requests in seconds (default: 2.0)')
    parser.add_argument('--no-resume', action='store_true',
                      help='Do not resume from previous crawl state')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url
    
    # Check API key
    if "GOOGLE_APIKEY" not in os.environ:
        print("❌ Error: GOOGLE_APIKEY environment variable is not set")
        print("Please set your Gemini API key first:")
        print("  Windows: $env:GOOGLE_APIKEY = 'your_api_key'")
        print("  Unix:    export GOOGLE_APIKEY='your_api_key'")
        return
    
    print("🚀 Website Documentation Scraper")
    print("=" * 50)
    print(f"🌐 URL: {args.url}")
    print(f"📁 Output: {args.output}")
    print(f"🔢 Max Depth: {args.depth}")
    print(f"📄 Max Pages: {args.pages}")
    print(f"⏱️  Delay: {args.delay}s")
    print(f"🔄 Resume: {not args.no_resume}")
    print()
    
    try:
        # Initialize scraper
        scraper = WebsiteDocumentationScraper(
            base_url=args.url,
            output_dir=args.output,
            max_depth=args.depth,
            delay=args.delay,
            max_pages=args.pages
        )
        
        # Run scraper
        summary = scraper.crawl_website(resume=not args.no_resume)
        scraper.generate_index()
        
        print("\n✨ Crawl Summary:")
        print("=" * 40)
        for key, value in summary.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n📁 Documentation saved to: {args.output}")
        print(f"📚 Check index.md for navigation")
        
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
