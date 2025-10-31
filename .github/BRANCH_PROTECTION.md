# Branch Protection Rules

This document describes the recommended branch protection rules for the Octa Music repository.

## Main Branch (`main`)

The `main` branch is the production branch and should be protected with the following rules:

### Required Status Checks
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

**Required checks:**
- `Quality Checks` (from Integration workflow)
- `Test Matrix (ubuntu-latest, 3.10)` (from Integration workflow)
- `Integration Tests` (from Integration workflow)
- `CodeQL / Analyze Code` (from CodeQL workflow)

### Pull Request Reviews
- ✅ Require pull request reviews before merging
- ✅ Required number of approving reviews: 1
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (defined in `.github/CODEOWNERS`)

### Additional Rules
- ✅ Require linear history (enforce rebase/squash merging)
- ✅ Include administrators (applies rules to repository admins too)
- ❌ Do not allow force pushes
- ❌ Do not allow deletions

### Merge Options
- ✅ Allow squash merging (recommended)
- ✅ Allow merge commits
- ❌ Allow rebase merging (optional, based on team preference)

## Development Branch (`development`)

The `development` branch is for integrating features before production and should have lighter protection:

### Required Status Checks
- ✅ Require status checks to pass before merging

**Required checks:**
- `Quality Checks` (from Integration workflow)
- `Test Matrix (ubuntu-latest, 3.10)` (from Integration workflow)

### Pull Request Reviews
- ✅ Require pull request reviews before merging
- ✅ Required number of approving reviews: 1
- ❌ Do not dismiss stale approvals (less strict than main)

### Additional Rules
- ❌ Do not allow force pushes
- ❌ Do not allow deletions

## Feature Branches (`feature/*`)

Feature branches don't need branch protection rules as they are temporary working branches.

**Naming convention:** `feature/description-of-feature`

## Bugfix Branches (`bugfix/*`)

Bugfix branches don't need branch protection rules as they are temporary working branches.

**Naming convention:** `bugfix/description-of-bug`

## Hotfix Branches (`hotfix/*`)

Hotfix branches may have expedited review processes but should still pass CI checks.

**Naming convention:** `hotfix/description-of-urgent-fix`

## Release Branches (`release/*`)

Release branches should have similar protection to `main`:

### Required Status Checks
- ✅ Require status checks to pass before merging

**Required checks:**
- All integration workflow checks
- CodeQL security scanning

**Naming convention:** `release/v1.2.3`

## Configuring Branch Protection Rules

To configure these rules in GitHub:

1. Go to your repository on GitHub
2. Click on **Settings**
3. Click on **Branches** in the left sidebar
4. Click **Add rule** or edit an existing rule
5. Enter the branch name pattern (e.g., `main`, `development`, `release/*`)
6. Check the boxes for the desired protection rules
7. Click **Create** or **Save changes**

## Environment Protection Rules

For the `production` environment used in deployments:

1. Go to **Settings** → **Environments** → **production**
2. Configure:
   - ✅ Required reviewers: Add at least one reviewer for production deployments
   - ✅ Wait timer: Optional 5-minute wait before deployment
   - ✅ Deployment branches: Only `main` branch can deploy to production

## Ruleset Best Practices

- **Always require CI to pass** before merging to protected branches
- **Enforce code reviews** for quality assurance and knowledge sharing
- **Use CODEOWNERS** to automatically request reviews from relevant team members
- **Protect against force pushes** to maintain commit history integrity
- **Use status checks** to ensure code quality, tests, and security scans pass
- **Regularly review and update** branch protection rules as the project evolves

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
