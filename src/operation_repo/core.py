"""
Core operations for op repo - init, backup, remove, status.
"""

import os
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

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

    def _generate_zip_name(self) -> str:
        """Generate a timestamped backup filename."""
        folder_name = self.pwd.name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        return f"{folder_name}-{timestamp}-backup.zip"

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
        
        readme_path.touch()
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
        """Show current op repo status."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return
        
        # Count files
        ignored_paths = self._get_ignored_paths()
        all_files = list(self.pwd.rglob("*"))
        tracked_files = [f for f in all_files if f.is_file() and f not in ignored_paths]
        
        # Get backups
        op_folder = self.pwd / ".op"
        backups = list(op_folder.glob("*.zip")) if op_folder.exists() else []
        
        # Create status table
        table = Table(title=f"Op Repo: {self.pwd.name}", show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Location", str(self.pwd))
        table.add_row("Tracked files", str(len(tracked_files)))
        table.add_row("Backups", str(len(backups)))
        
        console.print(table)
        
        if backups:
            console.print("\n[bold]Backups:[/bold]")
            for backup in sorted(backups, reverse=True):
                size_mb = backup.stat().st_size / (1024 * 1024)
                console.print(f"  • {backup.name} ({size_mb:.2f} MB)")

    def backup(self) -> str:
        """Backup op repo to a zip file (respects .opignore)."""
        ignored_paths = self._get_ignored_paths()
        zip_name = self._generate_zip_name()
        zip_path = self.pwd / ".op" / zip_name
        
        # Get files to backup
        all_files = [f for f in self.pwd.rglob("*") if f.is_file()]
        files_to_zip = [f for f in all_files if f not in ignored_paths and f != zip_path]
        
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating backup...", total=len(files_to_zip))
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                for file_path in files_to_zip:
                    relative_path = file_path.relative_to(self.pwd)
                    backup_zip.write(file_path, relative_path)
                    progress.advance(task)
        
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        console.print(f"\n[bold green]✓ Backup saved:[/bold green] {zip_path}")
        console.print(f"  Files: {len(files_to_zip)} | Size: {size_mb:.2f} MB")
        
        return str(zip_path)

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
