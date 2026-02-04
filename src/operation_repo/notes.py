"""
Notes system for op repo - Quick note-taking during operations.

Handles: notes add, notes list, notes search, notes delete
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


class NotesManager:
    """Handles quick note-taking for op repo."""

    def __init__(self) -> None:
        self.pwd = Path.cwd()
        self.op_dir = self.pwd / ".op"
        self.notes_file = self.op_dir / "notes.json"

    def _is_op_repo(self) -> bool:
        """Check if current directory is an op repo."""
        return (self.pwd / ".opignore").exists()

    def _load_notes(self) -> list[dict]:
        """Load notes from file."""
        if not self.notes_file.exists():
            return []
        with open(self.notes_file, "r") as f:
            return json.load(f)

    def _save_notes(self, notes: list[dict]) -> None:
        """Save notes to file."""
        self.op_dir.mkdir(parents=True, exist_ok=True)
        with open(self.notes_file, "w") as f:
            json.dump(notes, f, indent=2)

    def _generate_note_id(self, notes: list[dict]) -> int:
        """Generate the next note ID."""
        if not notes:
            return 1
        return max(n["id"] for n in notes) + 1

    def add(
        self,
        content: str,
        tag: Optional[str] = None,
        priority: str = "normal"
    ) -> int:
        """Add a new note."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            raise SystemExit(1)

        notes = self._load_notes()
        note_id = self._generate_note_id(notes)

        note = {
            "id": note_id,
            "content": content,
            "tag": tag,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "done": False
        }

        notes.append(note)
        self._save_notes(notes)

        priority_colors = {
            "high": "red",
            "normal": "white",
            "low": "dim"
        }
        color = priority_colors.get(priority, "white")

        console.print(f"[green]✓[/green] Note #{note_id} added")
        if tag:
            console.print(f"  [cyan]Tag:[/cyan] {tag}")

        return note_id

    def list_notes(
        self,
        tag: Optional[str] = None,
        show_done: bool = False,
        limit: int = 20
    ) -> None:
        """List all notes."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return

        notes = self._load_notes()

        if not notes:
            console.print("[yellow]No notes yet[/yellow]")
            console.print("  Use: op notes add \"your note\"")
            return

        # Filter by tag
        if tag:
            notes = [n for n in notes if n.get("tag") == tag]

        # Filter done/undone
        if not show_done:
            notes = [n for n in notes if not n.get("done", False)]

        # Sort by timestamp (newest first)
        notes.sort(key=lambda n: n["timestamp"], reverse=True)

        if not notes:
            console.print("[yellow]No matching notes[/yellow]")
            return

        # Create table
        table = Table(title="Notes", box=None)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Note", style="white")
        table.add_column("Tag", style="green", width=12)
        table.add_column("Priority", width=8)
        table.add_column("Time", style="dim", width=16)

        priority_styles = {
            "high": "[bold red]high[/bold red]",
            "normal": "normal",
            "low": "[dim]low[/dim]"
        }

        for note in notes[:limit]:
            ts = datetime.fromisoformat(note["timestamp"])
            time_str = ts.strftime("%m-%d %H:%M")

            done_marker = "[dim]✓[/dim] " if note.get("done") else ""
            content = done_marker + note["content"]

            # Truncate long content
            if len(content) > 50:
                content = content[:47] + "..."

            table.add_row(
                str(note["id"]),
                content,
                note.get("tag") or "-",
                priority_styles.get(note.get("priority", "normal"), "normal"),
                time_str
            )

        console.print(table)

        if len(notes) > limit:
            console.print(f"\n[dim]Showing {limit} of {len(notes)} notes[/dim]")

        # Show available tags
        all_notes = self._load_notes()
        tags = set(n.get("tag") for n in all_notes if n.get("tag"))
        if tags:
            console.print(f"\n[dim]Tags: {', '.join(sorted(tags))}[/dim]")

    def search(self, query: str) -> None:
        """Search notes by content."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return

        notes = self._load_notes()
        query_lower = query.lower()

        matches = [
            n for n in notes
            if query_lower in n["content"].lower()
            or (n.get("tag") and query_lower in n["tag"].lower())
        ]

        if not matches:
            console.print(f"[yellow]No notes matching '{query}'[/yellow]")
            return

        console.print(f"[bold]Found {len(matches)} matching notes:[/bold]\n")

        for note in matches:
            ts = datetime.fromisoformat(note["timestamp"])
            time_str = ts.strftime("%Y-%m-%d %H:%M")
            tag_str = f" [cyan][{note['tag']}][/cyan]" if note.get("tag") else ""

            console.print(f"[bold]#{note['id']}[/bold]{tag_str} - {time_str}")
            console.print(f"  {note['content']}\n")

    def delete(self, note_id: int) -> bool:
        """Delete a note by ID."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return False

        notes = self._load_notes()

        # Find note
        note_idx = None
        for i, n in enumerate(notes):
            if n["id"] == note_id:
                note_idx = i
                break

        if note_idx is None:
            console.print(f"[red]✗[/red] Note #{note_id} not found")
            return False

        deleted = notes.pop(note_idx)
        self._save_notes(notes)

        console.print(f"[green]✓[/green] Deleted note #{note_id}")
        console.print(f"  [dim]{deleted['content'][:50]}...[/dim]" if len(deleted['content']) > 50 else f"  [dim]{deleted['content']}[/dim]")

        return True

    def done(self, note_id: int) -> bool:
        """Mark a note as done."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return False

        notes = self._load_notes()

        for note in notes:
            if note["id"] == note_id:
                note["done"] = True
                self._save_notes(notes)
                console.print(f"[green]✓[/green] Note #{note_id} marked as done")
                return True

        console.print(f"[red]✗[/red] Note #{note_id} not found")
        return False

    def undone(self, note_id: int) -> bool:
        """Mark a note as not done."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return False

        notes = self._load_notes()

        for note in notes:
            if note["id"] == note_id:
                note["done"] = False
                self._save_notes(notes)
                console.print(f"[green]✓[/green] Note #{note_id} marked as not done")
                return True

        console.print(f"[red]✗[/red] Note #{note_id} not found")
        return False

    def clear(self, force: bool = False) -> bool:
        """Clear all notes."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            return False

        notes = self._load_notes()

        if not notes:
            console.print("[yellow]No notes to clear[/yellow]")
            return True

        if not force:
            import typer
            confirm = typer.confirm(f"Delete all {len(notes)} notes?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                return False

        self._save_notes([])
        console.print(f"[green]✓[/green] Cleared {len(notes)} notes")
        return True

    def export_markdown(self, output_path: Optional[str] = None) -> str:
        """Export notes to markdown file."""
        if not self._is_op_repo():
            console.print("[red]✗[/red] Not an op repo (run 'op init' first)")
            raise SystemExit(1)

        notes = self._load_notes()

        if not notes:
            console.print("[yellow]No notes to export[/yellow]")
            raise SystemExit(1)

        # Generate markdown
        lines = ["# Operation Notes\n"]

        # Group by tag
        by_tag: dict[str, list] = {"untagged": []}
        for note in notes:
            tag = note.get("tag") or "untagged"
            if tag not in by_tag:
                by_tag[tag] = []
            by_tag[tag].append(note)

        for tag, tag_notes in sorted(by_tag.items()):
            if tag != "untagged":
                lines.append(f"\n## {tag.title()}\n")
            elif by_tag.get("untagged"):
                lines.append("\n## General Notes\n")

            for note in sorted(tag_notes, key=lambda n: n["timestamp"]):
                ts = datetime.fromisoformat(note["timestamp"])
                time_str = ts.strftime("%Y-%m-%d %H:%M")
                done = "~~" if note.get("done") else ""
                done_end = "~~" if note.get("done") else ""
                priority_marker = "🔴 " if note.get("priority") == "high" else ""

                lines.append(f"- {priority_marker}{done}{note['content']}{done_end} *({time_str})*")

        # Write to file
        if output_path:
            out_file = Path(output_path)
        else:
            out_file = self.pwd / "NOTES.md"

        out_file.write_text("\n".join(lines))
        console.print(f"[green]✓[/green] Notes exported to {out_file}")

        return str(out_file)
