# Mirror Repository Information

This directory contains GitHub-specific files for the mirror repository setup.

## Structure

```
.github/
├── ISSUE_TEMPLATE/          # Issue templates for bug reports and features
│   ├── bug_report.md
│   ├── feature_request.md
│   └── config.yml
├── workflows/               # GitHub Actions
│   ├── close-prs.yml       # Auto-closes pull requests
│   └── sync-check.yml      # Monitors sync status
├── CONTRIBUTING.md         # Contribution guidelines
├── pull_request_template.md # PR template (redirects to GitLab)
├── README_GITHUB.md        # GitHub-specific README
└── MIRROR_INFO.md          # This file
```

## How It Works

1. **GitLab** pushes changes to GitHub automatically via repository mirroring
2. **GitHub Issues** are used for community bug reports and feature requests
3. **GitHub PRs** are automatically closed with instructions to use GitLab
4. **Sync monitoring** runs every 6 hours to ensure mirrors stay in sync

## Maintenance

- Monitor GitHub issues regularly
- Ensure GitLab mirror settings are working
- Update community files as needed
- Keep documentation synchronized