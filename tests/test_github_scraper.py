#!/usr/bin/env python3
"""
Test GitHub Repository Scraper
==============================

Test script to scrape your GitHub repository and save documentation
to the doc-vault folder.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from web_doc_scraper.scraper import WebsiteDocumentationScraper

def main():
    """Test the scraper on your GitHub repository"""
    
    # Ensure API key is set
    if "GOOGLE_APIKEY" not in os.environ:
        print("❌ Error: GOOGLE_APIKEY environment variable is not set")
        print("Please set your Gemini API key first.")
        return
    
    print("🚀 Testing Website Documentation Scraper")
    print("=" * 60)
    
    # Configure scraper for your GitHub repository
    github_url = "https://github.com/Antonio-Parada/website-documentation-scraper"
    output_dir = Path("C:/Users/apara/OneDrive/Documents/doc-vault/github-repo-docs")
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    print(f"📋 Target URL: {github_url}")
    print(f"📁 Output Directory: {output_dir}")
    print(f"⚙️  Configuration:")
    print(f"   - Max Depth: 2 (GitHub repo + README)")
    print(f"   - Max Pages: 10 (lightweight test)")
    print(f"   - Delay: 1.5 seconds")
    print()
    
    # Initialize scraper
    scraper = WebsiteDocumentationScraper(
        base_url=github_url,
        output_dir=str(output_dir),
        max_depth=2,  # Limited depth for GitHub
        delay=1.5,    # Respectful delay
        max_pages=10  # Small test
    )
    
    try:
        # Run the scraper
        print("🔍 Starting scrape...")
        summary = scraper.crawl_website(resume=True)
        
        # Generate index
        scraper.generate_index()
        
        print("\n✨ Scraping completed successfully!")
        print("=" * 60)
        
        # Display summary
        print("📈 Summary:")
        print(f"   Pages processed: {summary.get('processed_count', 0)}")
        print(f"   URLs visited: {summary.get('visited_count', 0)}")
        print(f"   Failed URLs: {summary.get('failed_count', 0)}")
        print(f"   Time elapsed: {summary.get('elapsed_time', 0):.1f} seconds")
        print(f"   Pages per second: {summary.get('pages_per_second', 0):.2f}")
        
        # List generated files
        print(f"\n📄 Generated files in {output_dir}:")
        md_files = list(output_dir.glob("*.md"))
        for file in sorted(md_files):
            file_size = file.stat().st_size
            print(f"   - {file.name} ({file_size:,} bytes)")
        
        if md_files:
            print(f"\n🎉 Successfully generated {len(md_files)} markdown files!")
            print(f"📚 Check the index.md file for navigation")
        else:
            print("\n⚠️  No markdown files were generated")
            
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n📁 Output saved to: {output_dir}")
    print("🔗 You can now view the generated documentation!")

if __name__ == "__main__":
    main()
