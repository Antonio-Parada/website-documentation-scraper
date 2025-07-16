"""
Complete GitHub Repository Crawler with Gemini 2.5 Flash
=========================================================

This is the complete solution for crawling GitHub repositories using ScrapeGraph AI
with Google's Gemini 2.5 Flash model. It includes:

- Single repository crawling
- Batch processing
- CSV and JSON export
- Error handling
- Progress tracking
- Customizable prompts
- Rate limiting

Usage:
    python complete_github_crawler.py
"""

import os
import json
import csv
import time
import argparse
from datetime import datetime
from typing import List, Dict, Optional
from scrapegraphai.graphs import SmartScraperGraph

# Set the Gemini API key (set this as an environment variable)
# os.environ["GOOGLE_APIKEY"] = "your_gemini_api_key_here"

class GitHubRepositoryCrawler:
    """Complete GitHub repository crawler with Gemini 2.5 Flash"""
    
    def __init__(self, delay: float = 2.0, verbose: bool = False):
        """
        Initialize the crawler
        
        Args:
            delay: Delay between requests in seconds
            verbose: Enable verbose output
        """
        self.delay = delay
        self.verbose = verbose
        self.results = []
        
        # Configuration for Gemini 2.5 Flash
        self.config = {
            "llm": {
                "api_key": os.environ["GOOGLE_APIKEY"],
                "model": "google_genai/gemini-2.5-flash",
                "temperature": 0.1,
            },
            "verbose": self.verbose,
            "headless": True,
        }
    
    def get_basic_prompt(self) -> str:
        """Get basic repository information prompt"""
        return """Extract repository information in this exact JSON format:
        {
            "name": "repository name",
            "owner": "owner username",
            "description": "repository description",
            "stars": "star count (just the number)",
            "forks": "fork count (just the number)", 
            "issues": "open issues count (just the number)",
            "language": "primary programming language",
            "license": "license type",
            "topics": ["topic1", "topic2", "topic3"],
            "last_release": "latest release version",
            "readme_summary": "brief summary of what this repository does"
        }
        
        Extract accurate information from the GitHub repository page.
        """
    
    def get_detailed_prompt(self) -> str:
        """Get detailed repository information prompt"""
        return """Extract comprehensive repository information in JSON format:
        {
            "basic_info": {
                "name": "repository name",
                "owner": "owner username",
                "description": "repository description",
                "url": "repository URL",
                "homepage": "project homepage if available"
            },
            "statistics": {
                "stars": "star count",
                "forks": "fork count",
                "watchers": "watcher count",
                "issues": "open issues count",
                "pull_requests": "open pull requests count",
                "contributors": "contributor count if visible"
            },
            "technical_info": {
                "primary_language": "main programming language",
                "languages": ["list of all languages"],
                "license": "license type",
                "size": "repository size",
                "default_branch": "default branch name"
            },
            "activity": {
                "last_commit": "last commit date",
                "created_date": "creation date",
                "last_release": "latest release version",
                "release_date": "latest release date"
            },
            "content": {
                "readme_summary": "comprehensive summary of README",
                "topics": ["repository topics"],
                "has_wiki": "true/false",
                "has_pages": "true/false",
                "has_actions": "true/false",
                "has_discussions": "true/false"
            },
            "community": {
                "has_code_of_conduct": "true/false",
                "has_contributing": "true/false",
                "has_security": "true/false",
                "has_issue_templates": "true/false"
            }
        }
        
        Focus on accuracy and completeness of the extracted information.
        """
    
    def crawl_repository(self, repo_url: str, detailed: bool = False) -> Dict:
        """
        Crawl a single repository
        
        Args:
            repo_url: URL of the GitHub repository
            detailed: Whether to extract detailed information
            
        Returns:
            Dictionary containing crawled data
        """
        prompt = self.get_detailed_prompt() if detailed else self.get_basic_prompt()
        
        graph = SmartScraperGraph(
            prompt=prompt,
            source=repo_url,
            config=self.config
        )
        
        try:
            result = graph.run()
            return {
                "url": repo_url,
                "success": True,
                "data": result.get("content", {}),
                "timestamp": datetime.now().isoformat(),
                "error": None,
                "detailed": detailed
            }
        except Exception as e:
            return {
                "url": repo_url,
                "success": False,
                "data": {},
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "detailed": detailed
            }
    
    def crawl_repositories(self, repo_urls: List[str], detailed: bool = False) -> List[Dict]:
        """
        Crawl multiple repositories
        
        Args:
            repo_urls: List of GitHub repository URLs
            detailed: Whether to extract detailed information
            
        Returns:
            List of dictionaries containing crawled data
        """
        total = len(repo_urls)
        
        print(f"🚀 Starting {'detailed' if detailed else 'basic'} crawling of {total} repositories...")
        print("=" * 70)
        
        for i, url in enumerate(repo_urls, 1):
            print(f"🔍 Crawling ({i}/{total}): {url}")
            
            result = self.crawl_repository(url, detailed)
            self.results.append(result)
            
            if result["success"]:
                repo_name = result["data"].get("name") or result["data"].get("basic_info", {}).get("name", "Unknown")
                print(f"✅ Successfully crawled: {repo_name}")
            else:
                print(f"❌ Failed to crawl: {result['error']}")
            
            # Show progress
            progress = (i / total) * 100
            print(f"📊 Progress: {progress:.1f}% ({i}/{total})")
            
            # Be respectful with delays
            if i < total:
                print(f"⏳ Waiting {self.delay} seconds...")
                time.sleep(self.delay)
            
            print("-" * 70)
        
        return self.results
    
    def export_to_csv(self, filename: str = "github_repositories.csv") -> None:
        """Export results to CSV file"""
        if not self.results:
            print("⚠️  No results to export")
            return
        
        # Check if we have detailed results
        has_detailed = any(r.get("detailed", False) for r in self.results)
        
        if has_detailed:
            fieldnames = [
                "url", "name", "owner", "description", "stars", "forks", "issues",
                "language", "license", "topics", "last_release", "readme_summary",
                "watchers", "contributors", "created_date", "has_wiki", "has_pages",
                "success", "error", "timestamp"
            ]
        else:
            fieldnames = [
                "url", "name", "owner", "description", "stars", "forks", "issues",
                "language", "license", "topics", "last_release", "readme_summary",
                "success", "error", "timestamp"
            ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                row = {
                    "url": result["url"],
                    "success": result["success"],
                    "error": result["error"],
                    "timestamp": result["timestamp"]
                }
                
                if result["success"] and result["data"]:
                    data = result["data"]
                    
                    if result.get("detailed", False):
                        # Handle detailed format
                        basic_info = data.get("basic_info", {})
                        stats = data.get("statistics", {})
                        tech_info = data.get("technical_info", {})
                        activity = data.get("activity", {})
                        content = data.get("content", {})
                        
                        row.update({
                            "name": basic_info.get("name", ""),
                            "owner": basic_info.get("owner", ""),
                            "description": basic_info.get("description", ""),
                            "stars": stats.get("stars", ""),
                            "forks": stats.get("forks", ""),
                            "issues": stats.get("issues", ""),
                            "language": tech_info.get("primary_language", ""),
                            "license": tech_info.get("license", ""),
                            "topics": ", ".join(content.get("topics", [])),
                            "last_release": activity.get("last_release", ""),
                            "readme_summary": content.get("readme_summary", ""),
                            "watchers": stats.get("watchers", ""),
                            "contributors": stats.get("contributors", ""),
                            "created_date": activity.get("created_date", ""),
                            "has_wiki": content.get("has_wiki", ""),
                            "has_pages": content.get("has_pages", ""),
                        })
                    else:
                        # Handle basic format
                        row.update({
                            "name": data.get("name", ""),
                            "owner": data.get("owner", ""),
                            "description": data.get("description", ""),
                            "stars": data.get("stars", ""),
                            "forks": data.get("forks", ""),
                            "issues": data.get("issues", ""),
                            "language": data.get("language", ""),
                            "license": data.get("license", ""),
                            "topics": ", ".join(data.get("topics", [])) if data.get("topics") else "",
                            "last_release": data.get("last_release", ""),
                            "readme_summary": data.get("readme_summary", ""),
                        })
                
                writer.writerow(row)
        
        print(f"📊 Results exported to {filename}")
    
    def export_to_json(self, filename: str = "github_repositories.json") -> None:
        """Export results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"📄 Results exported to {filename}")
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.results:
            return {}
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        failed = total - successful
        
        return {
            "total_crawled": total,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            "average_delay": self.delay,
            "crawl_type": "detailed" if any(r.get("detailed", False) for r in self.results) else "basic"
        }
    
    def print_summary(self) -> None:
        """Print crawling summary"""
        summary = self.get_summary()
        if not summary:
            print("⚠️  No results to summarize")
            return
        
        print("\n📈 Crawling Summary:")
        print("=" * 40)
        for key, value in summary.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="GitHub Repository Crawler with Gemini 2.5 Flash")
    parser.add_argument("--repos", nargs="+", help="GitHub repository URLs to crawl")
    parser.add_argument("--detailed", action="store_true", help="Extract detailed information")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests (seconds)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", default="github_repositories", help="Output filename (without extension)")
    
    args = parser.parse_args()
    
    # Default repositories if none provided
    if not args.repos:
        args.repos = [
            "https://github.com/ScrapeGraphAI/Scrapegraph-ai",
            "https://github.com/microsoft/vscode",
            "https://github.com/pytorch/pytorch"
        ]
    
    print("🚀 GitHub Repository Crawler with Gemini 2.5 Flash")
    print("=" * 60)
    print(f"📋 Crawling {len(args.repos)} repositories...")
    print(f"⚙️  Mode: {'Detailed' if args.detailed else 'Basic'}")
    print(f"⏱️  Delay: {args.delay} seconds")
    print()
    
    # Initialize crawler
    crawler = GitHubRepositoryCrawler(delay=args.delay, verbose=args.verbose)
    
    # Crawl repositories
    results = crawler.crawl_repositories(args.repos, detailed=args.detailed)
    
    # Export results
    print("\n📤 Exporting results...")
    crawler.export_to_csv(f"{args.output}.csv")
    crawler.export_to_json(f"{args.output}.json")
    
    # Show summary
    crawler.print_summary()
    
    print("\n✨ Crawling completed successfully!")
    print(f"💾 Check {args.output}.csv and {args.output}.json for results")

if __name__ == "__main__":
    main()
