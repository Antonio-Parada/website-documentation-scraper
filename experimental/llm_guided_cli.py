#!/usr/bin/env python3
"""
LLM-Guided CLI for Website Documentation Scraper
=================================================

This experimental module uses Gemini to intelligently configure scraper parameters
based on the target website's structure and content type.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from scrapegraphai.graphs import SmartScraperGraph

class LLMGuidedScraper:
    """LLM-guided scraper configuration system"""
    
    def __init__(self):
        self.gemini_config = {
            "llm": {
                "api_key": os.environ.get("GOOGLE_APIKEY"),
                "model": "google_genai/gemini-2.5-flash",
                "temperature": 0.1,
            },
            "verbose": False,
            "headless": True,
        }
        
        # Session memory for iterative guidance
        self.session_memory = {
            "target_url": None,
            "initial_analysis": None,
            "scraping_history": [],
            "user_preferences": {},
            "configuration_history": []
        }
    
    def analyze_website_structure(self, url: str) -> Dict:
        """Use Gemini to analyze website structure and suggest optimal scraping configuration"""
        
        system_prompt = """
        You are an expert web scraping analyst. Analyze the given website URL and provide intelligent recommendations for scraping configuration.
        
        Your task is to:
        1. Analyze the website's structure, content type, and documentation patterns
        2. Suggest optimal scraping parameters
        3. Identify specific content areas to focus on
        4. Recommend crawling strategies
        
        Return your analysis in this exact JSON format:
        {
            "website_analysis": {
                "site_type": "documentation|blog|corporate|api|github|wiki|forum|other",
                "content_depth": "shallow|medium|deep",
                "documentation_quality": "high|medium|low",
                "main_content_areas": ["area1", "area2", "area3"],
                "navigation_complexity": "simple|moderate|complex",
                "estimated_pages": 50,
                "update_frequency": "static|occasional|frequent"
            },
            "scraping_recommendations": {
                "optimal_depth": 3,
                "recommended_pages": 50,
                "suggested_delay": 2.0,
                "priority_patterns": ["/docs/", "/guide/", "/api/"],
                "avoid_patterns": ["/login", "/admin", "/search"],
                "content_focus": "main_documentation|all_content|specific_sections"
            },
            "expected_output": {
                "file_count_estimate": 25,
                "content_type": "technical_docs|tutorials|reference|mixed",
                "quality_expectation": "high|medium|low",
                "special_considerations": ["code_blocks", "tables", "images", "links"]
            },
            "crawling_strategy": {
                "approach": "breadth_first|depth_first|targeted",
                "starting_points": ["primary_url", "sitemap", "index_page"],
                "termination_criteria": "page_limit|depth_limit|content_quality",
                "resume_recommendation": true
            }
        }
        
        Be specific and actionable in your recommendations. Consider the website's purpose, structure, and likely content organization.
        """
        
        try:
            graph = SmartScraperGraph(
                prompt=system_prompt,
                source=url,
                config=self.gemini_config
            )
            
            result = graph.run()
            analysis = result.get("content", {})
            
            # Store in session memory
            self.session_memory["target_url"] = url
            self.session_memory["initial_analysis"] = analysis
            self.session_memory["configuration_history"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "initial_analysis",
                "data": analysis
            })
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing website: {e}")
            return self.get_fallback_analysis(url)
    
    def get_fallback_analysis(self, url: str) -> Dict:
        """Provide fallback analysis when LLM fails"""
        return {
            "website_analysis": {
                "site_type": "other",
                "content_depth": "medium",
                "documentation_quality": "medium",
                "main_content_areas": ["main_content"],
                "navigation_complexity": "moderate",
                "estimated_pages": 50,
                "update_frequency": "static"
            },
            "scraping_recommendations": {
                "optimal_depth": 3,
                "recommended_pages": 50,
                "suggested_delay": 2.0,
                "priority_patterns": [],
                "avoid_patterns": ["/login", "/admin"],
                "content_focus": "main_documentation"
            },
            "expected_output": {
                "file_count_estimate": 25,
                "content_type": "mixed",
                "quality_expectation": "medium",
                "special_considerations": []
            },
            "crawling_strategy": {
                "approach": "breadth_first",
                "starting_points": ["primary_url"],
                "termination_criteria": "page_limit",
                "resume_recommendation": True
            }
        }
    
    def translate_to_scraper_config(self, analysis: Dict, user_overrides: Dict = None) -> Dict:
        """Translate LLM analysis to scraper configuration parameters"""
        
        recommendations = analysis.get("scraping_recommendations", {})
        strategy = analysis.get("crawling_strategy", {})
        
        # Base configuration from LLM analysis
        config = {
            "max_depth": recommendations.get("optimal_depth", 3),
            "max_pages": recommendations.get("recommended_pages", 50),
            "delay": recommendations.get("suggested_delay", 2.0),
            "resume": strategy.get("resume_recommendation", True),
            "output_dir": "docs",
            "verbose": False
        }
        
        # Apply user overrides
        if user_overrides:
            config.update(user_overrides)
        
        return config
    
    def get_refinement_suggestions(self, initial_results: Dict) -> Dict:
        """Get refinement suggestions based on initial scraping results"""
        
        refinement_prompt = f"""
        Based on the initial scraping results, provide refinement suggestions for the next scraping iteration.
        
        Initial Results Summary:
        - Pages processed: {initial_results.get('processed_count', 0)}
        - Pages visited: {initial_results.get('visited_count', 0)}
        - Failed pages: {initial_results.get('failed_count', 0)}
        - Pending pages: {initial_results.get('pending_count', 0)}
        - Average content quality: {initial_results.get('avg_quality', 'unknown')}
        
        Session Memory:
        - Target URL: {self.session_memory.get('target_url')}
        - Previous analysis: {json.dumps(self.session_memory.get('initial_analysis', {}), indent=2)}
        
        Provide refinement suggestions in this JSON format:
        {{
            "assessment": {{
                "current_performance": "excellent|good|poor",
                "content_quality": "high|medium|low",
                "coverage_completeness": "complete|partial|minimal",
                "issues_identified": ["issue1", "issue2"]
            }},
            "refinement_suggestions": {{
                "adjust_depth": "increase|decrease|maintain",
                "adjust_pages": "increase|decrease|maintain",
                "adjust_delay": "increase|decrease|maintain",
                "focus_areas": ["area1", "area2"],
                "skip_patterns": ["pattern1", "pattern2"]
            }},
            "next_iteration": {{
                "recommended_depth": 3,
                "recommended_pages": 50,
                "recommended_delay": 2.0,
                "priority_urls": ["url1", "url2"],
                "strategy_change": "continue|pivot|focus"
            }},
            "user_guidance": {{
                "message": "Clear guidance for the user",
                "options": ["option1", "option2", "option3"],
                "recommendation": "specific_recommendation"
            }}
        }}
        """
        
        try:
            # This would be a follow-up LLM call
            # For now, return a structured response
            return {
                "assessment": {
                    "current_performance": "good",
                    "content_quality": "medium",
                    "coverage_completeness": "partial",
                    "issues_identified": []
                },
                "refinement_suggestions": {
                    "adjust_depth": "maintain",
                    "adjust_pages": "increase",
                    "adjust_delay": "maintain",
                    "focus_areas": [],
                    "skip_patterns": []
                },
                "next_iteration": {
                    "recommended_depth": 3,
                    "recommended_pages": 100,
                    "recommended_delay": 2.0,
                    "priority_urls": [],
                    "strategy_change": "continue"
                },
                "user_guidance": {
                    "message": "Initial scraping completed successfully. Consider increasing page limit for more comprehensive coverage.",
                    "options": ["Continue with current settings", "Increase page limit", "Focus on specific sections"],
                    "recommendation": "Increase page limit to 100 for better coverage"
                }
            }
            
        except Exception as e:
            print(f"⚠️  Error getting refinement suggestions: {e}")
            return None
    
    def interactive_configuration(self, url: str) -> Dict:
        """Interactive CLI for LLM-guided configuration"""
        
        print(f"🤖 LLM-Guided Website Analysis")
        print("=" * 50)
        print(f"🌐 Target URL: {url}")
        print("🔍 Analyzing website structure...")
        
        # Get LLM analysis
        analysis = self.analyze_website_structure(url)
        
        if not analysis:
            print("❌ Failed to analyze website. Using default configuration.")
            return self.get_default_config()
        
        # Display analysis
        self.display_analysis(analysis)
        
        # Get user preferences
        user_overrides = self.get_user_preferences(analysis)
        
        # Generate final configuration
        final_config = self.translate_to_scraper_config(analysis, user_overrides)
        
        print("\n✅ Configuration Complete!")
        print("=" * 50)
        self.display_final_config(final_config)
        
        return final_config
    
    def display_analysis(self, analysis: Dict):
        """Display LLM analysis in a user-friendly format"""
        
        print("\n🔍 Website Analysis Results:")
        print("-" * 30)
        
        website_info = analysis.get("website_analysis", {})
        recommendations = analysis.get("scraping_recommendations", {})
        
        print(f"📊 Site Type: {website_info.get('site_type', 'Unknown')}")
        print(f"📚 Content Depth: {website_info.get('content_depth', 'Unknown')}")
        print(f"🎯 Documentation Quality: {website_info.get('documentation_quality', 'Unknown')}")
        print(f"📄 Estimated Pages: {website_info.get('estimated_pages', 'Unknown')}")
        
        print(f"\n💡 LLM Recommendations:")
        print(f"   🔢 Optimal Depth: {recommendations.get('optimal_depth', 3)}")
        print(f"   📄 Recommended Pages: {recommendations.get('recommended_pages', 50)}")
        print(f"   ⏱️  Suggested Delay: {recommendations.get('suggested_delay', 2.0)}s")
        
        focus_areas = website_info.get('main_content_areas', [])
        if focus_areas:
            print(f"   🎯 Focus Areas: {', '.join(focus_areas)}")
    
    def get_user_preferences(self, analysis: Dict) -> Dict:
        """Get user preferences and overrides"""
        
        recommendations = analysis.get("scraping_recommendations", {})
        user_overrides = {}
        
        print(f"\n🎛️  Configuration Options:")
        print("Press Enter to accept LLM recommendations or provide custom values:")
        
        # Depth
        suggested_depth = recommendations.get("optimal_depth", 3)
        depth_input = input(f"Max Depth (suggested: {suggested_depth}): ").strip()
        if depth_input:
            try:
                user_overrides["max_depth"] = int(depth_input)
            except ValueError:
                print("⚠️  Invalid depth, using suggestion")
        
        # Pages
        suggested_pages = recommendations.get("recommended_pages", 50)
        pages_input = input(f"Max Pages (suggested: {suggested_pages}): ").strip()
        if pages_input:
            try:
                user_overrides["max_pages"] = int(pages_input)
            except ValueError:
                print("⚠️  Invalid pages, using suggestion")
        
        # Delay
        suggested_delay = recommendations.get("suggested_delay", 2.0)
        delay_input = input(f"Delay (suggested: {suggested_delay}s): ").strip()
        if delay_input:
            try:
                user_overrides["delay"] = float(delay_input)
            except ValueError:
                print("⚠️  Invalid delay, using suggestion")
        
        # Output directory
        output_input = input("Output Directory (default: docs): ").strip()
        if output_input:
            user_overrides["output_dir"] = output_input
        
        return user_overrides
    
    def display_final_config(self, config: Dict):
        """Display final configuration"""
        
        print(f"🔧 Final Configuration:")
        print(f"   📊 Max Depth: {config.get('max_depth', 3)}")
        print(f"   📄 Max Pages: {config.get('max_pages', 50)}")
        print(f"   ⏱️  Delay: {config.get('delay', 2.0)}s")
        print(f"   📁 Output: {config.get('output_dir', 'docs')}")
        print(f"   🔄 Resume: {config.get('resume', True)}")
    
    def get_default_config(self) -> Dict:
        """Get default configuration when LLM fails"""
        return {
            "max_depth": 3,
            "max_pages": 50,
            "delay": 2.0,
            "resume": True,
            "output_dir": "docs",
            "verbose": False
        }
    
    def save_session(self, filename: str = None):
        """Save current session memory"""
        if not filename:
            filename = f"llm_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        session_file = Path("experimental") / filename
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_memory, f, indent=2)
        
        print(f"💾 Session saved to: {session_file}")
    
    def load_session(self, filename: str):
        """Load previous session memory"""
        session_file = Path("experimental") / filename
        
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                self.session_memory = json.load(f)
            print(f"📁 Session loaded from: {session_file}")
            return True
        
        print(f"❌ Session file not found: {session_file}")
        return False

def main():
    """Main function for LLM-guided CLI"""
    
    parser = argparse.ArgumentParser(description="LLM-Guided Website Documentation Scraper")
    parser.add_argument("url", help="Website URL to analyze and scrape")
    parser.add_argument("--load-session", help="Load previous session file")
    parser.add_argument("--save-session", help="Save session to file")
    parser.add_argument("--non-interactive", action="store_true", help="Use LLM recommendations without user input")
    
    args = parser.parse_args()
    
    # Check API key
    if not os.environ.get("GOOGLE_APIKEY"):
        print("❌ Error: GOOGLE_APIKEY environment variable is not set")
        return
    
    # Initialize LLM-guided scraper
    guided_scraper = LLMGuidedScraper()
    
    # Load session if specified
    if args.load_session:
        guided_scraper.load_session(args.load_session)
    
    try:
        if args.non_interactive:
            # Non-interactive mode - use LLM recommendations directly
            print("🤖 Non-interactive mode: Using LLM recommendations")
            analysis = guided_scraper.analyze_website_structure(args.url)
            config = guided_scraper.translate_to_scraper_config(analysis)
            guided_scraper.display_final_config(config)
        else:
            # Interactive mode
            config = guided_scraper.interactive_configuration(args.url)
        
        # Save session if specified
        if args.save_session:
            guided_scraper.save_session(args.save_session)
        
        print(f"\n🚀 Ready to scrape with optimized configuration!")
        print(f"💡 You can now run the scraper with these parameters:")
        print(f"   python website_doc_scraper.py {args.url} --depth {config['max_depth']} --pages {config['max_pages']} --delay {config['delay']} --output {config['output_dir']}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Configuration interrupted by user")
        
        # Save session anyway
        if args.save_session:
            guided_scraper.save_session(args.save_session)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
