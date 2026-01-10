"""
Website Documentation Scraper with Gemini 2.5 Flash
===================================================
"""

import os
import json
import time
import hashlib
import shutil
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse
from typing import List, Dict, Set, Tuple
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from scrapegraphai.graphs import SmartScraperGraph

# Import configuration
from .config import (
    SCRAPER_CONFIG,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MAX_PAGES,
    DEFAULT_DELAY
)

class WebsiteDocumentationScraper:
    """Complete website documentation scraper with markdown generation"""

    def __init__(self, base_url: str, output_dir: str = DEFAULT_OUTPUT_DIR,
                 max_depth: int = DEFAULT_MAX_DEPTH, delay: float = DEFAULT_DELAY,
                 max_pages: int = DEFAULT_MAX_PAGES):

        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.delay = delay
        self.max_pages = max_pages

        # State management
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.pending_urls: List[Tuple[str, int]] = [(base_url, 0)]
        self.processed_count = 0
        self.start_time = None

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.output_dir / "scraper_state.json"

        # Load config
        self.gemini_config = SCRAPER_CONFIG.copy()

        # File naming
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
        """Load previous scraping state with corruption protection"""
        if not self.state_file.exists():
            return False

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            self.visited_urls = set(state.get("visited_urls", []))
            self.failed_urls = set(state.get("failed_urls", []))
            # Convert list of lists back to list of tuples
            self.pending_urls = [tuple(item) for item in state.get("pending_urls", [(self.base_url, 0)])]
            self.processed_count = state.get("processed_count", 0)
            self.file_counter = state.get("file_counter", 0)
            self.url_to_filename = state.get("url_to_filename", {})

            print(f"📁 Loaded state: {len(self.visited_urls)} visited, {len(self.pending_urls)} pending")
            return True

        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Failed to load state (corrupt file): {e}")
            if self.state_file.exists():
                backup_path = self.state_file.with_suffix(f".bak.{int(time.time())}")
                try:
                    shutil.copy(self.state_file, backup_path)
                    print(f"   Backed up corrupt state to {backup_path}")
                except OSError:
                    pass
            return False
        except Exception as e:
            print(f"⚠️  Failed to load state: {e}")
            return False

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling"""
        try:
            parsed = urlparse(url)
            if parsed.netloc != self.domain: return False

            skip_exts = {'.pdf', '.jpg', '.png', '.gif', '.zip', '.exe', '.mp4'}
            if any(url.lower().endswith(ext) for ext in skip_exts): return False

            skip_paths = {'/login', '/logout', '/admin', '/api/', '/assets/', '/static/'}
            if any(path in url.lower() for path in skip_paths): return False

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
                full_url = urljoin(url, link['href'])
                parsed = urlparse(full_url)
                clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path,
                                     parsed.params, parsed.query, ''))

                if self.is_valid_url(clean_url) and clean_url not in self.visited_urls:
                    links.append(clean_url)

            return list(set(links))
        except Exception as e:
            print(f"❌ Failed to discover links from {url}: {e}")
            return []

    def generate_filename(self, url: str) -> str:
        """Generate a safe filename for the URL"""
        if url in self.url_to_filename:
            return self.url_to_filename[url]

        parsed = urlparse(url)
        path = parsed.path.strip('/').replace('/', '_') or 'index'

        if parsed.query:
            query_hash = hashlib.md5(parsed.query.encode()).hexdigest()[:8]
            path += f"_{query_hash}"

        filename = "".join(c for c in path if c.isalnum() or c in '-_')[:100]

        if filename in self.url_to_filename.values():
            self.file_counter += 1
            filename = f"{filename}_{self.file_counter}"

        filename += '.md'
        self.url_to_filename[url] = filename
        return filename

    def extract_content(self, url: str) -> Dict:
        """Extract content using SmartScraperGraph"""
        prompt = f"""
        Extract the main content from {url} as JSON:
        {{
            "title": "Page Title",
            "description": "Summary",
            "content": "Markdown content",
            "tags": ["tag1"],
            "navigation": ["links"]
        }}
        """

        try:
            # Instantiate fresh graph per request
            graph = SmartScraperGraph(
                prompt=prompt,
                source=url,
                config=self.gemini_config.copy()
            )

            result = graph.run()
            content_data = result.get("content", {})

            if not isinstance(content_data, dict):
                content_data = {"title": "Unknown", "content": str(content_data)}

            content_data.update({
                "url": url,
                "extraction_date": datetime.now().isoformat()
            })
            return content_data

        except Exception as e:
            print(f"❌ Extraction error for {url}: {e}")
            return None

    def save_markdown(self, content_data: Dict, filename: str):
        """Save content to file"""
        if not content_data: return False

        try:
            file_path = self.output_dir / filename
            content = f"# {content_data.get('title')}\n\n" \
                      f"> Source: {content_data.get('url')}\n\n" \
                      f"{content_data.get('content')}"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📄 Saved: {filename}")
            return True
        except Exception as e:
            print(f"❌ Save error: {e}")
            return False

    def process_url(self, url: str, depth: int) -> bool:
        print(f"🔍 Processing ({depth}): {url}")
        content = self.extract_content(url)
        filename = self.generate_filename(url)

        if self.save_markdown(content, filename):
            self.processed_count += 1
            if depth < self.max_depth:
                new_links = self.discover_links(url)
                for link in new_links:
                    if link not in self.visited_urls and link not in self.failed_urls:
                        self.pending_urls.append((link, depth + 1))
                print(f"🔗 Found {len(new_links)} new links")
            return True
        return False

    def crawl_website(self, resume: bool = True) -> Dict:
        if resume: self.load_state()
        self.start_time = time.time()

        print(f"🚀 Starting crawl: {self.base_url}")

        try:
            while self.pending_urls and self.processed_count < self.max_pages:
                url, depth = self.pending_urls.pop(0)
                if url in self.visited_urls: continue

                self.visited_urls.add(url)
                success = self.process_url(url, depth)

                if not success: self.failed_urls.add(url)

                if self.processed_count % 5 == 0: self.save_state()
                time.sleep(self.delay)

        except KeyboardInterrupt:
            print("\n⏹️  Crawl interrupted")
        finally:
            self.save_state()
            self.generate_index()
            return self.generate_summary()

    def generate_summary(self) -> Dict:
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            "processed": self.processed_count,
            "failed": len(self.failed_urls),
            "elapsed": elapsed
        }

    def generate_index(self):
        index_path = self.output_dir / "index.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(f"# Index\n\nGenerated: {datetime.now()}\n\n")
            for url, filename in sorted(self.url_to_filename.items()):
                f.write(f"- [{filename}]({filename})\n")
        print("📚 Generated index.md")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Web Doc Scraper')
    parser.add_argument('url', help='Target URL')
    parser.add_argument('--depth', type=int, default=DEFAULT_MAX_DEPTH)
    parser.add_argument('--pages', type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument('--delay', type=float, default=DEFAULT_DELAY)
    parser.add_argument('--output', default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--no-resume', action='store_true')

    args = parser.parse_args()

    if "GOOGLE_APIKEY" not in os.environ:
        print("❌ Error: GOOGLE_APIKEY environment variable is not set")
        return

    scraper = WebsiteDocumentationScraper(
        base_url=args.url,
        output_dir=args.output,
        max_depth=args.depth,
        max_pages=args.pages,
        delay=args.delay
    )
    scraper.crawl_website(resume=not args.no_resume)

if __name__ == "__main__":
    main()
