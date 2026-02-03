"""
Operation Repo CLI - Main entry point using Typer.

A Git-like tool for organizing operations, pentests, and projects.
"""

import typer
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from operation_repo.core import OpClass
from operation_repo.config import ConfigHandler
from operation_repo.server import OpClassToServer

# Initialize console and apps
console = Console()

# Main app
app = typer.Typer(
    name="op",
    help="Operation Repo - Stay organized like Git for your operations.",
    add_completion=False,
    rich_markup_mode="rich",
)

# Sub-command groups
server_app = typer.Typer(help="Server management commands (push, clone, list)")
app.add_typer(server_app, name="server")


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print("op version [bold]3.0.0[/bold]")
        raise typer.Exit()


def ensure_op_config() -> None:
    """Create default op config on first run."""
    config_handler = ConfigHandler()
    home_folder = config_handler.get_home_folder()
    op_dir = Path(home_folder) / ".op"
    op_conf = op_dir / "op.conf"
    opsdb_dir = op_dir / "opsdb"

    if op_dir.exists():
        return

    default_config = [
        "[SERVER]",
        "opsserver_ip = 127.0.0.1",
        "ssh_key = /path/to/your/key",
        "",
        "[FOLDER]",
        "# Add folders to create on init (folder_name = on)",
        "# Example: notes = on",
        "",
        "[FILE]",
        "# Add files to create on init (file_name = on)",
        "# Example: todo.txt = on",
        "",
        "[DB]",
        "# Add deployable scripts from ~/.op/opsdb/ (script_name = on)",
        "",
    ]

    try:
        op_dir.mkdir(parents=True, exist_ok=True)
        opsdb_dir.mkdir(parents=True, exist_ok=True)
        op_conf.write_text("\n".join(default_config))
        console.print(f"[green]✓[/green] Created config at {op_conf}")
    except PermissionError as e:
        console.print(f"[red]✗[/red] Permission denied creating config: {e}")
    except OSError as e:
        console.print(f"[red]✗[/red] Error creating config: {e}")


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version and exit."
    ),
) -> None:
    """
    Operation Repo - A Git-like CLI for organizing operations.
    
    Perfect for pentesters, HTB players, and developers.
    """
    ensure_op_config()


# =============================================================================
# Core Commands
# =============================================================================

@app.command()
def init(
    custom: Optional[str] = typer.Option(
        None, "--custom", "-c", metavar="TEMPLATE",
        help="Use a custom template from op.conf (e.g., op init -c web)"
    ),
) -> None:
    """
    Initialize a new op repo in the current directory.
    
    Creates default structure: .op/, .opignore, README.md, opsdb/
    """
    config_handler = ConfigHandler()
    op_class = OpClass()

    if custom:
        console.print(Panel(f"[bold blue]Initializing op repo with template: {custom}[/bold blue]"))
        op_class.init_template(config_handler, custom)
    else:
        console.print(Panel("[bold blue]Initializing op repo[/bold blue]"))
        op_class.init(config_handler)


@app.command()
def status() -> None:
    """
    Show current op repo status.
    
    Displays tracked files, backups, and repo info.
    """
    op_class = OpClass()
    op_class.status()


@app.command()
def backup() -> None:
    """
    Backup op repo into a timestamped .zip file.
    
    Respects .opignore - ignored files won't be included.
    """
    console.print(Panel("[bold blue]Backing up op repo[/bold blue]"))
    op_class = OpClass()
    op_class.backup()


@app.command()
def remove(
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Skip confirmation prompt"
    ),
) -> None:
    """
    Remove op repo files.
    
    Respects .opignore - ignored files will be preserved.
    """
    if not force:
        confirm = typer.confirm("Are you sure you want to remove op repo files?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit()

    console.print(Panel("[bold yellow]Removing op repo[/bold yellow]"))
    op_class = OpClass()
    op_class.remove()


# =============================================================================
# Server Commands (grouped under 'op server')
# =============================================================================

@server_app.command("list")
def server_list() -> None:
    """
    List all repos from opsserver.
    """
    config_handler = ConfigHandler()
    ip, key = config_handler.read_server_config()
    user = Path(key).stem.split("_")[0]
    
    server = OpClassToServer()
    server.list_repos_from_server(ip, key, user)


@server_app.command("push")
def server_push() -> None:
    """
    Push current repo to opsserver.
    """
    config_handler = ConfigHandler()
    ip, key = config_handler.read_server_config()
    user = Path(key).stem.split("_")[0]
    
    server = OpClassToServer()
    server.push_repo(ip, key, user)


@server_app.command("clone")
def server_clone(
    repo: str = typer.Argument(..., help="Repository name to clone"),
) -> None:
    """
    Clone a repo from opsserver.
    """
    config_handler = ConfigHandler()
    ip, key = config_handler.read_server_config()
    user = Path(key).stem.split("_")[0]
    
    server = OpClassToServer()
    server.clone_repo(ip, key, user, repo)


@server_app.command("view")
def server_view(
    repo: str = typer.Argument(..., help="Repository name to view"),
) -> None:
    """
    View README from a repo on opsserver.
    
    Opens the README in your browser using grip.
    """
    config_handler = ConfigHandler()
    ip, key = config_handler.read_server_config()
    user = Path(key).stem.split("_")[0]
    
    server = OpClassToServer()
    readme = server.cat_readme_from_opsserver(key, user, ip, repo)
    
    op_class = OpClass()
    op_class.view(readme)


# =============================================================================
# Shortcut Commands (for convenience - same as server commands)
# =============================================================================

@app.command("push")
def push() -> None:
    """
    [shortcut] Push current repo to opsserver.
    
    Same as: op server push
    """
    server_push()


@app.command("clone")
def clone(
    repo: str = typer.Argument(..., help="Repository name to clone"),
) -> None:
    """
    [shortcut] Clone a repo from opsserver.
    
    Same as: op server clone <repo>
    """
    server_clone(repo)


@app.command("list")
def list_repos() -> None:
    """
    [shortcut] List all repos from opsserver.
    
    Same as: op server list
    """
    server_list()


@app.command("view")
def view(
    repo: str = typer.Argument(..., help="Repository name to view"),
) -> None:
    """
    [shortcut] View README from opsserver repo.
    
    Same as: op server view <repo>
    """
    server_view(repo)


# =============================================================================
# Entry Point
# =============================================================================

def main_cli() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main_cli()
