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
            console.print("[red]✗[/red] No [SERVER] section in op.conf")
            console.print("    Please configure ~/.op/op.conf with:")
            console.print("    [SERVER]")
            console.print("    opsserver_ip = your.server.ip")
            console.print("    ssh_key = /path/to/your/key")
            raise SystemExit(1)
        
        try:
            server_ip = self.config["SERVER"]["opsserver_ip"]
            ssh_key = self.config["SERVER"]["ssh_key"]
        except KeyError as e:
            console.print(f"[red]✗[/red] Missing config key: {e}")
            raise SystemExit(1)
        
        # Remove brackets if present (legacy format)
        server_ip = server_ip.strip("[]")
        ssh_key = ssh_key.strip("[]")
        
        return server_ip, ssh_key

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
