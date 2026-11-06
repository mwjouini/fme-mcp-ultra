"""CLI Interface for fme-mcp-ultra."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from fme_mcp_ultra import __version__
from fme_mcp_ultra.core.config import settings
from fme_mcp_ultra.fme.fme_form_client import fme_form_client
from fme_mcp_ultra.server.mcp_server import mcp_server

cli = typer.Typer(
    name="fme-mcp-ultra",
    help="Universal, secure Model Context Protocol server for Safe Software FME 2025.2+.",
    add_completion=False,
)
console = Console()


@cli.command()
def serve(
    transport: str = typer.Option("stdio", "--transport", "-t", help="MCP transport: stdio, sse, streamable-http"),
    host: str = typer.Option(settings.host, "--host", "-h", help="Host address for HTTP/SSE"),
    port: int = typer.Option(settings.port, "--port", "-p", help="Port for HTTP/SSE"),
) -> None:
    """Launch the fme-mcp-ultra server."""
    if transport == "stdio":
        mcp_server.run(transport="stdio")
    elif transport in ("sse", "streamable-http"):
        console.print(f"[bold green]Starting fme-mcp-ultra {transport} server on {host}:{port}[/bold green]")
        mcp_server.run(transport=transport, host=host, port=port)
    else:
        console.print(f"[bold red]Unknown transport '{transport}'. Use stdio, sse, or streamable-http.[/bold red]")
        raise typer.Exit(code=1)


@cli.command()
def doctor() -> None:
    """Diagnose FME Form, fmeobjects bindings, and environment readiness."""
    console.print(Panel.fit("[bold blue]fme-mcp-ultra Environment Diagnostic[/bold blue]", border_style="blue"))

    table = Table(title="Diagnostic Checks")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Details", style="green")

    # 1. Server Version
    table.add_row("fme-mcp-ultra", "OK", f"v{__version__} (en-GB)")

    # 2. FME Form Local Detection
    info = fme_form_client.get_info()
    if info.get("installed"):
        table.add_row("FME Form", "[bold green]DETECTED[/bold green]", info.get("Version", "FME Form"))
        table.add_row("fme.exe Path", "OK", info.get("fme_executable", ""))
        table.add_row("Licence", "OK", info.get("Registration", ""))
    else:
        table.add_row("FME Form", "[bold red]NOT FOUND[/bold red]", "fme.exe not detected in standard paths")

    # 3. fmeobjects C-API
    if info.get("fmeobjects_loaded"):
        table.add_row("fmeobjects API", "[bold green]BOUND[/bold green]", "C-extension loaded successfully")
    else:
        table.add_row("fmeobjects API", "[bold yellow]FALLBACK[/bold yellow]", "Using subprocess CLI fallback")

    # 4. FME Flow Configuration
    flow_cfg = bool(settings.fme_flow_url and settings.fme_flow_token)
    table.add_row(
        "FME Flow API",
        "[bold green]CONFIGURED[/bold green]" if flow_cfg else "[dim]DISABLED[/dim]",
        settings.fme_flow_url or "Not configured",
    )

    console.print(table)


@cli.command()
def inspect(
    workspace_path: str = typer.Argument(..., help="Path to FME workspace (.fmw) file"),
) -> None:
    """Inspect an FME workspace and display published parameters and transformers."""
    try:
        data = fme_form_client.inspect_workspace(workspace_path)
        console.print(Panel.fit(f"[bold green]Workspace: {data['file_name']}[/bold green]"))

        # Published Parameters Table
        params = data.get("published_parameters", [])
        if params:
            t_params = Table(title=f"Published Parameters ({len(params)})")
            t_params.add_column("Parameter Name", style="cyan")
            t_params.add_column("Type", style="yellow")
            t_params.add_column("Default Value", style="white")
            t_params.add_column("Optional", style="green")
            for p in params:
                t_params.add_row(p["name"], p["type"], str(p["default_value"]), str(p["optional"]))
            console.print(t_params)

        # Transformers Table
        tfs = data.get("transformers", [])
        if tfs:
            t_tfs = Table(title=f"Transformers Pipeline ({len(tfs)} types)")
            t_tfs.add_column("Transformer", style="cyan")
            t_tfs.add_column("Occurrences", style="magenta")
            for t in tfs:
                t_tfs.add_row(t["name"], str(t["count"]))
            console.print(t_tfs)

    except Exception as e:
        console.print(f"[bold red]Inspection error: {e}[/bold red]")
        raise typer.Exit(code=1)


@cli.command()
def version() -> None:
    """Display fme-mcp-ultra version and build info."""
    console.print(f"fme-mcp-ultra v{__version__} - Apache-2.0")


if __name__ == "__main__":
    cli()

