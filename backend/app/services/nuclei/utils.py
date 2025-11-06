"""
Utility functions for Nuclei integration
"""
import hashlib
import json
from typing import List, Dict, Optional
from app.services.nuclei.models import NucleiResult


def hash_vulnerability(template_id: str, matched_at: str) -> str:
    """
    Create a hash for vulnerability deduplication

    Args:
        template_id: Nuclei template ID
        matched_at: URL/location where vulnerability was found

    Returns:
        SHA256 hash string
    """
    data = f"{template_id}:{matched_at}"
    return hashlib.sha256(data.encode()).hexdigest()


def extract_cve_ids(result: NucleiResult) -> List[str]:
    """
    Extract CVE IDs from Nuclei result

    Args:
        result: Nuclei scan result

    Returns:
        List of CVE IDs
    """
    cve_ids = []

    # Check tags
    for tag in result.info.tags or []:
        if tag.upper().startswith("CVE-"):
            cve_ids.append(tag.upper())

    # Check classification
    if result.info.classification:
        cve_id = result.info.classification.get("cve-id")
        if cve_id:
            if isinstance(cve_id, list):
                cve_ids.extend([c.upper() for c in cve_id])
            else:
                cve_ids.append(cve_id.upper())

    return list(set(cve_ids))  # Deduplicate


def extract_cwe_ids(result: NucleiResult) -> List[str]:
    """
    Extract CWE IDs from Nuclei result

    Args:
        result: Nuclei scan result

    Returns:
        List of CWE IDs
    """
    cwe_ids = []

    # Check tags
    for tag in result.info.tags or []:
        if tag.upper().startswith("CWE-"):
            cwe_ids.append(tag.upper())

    # Check classification
    if result.info.classification:
        cwe_id = result.info.classification.get("cwe-id")
        if cwe_id:
            if isinstance(cwe_id, list):
                cwe_ids.extend([c.upper() for c in cwe_id])
            else:
                cwe_ids.append(cwe_id.upper())

    return list(set(cwe_ids))  # Deduplicate


def extract_cvss_score(result: NucleiResult) -> Optional[str]:
    """
    Extract CVSS score from Nuclei result

    Args:
        result: Nuclei scan result

    Returns:
        CVSS score as string or None
    """
    if result.info.classification:
        # Try different field names
        for field in ["cvss-score", "cvss_score", "cvss"]:
            score = result.info.classification.get(field)
            if score:
                return str(score)

    return None


def parse_nuclei_jsonl(output: str) -> List[NucleiResult]:
    """
    Parse Nuclei JSONL output into structured results

    Args:
        output: Raw JSONL output from Nuclei

    Returns:
        List of parsed NucleiResult objects
    """
    results = []

    for line in output.strip().split("\n"):
        if not line.strip():
            continue

        try:
            data = json.loads(line)
            result = NucleiResult(**data)
            results.append(result)
        except json.JSONDecodeError:
            # Skip invalid JSON lines
            continue
        except Exception:
            # Skip lines that don't match our schema
            continue

    return results


def count_by_severity(results: List[NucleiResult]) -> Dict[str, int]:
    """
    Count vulnerabilities by severity

    Args:
        results: List of Nuclei results

    Returns:
        Dictionary with severity counts
    """
    counts = {
        "info": 0,
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0
    }

    for result in results:
        severity = result.info.severity.lower()
        if severity in counts:
            counts[severity] += 1

    return counts


def filter_by_severity(results: List[NucleiResult], severities: List[str]) -> List[NucleiResult]:
    """
    Filter results by severity levels

    Args:
        results: List of Nuclei results
        severities: List of severity levels to include

    Returns:
        Filtered list of results
    """
    severities_lower = [s.lower() for s in severities]
    return [r for r in results if r.info.severity.lower() in severities_lower]


def deduplicate_results(results: List[NucleiResult]) -> List[NucleiResult]:
    """
    Deduplicate Nuclei results based on template_id and matched_at

    Args:
        results: List of Nuclei results

    Returns:
        Deduplicated list of results
    """
    seen = set()
    unique_results = []

    for result in results:
        vuln_hash = hash_vulnerability(result.template_id, result.matched_at)
        if vuln_hash not in seen:
            seen.add(vuln_hash)
            unique_results.append(result)

    return unique_results
