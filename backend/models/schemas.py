#!/usr/bin/env python3
"""
API Data Models and Schemas
===========================

Pydantic models for request/response validation and serialization.
"""

from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SiteType(str, Enum):
    """Supported website types"""
    DOCUMENTATION = "documentation"
    API = "api"
    BLOG = "blog"
    GITHUB = "github"
    WIKI = "wiki"
    CORPORATE = "corporate"
    FORUM = "forum"
    OTHER = "other"

class JobStatus(str, Enum):
    """Job processing status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    SCRAPING = "scraping"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SiteComplexity(str, Enum):
    """Website complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

# Analysis Models
class PreAnalysisRequest(BaseModel):
    """Request model for pre-analysis"""
    url: HttpUrl = Field(..., description="URL to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://httpbin.org"
            }
        }

class PreAnalysisResponse(BaseModel):
    """Response model for pre-analysis results"""
    title: str = Field(..., description="Page title")
    description: str = Field(default="", description="Meta description")
    link_count: int = Field(..., description="Total number of links")
    internal_links: int = Field(..., description="Number of internal links")
    external_links: int = Field(..., description="Number of external links")
    heading_count: int = Field(..., description="Number of headings")
    image_count: int = Field(..., description="Number of images")
    code_block_count: int = Field(..., description="Number of code blocks")
    estimated_complexity: SiteComplexity = Field(..., description="Estimated site complexity")
    likely_site_type: SiteType = Field(..., description="Inferred site type")
    sample_links: List[str] = Field(default_factory=list, description="Sample internal links")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "httpbin.org",
                "description": "HTTP Request & Response Service",
                "link_count": 5,
                "internal_links": 1,
                "external_links": 4,
                "heading_count": 2,
                "image_count": 0,
                "code_block_count": 3,
                "estimated_complexity": "simple",
                "likely_site_type": "api",
                "sample_links": ["https://httpbin.org/forms/post"]
            }
        }

# LLM Analysis Models
class LLMAnalysisRequest(BaseModel):
    """Request model for LLM analysis"""
    url: HttpUrl = Field(..., description="URL to analyze")
    pre_analysis: Optional[PreAnalysisResponse] = Field(None, description="Pre-analysis results")
    
class WebsiteAnalysis(BaseModel):
    """Website analysis from LLM"""
    site_type: SiteType = Field(..., description="Detected site type")
    content_depth: str = Field(..., description="Content depth assessment")
    documentation_quality: str = Field(..., description="Documentation quality")
    main_content_areas: List[str] = Field(default_factory=list, description="Main content areas")
    navigation_complexity: str = Field(..., description="Navigation complexity")
    estimated_pages: int = Field(..., description="Estimated total pages")
    update_frequency: str = Field(..., description="Content update frequency")

class ScrapingRecommendations(BaseModel):
    """LLM scraping recommendations"""
    optimal_depth: int = Field(..., description="Recommended crawl depth")
    recommended_pages: int = Field(..., description="Recommended page limit")
    suggested_delay: float = Field(..., description="Suggested delay between requests")
    priority_patterns: List[str] = Field(default_factory=list, description="URL patterns to prioritize")
    avoid_patterns: List[str] = Field(default_factory=list, description="URL patterns to avoid")
    content_focus: str = Field(..., description="Content focus strategy")

class ExpectedOutput(BaseModel):
    """Expected output characteristics"""
    file_count_estimate: int = Field(..., description="Estimated file count")
    content_type: str = Field(..., description="Expected content type")
    quality_expectation: str = Field(..., description="Expected quality level")
    special_considerations: List[str] = Field(default_factory=list, description="Special handling needs")

class CrawlingStrategy(BaseModel):
    """Crawling strategy recommendations"""
    approach: str = Field(..., description="Crawling approach")
    starting_points: List[str] = Field(default_factory=list, description="Starting points")
    termination_criteria: str = Field(..., description="When to stop crawling")
    resume_recommendation: bool = Field(..., description="Whether to support resume")

class LLMAnalysisResponse(BaseModel):
    """Complete LLM analysis response"""
    website_analysis: WebsiteAnalysis
    scraping_recommendations: ScrapingRecommendations
    expected_output: ExpectedOutput
    crawling_strategy: CrawlingStrategy

# Scraping Job Models
class ScrapeJobRequest(BaseModel):
    """Request model for creating scraping job"""
    url: HttpUrl = Field(..., description="URL to scrape")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum crawl depth")
    max_pages: int = Field(default=50, ge=1, le=500, description="Maximum pages to scrape")
    delay: float = Field(default=2.0, ge=0.1, le=10.0, description="Delay between requests")
    output_format: str = Field(default="markdown", description="Output format")
    resume: bool = Field(default=True, description="Resume from previous crawl")
    llm_guided: bool = Field(default=True, description="Use LLM guidance")
    
    @validator('delay')
    def validate_delay(cls, v):
        if v < 0.1:
            raise ValueError('Delay must be at least 0.1 seconds')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://httpbin.org",
                "max_depth": 3,
                "max_pages": 50,
                "delay": 2.0,
                "output_format": "markdown",
                "resume": True,
                "llm_guided": True
            }
        }

class ScrapeJobResponse(BaseModel):
    """Response model for scraping job creation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    created_at: datetime = Field(..., description="Job creation timestamp")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "status": "pending",
                "created_at": "2024-01-01T12:00:00Z",
                "estimated_duration": 120
            }
        }

# Job Status Models
class JobProgress(BaseModel):
    """Job progress information"""
    processed_count: int = Field(..., description="Pages processed")
    visited_count: int = Field(..., description="Pages visited")
    failed_count: int = Field(..., description="Failed pages")
    pending_count: int = Field(..., description="Pending pages")
    current_url: Optional[str] = Field(None, description="Currently processing URL")
    elapsed_time: float = Field(..., description="Elapsed time in seconds")
    pages_per_second: float = Field(..., description="Processing speed")
    estimated_remaining: Optional[int] = Field(None, description="Estimated remaining seconds")

class JobStatusResponse(BaseModel):
    """Complete job status response"""
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Current status")
    progress: JobProgress = Field(..., description="Progress information")
    config: Dict[str, Any] = Field(..., description="Job configuration")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")

# Results Models
class ScrapedFile(BaseModel):
    """Information about a scraped file"""
    filename: str = Field(..., description="File name")
    url: str = Field(..., description="Source URL")
    size: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(..., description="Creation timestamp")
    word_count: int = Field(..., description="Word count")
    quality_score: Optional[float] = Field(None, description="Content quality score")

class JobResults(BaseModel):
    """Complete job results"""
    job_id: str = Field(..., description="Job identifier")
    files: List[ScrapedFile] = Field(..., description="Generated files")
    summary: Dict[str, Any] = Field(..., description="Scraping summary")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    download_url: str = Field(..., description="Download URL for results")

# System Prompt Models
class SystemPrompt(BaseModel):
    """System prompt configuration"""
    id: str = Field(..., description="Prompt identifier")
    name: str = Field(..., description="Human-readable name")
    version: str = Field(..., description="Version string")
    site_type: SiteType = Field(..., description="Target site type")
    prompt_text: str = Field(..., description="Actual prompt text")
    parameters: List[str] = Field(default_factory=list, description="Supported parameters")
    success_rate: float = Field(..., description="Historical success rate")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_active: bool = Field(default=True, description="Whether prompt is active")

class SystemPromptList(BaseModel):
    """List of available system prompts"""
    prompts: List[SystemPrompt] = Field(..., description="Available prompts")
    total: int = Field(..., description="Total count")

# Error Models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "validation_error",
                "message": "Invalid URL provided",
                "details": {"field": "url", "value": "not-a-url"}
            }
        }
