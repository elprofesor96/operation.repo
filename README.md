# Operation Repo 🎯

A Git-like CLI tool for organizing operations. Perfect for pentesters, HTB players, and developers who want to stay organized.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- 📁 **Initialize** operation repos with custom templates
- 💾 **Backup** your work to timestamped zip files
- 🧹 **Remove** files while respecting `.opignore`
- 📊 **Status** check your repo at a glance
- 🚀 **Push/Clone** to your own ops server
- 🎨 **Beautiful CLI** with Rich formatting

## Installation

### From PyPI (recommended)

```bash
pip install operation-repo
```

### From GitHub

```bash
pip install git+https://github.com/elprofesor96/operation.repo
```

### From source

```bash
git clone https://github.com/elprofesor96/operation.repo
cd operation.repo
pip install -e .
```

## Quick Start

```bash
# Initialize a new op repo
op init

# Check status
op status

# Backup your work
op backup

# Clean up (respects .opignore)
op remove
```

## Commands

| Command | Description |
|---------|-------------|
| `op init` | Initialize a new op repo |
| `op init -c web` | Initialize with custom template |
| `op status` | Show repo status |
| `op backup` | Create timestamped backup zip |
| `op remove` | Remove files (respects .opignore) |
| `op list` | List repos on opsserver |
| `op push` | Push repo to opsserver |
| `op clone <repo>` | Clone repo from opsserver |
| `op view <repo>` | View README from opsserver |

## Configuration

Configuration is stored in `~/.op/op.conf`:

```ini
[SERVER]
opsserver_ip = 192.168.1.100
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

[DB]
# Scripts to copy from ~/.op/opsdb/
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

[WEB_DEPLOYABLE]
dirbuster-list.txt = on
```

Then use: `op init -c web`

## .opignore

Files and folders in `.opignore` are:
- **Excluded** from backups
- **Preserved** during `op remove`

Example `.opignore`:
```
.op
*.zip
secrets/
.env
```

## Ops Server Setup

To use `push`, `clone`, and `list` commands, set up an ops server:

1. Configure SSH access in `~/.op/op.conf`
2. Ensure your SSH key has access to the server
3. Use commands:
   ```bash
   op push          # Upload current repo
   op list          # See all repos
   op clone myrepo  # Download a repo
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
ruff check src/
```

## Project Structure

```
operation.repo/
├── src/
│   └── operation_repo/
│       ├── __init__.py
│       ├── cli.py          # CLI entry point
│       ├── core.py         # Core operations
│       ├── config.py       # Config handling
│       └── server.py       # Server operations
├── tests/
├── pyproject.toml
└── README.md
```

## Credits

- Author: [elprofesor96](https://github.com/elprofesor96)
- Website: [elprofesor.io](https://elprofesor.io)

## License

MIT License - see [LICENSE.md](LICENSE.md)
