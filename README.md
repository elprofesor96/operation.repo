# Audit Repository (Git like)

# Description
RedTeam tool to stay organized. It is used for keeping better notes.

This project was inspired from Git command line.

Easy to start new engagements and keep track of your logs even if it's professional/corporate project or machines on hackthebox.

# Summary

- ## audit init
Creates ".auditignore" which is default file.

Creates files and folders from "audit.conf" such as nmap, obsidian, burp, etc.

Highly customizable in "audit.conf", can make your own audit repo init.

After installation, "audit.conf" file is found in "/etc/audit/audit.conf"

- ## audit backup
Creates a backup file (.zip) from all audit repo files/folders except ones from .auditignore

- ## audit remove
Remove/Delete all files/folders from audit repo except ones from .auditignore

# Install
- ## Automatic Install
From apt repo server. SOON
- ## Manual Install
From https://github.com/elProfesor96/audit.repo/releases , download latest .deb release.
```bash
sudo apt update
```
```bash
sudo apt install ./audit-latest-release.deb
```

# Usage
```bash
audit -h
```
```bash
audit init
```
```bash
audit backup
```
```bash
audit remove
```
## Example
SOON

