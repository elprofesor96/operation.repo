# Changelog

All notable changes to this project will be documented in this file.

## [v2.0.0] - 2024-4-14

### Added
- Refactor code to be more readable and changed from `AUDIT` to `OP` from operation.
- added CI scans snyk to defectdojo
- added CI scans semgrep to defectdojo
- added CI scans bandit to defectdojo

### Changed
- Changed name from audit.repo into operation.repo
- opsserver
- op init
- op init -c [custom]
- op remove
- op backup
- op list
- op push
- op clone
- refactor logic to use .operation and .opignore as defaults for using operation.repo app
- changed README.md to reflect operation.repo instead of audit.repo docs


## [v1.3.2] - 2022-11-7

### Added
- auditserver
- audit init
- audit init -c [custom]
- audit remove
- audit backup
- audit list
- audit push
- audit clone
- refactor logic to use .audit and .auditignore as defaults for using audit repo app


### Changed
- Updated dependencies to the latest versions.

### Fixed
- resolved deleteuser bug

## [v1.3.1] - 2022-11-3

### Added
- Core functionality of the application.
- audit init skeleton with remove and backup
