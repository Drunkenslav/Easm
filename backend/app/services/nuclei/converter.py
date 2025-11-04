"""
Convert Nuclei results to database models
"""
from datetime import datetime
from typing import Dict, Any
from app.services.nuclei.models import NucleiResult
from app.services.nuclei.utils import (
    hash_vulnerability,
    extract_cve_ids,
    extract_cwe_ids,
    extract_cvss_score,
)
from app.models.enums import VulnerabilitySeverity


def nuclei_result_to_vulnerability_data(
    result: NucleiResult,
    asset_id: int,
    scan_id: int,
) -> Dict[str, Any]:
    """
    Convert Nuclei result to vulnerability database model data

    Args:
        result: Nuclei scan result
        asset_id: Asset ID
        scan_id: Scan ID

    Returns:
        Dictionary suitable for Vulnerability model creation
    """
    # Extract metadata
    cve_ids = extract_cve_ids(result)
    cwe_ids = extract_cwe_ids(result)
    cvss_score = extract_cvss_score(result)

    # Create hash for deduplication
    vuln_hash = hash_vulnerability(result.template_id, result.matched_at)

    # Map severity
    severity_map = {
        "info": VulnerabilitySeverity.INFO,
        "low": VulnerabilitySeverity.LOW,
        "medium": VulnerabilitySeverity.MEDIUM,
        "high": VulnerabilitySeverity.HIGH,
        "critical": VulnerabilitySeverity.CRITICAL,
    }
    severity = severity_map.get(
        result.info.severity.lower(),
        VulnerabilitySeverity.MEDIUM
    )

    # Prepare extracted results
    extracted = result.extracted_results or []

    # Get current timestamp
    now = datetime.utcnow().isoformat()

    return {
        "asset_id": asset_id,
        "scan_id": scan_id,
        "template_id": result.template_id,
        "template_name": result.info.name,
        "template_path": result.template_path,
        "name": result.info.name,
        "description": result.info.description,
        "severity": severity.value,
        "matched_at": result.matched_at,
        "extracted_results": extracted,
        "request": result.request,
        "response": result.response,
        "curl_command": result.curl_command,
        "tags": result.info.tags or [],
        "cve_ids": cve_ids,
        "cwe_ids": cwe_ids,
        "cvss_score": cvss_score,
        "metadata": {
            "classification": result.info.classification or {},
            "nuclei_metadata": result.info.metadata or {},
            "type": result.type,
            "matcher_name": result.matcher_name,
            "ip": result.ip,
            "timestamp": result.timestamp,
        },
        "reference_urls": result.info.reference or [],
        "hash": vuln_hash,
        "first_seen_at": now,
        "last_seen_at": now,
        "occurrences": 1,
    }
