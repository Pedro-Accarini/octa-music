# GitHub Workflow Status Configuration

This document outlines the required status checks for pull requests to protected branches.

## Required Status Checks for `main` Branch

The following status checks must pass before a pull request can be merged to `main`:

### From Integration Workflow
1. **Quality Checks** - Ensures code formatting, linting, and static analysis pass
2. **Test Matrix (ubuntu-latest, 3.10)** - Core test suite on primary platform
3. **Integration Tests** - Full integration test suite with version validation

### From CodeQL Workflow
1. **Analyze Code (python)** - Security vulnerability scanning for Python code
2. **Analyze Code (javascript)** - Security vulnerability scanning for JavaScript code

## Optional Status Checks

These checks are recommended but not required:

### From Integration Workflow (Test Matrix)
- Test Matrix (ubuntu-latest, 3.8)
- Test Matrix (ubuntu-latest, 3.9)
- Test Matrix (ubuntu-latest, 3.11)
- Test Matrix (ubuntu-latest, 3.12)
- Test Matrix (windows-latest, 3.10)
- Test Matrix (macos-latest, 3.10)

## Configuring Required Status Checks

1. Navigate to repository **Settings** → **Branches**
2. Click **Edit** on the `main` branch rule (or **Add rule** if it doesn't exist)
3. Check **Require status checks to pass before merging**
4. Check **Require branches to be up to date before merging**
5. Search for and select the required status checks listed above
6. Click **Save changes**

## Bypassing Status Checks

Repository administrators can bypass status checks in emergency situations, but this should be avoided whenever possible. If you need to bypass checks:

1. Document the reason in the PR description
2. Create a follow-up issue to address any skipped checks
3. Notify the team through appropriate channels

## Troubleshooting Failed Status Checks

### Quality Checks Failed
- Run `black src/ tests/` to auto-format code
- Run `flake8 src/ tests/` to check for linting issues
- Fix any issues reported by the linter

### Test Failures
- Run `pytest tests/ -v` locally to reproduce
- Check the workflow logs for specific failure details
- Ensure all dependencies are properly installed

### CodeQL Alerts
- Review the security alerts in the **Security** tab
- Address or dismiss alerts as appropriate
- Re-run the CodeQL workflow after fixes

## Workflow Dispatch

Some workflows can be manually triggered:

1. Go to **Actions** tab
2. Select the workflow
3. Click **Run workflow**
4. Choose the branch and click **Run workflow**

## Best Practices

- ✅ Always run local CI checks before pushing (`./scripts/local-ci.sh`)
- ✅ Keep your branch up to date with the base branch
- ✅ Address CI failures promptly
- ✅ Review CodeQL alerts before merging
- ✅ Use descriptive commit messages
- ❌ Don't force push to shared branches
- ❌ Don't merge with failing status checks (unless absolutely necessary)
