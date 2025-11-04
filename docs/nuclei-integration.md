# Nuclei Integration

This document describes the Nuclei scanner integration in the EASM platform.

## Overview

The platform uses [Nuclei](https://github.com/projectdiscovery/nuclei) as its vulnerability scanning engine. Nuclei is a fast, customizable vulnerability scanner based on simple YAML templates.

## Architecture

The Nuclei integration consists of several components:

### 1. Scanner Service (`app/services/nuclei/scanner.py`)

The `NucleiScanner` class wraps the Nuclei CLI and provides:
- Async scan execution
- Configuration management
- Template updates
- Version checking

```python
from app.services.nuclei import get_nuclei_scanner, NucleiScanConfig

scanner = get_nuclei_scanner()

config = NucleiScanConfig(
    targets=["https://example.com"],
    severity=["high", "critical"],
    rate_limit=150,
    threads=25
)

result = await scanner.scan(config)
```

### 2. Data Models (`app/services/nuclei/models.py`)

Pydantic models for:
- `NucleiScanConfig`: Scan configuration
- `NucleiResult`: Individual vulnerability finding
- `NucleiScanResult`: Complete scan results
- `NucleiInfo`: Template metadata

### 3. Utilities (`app/services/nuclei/utils.py`)

Helper functions for:
- Parsing JSONL output
- Extracting CVE/CWE IDs
- Vulnerability deduplication
- Severity counting and filtering

### 4. Converter (`app/services/nuclei/converter.py`)

Converts Nuclei results to database models:
```python
from app.services.nuclei.converter import nuclei_result_to_vulnerability_data

vuln_data = nuclei_result_to_vulnerability_data(
    nuclei_result,
    asset_id=1,
    scan_id=1
)
# Returns dict ready for Vulnerability model
```

## Configuration

Configure Nuclei in `.env`:

```env
# Nuclei binary path
NUCLEI_PATH=/usr/local/bin/nuclei

# Templates directory
NUCLEI_TEMPLATES_PATH=./nuclei-templates

# Scan settings
NUCLEI_RATE_LIMIT=150
NUCLEI_BULK_SIZE=25
NUCLEI_THREADS=25
```

## Scan Workflow

1. **Create Scan**: Create a `Scan` record in the database
2. **Execute**: `ScanService.execute_scan()` runs Nuclei
3. **Parse Results**: Nuclei JSONL output is parsed
4. **Store Vulnerabilities**: Results are saved as `Vulnerability` records
5. **Deduplication**: Existing vulnerabilities are updated with occurrence count

## Deduplication

Vulnerabilities are deduplicated using a hash of:
- Template ID
- Matched location (URL)

When the same vulnerability is found again:
- `occurrences` count is incremented
- `last_seen_at` is updated
- No duplicate record is created

## Scan Templates

Create reusable scan configurations:

```python
from app.schemas.scan import ScanTemplateCreate

template = ScanTemplateCreate(
    name="Critical CVE Scan",
    description="Scan for critical CVEs",
    nuclei_severity=["critical"],
    nuclei_tags=["cve"],
    rate_limit=150,
    threads=25
)

scan_template = await scan_service.create_template(template)
```

## Error Handling

Custom exceptions:
- `NucleiNotFoundError`: Binary not found
- `NucleiExecutionError`: Execution failed
- `NucleiTimeoutError`: Scan timeout
- `NucleiParseError`: Output parsing failed

## Template Management

Update Nuclei templates:

```python
scanner = get_nuclei_scanner()
success = await scanner.update_templates()
```

Check Nuclei version:

```python
version = await scanner.get_version()
```

## Advanced Configuration

### Custom Nuclei Arguments

```python
config = NucleiScanConfig(
    targets=["https://example.com"],
    custom_args=["-proxy", "http://proxy:8080"]
)
```

### Template Filtering

```python
config = NucleiScanConfig(
    targets=["https://example.com"],
    templates=["/path/to/specific/template.yaml"],
    tags=["cve", "rce"],
    exclude_tags=["dos"],
    severity=["high", "critical"]
)
```

### Output Options

```python
config = NucleiScanConfig(
    targets=["https://example.com"],
    include_request=True,
    include_response=True,  # Can be large
    include_curl=True
)
```

## Performance Tuning

Adjust scan performance:

```python
config = NucleiScanConfig(
    targets=targets,
    rate_limit=300,      # Requests per second
    bulk_size=50,        # Parallel template processing
    threads=50,          # Concurrent threads
    timeout=7200         # 2 hour timeout
)
```

**Note**: Higher values increase speed but also resource usage and target load.

## Integration with Celery (Tier B/C)

For background scanning in Tier B/C, scans are executed as Celery tasks:

```python
# In workers/scan_tasks.py
@celery_app.task
async def execute_scan_task(scan_id: int):
    async with get_db() as db:
        scan_service = get_scan_service(db)
        await scan_service.execute_scan(scan_id)
```

## Best Practices

1. **Always set timeouts**: Prevent hung scans
2. **Use templates**: Create reusable configurations
3. **Monitor rate limits**: Avoid overwhelming targets
4. **Check deduplication**: Review `occurrences` field
5. **Update templates regularly**: `scanner.update_templates()`

## Troubleshooting

### Nuclei not found
```
NucleiNotFoundError: Nuclei binary not found at /usr/local/bin/nuclei
```
**Solution**: Install Nuclei or update `NUCLEI_PATH` in `.env`

### Templates not found
```
[WRN] No templates found in: ./nuclei-templates
```
**Solution**: Run `nuclei -update-templates` or update `NUCLEI_TEMPLATES_PATH`

### Timeout errors
```
NucleiTimeoutError: Nuclei scan timeout after 3600 seconds
```
**Solution**: Increase `timeout` in scan config or reduce target count

## References

- [Nuclei Documentation](https://docs.projectdiscovery.io/tools/nuclei)
- [Nuclei Templates](https://github.com/projectdiscovery/nuclei-templates)
- [Template Writing Guide](https://docs.projectdiscovery.io/templating-guide)
