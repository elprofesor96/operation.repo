# Operation Repo 🎯

A Git-like CLI tool for organizing operations. Perfect for pentesters, HTB players, and developers who want to stay organized.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 📁 **Initialize** operation repos with custom templates
- 🔖 **Commit** snapshots of your work with messages
- 📦 **Export** to zip, tar.gz with optional encryption
- 📝 **Notes** quick note-taking during operations
- 📊 **Status** see repo state and uncommitted changes
- 🚀 **Push/Clone** to your own ops server
- 🎨 **Beautiful CLI** with Rich formatting

## Installation

### From GitHub

```bash
pip install git+https://github.com/elprofesor96/operation.repo
```

### From source

```bash
git clone https://github.com/elprofesor96/operation.repo
cd operation.repo
pip install .
```

## Quick Start

```bash
# Initialize a new op repo
op init

# Make some changes, then commit
op commit -m "initial recon complete"

# Check status
op status

# Export your work
op export

# View commit history
op log
```

## Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `op init` | Initialize a new op repo |
| `op init -c web` | Initialize with custom template |
| `op status` | Show repo status with change detection |
| `op remove` | Remove files (respects .opignore) |

### Commit System

| Command | Description |
|---------|-------------|
| `op commit -m "message"` | Create a snapshot of current state |
| `op log` | Show commit history |
| `op log -n 20` | Show last 20 commits |
| `op diff` | Show changes since last commit |
| `op diff abc123` | Compare with specific commit |
| `op show abc123` | Show commit details |
| `op checkout abc123` | Restore to a specific commit |

### Export

| Command | Description |
|---------|-------------|
| `op export` | Export to zip (default) |
| `op export -f tar.gz` | Export to tar.gz |
| `op export -e` | Export with GPG encryption |
| `op export -o backup.zip` | Export to custom path |

### Notes

| Command | Description |
|---------|-------------|
| `op notes add "found SQLi"` | Add a quick note |
| `op notes add "critical" -t vuln -p high` | Add with tag and priority |
| `op notes list` | List all notes |
| `op notes list -t vuln` | Filter by tag |
| `op notes search "SQL"` | Search notes |
| `op notes done 3` | Mark note #3 as done |
| `op notes delete 3` | Delete note #3 |
| `op notes export` | Export to NOTES.md |
| `op notes clear` | Clear all notes |

### Templates

| Command | Description |
|---------|-------------|
| `op template list` | List available templates |
| `op template show web` | Show template details |
| `op template create` | Create template interactively |
| `op template delete web` | Delete a template |

### Remote & Org

| Command | Description |
|---------|-------------|
| `op remote` | Show remote and org config |
| `op remote add -s <host> -k <key>` | Add or update remote server |
| `op remote remove` | Reset remote server config |
| `op remote set-org <org>` | Set default org for this repo |
| `op remote remove-org` | Remove org (pushes go to private) |

### Server

| Command | Description |
|---------|-------------|
| `op push` | Push repo to opsserver (uses saved org) |
| `op push --org <org>` | Push to org and save it as default |
| `op clone <repo>` | Clone repo from opsserver |
| `op server list` | List repos on opsserver |
| `op server view <repo>` | View README from opsserver |

## Configuration

Configuration is stored in `~/.op/op.conf`:

```ini
[SERVER]
host = 192.168.1.100
ssh_key = ~/.ssh/ops_key

[FOLDER]
# Folders to create on 'op init'
notes = on
scans = on
exploits = on
loot = on

[FILE]
# Files to create on 'op init'
todo.txt = on
credentials.txt = on

[SCRIPTS]
# scripts from ~/.op/opscripts/
linpeas.sh = on
```

### Custom Templates

Create custom templates for different operation types:

```ini
[WEB_FOLDER]
recon = on
burp = on
screenshots = on

[WEB_FILE]
urls.txt = on
params.txt = on

[WEB_SCRIPTS]
dirbuster-list.txt = on
```

Then use: `op init -c web`

Or create interactively: `op template create`

## .opignore

Files and folders in `.opignore` are:
- **Excluded** from exports and commits
- **Preserved** during `op remove`

Example `.opignore`:
```
.op
*.zip
secrets/
.env
```

## Repo Structure

After `op init`, your repo looks like:

```
my-operation/
├── .op/
│   ├── commits/       # Commit snapshots
│   ├── exports/       # Exported archives
│   ├── config         # Repo-level config (org, etc.)
│   ├── notes.json     # Your notes
│   └── HEAD           # Current commit pointer
├── .opignore
├── README.md
└── opscripts/
```

## Workflow Example

```bash
# Start a new pentest
mkdir acme-corp && cd acme-corp
op init -c pentest

# Take notes as you go
op notes add "target: 10.10.10.1" -t recon
op notes add "found open port 8080" -t recon
op notes add "possible SQLi on /login" -t vuln -p high

# Commit your progress
op commit -m "initial recon complete"

# Continue working...
op commit -m "exploited SQLi, got user shell"

# Check what changed
op diff

# View history
op log

# Export for report
op export -f zip

# Push to your server (private)
op push

# Or set an org and push there
op remote set-org acme
op push                  # goes to acme automatically
```

## Development

```bash
# Clone and install in dev mode
git clone https://github.com/elprofesor96/operation.repo
cd operation.repo
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/operation_repo/
```

## Project Structure

```
operation.repo/
├── src/
│   └── operation_repo/
│       ├── __init__.py
│       ├── cli.py          # Typer CLI entry point
│       ├── core.py         # Init, export, remove, status
│       ├── config.py       # Config handling
│       ├── server.py       # Server operations
│       ├── commits.py      # Commit system
│       ├── notes.py        # Notes system
│       └── templates.py    # Template management
├── tests/
├── pyproject.toml
└── README.md
```

## Credits

- Author: [elprofesor96](https://github.com/elprofesor96)
- Website: [elprofesor.io](https://elprofesor.io)

## License

[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) -  [LICENSE.md](LICENSE.md)

Free to use for any purpose — personal, work, research, bug bounty, whatever.  

Just credit me if reference in blog posts and articles. 

Don't sell the tool itself, and don't redistribute modified versions.

## Support

If you find this tool useful and want to support its development and my work:

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Buy%20me%20a%20coffee-ff5f5f?logo=ko-fi&logoColor=white)](https://ko-fi.com/elprofesor96)

