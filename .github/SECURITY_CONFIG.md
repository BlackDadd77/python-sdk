# GitHub Repository Security Configuration

This document describes the security configurations applied to this repository for private use.

## Workflow Security

All GitHub Actions workflows in this repository include security restrictions:

### Private Repository Enforcement
All workflows check `github.event.repository.private == true` to ensure they only run on private repositories. This prevents:
- Unauthorized workflow runs on public forks
- Exposure of sensitive build/test processes
- Misuse of repository resources

### Pull Request Workflow Restrictions
The pull request workflow (`.github/workflows/pull-request-checks.yml`) includes:
- **Trigger Types**: Only `opened`, `synchronize`, and `reopened` events
- **Branch Targets**: Only PRs targeting `main` or version branches (`v*.*.*`)
- **Merged PR Check**: Excludes merged PRs with `github.event.pull_request.merged == false`

### Disabled Features
- **README Snippet Validation**: Disabled in `shared.yml` with `if: false` to prevent unnecessary runs on merged branches

## Branch Protection (Recommended Settings)

For maximum security, configure the following branch protection rules via GitHub Settings:

### Main Branch
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators in restrictions
- Restrict who can push to matching branches

### Version Branches (v*.*.*)
- Same settings as main branch
- Allow only release managers to push directly

## Repository Settings (Recommended)

Configure these settings in your GitHub repository:

1. **Visibility**: Set to Private
2. **Collaborators**: Limit to necessary team members only
3. **Actions Permissions**:
   - Allow selected actions only
   - Allow actions created by GitHub
   - Allow actions by verified creators
4. **Workflow Permissions**:
   - Read repository contents and packages permissions
   - Enable "Allow GitHub Actions to create and approve pull requests" only if needed

## Environment Protection

For workflows that deploy or publish (like `publish-pypi.yml`):
- Use GitHub Environments with protection rules
- Require reviewers for production deployments
- Use environment secrets for sensitive credentials

## Monitoring

Regularly review:
- Workflow run history
- Failed security checks
- Dependabot alerts
- Code scanning alerts
- Secret scanning alerts

## Questions

For questions about these security configurations, contact the repository administrators.
