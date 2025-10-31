# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CodeQL security analysis workflow for automated vulnerability scanning
- Dependabot configuration for automated dependency updates
- Security policy (SECURITY.md) with vulnerability reporting guidelines
- CODEOWNERS file for automated code review assignments
- GitHub issue templates (bug report, feature request, documentation)
- Pull request template with comprehensive checklist
- CONTRIBUTING.md with contribution guidelines
- AUTHORS.md to credit contributors
- .editorconfig for consistent code formatting across editors
- Pre-commit hooks configuration for code quality checks
- Improved CI workflow with:
  - Matrix testing across multiple Python versions (3.8-3.12)
  - Matrix testing across multiple OS (Ubuntu, Windows, macOS)
  - Code quality checks (Black, Flake8, Pylint, Mypy)
  - Code coverage reporting
  - Parallel job execution for faster CI
- Enhanced CD workflow with:
  - Pre-deployment validation checks
  - Deployment health checks
  - Deployment status tracking via GitHub Deployments API
  - Rollback capability documentation
  - Better error handling and reporting
- Comprehensive workflow summaries with status badges
- Timeout configurations for all workflow jobs

### Changed
- Improved Integration workflow with better error messages
- Enhanced Deployment workflow with multi-stage deployment process
- Updated CI checks to be more robust and informative
- Improved versioning validation to handle edge cases
- Better branch strategy documentation

### Fixed
- Branch names in deployment workflow (changed from 'development' to 'main')
- Version checking to handle missing tags gracefully
- Improved error handling in deployment scripts

### Security
- Added CodeQL scanning for security vulnerabilities
- Enabled Dependabot for dependency security updates
- Added secret scanning protection guidelines

## [2.5.3] - Previous Release

### Added
- Flask-based web application
- Spotify API integration
- YouTube search functionality
- API health check endpoint
- Rate limiting on API endpoints
- CORS support
- Multiple environment support (dev, pre, prod)
- Comprehensive test suite
- GitHub Actions CI/CD pipeline
- Render deployment integration

### Features
- Search for artists by name
- Display artist information (followers, popularity, image)
- Responsive web interface
- Environment-based configuration

[Unreleased]: https://github.com/Pedro-Accarini/octa-music/compare/2.5.3...HEAD
[2.5.3]: https://github.com/Pedro-Accarini/octa-music/releases/tag/2.5.3
