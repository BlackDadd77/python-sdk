# SSH Deployment Setup

This document explains how to set up SSH keys for deployment workflows in this repository.

## SSH Key Configuration

The repository uses SSH keys for secure deployment operations. The following SSH key has been configured for deployment:

**SSH Key Details:**
- Type: `ssh-ed25519`
- Public Key: `AAAAC3NzaC1lZDI1NTE5AAAAICaC17twmoo+wblejien/I992Omju1uPJcCgj7zaeRfm`
- Email: `lailawanahar1980@gmail.com`

## Setup Instructions

### 1. Add SSH Key to GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `SSH_DEPLOY_KEY`
5. Value: Your private SSH key (the one that corresponds to the public key above)
6. Click **Add secret**

### 2. Workflow Configuration

The SSH key is configured in `.github/workflows/publish-pypi.yml` for the documentation deployment job:

```yaml
- name: Setup SSH Deploy Key
  uses: webfactory/ssh-agent@v0.9.0
  with:
    ssh-private-key: ${{ secrets.SSH_DEPLOY_KEY }}
```

### 3. Usage

The SSH key is automatically used when the deployment workflow runs. It enables:
- Secure git operations during deployment
- Push access to deploy documentation
- Authenticated repository access

## Running the Snippet

To test the SSH configuration snippet:

```bash
# Run the SSH deployment configuration example
python examples/snippets/servers/ssh_deployment_config.py
```

## Security Notes

⚠️ **Important Security Information:**
- Never commit private SSH keys to the repository
- Always store private keys as GitHub Secrets
- Only the public key should be visible in documentation
- Rotate keys regularly for security
- Use deploy keys with minimal required permissions

## Related Files

- Workflow file: `.github/workflows/publish-pypi.yml`
- Configuration snippet: `examples/snippets/servers/ssh_deployment_config.py`
- Snippet update script: `scripts/update_readme_snippets.py`
