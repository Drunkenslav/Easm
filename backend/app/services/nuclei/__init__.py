"""
Nuclei integration service
"""
from app.services.nuclei.scanner import NucleiScanner, get_nuclei_scanner
from app.services.nuclei.models import (
    NucleiScanConfig,
    NucleiScanResult,
    NucleiResult,
    NucleiTemplateInfo,
)
from app.services.nuclei.utils import (
    hash_vulnerability,
    extract_cve_ids,
    extract_cwe_ids,
    extract_cvss_score,
    parse_nuclei_jsonl,
    count_by_severity,
    filter_by_severity,
    deduplicate_results,
)
from app.services.nuclei.exceptions import (
    NucleiError,
    NucleiNotFoundError,
    NucleiExecutionError,
    NucleiTemplateError,
    NucleiParseError,
    NucleiTimeoutError,
)

__all__ = [
    # Scanner
    "NucleiScanner",
    "get_nuclei_scanner",
    # Models
    "NucleiScanConfig",
    "NucleiScanResult",
    "NucleiResult",
    "NucleiTemplateInfo",
    # Utils
    "hash_vulnerability",
    "extract_cve_ids",
    "extract_cwe_ids",
    "extract_cvss_score",
    "parse_nuclei_jsonl",
    "count_by_severity",
    "filter_by_severity",
    "deduplicate_results",
    # Exceptions
    "NucleiError",
    "NucleiNotFoundError",
    "NucleiExecutionError",
    "NucleiTemplateError",
    "NucleiParseError",
    "NucleiTimeoutError",
]
