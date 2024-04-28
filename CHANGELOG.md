# Changelog

All notable changes to this project will be documented in this file.

## [v2.0.0] - 2024-4-28
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


## [v1.3.2] - 2022-11-7

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

## [v1.3.1] - 2022-11-3

- Core functionality of the application.
- audit init skeleton with remove and backup.
