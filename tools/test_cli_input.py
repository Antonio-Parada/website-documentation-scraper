#!/usr/bin/env python3
"""
CLI Input Testing Tool
======================

Tool to test and validate CLI input parameters before running the main scraper.
This helps debug argument parsing and parameter validation.
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

def test_cli_arguments():
    """Test CLI argument parsing with various scenarios"""
    
    print("🧪 CLI Input Testing Tool")
    print("=" * 50)
    
    # Test scenarios
    test_cases = [
        # Basic usage
        ["https://example.com"],
        
        # With depth and pages
        ["https://example.com", "--depth", "3", "--pages", "50"],
        
        # Short flags
        ["https://example.com", "-d", "2", "-p", "25"],
        
        # Custom output
        ["https://example.com", "--output", "test_docs"],
        
        # All options
        ["https://example.com", "--depth", "4", "--pages", "100", "--output", "full_test", "--delay", "1.5", "--verbose"],
        
        # No resume
        ["https://example.com", "--no-resume"],
        
        # URL without https
        ["example.com", "--depth", "2"],
        
        # Invalid depth (should fail)
        ["https://example.com", "--depth", "0"],
        
        # Invalid pages (should fail)
        ["https://example.com", "--pages", "-1"],
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {' '.join(test_case)}")
        print("-" * 40)
        
        try:
            # Parse arguments
            parser = create_test_parser()
            args = parser.parse_args(test_case)
            
            # Validate and process
            result = validate_args(args)
            
            if result["valid"]:
                print(f"✅ PASSED")
                print(f"   URL: {result['url']}")
                print(f"   Depth: {result['depth']}")
                print(f"   Pages: {result['pages']}")
                print(f"   Output: {result['output']}")
                print(f"   Delay: {result['delay']}")
                print(f"   Resume: {result['resume']}")
                print(f"   Verbose: {result['verbose']}")
            else:
                print(f"❌ FAILED: {result['error']}")
                
        except SystemExit:
            print("❌ FAILED: Argument parsing error")
        except Exception as e:
            print(f"❌ FAILED: {e}")

def create_test_parser():
    """Create argument parser for testing"""
    parser = argparse.ArgumentParser(
        description='Website Documentation Scraper with Gemini 2.5 Flash',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('url', help='Website URL to scrape')
    parser.add_argument('--depth', '-d', type=int, default=3, 
                      help='Maximum crawl depth (default: 3)')
    parser.add_argument('--pages', '-p', type=int, default=100,
                      help='Maximum number of pages to process (default: 100)')
    parser.add_argument('--output', '-o', default='docs',
                      help='Output directory for markdown files (default: docs)')
    parser.add_argument('--delay', type=float, default=2.0,
                      help='Delay between requests in seconds (default: 2.0)')
    parser.add_argument('--no-resume', action='store_true',
                      help='Do not resume from previous crawl state')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    
    return parser

def validate_args(args):
    """Validate parsed arguments"""
    result = {
        "valid": True,
        "error": None,
        "url": args.url,
        "depth": args.depth,
        "pages": args.pages,
        "output": args.output,
        "delay": args.delay,
        "resume": not args.no_resume,
        "verbose": args.verbose
    }
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        result["url"] = 'https://' + args.url
    
    # Validate depth
    if args.depth < 1:
        result["valid"] = False
        result["error"] = "Depth must be at least 1"
        return result
    
    if args.depth > 10:
        result["valid"] = False
        result["error"] = "Depth should not exceed 10 for safety"
        return result
    
    # Validate pages
    if args.pages < 1:
        result["valid"] = False
        result["error"] = "Pages must be at least 1"
        return result
    
    if args.pages > 1000:
        result["valid"] = False
        result["error"] = "Pages should not exceed 1000 for safety"
        return result
    
    # Validate delay
    if args.delay < 0.1:
        result["valid"] = False
        result["error"] = "Delay must be at least 0.1 seconds"
        return result
    
    if args.delay > 60:
        result["valid"] = False
        result["error"] = "Delay should not exceed 60 seconds"
        return result
    
    # Validate output directory
    try:
        Path(args.output).resolve()
    except Exception:
        result["valid"] = False
        result["error"] = f"Invalid output directory: {args.output}"
        return result
    
    return result

def interactive_test():
    """Interactive CLI testing"""
    print("\n🎯 Interactive CLI Testing")
    print("=" * 50)
    print("Enter CLI arguments to test (or 'quit' to exit):")
    print("Example: https://example.com --depth 3 --pages 50")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            # Parse user input
            args = user_input.split()
            
            print(f"\n🔍 Testing: {user_input}")
            print("-" * 30)
            
            # Test the arguments
            parser = create_test_parser()
            parsed_args = parser.parse_args(args)
            result = validate_args(parsed_args)
            
            if result["valid"]:
                print("✅ Valid arguments!")
                print(f"   Processed URL: {result['url']}")
                print(f"   Configuration: depth={result['depth']}, pages={result['pages']}")
                print(f"   Output: {result['output']}")
                print(f"   Timing: delay={result['delay']}, resume={result['resume']}")
            else:
                print(f"❌ Invalid: {result['error']}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except SystemExit:
            print("❌ Invalid arguments - check syntax")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main testing function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        test_cli_arguments()
        
        # Ask if user wants interactive mode
        response = input("\n🎯 Run interactive testing? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            interactive_test()

if __name__ == "__main__":
    main()
