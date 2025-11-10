"""
SSH Deployment Configuration Example

This example demonstrates how to configure SSH keys for deployment workflows.
The SSH key should be stored as a GitHub secret and used in deployment workflows.

SSH Key Information:
- Type: ssh-ed25519
- Key: AAAAC3NzaC1lZDI1NTE5AAAAICaC17twmoo+wblejien/I992Omju1uPJcCgj7zaeRfm
- Email: lailawanahar1980@gmail.com
"""

import os
from pathlib import Path


def configure_ssh_deployment():
    """Configure SSH for deployment operations."""
    # In GitHub Actions, SSH keys are typically configured using:
    # - webfactory/ssh-agent action for SSH operations
    # - SSH key stored as a repository secret (SSH_DEPLOY_KEY)
    
    ssh_config = {
        "key_type": "ssh-ed25519",
        "key_fingerprint": "AAAAC3NzaC1lZDI1NTE5AAAAICaC17twmoo+wblejien/I992Omju1uPJcCgj7zaeRfm",
        "email": "lailawanahar1980@gmail.com",
        "usage": "GitHub Actions deployment workflow"
    }
    
    return ssh_config


def get_deployment_info():
    """Get deployment configuration information."""
    return {
        "workflow": ".github/workflows/publish-pypi.yml",
        "ssh_agent_action": "webfactory/ssh-agent@v0.9.0",
        "secret_name": "SSH_DEPLOY_KEY",
        "description": "SSH key for deploying documentation and releases"
    }


if __name__ == "__main__":
    config = configure_ssh_deployment()
    print("SSH Deployment Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\nDeployment Info:")
    info = get_deployment_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
