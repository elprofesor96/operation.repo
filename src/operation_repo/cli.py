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
from operation_repo.commits import CommitManager
from operation_repo.notes import NotesManager
from operation_repo.templates import TemplateManager

# Initialize console
console = Console()

# =============================================================================
# App Setup
# =============================================================================

app = typer.Typer(
    name="op",
    help="Operation Repo - Stay organized like Git for your operations.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Sub-command groups
server_app = typer.Typer(help="Server management commands")
notes_app = typer.Typer(help="Quick note-taking commands")
template_app = typer.Typer(help="Template management commands")

app.add_typer(server_app, name="server")
app.add_typer(notes_app, name="notes")
app.add_typer(template_app, name="template")


# =============================================================================
# Callbacks & Helpers
# =============================================================================

def version_callback(value: bool) -> None:
    if value:
        console.print("op version [bold]3.0.0[/bold]")
        raise typer.Exit()


def ensure_op_config() -> None:
    config_handler = ConfigHandler()
    home_folder = config_handler.get_home_folder()
    op_dir = Path(home_folder) / ".op"
    op_conf = op_dir / "op.conf"
    opsdb_dir = op_dir / "opsdb"

    if op_dir.exists():
        return

    default_config = """[SERVER]
opsserver_ip = 127.0.0.1
ssh_key = /path/to/your/key

[FOLDER]
# folders to create (name = on)

[FILE]
# files to create (name = on)

[DB]
# deployables from ~/.op/opsdb/ (name = on)
"""
    try:
        op_dir.mkdir(parents=True, exist_ok=True)
        opsdb_dir.mkdir(parents=True, exist_ok=True)
        op_conf.write_text(default_config)
    except (PermissionError, OSError):
        pass


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback, is_eager=True),
) -> None:
    """Operation Repo - A Git-like CLI for organizing operations."""
    ensure_op_config()


# =============================================================================
# Core Commands
# =============================================================================

@app.command()
def init(
    custom: Optional[str] = typer.Option(None, "--custom", "-c", help="Use custom template"),
) -> None:
    """Initialize a new op repo."""
    config_handler = ConfigHandler()
    op_class = OpClass()
    if custom:
        console.print(Panel(f"[bold blue]Init with template: {custom}[/bold blue]"))
        op_class.init_template(config_handler, custom)
    else:
        console.print(Panel("[bold blue]Initializing op repo[/bold blue]"))
        op_class.init(config_handler)


@app.command()
def status() -> None:
    """Show op repo status."""
    OpClass().status()


@app.command()
def export(
    format: str = typer.Option("zip", "--format", "-f", help="Format: zip, tar.gz, tar"),
    encrypt: bool = typer.Option(False, "--encrypt", "-e", help="Encrypt with GPG"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output path"),
) -> None:
    """Export op repo (respects .opignore)."""
    console.print(Panel(f"[bold blue]Exporting ({format})[/bold blue]"))
    OpClass().export(format=format, encrypt=encrypt, output=output)


@app.command()
def remove(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Remove op repo files (respects .opignore)."""
    if not force and not typer.confirm("Remove op repo files?"):
        raise typer.Exit()
    console.print(Panel("[bold yellow]Removing op repo[/bold yellow]"))
    OpClass().remove()


# =============================================================================
# Commit Commands
# =============================================================================

@app.command()
def commit(
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Author name"),
) -> None:
    """Create a snapshot of current state."""
    CommitManager().commit(message=message, author=author)


@app.command()
def log(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of commits"),
) -> None:
    """Show commit history."""
    CommitManager().log(limit=limit)


@app.command()
def checkout(
    commit_id: str = typer.Argument(..., help="Commit ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Restore to a specific commit."""
    CommitManager().checkout(commit_id=commit_id, force=force)


@app.command()
def diff(
    commit_id: Optional[str] = typer.Argument(None, help="Compare with commit (default: HEAD)"),
) -> None:
    """Show changes since last commit."""
    CommitManager().diff(commit_id=commit_id)


@app.command()
def show(
    commit_id: str = typer.Argument(..., help="Commit ID to show"),
) -> None:
    """Show details of a commit."""
    CommitManager().show(commit_id=commit_id)


# =============================================================================
# Notes Commands
# =============================================================================

@notes_app.command("add")
def notes_add(
    content: str = typer.Argument(..., help="Note content"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Tag for the note"),
    priority: str = typer.Option("normal", "--priority", "-p", help="Priority: high, normal, low"),
) -> None:
    """Add a quick note."""
    NotesManager().add(content=content, tag=tag, priority=priority)


@notes_app.command("list")
def notes_list(
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
    all: bool = typer.Option(False, "--all", "-a", help="Include done notes"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max notes to show"),
) -> None:
    """List all notes."""
    NotesManager().list_notes(tag=tag, show_done=all, limit=limit)


@notes_app.command("search")
def notes_search(
    query: str = typer.Argument(..., help="Search query"),
) -> None:
    """Search notes."""
    NotesManager().search(query=query)


@notes_app.command("done")
def notes_done(
    note_id: int = typer.Argument(..., help="Note ID"),
) -> None:
    """Mark note as done."""
    NotesManager().done(note_id=note_id)


@notes_app.command("delete")
def notes_delete(
    note_id: int = typer.Argument(..., help="Note ID"),
) -> None:
    """Delete a note."""
    NotesManager().delete(note_id=note_id)


@notes_app.command("export")
def notes_export(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
) -> None:
    """Export notes to markdown."""
    NotesManager().export_markdown(output_path=output)


@notes_app.command("clear")
def notes_clear(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Clear all notes."""
    NotesManager().clear(force=force)


# =============================================================================
# Template Commands
# =============================================================================

@template_app.command("list")
def template_list() -> None:
    """List available templates."""
    TemplateManager().list_templates()


@template_app.command("show")
def template_show(
    name: str = typer.Argument(..., help="Template name"),
) -> None:
    """Show template details."""
    TemplateManager().show(template_name=name)


@template_app.command("create")
def template_create() -> None:
    """Create a new template interactively."""
    TemplateManager().create()


@template_app.command("delete")
def template_delete(
    name: str = typer.Argument(..., help="Template name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a template."""
    TemplateManager().delete(name=name, force=force)


# =============================================================================
# Server Commands
# =============================================================================

@server_app.command("list")
def server_list() -> None:
    """List repos on opsserver."""
    config = ConfigHandler()
    ip, key = config.read_server_config()
    user = Path(key).stem.split("_")[0]
    OpClassToServer().list_repos_from_server(ip, key, user)


@server_app.command("view")
def server_view(repo: str = typer.Argument(..., help="Repo name")) -> None:
    """View README from opsserver."""
    config = ConfigHandler()
    ip, key = config.read_server_config()
    user = Path(key).stem.split("_")[0]
    readme = OpClassToServer().cat_readme_from_opsserver(key, user, ip, repo)
    OpClass().view(readme)


# =============================================================================
# Top-level Commands (push, clone)
# =============================================================================

@app.command("push")
def push() -> None:
    """Push repo to opsserver."""
    config = ConfigHandler()
    ip, key = config.read_server_config()
    user = Path(key).stem.split("_")[0]
    OpClassToServer().push_repo(ip, key, user)


@app.command("clone")
def clone(repo: str = typer.Argument(..., help="Repo name")) -> None:
    """Clone repo from opsserver."""
    config = ConfigHandler()
    ip, key = config.read_server_config()
    user = Path(key).stem.split("_")[0]
    OpClassToServer().clone_repo(ip, key, user, repo)


# =============================================================================
# Entry Point
# =============================================================================

def main_cli() -> None:
    app()


if __name__ == "__main__":
    main_cli()
