"""
Quick test of the GitHub batch crawler
"""

import os
import sys
sys.path.append(".")

from github_batch_crawler import GitHubRepoCrawler

def test_crawler():
    print("🧪 Testing GitHub Batch Crawler with Gemini 2.5 Flash")
    print("=" * 55)
    print()
    
    # Test with just 2 repositories
    test_repos = [
        "https://github.com/ScrapeGraphAI/Scrapegraph-ai",
        "https://github.com/microsoft/vscode"
    ]
    
    # Initialize crawler with shorter delay for testing
    crawler = GitHubRepoCrawler(delay=1)
    
    # Crawl repositories
    print("🔄 Starting test crawling...")
    results = crawler.crawl_repositories(test_repos)
    
    # Export results
    print("\n📤 Exporting test results...")
    crawler.export_to_csv("test_github_repositories.csv")
    crawler.export_to_json("test_github_repositories.json")
    
    # Show summary
    print("\n📈 Test Summary:")
    summary = crawler.get_summary()
    for key, value in summary.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    test_crawler()
