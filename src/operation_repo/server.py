"""
Server operations for op repo - push, clone, list, view from opsserver.
"""

import subprocess
import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


class OpClassToServer:
    """Handles communication with the ops server via SSH/SCP."""

    def __init__(self) -> None:
        pass

    def _run_ssh_command(
        self,
        key: str,
        user: str,
        ip: str,
        command: str,
        capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a command on the remote server via SSH."""
        ssh_cmd = [
            "ssh",
            "-i", key,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"{user}@{ip}",
            command
        ]

        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except FileNotFoundError:
            console.print("[red]✗[/red] SSH not found. Please install OpenSSH.")
            raise SystemExit(1)

    def _run_scp_upload(
        self,
        key: str,
        local_path: str,
        user: str,
        ip: str,
        remote_path: str
    ) -> bool:
        """Upload a file to the remote server via SCP."""
        scp_cmd = [
            "scp",
            "-i", key,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            local_path,
            f"{user}@{ip}:{remote_path}"
        ]

        try:
            result = subprocess.run(
                scp_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            console.print("[red]✗[/red] SCP not found. Please install OpenSSH.")
            raise SystemExit(1)

    def _run_scp_download(
        self,
        key: str,
        user: str,
        ip: str,
        remote_path: str,
        local_path: str
    ) -> bool:
        """Download a file from the remote server via SCP."""
        scp_cmd = [
            "scp",
            "-i", key,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            "-r",  # Recursive for directories
            f"{user}@{ip}:{remote_path}",
            local_path
        ]

        try:
            result = subprocess.run(
                scp_cmd,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            console.print("[red]✗[/red] SCP not found. Please install OpenSSH.")
            raise SystemExit(1)

    def list_repos_from_server(self, ip: str, key: str, user: str) -> list[str]:
        """List all repositories on the opsserver."""
        console.print(f"\n[bold]Listing repos from {ip}...[/bold]\n")

        # List directories in user's home on the server
        result = self._run_ssh_command(
            key=key,
            user=user,
            ip=ip,
            command="ls -1 ~/"
        )

        if result.returncode != 0:
            console.print("[red]✗[/red] Failed to connect to server")
            if result.stderr:
                console.print(f"    Error: {result.stderr.strip()}")
            return []

        repos = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]

        if not repos:
            console.print("[yellow]No repos found on server[/yellow]")
            return []

        table = Table(title="Repositories on opsserver")
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Name", style="green")

        for i, repo in enumerate(repos, 1):
            table.add_row(str(i), repo)

        console.print(table)
        return repos

    def push_repo(self, ip: str, key: str, user: str) -> bool:
        """Push the current repo to opsserver."""
        pwd = Path.cwd()
        repo_name = pwd.name

        console.print(f"\n[bold]Pushing '{repo_name}' to {ip}...[/bold]\n")

        # First export the repo
        from operation_repo.core import OpClass
        op_class = OpClass()

        try:
            export_path = op_class.export(format="zip")
        except SystemExit:
            console.print("[red]✗[/red] Failed to create export for push")
            return False

        # Upload the export
        remote_path = f"~/{repo_name}.zip"

        console.print(f"[cyan]Uploading to {user}@{ip}:{remote_path}...[/cyan]")

        success = self._run_scp_upload(
            key=key,
            local_path=export_path,
            user=user,
            ip=ip,
            remote_path=remote_path
        )

        if success:
            # Extract on server
            extract_cmd = f"cd ~ && unzip -o {repo_name}.zip -d {repo_name} && rm {repo_name}.zip"
            result = self._run_ssh_command(key=key, user=user, ip=ip, command=extract_cmd)

            if result.returncode == 0:
                console.print(f"\n[bold green]✓ Pushed '{repo_name}' successfully![/bold green]")
                return True
            else:
                console.print("[red]✗[/red] Failed to extract on server")
                return False
        else:
            console.print("[red]✗[/red] Failed to upload to server")
            return False

    def clone_repo(self, ip: str, key: str, user: str, repo: str) -> bool:
        """Clone a repo from opsserver."""
        console.print(f"\n[bold]Cloning '{repo}' from {ip}...[/bold]\n")

        local_path = Path.cwd() / repo

        if local_path.exists():
            console.print(f"[red]✗[/red] Directory '{repo}' already exists")
            return False

        # Download the repo
        success = self._run_scp_download(
            key=key,
            user=user,
            ip=ip,
            remote_path=f"~/{repo}",
            local_path=str(local_path)
        )

        if success:
            console.print(f"\n[bold green]✓ Cloned '{repo}' successfully![/bold green]")
            console.print(f"    Location: {local_path}")
            return True
        else:
            console.print("[red]✗[/red] Failed to clone repo")
            return False

    def cat_readme_from_opsserver(
        self,
        key: str,
        user: str,
        ip: str,
        repo: str
    ) -> str:
        """Fetch README.md from a repo on opsserver and save locally."""
        console.print(f"\n[bold]Fetching README from '{repo}'...[/bold]\n")

        # Get README content
        result = self._run_ssh_command(
            key=key,
            user=user,
            ip=ip,
            command=f"cat ~/{repo}/README.md"
        )

        if result.returncode != 0:
            console.print("[red]✗[/red] Failed to fetch README")
            if result.stderr:
                console.print(f"    Error: {result.stderr.strip()}")
            raise SystemExit(1)

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.md',
            prefix=f'{repo}_README_',
            delete=False
        )
        temp_file.write(result.stdout)
        temp_file.close()

        console.print(f"[green]✓[/green] README saved to {temp_file.name}")
        return temp_file.name
