#!/usr/bin/env python3
"""
Test Multiple Sites Scraper
============================

Test script to scrape multiple example sites and organize them in doc-vault.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from website_doc_scraper import WebsiteDocumentationScraper

def test_site(site_config):
    """Test scraping a single site"""
    print(f"🚀 Testing: {site_config['name']}")
    print(f"📋 URL: {site_config['url']}")
    print(f"📁 Output: {site_config['output_dir']}")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path(site_config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize scraper
    scraper = WebsiteDocumentationScraper(
        base_url=site_config['url'],
        output_dir=str(output_dir),
        max_depth=site_config.get('max_depth', 2),
        delay=site_config.get('delay', 1.5),
        max_pages=site_config.get('max_pages', 5)
    )
    
    try:
        # Run the scraper
        start_time = time.time()
        summary = scraper.crawl_website(resume=True)
        scraper.generate_index()
        
        elapsed = time.time() - start_time
        
        print(f"✅ {site_config['name']} completed in {elapsed:.1f}s")
        print(f"   📄 Pages: {summary.get('processed_count', 0)}")
        print(f"   ✅ Success: {summary.get('visited_count', 0)} visited")
        print(f"   ❌ Failed: {summary.get('failed_count', 0)}")
        
        # List files
        md_files = list(output_dir.glob("*.md"))
        print(f"   📚 Generated: {len(md_files)} files")
        
        return {
            'name': site_config['name'],
            'success': True,
            'files': len(md_files),
            'pages': summary.get('processed_count', 0),
            'elapsed': elapsed
        }
        
    except Exception as e:
        print(f"❌ Failed to scrape {site_config['name']}: {e}")
        return {
            'name': site_config['name'],
            'success': False,
            'error': str(e),
            'elapsed': 0
        }

def main():
    """Test multiple sites"""
    
    # Ensure API key is set
    if "GOOGLE_APIKEY" not in os.environ:
        print("❌ Error: GOOGLE_APIKEY environment variable is not set")
        return
    
    print("🚀 Testing Website Documentation Scraper on Multiple Sites")
    print("=" * 70)
    
    # Base directory for all documentation
    base_dir = Path("C:/Users/apara/OneDrive/Documents/doc-vault")
    
    # Test sites configuration
    test_sites = [
        {
            'name': 'Your GitHub Repository',
            'url': 'https://github.com/Antonio-Parada/website-documentation-scraper',
            'output_dir': str(base_dir / 'github-repo-docs'),
            'max_depth': 2,
            'max_pages': 3,
            'delay': 1.5
        },
        {
            'name': 'HTTPBin API Documentation',
            'url': 'https://httpbin.org',
            'output_dir': str(base_dir / 'httpbin-docs'),
            'max_depth': 2,
            'max_pages': 5,
            'delay': 1.0
        },
        {
            'name': 'Python.org Documentation Sample',
            'url': 'https://docs.python.org/3/tutorial/',
            'output_dir': str(base_dir / 'python-tutorial-docs'),
            'max_depth': 1,
            'max_pages': 3,
            'delay': 2.0
        }
    ]
    
    results = []
    
    for i, site_config in enumerate(test_sites, 1):
        print(f"\\n[{i}/{len(test_sites)}] Starting test...")
        result = test_site(site_config)
        results.append(result)
        
        if i < len(test_sites):
            print("\\n⏳ Waiting 5 seconds before next test...")
            time.sleep(5)
        
        print("-" * 70)
    
    # Summary report
    print("\\n📊 FINAL SUMMARY")
    print("=" * 70)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if successful:
        print("\\n🎉 Successfully scraped:")
        for result in successful:
            print(f"   - {result['name']}: {result['files']} files, {result['pages']} pages ({result['elapsed']:.1f}s)")
    
    if failed:
        print("\\n⚠️  Failed to scrape:")
        for result in failed:
            print(f"   - {result['name']}: {result.get('error', 'Unknown error')}")
    
    print(f"\\n📁 All documentation saved to: {base_dir}")
    print("📚 Check each subfolder for the generated markdown files!")
    
    # Create master index
    create_master_index(base_dir, results)

def create_master_index(base_dir, results):
    """Create a master index of all scraped documentation"""
    
    index_content = f\"\"\"# Documentation Vault Index

> **Generated:** {datetime.now().isoformat()}  
> **Total Sites:** {len(results)}  
> **Successful:** {len([r for r in results if r['success']])}

## 📚 Available Documentation

\"\"\"
    
    for result in results:
        if result['success']:
            folder_name = Path(result.get('output_dir', '')).name
            index_content += f\"\"\"
### {result['name']}
- **Folder:** `{folder_name}/`
- **Files:** {result.get('files', 0)} markdown files
- **Pages:** {result.get('pages', 0)} processed
- **Time:** {result.get('elapsed', 0):.1f} seconds

\"\"\"
        else:
            index_content += f\"\"\"
### {result['name']} (Failed)
- **Error:** {result.get('error', 'Unknown error')}

\"\"\"
    
    index_content += \"\"\"
## 🔍 How to Use

1. Navigate to any subfolder
2. Open `index.md` for navigation
3. Browse individual markdown files
4. Use a markdown viewer for best experience

---

*Generated automatically by Website Documentation Scraper*
\"\"\"
    
    # Save master index
    with open(base_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"📋 Master index created: {base_dir / 'README.md'}")

if __name__ == "__main__":
    main()
