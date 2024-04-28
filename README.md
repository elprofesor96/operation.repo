# Operation Repository (Git like)

# Description
RedTeam tool to stay organized. It is used for keeping better notes.

This project was inspired from Git command line.

Easy to start new engagements and keep track of your logs even if it's professional/corporate project or machines on hackthebox.

# Summary

- ## op init
Creates ".opignore" which is default file.

Creates files and folders from "op.conf" such as nmap, obsidian, burp, etc.

Highly customizable in "op.conf", can make your own audit repo init.

After installation, "op.conf" file is found in "/etc/op/op.conf"

- ## op backup
Creates a backup file (.zip) from all audit repo files/folders except ones from .opignore

- ## op remove
Remove/Delete all files/folders from audit repo except ones from .opignore

# Install
- ## Automatic Install from apt server (RELEASED)
From apt repo server. SOON
- ## Automatic Install from github release page (RELEASED)
From https://github.com/elProfesor96/operation.repo/releases , download latest .deb release.
```bash
sudo apt update
```
```bash
sudo apt install ./audit-latest-release.deb
```
- ## Manual install from git clone (ONLY for DEV)
Git clone repo.
```bash
git clone https://github.com/elProfesor96/audit.repo.git
```
Change those lines in ConfigHandler.py to your current paths from your cloned repo. 

Change to the FULL PATH and git repo while developing.
```python
self.home_folder = os.path.expanduser("~") (change to git repo folder)
```

# Usage
```bash
op -h
```
```bash
op init
```
```bash
op backup
```
```bash
op remove
```
# Example
SOON

# Ops Server
working

