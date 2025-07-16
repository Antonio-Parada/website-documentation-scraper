#!/usr/bin/env python3
"""
Smart Scraper Integration
=========================

This module integrates LLM-guided configuration with the actual scraping process,
providing an end-to-end intelligent scraping solution.
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from llm_guided_cli import LLMGuidedScraper
from website_doc_scraper import WebsiteDocumentationScraper

class SmartScraper:
    """Intelligent scraper that uses LLM guidance for optimal configuration"""
    
    def __init__(self):
        self.llm_guide = LLMGuidedScraper()
        self.scraper = None
        self.current_config = None
        
    def analyze_and_scrape(self, url: str, interactive: bool = True, 
                          user_overrides: dict = None) -> dict:
        """Complete workflow: analyze, configure, and scrape"""
        
        print("🚀 Smart Scraper - LLM-Guided Website Documentation")
        print("=" * 60)
        
# Pre-step: Perform BeautifulSoup pre-analysis
        pre_analysis = self.llm_guide.pre_analyze_with_beautifulsoup(url)
        if pre_analysis:
            print("Pre-analysis data:", pre_analysis)

        # Step 1: Get LLM analysis and configuration
        if interactive:
            config = self.llm_guide.interactive_configuration(url)
        else:
            analysis = self.llm_guide.analyze_website_structure(url)
            config = self.llm_guide.translate_to_scraper_config(analysis, user_overrides)
        
        self.current_config = config
        
        # Step 2: Initialize scraper with LLM-optimized configuration
        self.scraper = WebsiteDocumentationScraper(
            base_url=url,
            output_dir=config.get('output_dir', 'docs'),
            max_depth=config.get('max_depth', 3),
            delay=config.get('delay', 2.0),
            max_pages=config.get('max_pages', 50)
        )
        
        print(f"\n🔄 Starting intelligent scraping process...")
        print(f"📊 Configuration: depth={config['max_depth']}, pages={config['max_pages']}, delay={config['delay']}")
        
        # Step 3: Run the scraper
        try:
            summary = self.scraper.crawl_website(resume=config.get('resume', True))
            self.scraper.generate_index()
            
            print(f"\n✅ Scraping completed successfully!")
            
            # Step 4: Analyze results and provide insights
            insights = self.analyze_results(summary)
            
            return {
                'config': config,
                'summary': summary,
                'insights': insights,
                'success': True
            }
            
        except Exception as e:
            print(f"\n❌ Scraping failed: {e}")
            return {
                'config': config,
                'error': str(e),
                'success': False
            }
    
    def analyze_results(self, summary: dict) -> dict:
        """Analyze scraping results and provide insights"""
        
        print(f"\n🔍 Analyzing scraping results...")
        
        # Calculate efficiency metrics
        processed = summary.get('processed_count', 0)
        visited = summary.get('visited_count', 0)
        failed = summary.get('failed_count', 0)
        pending = summary.get('pending_count', 0)
        elapsed = summary.get('elapsed_time', 0)
        
        efficiency = (processed / visited) * 100 if visited > 0 else 0
        completion_rate = (processed / (processed + pending)) * 100 if (processed + pending) > 0 else 100
        
        insights = {
            'efficiency': efficiency,
            'completion_rate': completion_rate,
            'pages_per_second': summary.get('pages_per_second', 0),
            'failure_rate': (failed / visited) * 100 if visited > 0 else 0,
            'performance_grade': self.calculate_performance_grade(efficiency, completion_rate, failed, processed),
            'recommendations': self.generate_recommendations(summary)
        }
        
        # Display insights
        print(f"📊 Scraping Insights:")
        print(f"   ⚡ Efficiency: {efficiency:.1f}%")
        print(f"   📈 Completion: {completion_rate:.1f}%")
        print(f"   🚀 Speed: {summary.get('pages_per_second', 0):.2f} pages/sec")
        print(f"   🎯 Performance Grade: {insights['performance_grade']}")
        
        if insights['recommendations']:
            print(f"   💡 Recommendations:")
            for rec in insights['recommendations']:
                print(f"      • {rec}")
        
        return insights
    
    def calculate_performance_grade(self, efficiency: float, completion: float, 
                                  failed: int, processed: int) -> str:
        """Calculate overall performance grade"""
        
        score = 0
        
        # Efficiency scoring (40 points)
        if efficiency >= 80:
            score += 40
        elif efficiency >= 60:
            score += 30
        elif efficiency >= 40:
            score += 20
        else:
            score += 10
        
        # Completion scoring (30 points)
        if completion >= 90:
            score += 30
        elif completion >= 70:
            score += 20
        elif completion >= 50:
            score += 15
        else:
            score += 5
        
        # Volume scoring (20 points)
        if processed >= 50:
            score += 20
        elif processed >= 20:
            score += 15
        elif processed >= 10:
            score += 10
        else:
            score += 5
        
        # Reliability scoring (10 points)
        if failed == 0:
            score += 10
        elif failed <= 2:
            score += 7
        elif failed <= 5:
            score += 5
        else:
            score += 2
        
        # Convert to letter grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def generate_recommendations(self, summary: dict) -> list:
        """Generate actionable recommendations based on results"""
        
        recommendations = []
        
        processed = summary.get('processed_count', 0)
        visited = summary.get('visited_count', 0)
        failed = summary.get('failed_count', 0)
        pending = summary.get('pending_count', 0)
        speed = summary.get('pages_per_second', 0)
        
        # Volume recommendations
        if processed < 10:
            recommendations.append("Consider increasing max_pages to capture more content")
        elif pending > processed * 2:
            recommendations.append("Many pages remain unprocessed - consider resuming crawl")
        
        # Speed recommendations
        if speed < 0.1:
            recommendations.append("Scraping is quite slow - consider reducing delay if appropriate")
        elif speed > 1.0:
            recommendations.append("High speed detected - ensure respectful crawling practices")
        
        # Reliability recommendations
        if failed > processed * 0.1:
            recommendations.append("High failure rate - check network connectivity and site accessibility")
        
        # Completion recommendations
        completion_rate = (processed / (processed + pending)) * 100 if (processed + pending) > 0 else 100
        if completion_rate < 50:
            recommendations.append("Low completion rate - consider increasing max_pages or resuming")
        
        return recommendations
    
    def suggest_next_iteration(self, results: dict) -> dict:
        """Suggest configuration for next iteration based on results"""
        
        if not results.get('success'):
            return None
        
        summary = results['summary']
        current_config = results['config']
        
        # Use LLM to get refinement suggestions
        refinement = self.llm_guide.get_refinement_suggestions(summary)
        
        if refinement:
            next_config = current_config.copy()
            
            # Apply refinement suggestions
            next_iteration = refinement.get('next_iteration', {})
            if next_iteration:
                next_config.update({
                    'max_depth': next_iteration.get('recommended_depth', current_config['max_depth']),
                    'max_pages': next_iteration.get('recommended_pages', current_config['max_pages']),
                    'delay': next_iteration.get('recommended_delay', current_config['delay'])
                })
            
            return {
                'config': next_config,
                'guidance': refinement.get('user_guidance', {}),
                'assessment': refinement.get('assessment', {})
            }
        
        return None

def main():
    """Main function for smart scraper CLI"""
    
    parser = argparse.ArgumentParser(description="Smart Scraper - LLM-Guided Website Documentation")
    parser.add_argument("url", help="Website URL to analyze and scrape")
    parser.add_argument("--non-interactive", action="store_true", help="Use LLM recommendations without user input")
    parser.add_argument("--depth", type=int, help="Override max depth")
    parser.add_argument("--pages", type=int, help="Override max pages")
    parser.add_argument("--delay", type=float, help="Override delay")
    parser.add_argument("--output", help="Override output directory")
    parser.add_argument("--iterate", action="store_true", help="Suggest next iteration after completion")
    
    args = parser.parse_args()
    
    # Check API key
    if not os.environ.get("GOOGLE_APIKEY"):
        print("❌ Error: GOOGLE_APIKEY environment variable is not set")
        return
    
    # Prepare user overrides
    user_overrides = {}
    if args.depth:
        user_overrides['max_depth'] = args.depth
    if args.pages:
        user_overrides['max_pages'] = args.pages
    if args.delay:
        user_overrides['delay'] = args.delay
    if args.output:
        user_overrides['output_dir'] = args.output
    
    # Initialize smart scraper
    smart_scraper = SmartScraper()
    
    try:
        # Run intelligent scraping
        results = smart_scraper.analyze_and_scrape(
            url=args.url,
            interactive=not args.non_interactive,
            user_overrides=user_overrides
        )
        
        if results['success']:
            print(f"\n🎉 Smart scraping completed successfully!")
            print(f"📁 Results saved to: {results['config']['output_dir']}")
            
            # Suggest next iteration if requested
            if args.iterate:
                next_suggestion = smart_scraper.suggest_next_iteration(results)
                if next_suggestion:
                    print(f"\n🔮 Next Iteration Suggestions:")
                    guidance = next_suggestion.get('guidance', {})
                    if guidance:
                        print(f"💡 {guidance.get('message', 'Consider running another iteration')}")
                        print(f"🎯 Recommendation: {guidance.get('recommendation', 'Continue with current approach')}")
                    
                    next_config = next_suggestion.get('config', {})
                    if next_config:
                        print(f"⚙️  Suggested next config: depth={next_config.get('max_depth')}, pages={next_config.get('max_pages')}, delay={next_config.get('delay')}")
        else:
            print(f"\n❌ Smart scraping failed: {results.get('error', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Smart scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
