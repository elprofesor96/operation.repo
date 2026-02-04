"""
Template management for op repo.

Handles: template list, template create, template show
"""

import configparser
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


class TemplateManager:
    """Handles template management for op repo."""

    def __init__(self) -> None:
        self.home_folder = Path.home()
        self.config_path = self.home_folder / ".op" / "op.conf"
        self.config = configparser.ConfigParser()
        
        if self.config_path.exists():
            self.config.read(self.config_path)

    def _reload_config(self) -> None:
        """Reload config from file."""
        self.config = configparser.ConfigParser()
        if self.config_path.exists():
            self.config.read(self.config_path)

    def _get_templates(self) -> dict[str, dict]:
        """Get all custom templates from config."""
        templates: dict[str, dict] = {}
        
        for section in self.config.sections():
            # Skip default sections
            if section in ("SERVER", "FOLDER", "FILE", "DB"):
                continue
            
            # Parse template name from section (e.g., "WEB_FOLDER" -> "web")
            parts = section.split("_")
            if len(parts) >= 2:
                template_name = parts[0].lower()
                section_type = "_".join(parts[1:]).upper()
                
                if template_name not in templates:
                    templates[template_name] = {
                        "name": template_name,
                        "folders": [],
                        "files": [],
                        "deployables": []
                    }
                
                # Parse items in section
                for key, value in self.config[section].items():
                    if value.lower() in ("on", "true", "yes", "1"):
                        if "FOLDER" in section_type:
                            templates[template_name]["folders"].append(key)
                        elif "FILE" in section_type:
                            templates[template_name]["files"].append(key)
                        elif "DEPLOYABLE" in section_type or "DB" in section_type:
                            templates[template_name]["deployables"].append(key)
        
        return templates

    def list_templates(self) -> None:
        """List all available templates."""
        templates = self._get_templates()
        
        # Add default template info
        console.print(Panel("[bold]Available Templates[/bold]"))
        
        # Default template
        console.print("\n[bold cyan]default[/bold cyan] (built-in)")
        console.print("  Creates: .op/, .opignore, README.md, opsdb/")
        console.print("  Plus any items in [FOLDER], [FILE], [DB] sections")
        
        if not templates:
            console.print("\n[dim]No custom templates found.[/dim]")
            console.print("[dim]Create one with: op template create[/dim]")
            return

        # Custom templates
        for name, template in sorted(templates.items()):
            console.print(f"\n[bold cyan]{name}[/bold cyan]")
            
            if template["folders"]:
                console.print(f"  [green]Folders:[/green] {', '.join(template['folders'])}")
            if template["files"]:
                console.print(f"  [green]Files:[/green] {', '.join(template['files'])}")
            if template["deployables"]:
                console.print(f"  [green]Deployables:[/green] {', '.join(template['deployables'])}")
        
        console.print(f"\n[dim]Use: op init -c <template>[/dim]")

    def show(self, template_name: str) -> None:
        """Show details of a specific template."""
        templates = self._get_templates()
        
        if template_name == "default":
            console.print(Panel("[bold]Default Template[/bold]"))
            console.print("\nAlways creates:")
            console.print("  • .op/")
            console.print("  • .opignore")
            console.print("  • README.md")
            console.print("  • opsdb/")
            console.print("  • opsdb/index.html")
            
            # Show default config items
            if "FOLDER" in self.config.sections():
                folders = [k for k, v in self.config["FOLDER"].items() if v.lower() in ("on", "true")]
                if folders:
                    console.print(f"\n[green]Folders from config:[/green] {', '.join(folders)}")
            
            if "FILE" in self.config.sections():
                files = [k for k, v in self.config["FILE"].items() if v.lower() in ("on", "true")]
                if files:
                    console.print(f"[green]Files from config:[/green] {', '.join(files)}")
            return

        if template_name not in templates:
            console.print(f"[red]✗[/red] Template '{template_name}' not found")
            console.print("  Use: op template list")
            return

        template = templates[template_name]
        
        console.print(Panel(f"[bold]Template: {template_name}[/bold]"))
        
        if template["folders"]:
            console.print("\n[bold]Folders:[/bold]")
            for f in template["folders"]:
                console.print(f"  • {f}")
        
        if template["files"]:
            console.print("\n[bold]Files:[/bold]")
            for f in template["files"]:
                console.print(f"  • {f}")
        
        if template["deployables"]:
            console.print("\n[bold]Deployables:[/bold]")
            for d in template["deployables"]:
                console.print(f"  • {d}")

        console.print(f"\n[dim]Use: op init -c {template_name}[/dim]")

    def create(self) -> None:
        """Interactively create a new template."""
        console.print(Panel("[bold]Create New Template[/bold]"))
        
        # Get template name
        name = Prompt.ask("Template name (e.g., web, pentest, api)").strip().lower()
        
        if not name:
            console.print("[red]✗[/red] Template name required")
            return
        
        if not name.isalnum():
            console.print("[red]✗[/red] Template name must be alphanumeric")
            return

        # Check if exists
        templates = self._get_templates()
        if name in templates:
            if not Confirm.ask(f"Template '{name}' exists. Overwrite?"):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Get folders
        console.print("\n[bold]Folders to create[/bold] (comma-separated, or empty to skip)")
        folders_input = Prompt.ask("Folders", default="")
        folders = [f.strip() for f in folders_input.split(",") if f.strip()]

        # Get files
        console.print("\n[bold]Files to create[/bold] (comma-separated, or empty to skip)")
        files_input = Prompt.ask("Files", default="")
        files = [f.strip() for f in files_input.split(",") if f.strip()]

        # Get deployables
        console.print("\n[bold]Deployables to copy[/bold] (from ~/.op/opsdb/, comma-separated)")
        deploy_input = Prompt.ask("Deployables", default="")
        deployables = [d.strip() for d in deploy_input.split(",") if d.strip()]

        # Confirm
        console.print("\n[bold]Template Summary:[/bold]")
        console.print(f"  Name: {name}")
        console.print(f"  Folders: {folders or '(none)'}")
        console.print(f"  Files: {files or '(none)'}")
        console.print(f"  Deployables: {deployables or '(none)'}")

        if not Confirm.ask("\nCreate this template?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

        # Write to config
        self._write_template(name, folders, files, deployables)
        
        console.print(f"\n[bold green]✓ Template '{name}' created![/bold green]")
        console.print(f"  Use: op init -c {name}")

    def _write_template(
        self,
        name: str,
        folders: list[str],
        files: list[str],
        deployables: list[str]
    ) -> None:
        """Write template to config file."""
        name_upper = name.upper()
        
        # Remove existing sections for this template
        for section in list(self.config.sections()):
            if section.startswith(f"{name_upper}_"):
                self.config.remove_section(section)

        # Add new sections
        folder_section = f"{name_upper}_FOLDER"
        file_section = f"{name_upper}_FILE"
        deploy_section = f"{name_upper}_DEPLOYABLE"

        self.config.add_section(folder_section)
        for f in folders:
            self.config.set(folder_section, f, "on")

        self.config.add_section(file_section)
        for f in files:
            self.config.set(file_section, f, "on")

        self.config.add_section(deploy_section)
        for d in deployables:
            self.config.set(deploy_section, d, "on")

        # Write config
        with open(self.config_path, "w") as f:
            self.config.write(f)

    def delete(self, name: str, force: bool = False) -> bool:
        """Delete a template."""
        templates = self._get_templates()
        
        if name not in templates:
            console.print(f"[red]✗[/red] Template '{name}' not found")
            return False

        if not force:
            if not Confirm.ask(f"Delete template '{name}'?"):
                console.print("[yellow]Cancelled[/yellow]")
                return False

        name_upper = name.upper()
        
        # Remove sections
        for section in list(self.config.sections()):
            if section.startswith(f"{name_upper}_"):
                self.config.remove_section(section)

        # Write config
        with open(self.config_path, "w") as f:
            self.config.write(f)

        console.print(f"[green]✓[/green] Template '{name}' deleted")
        return True
