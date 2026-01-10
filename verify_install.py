#!/usr/bin/env python3
import sys
import os
import shutil

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

try:
    from web_doc_scraper.scraper import WebsiteDocumentationScraper
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you are running this from the project root and dependencies are installed.")
    sys.exit(1)

def verify():
    print("🔍 Verifying Website Documentation Scraper Installation...")

    # Check API Key
    if "GOOGLE_APIKEY" not in os.environ:
        print("❌ Error: GOOGLE_APIKEY environment variable is not set.")
        print("Please set it to your Gemini API key.")
        sys.exit(1)
    print("✅ GOOGLE_APIKEY found.")

    # Setup test
    test_url = "http://example.com"
    output_dir = "test_output"

    # Clean previous output
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    print(f"🚀 Attempting to scrape single page: {test_url}")

    try:
        scraper = WebsiteDocumentationScraper(
            base_url=test_url,
            output_dir=output_dir,
            max_depth=1,
            max_pages=1,
            delay=1.0
        )

        # Override config to be less verbose if needed,
        # but the default config in config.py should be used.

        # Run scraping for just one page
        # We can use process_url directly to avoid the loop overhead/logic of crawl_website for a simple test
        # But crawl_website(resume=False) is better integration test
        summary = scraper.crawl_website(resume=False)

        if summary['processed_count'] > 0:
            print(f"✅ Successfully scraped {summary['processed_count']} page(s).")
            print(f"✅ Output saved to {output_dir}/")
        else:
            print("⚠️  Scraper ran but processed 0 pages. Check network or API quota.")

    except Exception as e:
        print(f"❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("✨ Verification Complete.")

if __name__ == "__main__":
    verify()
