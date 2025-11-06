"""
Nuclei scanner service
"""
import os
import asyncio
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Optional
from loguru import logger

from app.core.config import settings
from app.services.nuclei.models import NucleiScanConfig, NucleiScanResult, NucleiResult
from app.services.nuclei.utils import parse_nuclei_jsonl, count_by_severity
from app.services.nuclei.exceptions import (
    NucleiNotFoundError,
    NucleiExecutionError,
    NucleiTimeoutError,
)


class NucleiScanner:
    """
    Nuclei scanner wrapper service
    """

    def __init__(self):
        self.nuclei_path = settings.nuclei_path
        self.templates_path = settings.nuclei_templates_path
        self._verify_nuclei()

    def _verify_nuclei(self):
        """Verify that Nuclei binary exists and is executable"""
        if not os.path.exists(self.nuclei_path):
            raise NucleiNotFoundError(
                f"Nuclei binary not found at {self.nuclei_path}. "
                "Please install Nuclei: https://github.com/projectdiscovery/nuclei"
            )

        if not os.access(self.nuclei_path, os.X_OK):
            raise NucleiNotFoundError(
                f"Nuclei binary at {self.nuclei_path} is not executable"
            )

        logger.info(f"Nuclei binary found at {self.nuclei_path}")

    def _build_command(self, config: NucleiScanConfig, targets_file: str, output_file: str) -> List[str]:
        """
        Build Nuclei command from configuration

        Args:
            config: Scan configuration
            targets_file: Path to targets file
            output_file: Path to output file

        Returns:
            Command as list of strings
        """
        cmd = [
            self.nuclei_path,
            "-l", targets_file,  # List of targets
            "-json",  # JSON output
            "-o", output_file,  # Output file
            "-silent",  # Silent mode
            "-no-color",  # No color output
        ]

        # Templates
        if config.templates:
            for template in config.templates:
                cmd.extend(["-t", template])
        elif os.path.exists(self.templates_path):
            cmd.extend(["-t", self.templates_path])

        # Tags
        if config.tags:
            cmd.extend(["-tags", ",".join(config.tags)])

        # Exclude tags
        if config.exclude_tags:
            cmd.extend(["-exclude-tags", ",".join(config.exclude_tags)])

        # Severity filter
        if config.severity:
            cmd.extend(["-severity", ",".join(config.severity)])

        # Rate limiting
        cmd.extend(["-rate-limit", str(config.rate_limit)])
        cmd.extend(["-bulk-size", str(config.bulk_size)])
        cmd.extend(["-c", str(config.threads)])

        # Redirects
        if config.follow_redirects:
            cmd.append("-follow-redirects")
        if config.follow_host_redirects:
            cmd.append("-follow-host-redirects")
        if config.max_redirects:
            cmd.extend(["-max-redirects", str(config.max_redirects)])
        if config.disable_redirects:
            cmd.append("-disable-redirects")

        # Output options
        if config.include_request:
            cmd.append("-include-rr")  # Include request/response
        if config.include_response:
            cmd.append("-include-response")
        if config.include_curl:
            cmd.append("-include-curl")

        # Custom arguments
        if config.custom_args:
            cmd.extend(config.custom_args)

        return cmd

    async def scan(self, config: NucleiScanConfig) -> NucleiScanResult:
        """
        Execute a Nuclei scan

        Args:
            config: Scan configuration

        Returns:
            NucleiScanResult with scan results
        """
        start_time = time.time()

        # Create temporary files for targets and output
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as targets_file:
            targets_file.write("\n".join(config.targets))
            targets_file_path = targets_file.name

        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        output_file.close()
        output_file_path = output_file.name

        try:
            # Build command
            cmd = self._build_command(config, targets_file_path, output_file_path)
            logger.info(f"Executing Nuclei: {' '.join(cmd)}")

            # Execute Nuclei
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise NucleiTimeoutError(
                    f"Nuclei scan timeout after {config.timeout} seconds"
                )

            duration = time.time() - start_time

            stdout_str = stdout.decode("utf-8", errors="ignore")
            stderr_str = stderr.decode("utf-8", errors="ignore")

            # Read output file
            results = []
            if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
                with open(output_file_path, "r") as f:
                    output_content = f.read()
                    results = parse_nuclei_jsonl(output_content)

            # Check for errors
            if process.returncode != 0 and not results:
                error_msg = stderr_str or "Unknown error"
                logger.error(f"Nuclei scan failed: {error_msg}")
                return NucleiScanResult(
                    success=False,
                    stdout=stdout_str,
                    stderr=stderr_str,
                    exit_code=process.returncode,
                    duration_seconds=duration,
                    error_message=error_msg,
                )

            # Count by severity
            severity_counts = count_by_severity(results)

            logger.info(
                f"Nuclei scan completed in {duration:.2f}s. "
                f"Found {len(results)} vulnerabilities"
            )

            return NucleiScanResult(
                success=True,
                vulnerabilities=results,
                total_vulnerabilities=len(results),
                vulnerabilities_by_severity=severity_counts,
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=process.returncode,
                duration_seconds=duration,
            )

        except NucleiTimeoutError:
            raise
        except Exception as e:
            logger.error(f"Error executing Nuclei scan: {str(e)}")
            raise NucleiExecutionError(f"Failed to execute Nuclei scan: {str(e)}")
        finally:
            # Clean up temporary files
            try:
                os.unlink(targets_file_path)
                os.unlink(output_file_path)
            except Exception:
                pass

    async def update_templates(self) -> bool:
        """
        Update Nuclei templates

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Updating Nuclei templates...")

            cmd = [self.nuclei_path, "-update-templates"]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info("Nuclei templates updated successfully")
                return True
            else:
                logger.error(f"Failed to update templates: {stderr.decode()}")
                return False

        except Exception as e:
            logger.error(f"Error updating Nuclei templates: {str(e)}")
            return False

    async def get_version(self) -> Optional[str]:
        """
        Get Nuclei version

        Returns:
            Version string or None
        """
        try:
            cmd = [self.nuclei_path, "-version"]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return stdout.decode().strip()

            return None

        except Exception as e:
            logger.error(f"Error getting Nuclei version: {str(e)}")
            return None


# Singleton instance
_scanner_instance: Optional[NucleiScanner] = None


def get_nuclei_scanner() -> NucleiScanner:
    """Get or create Nuclei scanner singleton instance"""
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = NucleiScanner()
    return _scanner_instance
