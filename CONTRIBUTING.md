# Contributing to Octa Music

First off, thank you for considering contributing to Octa Music! It's people like you that make Octa Music such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Style Guidelines](#style-guidelines)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

Before you begin:
- Have you read the [Code of Conduct](CODE_OF_CONDUCT.md)?
- Check out the [existing issues](https://github.com/Pedro-Accarini/octa-music/issues)
- Review the [documentation](README.md)

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find that you don't need to create one. When you create a bug report, include as many details as possible using our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Create an issue using our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and provide the following information:

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain the behavior you expected to see
- Explain why this enhancement would be useful

### Your First Code Contribution

Unsure where to begin? You can start by looking through these `good-first-issue` and `help-wanted` issues:

- **Good first issues** - issues which should only require a few lines of code
- **Help wanted issues** - issues which should be a bit more involved

### Pull Requests

Please follow these steps to have your contribution considered:

1. Follow the [style guidelines](#style-guidelines)
2. Follow the [pull request template](.github/PULL_REQUEST_TEMPLATE.md)
3. After you submit your pull request, verify that all status checks are passing

## Style Guidelines

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- Consider using conventional commits format:
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation changes
  - `style:` formatting, missing semicolons, etc.
  - `refactor:` code refactoring
  - `test:` adding or updating tests
  - `chore:` maintenance tasks

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use [Black](https://github.com/psf/black) for code formatting
- Use [Flake8](https://flake8.pycqa.org/) for linting
- Maximum line length is 127 characters
- Use type hints where appropriate
- Write docstrings for all public modules, functions, classes, and methods

### JavaScript/HTML/CSS Style Guide

- Use consistent indentation (2 spaces for HTML/CSS/JS)
- Use meaningful variable and function names
- Comment complex logic

### Testing

- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting a PR
- Aim for high test coverage
- Use descriptive test names that explain what is being tested

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/octa-music.git
   cd octa-music
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install flake8 black pylint mypy pytest-cov
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Spotify API credentials
   ```

5. **Run tests**
   ```bash
   pytest tests/ -v
   ```

6. **Run the application**
   ```bash
   python src/main.py
   ```

## Pull Request Process

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/your-bugfix-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Add tests for your changes
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Format code
   black src/ tests/
   
   # Lint code
   flake8 src/ tests/
   
   # Run tests
   pytest tests/ -v --cov=src
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Submit the PR

7. **Wait for review**
   - Address any feedback from reviewers
   - Make requested changes
   - Update your PR

## Branch Naming Convention

- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `hotfix/description` - for urgent fixes
- `release/version` - for release branches
- `docs/description` - for documentation updates

## Questions?

Feel free to open an issue with your question or contact the maintainers.

Thank you for contributing to Octa Music! 🎵
