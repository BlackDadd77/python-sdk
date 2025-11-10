# Security Policy

Thank you for helping us keep the SDKs and systems they interact with secure.

## Private Repository Security Configuration

This repository is configured with enhanced security measures for private use:

- **Workflow Restrictions**: All GitHub Actions workflows are configured to run only on private repositories using `if: github.event.repository.private == true` conditions
- **Branch Protection**: Pull request workflows only run on active PRs (not merged) targeting specific branches (main, v*.*.*)
- **Snippet Validation**: README snippet validation is disabled for private repositories to prevent unnecessary workflow runs
- **Access Control**: Only authorized collaborators can trigger workflows through push events or pull requests

These configurations ensure that:
1. Workflows cannot be triggered on public forks
2. Merged pull requests do not trigger redundant workflow runs
3. Repository resources are protected for private use only

## Reporting Security Issues

This SDK is maintained by [Anthropic](https://www.anthropic.com/) as part of the Model Context Protocol project.

The security of our systems and user data is Anthropic’s top priority. We appreciate the work of security researchers acting in good faith in identifying and reporting potential vulnerabilities.

Our security program is managed on HackerOne and we ask that any validated vulnerability in this functionality be reported through their [submission form](https://hackerone.com/anthropic-vdp/reports/new?type=team&report_type=vulnerability).

## Vulnerability Disclosure Program

Our Vulnerability Program Guidelines are defined on our [HackerOne program page](https://hackerone.com/anthropic-vdp).
