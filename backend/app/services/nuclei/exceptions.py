"""
Custom exceptions for Nuclei integration
"""


class NucleiError(Exception):
    """Base exception for Nuclei-related errors"""
    pass


class NucleiNotFoundError(NucleiError):
    """Nuclei binary not found"""
    pass


class NucleiExecutionError(NucleiError):
    """Error executing Nuclei scan"""
    pass


class NucleiTemplateError(NucleiError):
    """Error with Nuclei templates"""
    pass


class NucleiParseError(NucleiError):
    """Error parsing Nuclei output"""
    pass


class NucleiTimeoutError(NucleiError):
    """Nuclei scan timeout"""
    pass
