"""
Data models for Nuclei integration
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NucleiInfo(BaseModel):
    """Nuclei template info section"""
    name: str
    author: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    description: Optional[str] = None
    reference: Optional[List[str]] = []
    severity: str
    classification: Optional[Dict[str, Any]] = {}
    metadata: Optional[Dict[str, Any]] = {}


class NucleiMatcher(BaseModel):
    """Nuclei matcher information"""
    name: Optional[str] = None
    type: Optional[str] = None
    matched_at: Optional[str] = None


class NucleiExtractedResult(BaseModel):
    """Extracted results from Nuclei"""
    name: Optional[str] = None
    value: Optional[str] = None


class NucleiResult(BaseModel):
    """
    Parsed Nuclei JSON output result
    Schema based on Nuclei's JSONL output format
    """
    # Template information
    template_id: str = Field(..., alias="template-id")
    template_path: str = Field(..., alias="template-path")
    info: NucleiInfo

    # Match information
    type: str
    host: str
    matched_at: str = Field(..., alias="matched-at")
    matched_line: Optional[str] = Field(None, alias="matched-line")

    # Extracted data
    extracted_results: Optional[List[str]] = Field(None, alias="extracted-results")

    # Request/Response
    request: Optional[str] = None
    response: Optional[str] = None

    # Additional fields
    matcher_name: Optional[str] = Field(None, alias="matcher-name")
    curl_command: Optional[str] = Field(None, alias="curl-command")

    # Metadata
    timestamp: str
    matcher_status: Optional[bool] = Field(None, alias="matcher-status")
    ip: Optional[str] = None

    class Config:
        populate_by_name = True


class NucleiScanConfig(BaseModel):
    """Configuration for a Nuclei scan"""
    targets: List[str] = Field(..., min_length=1)
    templates: Optional[List[str]] = None  # Specific template paths
    tags: Optional[List[str]] = None  # Template tags to include
    exclude_tags: Optional[List[str]] = None
    severity: Optional[List[str]] = None  # Filter by severity
    rate_limit: int = Field(default=150, ge=1, le=1000)
    bulk_size: int = Field(default=25, ge=1, le=100)
    threads: int = Field(default=25, ge=1, le=100)
    timeout: int = Field(default=3600, ge=60, le=7200)

    # Additional options
    follow_redirects: bool = True
    follow_host_redirects: bool = False
    max_redirects: int = 10
    disable_redirects: bool = False

    # Output options
    include_request: bool = True
    include_response: bool = False  # Can be large
    include_curl: bool = True

    # Advanced options
    custom_args: Optional[List[str]] = None


class NucleiScanResult(BaseModel):
    """Complete Nuclei scan result"""
    success: bool
    vulnerabilities: List[NucleiResult] = []
    total_vulnerabilities: int = 0
    vulnerabilities_by_severity: Dict[str, int] = {}
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


class NucleiTemplateInfo(BaseModel):
    """Information about a Nuclei template"""
    id: str
    name: str
    author: List[str] = []
    severity: str
    tags: List[str] = []
    description: Optional[str] = None
    reference: List[str] = []
    path: str
