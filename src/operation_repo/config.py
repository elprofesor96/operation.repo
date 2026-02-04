"""
Configuration handler for op repo.

Reads and parses the op.conf file for folder structure, files, and deployables.
"""

import configparser
import os
from pathlib import Path

from rich.console import Console

console = Console()


class ConfigHandler:
    """Handles reading and parsing op.conf configuration."""

    def __init__(self) -> None:
        self.enabled_folders: list[str] = []
        self.enabled_files: list[str] = []
        self.enabled_deployable: list[str] = []
        
        self.home_folder = Path.home()
        self.config = configparser.ConfigParser()
        self.config_path = self.home_folder / ".op" / "op.conf"
        
        if self.config_path.exists():
            self.config.read(self.config_path)
        
        self.opsdb_folder_path = self.home_folder / ".op" / "opsdb"
        self.sections = self.config.sections()
        
        self.custom_template_sections: list[str] = []
        self.custom_template_sections_length = 3

    def get_home_folder(self) -> Path:
        """Return the user's home folder."""
        return self.home_folder

    def get_db_folder_path(self) -> Path:
        """Return the opsdb folder path."""
        return self.opsdb_folder_path

    def get_deployable_folder_path(self) -> Path:
        """Return the deployable folder path (alias for opsdb)."""
        return self.opsdb_folder_path

    def read_folder_structure(self) -> list[str]:
        """Read enabled folders from [FOLDER] section."""
        self.enabled_folders = []
        
        if "FOLDER" not in self.sections:
            return self.enabled_folders
        
        folder_section = self.config["FOLDER"]
        for folder, enabled in folder_section.items():
            if enabled.lower() in ("on", "true", "yes", "1"):
                self.enabled_folders.append(folder)
        
        return self.enabled_folders

    def read_file_structure(self) -> list[str]:
        """Read enabled files from [FILE] section."""
        self.enabled_files = []
        
        if "FILE" not in self.sections:
            return self.enabled_files
        
        file_section = self.config["FILE"]
        for file, enabled in file_section.items():
            if enabled.lower() in ("on", "true", "yes", "1"):
                self.enabled_files.append(file)
        
        return self.enabled_files

    def read_db_structure(self) -> list[str]:
        """Read enabled deployables from [DB] section."""
        self.enabled_deployable = []
        
        if "DB" not in self.sections:
            return self.enabled_deployable
        
        db_section = self.config["DB"]
        for db, enabled in db_section.items():
            if enabled.lower() in ("on", "true", "yes", "1"):
                self.enabled_deployable.append(db)
        
        return self.enabled_deployable

    def read_server_config(self) -> tuple[str, str]:
        """Read server configuration (IP and SSH key)."""
        if "SERVER" not in self.sections:
            console.print("[red]✗[/red] No server configured")
            console.print("    Use: op remote add -h <host> -k <key>")
            raise SystemExit(1)
        
        try:
            server_ip = self.config["SERVER"]["opsserver_ip"]
            ssh_key = self.config["SERVER"]["ssh_key"]
        except KeyError as e:
            console.print(f"[red]✗[/red] Missing config key: {e}")
            console.print("    Use: op remote add -h <host> -k <key>")
            raise SystemExit(1)
        
        # Remove brackets if present (legacy format)
        server_ip = server_ip.strip("[]")
        ssh_key = ssh_key.strip("[]")
        
        return server_ip, ssh_key

    def show_server_config(self) -> None:
        """Display current server configuration."""
        if "SERVER" not in self.sections:
            console.print("[yellow]No remote configured[/yellow]")
            console.print("  Use: op remote add -h <host> -k <key>")
            return
        
        try:
            ip = self.config["SERVER"].get("opsserver_ip", "").strip("[]")
            key = self.config["SERVER"].get("ssh_key", "").strip("[]")
        except KeyError:
            console.print("[yellow]No remote configured[/yellow]")
            return

        is_default_ip = ip in ("127.0.0.1", "")
        is_default_key = key in ("/path/to/your/key", "")

        from rich.table import Table
        table = Table(title="Remote Configuration", show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value")

        if is_default_ip:
            table.add_row("Host", f"[dim]{ip} (not configured)[/dim]")
        else:
            table.add_row("Host", f"[green]{ip}[/green]")

        if is_default_key:
            table.add_row("SSH Key", f"[dim]{key} (not configured)[/dim]")
        else:
            # Check if key file exists
            key_path = Path(key).expanduser()
            if key_path.exists():
                table.add_row("SSH Key", f"[green]{key}[/green]")
            else:
                table.add_row("SSH Key", f"[red]{key} (file not found)[/red]")

        table.add_row("Config", str(self.config_path))

        console.print(table)

    def write_server_config(
        self,
        host: str | None = None,
        key: str | None = None
    ) -> None:
        """Write server configuration to op.conf."""
        # Ensure SERVER section exists
        if "SERVER" not in self.config.sections():
            self.config.add_section("SERVER")

        if host:
            self.config.set("SERVER", "opsserver_ip", host)
        if key:
            # Expand ~ to full path
            key_expanded = str(Path(key).expanduser())
            self.config.set("SERVER", "ssh_key", key_expanded)

        # Write config
        with open(self.config_path, "w") as f:
            self.config.write(f)

        # Reload
        self.config.read(self.config_path)
        self.sections = self.config.sections()

        # Show what was updated
        if host:
            console.print(f"[green]✓[/green] Host set to: {host}")
        if key:
            console.print(f"[green]✓[/green] SSH key set to: {key}")

    def remove_server_config(self) -> None:
        """Remove server configuration."""
        if "SERVER" in self.config.sections():
            self.config.set("SERVER", "opsserver_ip", "127.0.0.1")
            self.config.set("SERVER", "ssh_key", "/path/to/your/key")

            with open(self.config_path, "w") as f:
                self.config.write(f)

            console.print("[green]✓[/green] Remote configuration reset")

    def check_custom_template(self, template: str) -> bool:
        """
        Check if a custom template exists and has all required sections.
        
        A valid template needs 3 sections:
        - {template}_FOLDER
        - {template}_FILE  
        - {template}_DEPLOYABLE (or {template}_DB)
        """
        self.custom_template_sections = []
        template_upper = template.upper()
        
        for section in self.sections:
            section_upper = section.upper()
            if template_upper in section_upper:
                self.custom_template_sections.append(section)
        
        if len(self.custom_template_sections) < self.custom_template_sections_length:
            console.print()
            console.print(f"[red]✗[/red] Custom template '{template}' is not configured properly")
            console.print("    Please add these sections to ~/.op/op.conf:")
            console.print(f"    [{template}_FOLDER]")
            console.print(f"    [{template}_FILE]")
            console.print(f"    [{template}_DEPLOYABLE]")
            raise SystemExit(1)
        
        return True

    def read_custom_folder_structure(self) -> list[str]:
        """Read enabled folders from custom template's FOLDER section."""
        self.enabled_folders = []
        
        # Find the FOLDER section for this template
        folder_section = None
        for section in self.custom_template_sections:
            if "FOLDER" in section.upper():
                folder_section = section
                break
        
        if folder_section is None:
            return self.enabled_folders
        
        for folder, enabled in self.config[folder_section].items():
            if enabled.lower() in ("on", "true", "yes", "1"):
                self.enabled_folders.append(folder)
        
        return self.enabled_folders

    def read_custom_file_structure(self) -> list[str]:
        """Read enabled files from custom template's FILE section."""
        self.enabled_files = []
        
        # Find the FILE section for this template
        file_section = None
        for section in self.custom_template_sections:
            if "FILE" in section.upper():
                file_section = section
                break
        
        if file_section is None:
            return self.enabled_files
        
        for file, enabled in self.config[file_section].items():
            if enabled.lower() in ("on", "true", "yes", "1"):
                self.enabled_files.append(file)
        
        return self.enabled_files

    def read_custom_deployable_structure(self) -> list[str]:
        """Read enabled deployables from custom template's DEPLOYABLE section."""
        self.enabled_deployable = []
        
        # Find the DEPLOYABLE or DB section for this template
        deploy_section = None
        for section in self.custom_template_sections:
            section_upper = section.upper()
            if "DEPLOYABLE" in section_upper or "DB" in section_upper:
                deploy_section = section
                break
        
        if deploy_section is None:
            return self.enabled_deployable
        
        for deploy, enabled in self.config[deploy_section].items():
            if enabled.lower() in ("on", "true", "yes", "1"):
                self.enabled_deployable.append(deploy)
        
        return self.enabled_deployable
