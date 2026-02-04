"""
Core operations for op repo - init, export, remove, status.
"""

import hashlib
import os
import shutil
import subprocess
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


class OpClass:
    """Handles core op repo operations."""

    def __init__(self) -> None:
        self.pwd = Path.cwd()

    def _is_op_repo(self) -> bool:
        """Check if current directory is an op repo."""
        return (self.pwd / ".opignore").exists()

    def _read_opignore(self) -> list[str]:
        """Read and return lines from .opignore file."""
        opignore_path = self.pwd / ".opignore"
        
        if not opignore_path.exists():
            console.print("[red]✗[/red] Not an op repo (no .opignore found)")
            raise SystemExit(1)
        
        with open(opignore_path, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def _get_ignored_paths(self) -> set[Path]:
        """Get all paths that should be ignored (including nested)."""
        ignored_lines = self._read_opignore()
        ignored_paths: set[Path] = set()
        
        for line in ignored_lines:
            path = self.pwd / line
            ignored_paths.add(path)
            
            # Add all nested files/folders if it's a directory
            if path.is_dir():
                for nested in path.rglob("*"):
                    ignored_paths.add(nested)
        
        return ignored_paths

    def _write_to_opignore(self, line: str) -> None:
        """Append a line to .opignore file."""
        opignore_path = self.pwd / ".opignore"
        with open(opignore_path, "a") as f:
            f.write(line + "\n")

    def _generate_export_name(self, format: str = "zip") -> str:
        """Generate a timestamped export filename."""
        folder_name = self.pwd.name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        return f"{folder_name}-{timestamp}-export.{format}"

    def _get_tracked_files(self) -> list[Path]:
        """Get list of tracked files (not in .opignore)."""
        ignored_paths = self._get_ignored_paths()
        all_files = [f for f in self.pwd.rglob("*") if f.is_file()]
        return [f for f in all_files if f not in ignored_paths]

    def _file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of a file."""
        with open(filepath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def create_opfolder(self, total: int = 5) -> None:
        """Create the .op folder."""
        op_folder = self.pwd / ".op"
        
        if op_folder.exists():
            console.print("[red]✗[/red] Op repo is already initialized!")
            raise SystemExit(1)
        
        op_folder.mkdir()
        console.print(f"[green]✓[/green] [1/{total}] Created {op_folder}")

    def create_opignore(self, total: int = 5) -> None:
        """Create the .opignore file."""
        opignore_path = self.pwd / ".opignore"
        
        if opignore_path.exists():
            console.print("[red]✗[/red] Op repo is already initialized!")
            raise SystemExit(1)
        
        opignore_path.touch()
        console.print(f"[green]✓[/green] [2/{total}] Created {opignore_path}")

    def create_readme(self, total: int = 5) -> None:
        """Create README.md file."""
        readme_path = self.pwd / "README.md"
        
        if readme_path.exists():
            console.print("[yellow]![/yellow] README.md already exists, skipping")
            return
        
        # Create with template content
        template = f"""# {self.pwd.name}

## Overview

Operation initialized on {datetime.now().strftime("%Y-%m-%d %H:%M")}.

## Notes

- 

## Findings

- 

## Timeline

| Date | Event |
|------|-------|
| {datetime.now().strftime("%Y-%m-%d")} | Operation started |

"""
        readme_path.write_text(template)
        console.print(f"[green]✓[/green] [3/{total}] Created {readme_path}")

    def create_opsdb(self, total: int = 5) -> None:
        """Create opsdb folder with index.html."""
        opsdb_path = self.pwd / "opsdb"
        index_path = opsdb_path / "index.html"
        
        if opsdb_path.exists():
            console.print("[yellow]![/yellow] opsdb already exists, skipping")
            return
        
        opsdb_path.mkdir()
        console.print(f"[green]✓[/green] [4/{total}] Created {opsdb_path}")
        
        index_path.touch()
        console.print(f"[green]✓[/green] [5/{total}] Created {index_path}")

    def create_default(self) -> None:
        """Create default op repo structure."""
        self.create_opfolder()
        self.create_opignore()
        self._write_to_opignore(".op")
        self.create_readme()
        self.create_opsdb()

    def create_folders(self, folder_list: list[str]) -> None:
        """Create folders from config."""
        if not folder_list:
            return
        
        console.print("\n[bold]Creating folders:[/bold]")
        for i, folder in enumerate(folder_list, 1):
            folder_path = self.pwd / folder
            try:
                folder_path.mkdir(parents=True, exist_ok=False)
                console.print(f"[green]✓[/green] [{i}/{len(folder_list)}] Created {folder_path}")
            except FileExistsError:
                console.print(f"[yellow]![/yellow] [{i}/{len(folder_list)}] {folder} already exists")
            except PermissionError as e:
                console.print(f"[red]✗[/red] [{i}/{len(folder_list)}] Permission denied: {e}")

    def create_files(self, file_list: list[str]) -> None:
        """Create files from config."""
        if not file_list:
            return
        
        console.print("\n[bold]Creating files:[/bold]")
        for i, file in enumerate(file_list, 1):
            file_path = self.pwd / file
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch(exist_ok=False)
                console.print(f"[green]✓[/green] [{i}/{len(file_list)}] Created {file_path}")
            except FileExistsError:
                console.print(f"[yellow]![/yellow] [{i}/{len(file_list)}] {file} already exists")
            except PermissionError as e:
                console.print(f"[red]✗[/red] [{i}/{len(file_list)}] Permission denied: {e}")

    def create_deployables(self, deploy_list: list[str], deployable_db: str) -> None:
        """Copy deployable scripts from the deployable database."""
        if not deploy_list:
            return
        
        deployable_dir = self.pwd / "deployable"
        deployable_dir.mkdir(exist_ok=True)
        
        console.print("\n[bold]Creating deployables:[/bold]")
        for i, deploy in enumerate(deploy_list, 1):
            source = Path(deployable_db) / deploy
            
            # Handle nested paths - use only the filename
            if "/" in deploy:
                dest_name = deploy.split("/")[-1]
            else:
                dest_name = deploy
            
            dest = deployable_dir / dest_name
            
            try:
                if source.is_file():
                    shutil.copy(source, dest)
                    console.print(f"[green]✓[/green] [{i}/{len(deploy_list)}] Copied {dest}")
                elif source.is_dir():
                    shutil.copytree(source, dest)
                    console.print(f"[green]✓[/green] [{i}/{len(deploy_list)}] Copied {dest}")
                else:
                    console.print(f"[red]✗[/red] [{i}/{len(deploy_list)}] Source not found: {source}")
            except FileExistsError:
                console.print(f"[yellow]![/yellow] [{i}/{len(deploy_list)}] {dest_name} already exists")
            except PermissionError as e:
                console.print(f"[red]✗[/red] [{i}/{len(deploy_list)}] Permission denied: {e}")
            except shutil.Error as e:
                console.print(f"[red]✗[/red] [{i}/{len(deploy_list)}] Copy error: {e}")

    def init(self, config_handler) -> bool:
        """Initialize a new op repo with default settings."""
        console.print()
        
        self.create_default()
        
        enabled_folders = config_handler.read_folder_structure() or []
        self.create_folders(enabled_folders)
        
        enabled_files = config_handler.read_file_structure() or []
        self.create_files(enabled_files)
        
        enabled_deploys = config_handler.read_db_structure() or []
        deployable_db = config_handler.get_db_folder_path()
        self.create_deployables(enabled_deploys, deployable_db)
        
        console.print("\n[bold green]✓ Op repo initialized successfully![/bold green]")
        return True

    def init_template(self, config_handler, template: str) -> bool:
        """Initialize op repo with a custom template."""
        config_handler.check_custom_template(template)
        console.print()
        
        self.create_default()
        
        enabled_folders = config_handler.read_custom_folder_structure() or []
        self.create_folders(enabled_folders)
        
        enabled_files = config_handler.read_custom_file_structure() or []
        self.create_files(enabled_files)
        
        enabled_deploys = config_handler.read_custom_deployable_structure() or []
        deployable_db = config_handler.get_deployable_folder_path()
        self.create_deployables(enabled_deploys, deployable_db)
        
        console.print(f"\n[bold green]✓ Op repo initialized with template '{template}'![/bold green]")
        return True

    def status(self) -> None:
        """Show current op repo status with changes detection."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return
        
        # Count files
        ignored_paths = self._get_ignored_paths()
        all_files = list(self.pwd.rglob("*"))
        tracked_files = [f for f in all_files if f.is_file() and f not in ignored_paths]
        
        # Get exports
        op_folder = self.pwd / ".op"
        exports_dir = op_folder / "exports"
        exports = list(exports_dir.glob("*-export.*")) if exports_dir.exists() else []
        
        # Get commits
        commits_dir = op_folder / "commits"
        commits = list(commits_dir.glob("*.json")) if commits_dir.exists() else []
        
        # Get notes count
        notes_file = op_folder / "notes.json"
        notes_count = 0
        if notes_file.exists():
            import json
            with open(notes_file) as f:
                notes_count = len(json.load(f))
        
        # Get HEAD commit
        head_file = op_folder / "HEAD"
        head_commit = head_file.read_text().strip() if head_file.exists() else None
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in tracked_files if f.exists())
        size_mb = total_size / (1024 * 1024)
        
        # Create status display
        console.print(Panel(f"[bold]{self.pwd.name}[/bold]", subtitle="Op Repo Status"))
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("📁 Location", str(self.pwd))
        table.add_row("📄 Tracked files", str(len(tracked_files)))
        table.add_row("💾 Total size", f"{size_mb:.2f} MB")
        table.add_row("📦 Exports", str(len(exports)))
        table.add_row("🔖 Commits", str(len(commits)))
        table.add_row("📝 Notes", str(notes_count))
        
        if head_commit:
            table.add_row("🎯 HEAD", head_commit)
        
        console.print(table)
        
        # Show recent exports
        if exports:
            console.print("\n[bold]Recent exports:[/bold]")
            for export in sorted(exports, reverse=True)[:3]:
                size_mb = export.stat().st_size / (1024 * 1024)
                console.print(f"  • {export.name} ({size_mb:.2f} MB)")
        
        # Check for uncommitted changes
        if commits and head_commit:
            from operation_repo.commits import CommitManager
            cm = CommitManager()
            current = cm._get_file_snapshot()
            
            head_meta_file = commits_dir / f"{head_commit}.json"
            if head_meta_file.exists():
                import json
                with open(head_meta_file) as f:
                    head_meta = json.load(f)
                last_snapshot = head_meta.get("snapshot", {})
                
                changes = len(set(current.keys()) ^ set(last_snapshot.keys()))
                for path in current:
                    if path in last_snapshot and current[path] != last_snapshot[path]:
                        changes += 1
                
                if changes > 0:
                    console.print(f"\n[yellow]⚠ {changes} uncommitted changes[/yellow]")
                    console.print("  Use: op diff")

    def export(
        self,
        format: str = "zip",
        encrypt: bool = False,
        password: Optional[str] = None,
        output: Optional[str] = None
    ) -> str:
        """Export op repo to a file (respects .opignore)."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            raise SystemExit(1)
        
        ignored_paths = self._get_ignored_paths()
        
        # Determine output path
        if output:
            export_path = Path(output)
        else:
            export_name = self._generate_export_name(format)
            exports_dir = self.pwd / ".op" / "exports"
            exports_dir.mkdir(parents=True, exist_ok=True)
            export_path = exports_dir / export_name
        
        # Get files to export
        files_to_export = self._get_tracked_files()
        
        if not files_to_export:
            console.print("[yellow]![/yellow] No files to export")
            raise SystemExit(1)
        
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Creating {format} export...", total=len(files_to_export))
            
            if format == "zip":
                self._export_zip(export_path, files_to_export, progress, task)
            elif format == "tar.gz" or format == "tgz":
                self._export_targz(export_path, files_to_export, progress, task)
            elif format == "tar":
                self._export_tar(export_path, files_to_export, progress, task)
            else:
                console.print(f"[red]✗[/red] Unknown format: {format}")
                console.print("  Supported: zip, tar.gz, tar")
                raise SystemExit(1)
        
        # Encrypt if requested
        if encrypt:
            export_path = self._encrypt_file(export_path, password)
        
        size_mb = export_path.stat().st_size / (1024 * 1024)
        console.print(f"\n[bold green]✓ Export saved:[/bold green] {export_path}")
        console.print(f"  Files: {len(files_to_export)} | Size: {size_mb:.2f} MB")
        
        if encrypt:
            console.print("  [cyan]🔒 Encrypted[/cyan]")
        
        return str(export_path)

    def _export_zip(self, path: Path, files: list[Path], progress, task) -> None:
        """Export to ZIP format."""
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                relative_path = file_path.relative_to(self.pwd)
                zf.write(file_path, relative_path)
                progress.advance(task)

    def _export_targz(self, path: Path, files: list[Path], progress, task) -> None:
        """Export to tar.gz format."""
        with tarfile.open(path, "w:gz") as tf:
            for file_path in files:
                relative_path = file_path.relative_to(self.pwd)
                tf.add(file_path, arcname=relative_path)
                progress.advance(task)

    def _export_tar(self, path: Path, files: list[Path], progress, task) -> None:
        """Export to tar format."""
        with tarfile.open(path, "w") as tf:
            for file_path in files:
                relative_path = file_path.relative_to(self.pwd)
                tf.add(file_path, arcname=relative_path)
                progress.advance(task)

    def _encrypt_file(self, path: Path, password: Optional[str] = None) -> Path:
        """Encrypt a file using GPG."""
        if not password:
            import typer
            password = typer.prompt("Encryption password", hide_input=True)
        
        encrypted_path = path.with_suffix(path.suffix + ".gpg")
        
        try:
            subprocess.run(
                [
                    "gpg", "--symmetric", "--batch", "--yes",
                    "--passphrase", password,
                    "--output", str(encrypted_path),
                    str(path)
                ],
                check=True,
                capture_output=True
            )
            # Remove unencrypted file
            path.unlink()
            return encrypted_path
        except FileNotFoundError:
            console.print("[yellow]![/yellow] GPG not found, skipping encryption")
            return path
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗[/red] Encryption failed: {e}")
            return path

    # Keep backup as alias for export (backward compatibility)
    def backup(self) -> str:
        """Backup op repo (alias for export)."""
        return self.export(format="zip")

    def remove(self) -> bool:
        """Remove op repo files (respects .opignore)."""
        ignored_paths = self._get_ignored_paths()
        
        # Get all files and directories
        all_paths = list(self.pwd.rglob("*"))
        
        # Filter out ignored paths
        paths_to_remove = [p for p in all_paths if p not in ignored_paths]
        
        # Sort by depth (deepest first) to remove files before their parent dirs
        paths_to_remove.sort(key=lambda p: len(p.parts), reverse=True)
        
        console.print()
        removed_count = 0
        
        for path in paths_to_remove:
            try:
                if path.is_file():
                    path.unlink()
                    console.print(f"[red]✗[/red] Removed {path}")
                    removed_count += 1
                elif path.is_dir() and not any(path.iterdir()):
                    path.rmdir()
                    console.print(f"[red]✗[/red] Removed {path}/")
                    removed_count += 1
            except FileNotFoundError:
                pass
            except PermissionError as e:
                console.print(f"[yellow]![/yellow] Permission denied: {e}")
        
        # Clean up empty .op folder
        op_folder = self.pwd / ".op"
        if op_folder.exists() and not any(op_folder.iterdir()):
            op_folder.rmdir()
            console.print(f"[red]✗[/red] Removed {op_folder}/")
        
        console.print(f"\n[bold green]✓ Removed {removed_count} items[/bold green]")
        return True

    def view(self, readme_path: str) -> None:
        """View a README file using grip (GitHub-flavored markdown)."""
        try:
            subprocess.run(
                ["grip", "-b", readme_path],
                check=True,
                capture_output=False
            )
        except FileNotFoundError:
            console.print("[red]✗[/red] 'grip' not found. Install with: pip install grip")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗[/red] Error running grip: {e}")
