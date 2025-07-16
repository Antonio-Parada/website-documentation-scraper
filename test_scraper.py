"""
Simple test of the website documentation scraper
"""

from website_doc_scraper import WebsiteDocumentationScraper

def test_scraper():
    print("🧪 Testing Website Documentation Scraper")
    print("=" * 50)
    
    # Test with a simple website
    scraper = WebsiteDocumentationScraper(
        base_url="https://httpbin.org/",
        output_dir="test_docs",
        max_depth=1,
        delay=1.0,
        max_pages=3
    )
    
    try:
        summary = scraper.crawl_website(resume=False)
        scraper.generate_index()
        
        print("\n✅ Test completed successfully!")
        print("Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper()
