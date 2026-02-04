"""
Commit system for op repo - Git-like snapshots of your operation.

Handles: commit, log, checkout, diff
"""

import hashlib
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

console = Console()


class CommitManager:
    """Handles Git-like commit operations for op repo."""

    def __init__(self) -> None:
        self.pwd = Path.cwd()
        self.op_dir = self.pwd / ".op"
        self.commits_dir = self.op_dir / "commits"
        self.head_file = self.op_dir / "HEAD"
        self.index_file = self.op_dir / "index.json"

    def _is_op_repo(self) -> bool:
        """Check if current directory is an op repo."""
        return (self.pwd / ".opignore").exists()

    def _ensure_commits_dir(self) -> None:
        """Create commits directory if it doesn't exist."""
        self.commits_dir.mkdir(parents=True, exist_ok=True)

    def _read_opignore(self) -> list[str]:
        """Read .opignore file."""
        opignore_path = self.pwd / ".opignore"
        if not opignore_path.exists():
            return []
        with open(opignore_path, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def _get_ignored_paths(self) -> set[Path]:
        """Get all paths that should be ignored."""
        ignored_lines = self._read_opignore()
        ignored_paths: set[Path] = set()

        for line in ignored_lines:
            path = self.pwd / line
            ignored_paths.add(path)
            if path.is_dir():
                for nested in path.rglob("*"):
                    ignored_paths.add(nested)

        return ignored_paths

    def _get_tracked_files(self) -> list[Path]:
        """Get list of tracked files (not in .opignore)."""
        ignored_paths = self._get_ignored_paths()
        all_files = [f for f in self.pwd.rglob("*") if f.is_file()]
        return [f for f in all_files if f not in ignored_paths]

    def _generate_commit_id(self) -> str:
        """Generate a short unique commit ID."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}-{self.pwd}"
        return hashlib.sha1(hash_input.encode()).hexdigest()[:7]

    def _get_head(self) -> Optional[str]:
        """Get current HEAD commit ID."""
        if not self.head_file.exists():
            return None
        return self.head_file.read_text().strip()

    def _set_head(self, commit_id: str) -> None:
        """Set HEAD to a commit ID."""
        self.head_file.write_text(commit_id)

    def _get_commit_metadata(self, commit_id: str) -> Optional[dict]:
        """Get metadata for a commit."""
        meta_file = self.commits_dir / f"{commit_id}.json"
        if not meta_file.exists():
            return None
        with open(meta_file, "r") as f:
            return json.load(f)

    def _get_all_commits(self) -> list[dict]:
        """Get all commits in chronological order."""
        if not self.commits_dir.exists():
            return []

        commits = []
        for meta_file in self.commits_dir.glob("*.json"):
            with open(meta_file, "r") as f:
                commits.append(json.load(f))

        # Sort by timestamp (newest first)
        commits.sort(key=lambda c: c["timestamp"], reverse=True)
        return commits

    def _file_hash(self, filepath: Path) -> str:
        """Calculate hash of a file."""
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _get_file_snapshot(self) -> dict[str, str]:
        """Get current state of all tracked files as {relative_path: hash}."""
        snapshot = {}
        for f in self._get_tracked_files():
            rel_path = str(f.relative_to(self.pwd))
            snapshot[rel_path] = self._file_hash(f)
        return snapshot

    def commit(self, message: str, author: Optional[str] = None) -> str:
        """Create a new commit snapshot."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            raise SystemExit(1)

        self._ensure_commits_dir()

        commit_id = self._generate_commit_id()
        timestamp = datetime.now().isoformat()
        parent = self._get_head()

        # Get tracked files
        tracked_files = self._get_tracked_files()
        if not tracked_files:
            console.print("[yellow]![/yellow] Nothing to commit (no tracked files)")
            raise SystemExit(1)

        # Create snapshot zip
        zip_path = self.commits_dir / f"{commit_id}.zip"
        file_list = []

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in tracked_files:
                rel_path = file_path.relative_to(self.pwd)
                zf.write(file_path, rel_path)
                file_list.append(str(rel_path))

        # Create metadata
        metadata = {
            "id": commit_id,
            "message": message,
            "timestamp": timestamp,
            "author": author or "op-user",
            "parent": parent,
            "files": file_list,
            "file_count": len(file_list),
            "snapshot": self._get_file_snapshot()
        }

        meta_path = self.commits_dir / f"{commit_id}.json"
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        # Update HEAD
        self._set_head(commit_id)

        console.print(Panel(f"[bold green]✓ Commit created[/bold green]"))
        console.print(f"  [cyan]ID:[/cyan]      {commit_id}")
        console.print(f"  [cyan]Message:[/cyan] {message}")
        console.print(f"  [cyan]Files:[/cyan]   {len(file_list)}")

        return commit_id

    def log(self, limit: int = 10) -> None:
        """Show commit history."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return

        commits = self._get_all_commits()
        head = self._get_head()

        if not commits:
            console.print("[yellow]No commits yet[/yellow]")
            console.print("  Use: op commit -m \"your message\"")
            return

        console.print(Panel("[bold]Commit History[/bold]"))

        for i, commit in enumerate(commits[:limit]):
            is_head = commit["id"] == head
            head_marker = " [bold yellow](HEAD)[/bold yellow]" if is_head else ""

            # Format timestamp
            ts = datetime.fromisoformat(commit["timestamp"])
            time_str = ts.strftime("%Y-%m-%d %H:%M")

            console.print(f"\n[bold cyan]{commit['id']}[/bold cyan]{head_marker}")
            console.print(f"  [dim]{time_str}[/dim] - {commit['message']}")
            console.print(f"  [dim]{commit['file_count']} files[/dim]")

        if len(commits) > limit:
            console.print(f"\n[dim]... and {len(commits) - limit} more commits[/dim]")

    def restore(self, commit_id: str, force: bool = False) -> bool:
        """Restore files to a specific commit."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return False

        # Find the commit (support partial IDs)
        commits = self._get_all_commits()
        target_commit = None

        for commit in commits:
            if commit["id"].startswith(commit_id):
                target_commit = commit
                break

        if not target_commit:
            console.print(f"[red]✗[/red] Commit '{commit_id}' not found")
            return False

        commit_id = target_commit["id"]
        zip_path = self.commits_dir / f"{commit_id}.zip"

        if not zip_path.exists():
            console.print(f"[red]✗[/red] Commit snapshot not found: {zip_path}")
            return False

        if not force:
            console.print(f"[yellow]![/yellow] This will restore files to commit: {commit_id}")
            console.print(f"    Message: {target_commit['message']}")
            console.print(f"    Files: {target_commit['file_count']}")
            console.print()

            import typer
            confirm = typer.confirm("Continue?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                return False

        # Extract files from commit
        ignored_paths = self._get_ignored_paths()

        with zipfile.ZipFile(zip_path, 'r') as zf:
            for file_info in zf.infolist():
                target_path = self.pwd / file_info.filename

                # Skip if in ignored paths
                if target_path in ignored_paths:
                    continue

                # Create parent directories
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Extract file
                with zf.open(file_info) as src:
                    with open(target_path, 'wb') as dst:
                        dst.write(src.read())

        # Update HEAD
        self._set_head(commit_id)

        console.print(f"\n[bold green]✓ Restored to commit {commit_id}[/bold green]")
        console.print(f"  {target_commit['file_count']} files restored")

        return True

    def diff(self, commit_id: Optional[str] = None) -> None:
        """Show changes since last commit (or specific commit)."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return

        # Get target commit
        if commit_id:
            commits = self._get_all_commits()
            target = None
            for c in commits:
                if c["id"].startswith(commit_id):
                    target = c
                    break
            if not target:
                console.print(f"[red]✗[/red] Commit '{commit_id}' not found")
                return
        else:
            target_id = self._get_head()
            if not target_id:
                console.print("[yellow]No commits yet - nothing to compare[/yellow]")
                return
            target = self._get_commit_metadata(target_id)

        if not target:
            console.print("[yellow]No commits yet[/yellow]")
            return

        # Compare current state with commit
        current_snapshot = self._get_file_snapshot()
        commit_snapshot = target.get("snapshot", {})

        added = []
        modified = []
        deleted = []

        # Find added and modified files
        for path, hash_val in current_snapshot.items():
            if path not in commit_snapshot:
                added.append(path)
            elif commit_snapshot[path] != hash_val:
                modified.append(path)

        # Find deleted files
        for path in commit_snapshot:
            if path not in current_snapshot:
                deleted.append(path)

        # Display results
        console.print(Panel(f"[bold]Changes since commit {target['id']}[/bold]"))

        if not added and not modified and not deleted:
            console.print("[green]✓ No changes[/green]")
            return

        if added:
            console.print(f"\n[bold green]Added ({len(added)}):[/bold green]")
            for f in added:
                console.print(f"  [green]+[/green] {f}")

        if modified:
            console.print(f"\n[bold yellow]Modified ({len(modified)}):[/bold yellow]")
            for f in modified:
                console.print(f"  [yellow]~[/yellow] {f}")

        if deleted:
            console.print(f"\n[bold red]Deleted ({len(deleted)}):[/bold red]")
            for f in deleted:
                console.print(f"  [red]-[/red] {f}")

        console.print(f"\n[dim]Total: {len(added)} added, {len(modified)} modified, {len(deleted)} deleted[/dim]")

    def show(self, commit_id: str) -> None:
        """Show details of a specific commit."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return

        # Find commit
        commits = self._get_all_commits()
        target = None
        for c in commits:
            if c["id"].startswith(commit_id):
                target = c
                break

        if not target:
            console.print(f"[red]✗[/red] Commit '{commit_id}' not found")
            return

        # Display commit details
        ts = datetime.fromisoformat(target["timestamp"])

        console.print(Panel(f"[bold]Commit {target['id']}[/bold]"))

        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value")

        table.add_row("Message", target["message"])
        table.add_row("Author", target["author"])
        table.add_row("Date", ts.strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Parent", target["parent"] or "(none)")
        table.add_row("Files", str(target["file_count"]))

        console.print(table)

        console.print("\n[bold]Files in this commit:[/bold]")
        for f in target["files"][:20]:
            console.print(f"  • {f}")

        if len(target["files"]) > 20:
            console.print(f"  [dim]... and {len(target['files']) - 20} more[/dim]")
