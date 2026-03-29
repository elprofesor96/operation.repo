"""
Server operations for op repo - push, clone, list, view, pushes, diff via opsserver SSH.

Uses paramiko for native SSH transport. No subprocess, no SCP, no shell commands.
"""

import hashlib
import json
import os
import re
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

import paramiko
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()
_quiet_console = Console(quiet=True)

_ORG_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")


def _validate_org_name(name: str) -> None:
    """Validate an organization name. Raises SystemExit on invalid input."""
    if len(name) < 2 or len(name) > 100 or not _ORG_NAME_RE.match(name):
        console.print("[red]x[/red] Invalid org name (lowercase alphanumeric + hyphens, 2-100 chars)")
        raise SystemExit(1)


class UnknownHostKeyError(Exception):
    """Raised when the server host key is not in known_hosts."""
    pass


class SSHConnection:
    """Manages a paramiko SSH connection to opsserver."""

    def __init__(self, host: str, key_path: str, port: int = 2222) -> None:
        self.host = host
        self.port = port
        self.key_path = key_path
        self._client: paramiko.SSHClient | None = None

    def connect(self) -> paramiko.SSHClient:
        """Establish SSH connection using public key auth.

        Raises UnknownHostKeyError if the host key is not trusted.
        """
        if self._client is not None:
            return self._client

        key_file = Path(self.key_path).expanduser()
        if not key_file.exists():
            console.print(f"[red]x[/red] SSH key not found: {key_file}")
            raise SystemExit(1)

        client = paramiko.SSHClient()

        # Load known hosts from ~/.op/known_hosts (opsserver-specific)
        # Falls back to system known_hosts, rejects unknown hosts
        known_hosts = Path.home() / ".op" / "known_hosts"
        if known_hosts.exists():
            client.load_host_keys(str(known_hosts))
        system_known_hosts = Path.home() / ".ssh" / "known_hosts"
        if system_known_hosts.exists():
            client.load_system_host_keys(str(system_known_hosts))
        client.set_missing_host_key_policy(paramiko.RejectPolicy())

        try:
            pkey = self._load_key(str(key_file))
            client.connect(
                hostname=self.host,
                port=self.port,
                pkey=pkey,
                look_for_keys=False,
                allow_agent=False,
                timeout=10,
            )
        except paramiko.AuthenticationException:
            console.print("[red]x[/red] Authentication failed. Check your SSH key.")
            raise SystemExit(1) from None
        except paramiko.SSHException as e:
            if "not found in known_hosts" in str(e) or "Unknown server" in str(e):
                raise UnknownHostKeyError(self.host, self.port) from None
            console.print(f"[red]x[/red] Connection failed: {e}")
            raise SystemExit(1) from None
        except OSError as e:
            console.print(f"[red]x[/red] Connection failed: {e}")
            raise SystemExit(1) from None

        self._client = client
        return client

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def exec_command(self, command: str) -> tuple[int, bytes, bytes]:
        """Execute a command over SSH exec channel. Returns (exit_code, stdout, stderr)."""
        client = self.connect()
        transport = client.get_transport()
        if transport is None:
            raise RuntimeError("SSH transport not available")

        channel = transport.open_session()
        channel.exec_command(command)

        # Read all stdout and stderr
        stdout_chunks = []
        stderr_chunks = []

        while True:
            if channel.recv_ready():
                stdout_chunks.append(channel.recv(65536))
            if channel.recv_stderr_ready():
                stderr_chunks.append(channel.recv_stderr(65536))
            if channel.exit_status_ready():
                # Drain remaining data
                while channel.recv_ready():
                    stdout_chunks.append(channel.recv(65536))
                while channel.recv_stderr_ready():
                    stderr_chunks.append(channel.recv_stderr(65536))
                break

        exit_code = channel.recv_exit_status()
        channel.close()

        return exit_code, b"".join(stdout_chunks), b"".join(stderr_chunks)

    def exec_push(self, command: str, header: dict, archive_path: str, progress_console: Console | None = None) -> tuple[int, bytes, bytes]:
        """Execute a push command: send JSON header line + raw archive bytes on stdin."""
        client = self.connect()
        transport = client.get_transport()
        if transport is None:
            raise RuntimeError("SSH transport not available")

        channel = transport.open_session()
        channel.exec_command(command)

        # Send header as JSON line
        header_line = json.dumps(header) + "\n"
        channel.sendall(header_line.encode())

        # Stream archive file to stdin
        file_size = os.path.getsize(archive_path)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=progress_console or console,
        ) as progress:
            task = progress.add_task("Uploading...", total=file_size)

            with open(archive_path, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    channel.sendall(chunk)
                    progress.advance(task, len(chunk))

        channel.shutdown_write()

        # Read response
        stdout_chunks = []
        stderr_chunks = []

        while True:
            if channel.recv_ready():
                stdout_chunks.append(channel.recv(65536))
            if channel.recv_stderr_ready():
                stderr_chunks.append(channel.recv_stderr(65536))
            if channel.exit_status_ready():
                while channel.recv_ready():
                    stdout_chunks.append(channel.recv(65536))
                while channel.recv_stderr_ready():
                    stderr_chunks.append(channel.recv_stderr(65536))
                break

        exit_code = channel.recv_exit_status()
        channel.close()

        return exit_code, b"".join(stdout_chunks), b"".join(stderr_chunks)

    def exec_clone(self, command: str, dest_path: str) -> tuple[int, bytes]:
        """Execute a clone command: stream stdout (tar.gz) directly to a file."""
        client = self.connect()
        transport = client.get_transport()
        if transport is None:
            raise RuntimeError("SSH transport not available")

        channel = transport.open_session()
        channel.exec_command(command)

        stderr_chunks = []
        total_bytes = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("{task.fields[size]}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading...", size="0 B")

            with open(dest_path, "wb") as f:
                while True:
                    if channel.recv_ready():
                        chunk = channel.recv(65536)
                        if chunk:
                            f.write(chunk)
                            total_bytes += len(chunk)
                            progress.update(task, size=_format_size(total_bytes))
                    if channel.recv_stderr_ready():
                        stderr_chunks.append(channel.recv_stderr(65536))
                    if channel.exit_status_ready() and not channel.recv_ready():
                        # Final drain
                        while channel.recv_ready():
                            chunk = channel.recv(65536)
                            if chunk:
                                f.write(chunk)
                                total_bytes += len(chunk)
                        while channel.recv_stderr_ready():
                            stderr_chunks.append(channel.recv_stderr(65536))
                        break

        exit_code = channel.recv_exit_status()
        channel.close()

        return exit_code, b"".join(stderr_chunks)

    @staticmethod
    def _load_key(key_path: str) -> paramiko.PKey:
        """Load an SSH private key, trying all key types."""
        for key_class in (paramiko.Ed25519Key, paramiko.RSAKey, paramiko.ECDSAKey):
            try:
                return key_class.from_private_key_file(key_path)
            except (paramiko.SSHException, ValueError):
                continue
        raise paramiko.SSHException(f"Cannot load key: {key_path}")


class OpClassToServer:
    """Handles communication with opsserver over SSH."""

    def __init__(self) -> None:
        pass

    def _get_connection(self, host: str, key: str, port: int = 2222) -> SSHConnection:
        return SSHConnection(host=host, key_path=key, port=port)

    def _connect_or_fail(self, host: str, key: str, port: int = 2222) -> SSHConnection:
        """Connect, printing a helpful message if host key is unknown."""
        conn = self._get_connection(host, key, port)
        try:
            conn.connect()
        except UnknownHostKeyError:
            console.print(f"[red]x[/red] Unknown host key for {host}:{port}")
            console.print("    Run: [cyan]op server verify[/cyan]")
            raise SystemExit(1) from None
        return conn

    def verify_connection(self, host: str, key: str, port: int = 2222) -> bool:
        """Test SSH auth — handles host key trust on first connect."""
        known_hosts_path = Path.home() / ".op" / "known_hosts"

        # First, check if we already trust this host
        conn = self._get_connection(host, key, port)
        try:
            client = conn.connect()
        except UnknownHostKeyError:
            # Host key unknown — offer to trust it
            conn.close()
            if not self._trust_host_key(host, port, known_hosts_path):
                return False
            # Retry with the now-trusted key
            conn = self._get_connection(host, key, port)
            try:
                client = conn.connect()
            except (paramiko.SSHException, OSError, UnknownHostKeyError) as e:
                console.print(f"[red]x[/red] Connection failed: {e}")
                return False

        try:
            transport = client.get_transport()
            if transport is None:
                return False

            channel = transport.open_session()
            channel.invoke_shell()

            output = b""
            while True:
                if channel.recv_ready():
                    output += channel.recv(4096)
                if channel.exit_status_ready():
                    while channel.recv_ready():
                        output += channel.recv(4096)
                    break

            channel.close()
            msg = output.decode(errors="replace").strip()
            if msg:
                console.print(f"[green]{msg}[/green]")
            return True
        except (paramiko.SSHException, OSError) as e:
            console.print(f"[red]x[/red] Connection failed: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def _trust_host_key(host: str, port: int, known_hosts_path: Path) -> bool:
        """Fetch server host key, show fingerprint, ask user to trust it."""
        console.print(f"\n[yellow]Unknown host key for {host}:{port}[/yellow]\n")

        # Fetch the host key via a raw socket + transport
        try:
            import socket
            sock = socket.create_connection((host, port), timeout=10)
            transport = paramiko.Transport(sock)
            transport.connect()
            host_key = transport.get_remote_server_key()
            transport.close()
            sock.close()
        except (OSError, paramiko.SSHException) as e:
            console.print(f"[red]x[/red] Could not fetch host key: {e}")
            return False

        key_type = host_key.get_name()
        fingerprint = _key_fingerprint(host_key)

        console.print(f"  Host:        {host}:{port}")
        console.print(f"  Key type:    {key_type}")
        console.print(f"  Fingerprint: {fingerprint}")
        console.print()

        import typer
        if not typer.confirm("Trust this host key?"):
            console.print("[red]x[/red] Host key rejected")
            return False

        # Save to ~/.op/known_hosts
        known_hosts_path.parent.mkdir(parents=True, exist_ok=True)

        # Format: [host]:port key_type base64_key
        host_entry = f"[{host}]:{port}" if port != 22 else host
        key_b64 = host_key.get_base64()
        line = f"{host_entry} {key_type} {key_b64}\n"

        with open(known_hosts_path, "a") as f:
            f.write(line)

        console.print(f"[green]ok[/green] Host key saved to {known_hosts_path}")
        return True

    def push_repo(self, host: str, key: str, port: int = 2222, org: str | None = None) -> bool:
        """Push the current repo to opsserver via SSH."""
        pwd = Path.cwd()
        repo_name = pwd.name

        # Check this is an op repo first
        if not (pwd / ".opignore").exists():
            console.print("[red]x[/red] Not an op repo (run 'op init' first)")
            return False

        if org:
            _validate_org_name(org)
            target = f"{org}/{repo_name}"
        else:
            target = repo_name

        # Export to tar.gz in a temp file
        with console.status(f"[bold]Pushing '{target}' to {host}:{port}...[/bold]"):
            archive_path = self._create_archive(pwd)
        if archive_path is None:
            return False

        try:
            # Compute checksum and size
            file_size = os.path.getsize(archive_path)
            checksum = self._compute_checksum(archive_path)

            # First push from this project if no snapshot exists yet
            is_first_push = not (pwd / ".op" / "push-snapshot.json").exists()

            # Build push header
            header: dict = {
                "size": file_size,
                "checksum": f"sha256:{checksum}",
                "message": "",
            }
            if is_first_push:
                header["expect_new"] = True

            conn = self._connect_or_fail(host, key, port)
            try:
                exit_code, stdout, stderr = conn.exec_push(
                    command=f"push {target}",
                    header=header,
                    archive_path=archive_path,
                    progress_console=_quiet_console,
                )
            finally:
                conn.close()

            if exit_code != 0:
                self._print_error(stderr)
                return False

            # Parse and display result
            result = json.loads(stdout)
            display = f"{org}/{result['repo']}" if org else result['repo']
            console.print(f"\n[bold green]Pushed '{display}' v{result['version']}[/bold green]")
            console.print(f"  Size: {_format_size(result['size'])} | Files: {result['files']}")
            console.print(f"  Checksum: {result.get('checksum', 'n/a')}")

            try:
                self._save_push_snapshot(result["version"])
            except (OSError, KeyError):
                console.print("[yellow]![/yellow] Could not save push snapshot")

            return True

        finally:
            # Clean up temp archive
            os.unlink(archive_path)

    def push_repo_with_message(self, host: str, key: str, message: str, port: int = 2222, org: str | None = None) -> bool:
        """Push with a commit message."""
        pwd = Path.cwd()
        repo_name = pwd.name

        # Check this is an op repo first
        if not (pwd / ".opignore").exists():
            console.print("[red]x[/red] Not an op repo (run 'op init' first)")
            return False

        if org:
            _validate_org_name(org)
            target = f"{org}/{repo_name}"
        else:
            target = repo_name

        # Export to tar.gz in a temp file
        with console.status(f"[bold]Pushing '{target}' to {host}:{port}...[/bold]"):
            archive_path = self._create_archive(pwd)
        if archive_path is None:
            return False

        try:
            file_size = os.path.getsize(archive_path)
            checksum = self._compute_checksum(archive_path)

            is_first_push = not (pwd / ".op" / "push-snapshot.json").exists()

            header: dict = {
                "size": file_size,
                "checksum": f"sha256:{checksum}",
                "message": message,
            }
            if is_first_push:
                header["expect_new"] = True

            conn = self._connect_or_fail(host, key, port)
            try:
                exit_code, stdout, stderr = conn.exec_push(
                    command=f"push {target}",
                    header=header,
                    archive_path=archive_path,
                    progress_console=_quiet_console,
                )
            finally:
                conn.close()

            if exit_code != 0:
                self._print_error(stderr)
                return False

            result = json.loads(stdout)
            display = f"{org}/{result['repo']}" if org else result['repo']
            console.print(f"\n[bold green]Pushed '{display}' v{result['version']}[/bold green]")
            console.print(f"  Size: {_format_size(result['size'])} | Files: {result['files']}")
            console.print(f"  Checksum: {result.get('checksum', 'n/a')}")

            try:
                self._save_push_snapshot(result["version"])
            except (OSError, KeyError):
                console.print("[yellow]![/yellow] Could not save push snapshot")

            return True

        finally:
            os.unlink(archive_path)

    def clone_repo(self, host: str, key: str, repo: str, version: str | None = None, port: int = 2222) -> bool:
        """Clone a repo from opsserver via SSH."""
        console.print(f"\n[bold]Cloning '{repo}' from {host}:{port}...[/bold]\n")

        # For org repos (orgname/reponame), use just the repo name as local dir
        local_name = repo.split("/")[-1] if "/" in repo else repo
        local_path = Path.cwd() / local_name
        if local_path.exists():
            console.print(f"[red]x[/red] Directory '{local_name}' already exists")
            return False

        # Build clone command
        cmd = f"clone {repo}"
        if version is not None:
            cmd += f" {version}"

        # Stream tar.gz to temp file, then extract
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".tar.gz", prefix="op-clone-")
        os.close(tmp_fd)

        conn = self._connect_or_fail(host, key, port)
        try:
            exit_code, stderr = conn.exec_clone(command=cmd, dest_path=tmp_path)
        finally:
            conn.close()

        if exit_code != 0:
            os.unlink(tmp_path)
            self._print_error(stderr)
            return False

        # Extract tar.gz to local directory
        try:
            local_path.mkdir(parents=True, exist_ok=True)
            with tarfile.open(tmp_path, "r:gz") as tf:
                # Security: validate all members before extracting
                for member in tf.getmembers():
                    member_path = os.path.normpath(member.name)
                    if member_path.startswith("..") or os.path.isabs(member_path):
                        console.print(f"[red]x[/red] Unsafe path in archive: {member.name}")
                        return False
                    if member.issym() or member.islnk():
                        console.print(f"[red]x[/red] Symlinks not allowed: {member.name}")
                        return False

                tf.extractall(path=local_path, filter="data")

            console.print(f"\n[bold green]Cloned '{repo}'[/bold green]")
            console.print(f"  Location: {local_path}")
            return True
        except (tarfile.TarError, OSError) as e:
            console.print(f"[red]x[/red] Failed to extract archive: {e}")
            return False
        finally:
            os.unlink(tmp_path)

    def list_repos(self, host: str, key: str, port: int = 2222, org: str | None = None) -> list[dict]:
        """List all repos on opsserver (or in an organization)."""
        if org:
            _validate_org_name(org)
            console.print(f"\n[bold]Listing repos for org '{org}' from {host}:{port}...[/bold]\n")
            cmd = f"list {org}"
        else:
            console.print(f"\n[bold]Listing repos from {host}:{port}...[/bold]\n")
            cmd = "list"

        conn = self._connect_or_fail(host, key, port)
        try:
            exit_code, stdout, stderr = conn.exec_command(cmd)
        finally:
            conn.close()

        if exit_code != 0:
            self._print_error(stderr)
            return []

        repos = json.loads(stdout)

        if not repos:
            label = f"in org '{org}'" if org else "on server"
            console.print(f"[yellow]No repos found {label}[/yellow]")
            return []

        title = f"Repositories in {org}" if org else "Repositories on opsserver"
        table = Table(title=title)
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Name", style="green")
        table.add_column("Description", style="dim")
        table.add_column("Pushes", style="yellow", justify="right")
        table.add_column("Last Push", style="dim")
        table.add_column("Size", style="dim", justify="right")

        for i, repo in enumerate(repos, 1):
            table.add_row(
                str(i),
                repo["name"],
                repo.get("description") or "",
                str(repo.get("pushes", 0)),
                repo.get("last_push", ""),
                _format_size(repo.get("size", 0)),
            )

        console.print(table)
        return repos

    def view_repo(self, host: str, key: str, repo: str, port: int = 2222) -> dict | None:
        """View repo metadata and README from opsserver."""
        console.print(f"\n[bold]Viewing '{repo}' on {host}:{port}...[/bold]\n")

        conn = self._connect_or_fail(host, key, port)
        try:
            exit_code, stdout, stderr = conn.exec_command(f"view {repo}")
        finally:
            conn.close()

        if exit_code != 0:
            self._print_error(stderr)
            return None

        data = json.loads(stdout)

        console.print(f"[bold]{data['name']}[/bold]")
        if data.get("description"):
            console.print(f"  {data['description']}")
        console.print(f"  Pushes: {data.get('pushes', 0)}")

        readme = data.get("readme", "")
        if readme:
            console.print("\n[bold]README:[/bold]")
            console.print(readme)

        return data

    def list_pushes(self, host: str, key: str, repo: str, port: int = 2222) -> list[dict]:
        """List all push versions for a repo."""
        conn = self._connect_or_fail(host, key, port)
        try:
            exit_code, stdout, stderr = conn.exec_command(f"pushes {repo}")
        finally:
            conn.close()

        if exit_code != 0:
            self._print_error(stderr)
            return []

        pushes = json.loads(stdout)

        if not pushes:
            console.print(f"[yellow]No pushes found for '{repo}'[/yellow]")
            return []

        table = Table(title=f"Push history: {repo}")
        table.add_column("Version", style="cyan", justify="right")
        table.add_column("Message", style="white")
        table.add_column("Files", style="yellow", justify="right")
        table.add_column("Size", style="dim", justify="right")
        table.add_column("Date", style="dim")

        for p in pushes:
            table.add_row(
                f"v{p['version']}",
                p.get("message", ""),
                str(p.get("files", 0)),
                _format_size(p.get("size", 0)),
                p.get("created_at", ""),
            )

        console.print(table)
        return pushes

    def diff_versions(self, host: str, key: str, repo: str, from_ver: int, to_ver: int, port: int = 2222) -> dict | None:
        """Diff two push versions."""
        conn = self._connect_or_fail(host, key, port)
        try:
            exit_code, stdout, stderr = conn.exec_command(f"diff {repo} {from_ver} {to_ver}")
        finally:
            conn.close()

        if exit_code != 0:
            self._print_error(stderr)
            return None

        data = json.loads(stdout)

        if data.get("added"):
            console.print(f"\n[green]+ Added ({len(data['added'])}):[/green]")
            for f in data["added"]:
                console.print(f"  [green]+ {f}[/green]")

        if data.get("removed"):
            console.print(f"\n[red]- Removed ({len(data['removed'])}):[/red]")
            for f in data["removed"]:
                console.print(f"  [red]- {f}[/red]")

        if data.get("modified"):
            console.print(f"\n[yellow]~ Modified ({len(data['modified'])}):[/yellow]")
            for f in data["modified"]:
                console.print(f"  [yellow]~ {f}[/yellow]")

        console.print(f"\n  Unchanged: {data.get('unchanged', 0)}")
        return data

    def _create_archive(self, repo_path: Path) -> str | None:
        """Create a tar.gz archive of the repo (respects .opignore)."""
        from operation_repo.core import OpClass

        op = OpClass()
        files = op._get_tracked_files()

        if not files:
            console.print("[yellow]![/yellow] No files to push")
            return None

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".tar.gz", prefix="op-push-")
        os.close(tmp_fd)

        try:
            with tarfile.open(tmp_path, "w:gz") as tf:
                for file_path in files:
                    relative = file_path.relative_to(repo_path)
                    tf.add(str(file_path), arcname=str(relative))

            return tmp_path
        except (tarfile.TarError, OSError) as e:
            console.print(f"[red]x[/red] Failed to create archive: {e}")
            os.unlink(tmp_path)
            return None

    @staticmethod
    def _compute_checksum(file_path: str) -> str:
        """Compute SHA-256 checksum of a file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _save_push_snapshot(version: int) -> None:
        """Save a snapshot of tracked files after a successful push."""
        from operation_repo.commits import CommitManager

        cm = CommitManager()
        snapshot = cm._get_file_snapshot()

        push_data = {
            "timestamp": datetime.now().isoformat(),
            "version": version,
            "snapshot": snapshot,
        }

        push_snapshot_path = Path.cwd() / ".op" / "push-snapshot.json"
        with open(push_snapshot_path, "w") as f:
            json.dump(push_data, f, indent=2)

    @staticmethod
    def _print_error(stderr: bytes) -> None:
        """Parse and print a server error response."""
        try:
            err = json.loads(stderr)
            console.print(f"[red]x[/red] {err.get('error', 'Unknown error')}")
        except (json.JSONDecodeError, ValueError):
            msg = stderr.decode(errors="replace").strip()
            if msg:
                console.print(f"[red]x[/red] {msg}")
            else:
                console.print("[red]x[/red] Server error")


def _format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def _key_fingerprint(key: paramiko.PKey) -> str:
    """Compute SHA-256 fingerprint of a host key."""
    import base64
    digest = hashlib.sha256(key.asbytes()).digest()
    b64 = base64.b64encode(digest).decode().rstrip("=")
    return f"SHA256:{b64}"
