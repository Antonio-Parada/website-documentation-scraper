#!/usr/bin/env python3
"""
Output Analysis Tool
====================

Tool to analyze and validate scraper output including:
- Markdown file quality
- Content structure
- File organization
- Performance metrics
- Error detection
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import re

def analyze_output_directory(output_dir):
    """Analyze a scraper output directory"""
    
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print(f"❌ Output directory does not exist: {output_dir}")
        return None
    
    print(f"🔍 Analyzing Output Directory: {output_dir}")
    print("=" * 60)
    
    analysis = {
        "directory": str(output_path),
        "timestamp": datetime.now().isoformat(),
        "files": [],
        "summary": {},
        "issues": [],
        "recommendations": []
    }
    
    # Find all markdown files
    md_files = list(output_path.glob("*.md"))
    state_files = list(output_path.glob("*.json"))
    
    print(f"📄 Found {len(md_files)} markdown files")
    print(f"📊 Found {len(state_files)} state files")
    
    # Analyze each markdown file
    total_size = 0
    total_words = 0
    
    for md_file in md_files:
        file_analysis = analyze_markdown_file(md_file)
        analysis["files"].append(file_analysis)
        total_size += file_analysis["size"]
        total_words += file_analysis["word_count"]
        
        # Check for issues
        if file_analysis["size"] < 100:
            analysis["issues"].append(f"Very small file: {md_file.name} ({file_analysis['size']} bytes)")
        
        if file_analysis["word_count"] < 10:
            analysis["issues"].append(f"Very few words: {md_file.name} ({file_analysis['word_count']} words)")
        
        if not file_analysis["has_title"]:
            analysis["issues"].append(f"Missing title: {md_file.name}")
    
    # Analyze state files
    for state_file in state_files:
        if state_file.name == "scraper_state.json":
            state_analysis = analyze_state_file(state_file)
            analysis["state"] = state_analysis
    
    # Generate summary
    analysis["summary"] = {
        "total_files": len(md_files),
        "total_size": total_size,
        "average_size": total_size / len(md_files) if md_files else 0,
        "total_words": total_words,
        "average_words": total_words / len(md_files) if md_files else 0,
        "issues_found": len(analysis["issues"])
    }
    
    # Generate recommendations
    generate_recommendations(analysis)
    
    return analysis

def analyze_markdown_file(file_path):
    """Analyze a single markdown file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic metrics
        file_size = file_path.stat().st_size
        line_count = len(content.split('\n'))
        word_count = len(content.split())
        
        # Check structure
        has_title = bool(re.search(r'^# .+', content, re.MULTILINE))
        has_source = 'Source:' in content
        has_generated = 'Generated:' in content
        has_description = 'Description:' in content
        
        # Count elements
        heading_count = len(re.findall(r'^#+\s', content, re.MULTILINE))
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', content))
        code_block_count = len(re.findall(r'```', content))
        
        # Extract metadata
        title_match = re.search(r'^# (.+)', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "No title"
        
        source_match = re.search(r'Source:\*\* (.+)', content)
        source_url = source_match.group(1) if source_match else "Unknown"
        
        return {
            "filename": file_path.name,
            "size": file_size,
            "line_count": line_count,
            "word_count": word_count,
            "title": title,
            "source_url": source_url,
            "has_title": has_title,
            "has_source": has_source,
            "has_generated": has_generated,
            "has_description": has_description,
            "heading_count": heading_count,
            "link_count": link_count,
            "code_block_count": code_block_count // 2,  # Divide by 2 for opening/closing
            "quality_score": calculate_quality_score(content)
        }
        
    except Exception as e:
        return {
            "filename": file_path.name,
            "error": str(e),
            "size": 0,
            "word_count": 0,
            "quality_score": 0
        }

def calculate_quality_score(content):
    """Calculate a quality score for markdown content"""
    score = 0
    
    # Basic structure (40 points)
    if re.search(r'^# .+', content, re.MULTILINE):
        score += 10  # Has title
    if 'Source:' in content:
        score += 10  # Has source
    if 'Generated:' in content:
        score += 10  # Has timestamp
    if 'Description:' in content:
        score += 10  # Has description
    
    # Content richness (30 points)
    heading_count = len(re.findall(r'^#+\s', content, re.MULTILINE))
    if heading_count >= 3:
        score += 10  # Good heading structure
    
    link_count = len(re.findall(r'\[.*?\]\(.*?\)', content))
    if link_count >= 3:
        score += 10  # Good link content
    
    word_count = len(content.split())
    if word_count >= 100:
        score += 10  # Substantial content
    
    # Formatting (20 points)
    if '```' in content:
        score += 10  # Has code blocks
    if re.search(r'^\* .+', content, re.MULTILINE):
        score += 5   # Has bullet points
    if re.search(r'^\d+\. .+', content, re.MULTILINE):
        score += 5   # Has numbered lists
    
    # Completeness (10 points)
    if len(content) > 500:
        score += 10  # Good length
    
    return min(score, 100)  # Cap at 100

def analyze_state_file(state_file):
    """Analyze scraper state file"""
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        return {
            "base_url": state.get("base_url", "Unknown"),
            "processed_count": state.get("processed_count", 0),
            "visited_count": len(state.get("visited_urls", [])),
            "failed_count": len(state.get("failed_urls", [])),
            "pending_count": len(state.get("pending_urls", [])),
            "timestamp": state.get("timestamp", "Unknown"),
            "completion_rate": (state.get("processed_count", 0) / 
                              (state.get("processed_count", 0) + len(state.get("pending_urls", [])))) * 100
        }
        
    except Exception as e:
        return {"error": str(e)}

def generate_recommendations(analysis):
    """Generate recommendations based on analysis"""
    
    recommendations = []
    
    # File count recommendations
    if analysis["summary"]["total_files"] < 3:
        recommendations.append("Consider increasing max_pages or max_depth to capture more content")
    
    # Quality recommendations
    avg_quality = sum(f.get("quality_score", 0) for f in analysis["files"]) / len(analysis["files"]) if analysis["files"] else 0
    if avg_quality < 50:
        recommendations.append("Content quality is low - check if the right pages are being scraped")
    
    # Size recommendations
    if analysis["summary"]["average_size"] < 500:
        recommendations.append("Files are quite small - may need to adjust content extraction")
    
    # Word count recommendations
    if analysis["summary"]["average_words"] < 50:
        recommendations.append("Very few words per page - check content extraction prompts")
    
    # State-based recommendations
    if "state" in analysis:
        state = analysis["state"]
        if state.get("completion_rate", 0) < 50:
            recommendations.append("Crawl was incomplete - consider resuming or increasing limits")
        
        if state.get("failed_count", 0) > state.get("processed_count", 0) * 0.2:
            recommendations.append("High failure rate - check network connectivity and site accessibility")
    
    analysis["recommendations"] = recommendations

def print_analysis_report(analysis):
    """Print a formatted analysis report"""
    
    print("\n📊 ANALYSIS REPORT")
    print("=" * 60)
    
    # Summary
    summary = analysis["summary"]
    print(f"📄 Total Files: {summary['total_files']}")
    print(f"💾 Total Size: {summary['total_size']:,} bytes")
    print(f"📏 Average Size: {summary['average_size']:.1f} bytes")
    print(f"📝 Total Words: {summary['total_words']:,}")
    print(f"📊 Average Words: {summary['average_words']:.1f}")
    
    # State information
    if "state" in analysis:
        state = analysis["state"]
        print(f"\n🔄 CRAWL STATE")
        print(f"🌐 Base URL: {state.get('base_url', 'Unknown')}")
        print(f"✅ Processed: {state.get('processed_count', 0)}")
        print(f"👁️  Visited: {state.get('visited_count', 0)}")
        print(f"❌ Failed: {state.get('failed_count', 0)}")
        print(f"⏳ Pending: {state.get('pending_count', 0)}")
        print(f"📈 Completion: {state.get('completion_rate', 0):.1f}%")
    
    # File details
    print(f"\n📋 FILE DETAILS")
    for file_info in analysis["files"]:
        if "error" in file_info:
            print(f"❌ {file_info['filename']}: ERROR - {file_info['error']}")
        else:
            quality = file_info["quality_score"]
            quality_icon = "🟢" if quality >= 70 else "🟡" if quality >= 40 else "🔴"
            print(f"{quality_icon} {file_info['filename']}: {file_info['word_count']} words, Quality: {quality}%")
    
    # Issues
    if analysis["issues"]:
        print(f"\n⚠️  ISSUES FOUND ({len(analysis['issues'])})")
        for issue in analysis["issues"]:
            print(f"   • {issue}")
    
    # Recommendations
    if analysis["recommendations"]:
        print(f"\n💡 RECOMMENDATIONS")
        for rec in analysis["recommendations"]:
            print(f"   • {rec}")
    
    print(f"\n✅ Analysis complete!")

def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("Usage: python analyze_output.py <output_directory>")
        print("Example: python analyze_output.py docs")
        return
    
    output_dir = sys.argv[1]
    
    # Run analysis
    analysis = analyze_output_directory(output_dir)
    
    if analysis:
        print_analysis_report(analysis)
        
        # Save analysis to file
        analysis_file = Path(output_dir) / "analysis_report.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Analysis saved to: {analysis_file}")

if __name__ == "__main__":
    main()
