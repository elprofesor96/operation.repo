# Changelog

All notable changes to this project will be documented in this file.

## [3.0.0] - 2026-02-05

### 🚀 Major Rewrite

Complete rewrite from legacy argparse to modern Typer CLI with Rich formatting.

### ✨ New Features

- **Commit System** - Git-like snapshots of your operation
  - `op commit -m "message"` - Create a snapshot
  - `op log` - View commit history
  - `op diff` - Show changes since last commit
  - `op show <id>` - Show commit details
  - `op restore <id>` - Restore to a previous commit
- **Notes System** - Quick note-taking during operations
  - `op notes add "note"` - Add a note with optional tags and priority
  - `op notes list` - List, filter, and search notes
  - `op notes done <id>` - Mark notes as done
  - `op notes export` - Export to NOTES.md
- **Template Management** - Create and manage custom templates
  - `op template list` - List available templates
  - `op template create` - Interactive template creation
  - `op template show` - View template details
  - `op template delete` - Remove a template
- **Remote Configuration** - Manage server settings from CLI
  - `op remote` - Show current remote config
  - `op remote add -h <host> -k <key>` - Add or update remote
  - `op remote remove` - Reset remote config
- **Export** - Replaced `op backup` with more powerful export
  - `op export` - Export to zip (default)
  - `op export -f tar.gz` - Export to tar.gz
  - `op export -e` - Encrypt with GPG
  - `op export -o <path>` - Custom output path
  - Exports now stored in `.op/exports/`

### 🔧 Improvements

- **Modern CLI** - Replaced argparse with Typer + Rich
  - Auto-generated help for all commands
  - Beautiful formatted output with colors and tables
  - Progress bars for exports
  - Confirmation prompts for destructive operations
- **Security** - Replaced `os.system()` with `subprocess.run()` (no shell injection)
- **Status** - Now shows commits, notes, exports, uncommitted changes
- **README template** - `op init` now creates a pre-filled README with sections
- **Error handling** - Specific exceptions instead of bare `except:`
- **Type hints** - Full type annotations across all modules
- **Modern packaging** - Migrated from setup.py to pyproject.toml

### 🏗️ Architecture

- `cli.py` - Typer CLI entry point
- `core.py` - Init, export, remove, status
- `commits.py` - Commit system
- `notes.py` - Notes system
- `templates.py` - Template management
- `config.py` - Configuration handling
- `server.py` - Server operations

### 🔄 CI/CD

- GitHub Actions CI with linter, tests across Python 3.9-3.12
- Dependabot for dependency updates
- Release workflow for automated GitHub Releases

### ⚠️ Breaking Changes

- `op backup` renamed to `op export`
- `op list` / `op view` moved to `op server list` / `op server view`
- Requires Python 3.9+
- New dependency: `typer[all]>=0.9.0`, `rich>=13.0.0`


## [v2.1.1] - 2024-05-05
- remove tqdm
- easy install with brew
- 

## [v2.1.0] - 2024-05-04
- working opsserver (alpha)

## [v2.0.1] - 2024-05-04
- security patch tqdm
- security patch blinker
- changes confighandler to read server config from op.conf


## [v2.0.0] - 2024-04-30
- pip3 install from github.com
- added on elprofesor96/repos homebrew tap to brew install it.
- fix vulnerabilities snyk
- fix vulnerabilities dependabot
- modify ConfigHandler.py to read sections by name instead of index for more control
- each user has .op folder with op.conf and db in home
- added CI scans snyk to defectdojo
- added CI scans semgrep to defectdojo
- added CI scans bandit to defectdojo
- added dependabot
- added codeql
- added ruleset and protect branches
- added CHANGELOG.md
- BIG CHANGE op.conf, deployable(db) now in user home folder, no longer in /etc, each user with own config.
- Changed name from audit.repo into operation.repo
- opsserver 2.0.0 (linux only .deb)
- op init
- op init -c [custom]
- op remove
- op backup
- op list
- op push
- op clone
- REFACTOR and rethink code, redesign for `OP` instead of `AUDIT`


## [v1.3.2] - 2022-11-07

- auditserver
- audit init
- audit init -c [custom]
- audit remove
- audit backup
- audit list
- audit push
- audit clone
- refactor logic to use .audit and .auditignore as defaults for using audit repo app
- Updated dependencies to the latest versions.
- resolved deleteuser bug

## [v1.3.1] - 2022-11-03

- Core functionality of the application.
- audit init skeleton with remove and backup.
