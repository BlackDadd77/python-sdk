# SSH Setup for GitHub Actions

This document explains how to configure SSH authentication for GitHub Actions workflows in this repository.

## Overview

The workflows in this repository support both HTTPS (default) and SSH authentication for Git operations. SSH authentication is optional but recommended for:

- Enhanced security for deployments
- Accessing private repositories
- Performing authenticated Git operations

## Setup Instructions

### 1. Generate SSH Key Pair

Generate a new SSH key pair specifically for GitHub Actions:

```bash
ssh-keygen -t ed25519 -C "github-actions@python-sdk" -f ~/.ssh/python-sdk-deploy
```

This creates two files:
- `python-sdk-deploy` (private key)
- `python-sdk-deploy.pub` (public key)

### 2. Add Public Key to GitHub Repository

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Deploy keys**
3. Click **Add deploy key**
4. Title: "GitHub Actions Deploy Key"
5. Paste the contents of `python-sdk-deploy.pub`
6. Check **Allow write access** (required for pushing to gh-pages)
7. Click **Add key**

### 3. Add Private Key as Secret

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `SSH_PRIVATE_KEY`
5. Value: Paste the entire contents of `python-sdk-deploy` (private key)
6. Click **Add secret**

## How It Works

The workflows automatically detect if the `SSH_PRIVATE_KEY` secret is configured:

```yaml
- name: Setup SSH
  uses: webfactory/ssh-agent@v0.9.0
  if: ${{ secrets.SSH_PRIVATE_KEY != '' }}
  with:
    ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

### Affected Workflows

- **publish-docs-manually.yml**: Manual documentation publishing
- **publish-pypi.yml**: Documentation publishing on release

### Fallback Behavior

If `SSH_PRIVATE_KEY` is not configured, the workflows fall back to using HTTPS authentication with the default `GITHUB_TOKEN`, which is automatically provided by GitHub Actions.

## Security Best Practices

1. **Use dedicated keys**: Create separate SSH keys for GitHub Actions, don't reuse personal keys
2. **Rotate regularly**: Update SSH keys periodically (e.g., every 6-12 months)
3. **Limit permissions**: Only grant write access if absolutely necessary
4. **Monitor usage**: Regularly check deploy key usage in repository settings

## Troubleshooting

### Authentication Fails

If SSH authentication fails:

1. Verify the private key is correctly added as a secret
2. Ensure the public key is added as a deploy key with write access
3. Check that the key format is correct (no extra whitespace or line breaks)

### Workflow Still Uses HTTPS

The SSH setup step is conditional. If skipped:

1. Check that the secret is named exactly `SSH_PRIVATE_KEY`
2. Verify the secret is available in the repository (not organization-level only)
3. Check workflow logs for any setup errors

## Additional Resources

- [GitHub Deploy Keys Documentation](https://docs.github.com/en/developers/overview/managing-deploy-keys)
- [webfactory/ssh-agent Action](https://github.com/webfactory/ssh-agent)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
