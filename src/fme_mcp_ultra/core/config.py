"""Configuration management for fme-mcp-ultra."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings for fme-mcp-ultra."""

    model_config = SettingsConfigDict(
        env_prefix="FME_MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server details
    host: str = Field(default="0.0.0.0", description="Host address to bind to")
    port: int = Field(default=8000, description="Network port for HTTP/SSE transport")
    transport: str = Field(default="stdio", description="Default MCP transport (stdio or streamable-http)")
    log_level: str = Field(default="INFO", description="Log level (DEBUG, INFO, WARNING, ERROR)")
    environment: str = Field(default="production", description="Runtime environment")

    # Security settings
    auth_mode: str = Field(default="none", description="Authentication mode: none, api_key, oauth2")
    api_key: Optional[str] = Field(default=None, description="Static API key if api_key auth is used")
    encryption_key: Optional[str] = Field(default=None, description="32-byte base64 key for data-at-rest encryption")
    
    # PathGuard file system allowlists
    allowed_dirs: List[str] = Field(
        default_factory=lambda: [
            r"C:\Program Files\FME",
            r"C:\Program Files (x86)\FME",
            str(Path.cwd()),
            str(Path.cwd().parent),
            str(Path.home()),
        ],
        description="Directories permitted for file access",
    )

    # SSRF Guard domain allowlists
    allowed_outbound_domains: List[str] = Field(
        default_factory=lambda: ["safe.com", "github.com", "localhost"],
        description="Authorised outbound domains for federation and webhooks",
    )

    # FME Form (Local Desktop) configuration
    fme_form_enabled: bool = Field(default=True, description="Enable local FME Form engine execution")
    fme_dir: Optional[str] = Field(default=None, description="Explicit directory for FME Form installation")
    fme_timeout_seconds: int = Field(default=600, description="Default timeout for workspace execution in seconds")

    # FME Flow (Remote Server) configuration
    fme_flow_enabled: bool = Field(default=False, description="Enable remote FME Flow API integration")
    fme_flow_url: Optional[str] = Field(default=None, description="FME Flow root URL (e.g. https://fme-flow.internal)")
    fme_flow_token: Optional[str] = Field(default=None, description="FME Flow Bearer API token")
    fme_flow_verify_ssl: bool = Field(default=True, description="Enforce SSL/TLS certificate verification")


# Singleton instance
settings = Settings()
