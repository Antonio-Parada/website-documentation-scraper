#!/usr/bin/env python3
"""
Quick HTTPBin Test
==================

Quick test to scrape HTTPBin documentation.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from web_doc_scraper.scraper import WebsiteDocumentationScraper

def main():
    """Quick test on HTTPBin"""
    
    # Ensure API key is set
    if "GOOGLE_APIKEY" not in os.environ:
        print("❌ Error: GOOGLE_APIKEY environment variable is not set")
        return
    
    print("🚀 Quick Test: HTTPBin Documentation")
    print("=" * 50)
    
    # Configure scraper
    output_dir = Path("C:/Users/apara/OneDrive/Documents/doc-vault/httpbin-docs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scraper = WebsiteDocumentationScraper(
        base_url="https://httpbin.org",
        output_dir=str(output_dir),
        max_depth=1,
        delay=1.0,
        max_pages=3
    )
    
    try:
        print("🔍 Starting scrape...")
        summary = scraper.crawl_website(resume=True)
        scraper.generate_index()
        
        print("✅ Scraping completed!")
        print(f"📄 Pages: {summary.get('processed_count', 0)}")
        print(f"⏱️  Time: {summary.get('elapsed_time', 0):.1f}s")
        
        # List files
        md_files = list(output_dir.glob("*.md"))
        print(f"📚 Generated {len(md_files)} files:")
        for file in md_files:
            size = file.stat().st_size
            print(f"   - {file.name} ({size:,} bytes)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
