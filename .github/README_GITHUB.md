# ⚠️ This is a Mirror Repository

<div align="center">
  
  [![GitLab Repository](https://img.shields.io/badge/Primary_Repo-GitLab-orange?style=for-the-badge&logo=gitlab)](https://gitlab.com/enrichlayer/enrichlayer-py)
  [![PyPI version](https://img.shields.io/pypi/v/enrichlayer-api?style=for-the-badge)](https://pypi.org/project/enrichlayer-api/)
  
</div>

This repository is a **read-only mirror** of our primary repository hosted on GitLab.

## 🏠 Primary Repository
**All development happens on GitLab**: [gitlab.com/enrichlayer/enrichlayer-py](https://gitlab.com/enrichlayer/enrichlayer-py)

## Quick Links

| What | Where |
|------|-------|
| 🐛 **Report Issues** | ✅ HERE on GitHub - [Create Issue](https://github.com/enrichlayer/enrichlayer-py/issues/new/choose) |
| 🔧 **Submit Code** | ❌ NOT here - [Use GitLab](https://gitlab.com/enrichlayer/enrichlayer-py/-/merge_requests/new) |
| 📚 **Documentation** | [docs.enrichlayer.com](https://docs.enrichlayer.com) |
| 💬 **Discussions** | [GitHub Discussions](https://github.com/enrichlayer/enrichlayer-py/discussions) |
| 📦 **Install Package** | `pip install enrichlayer-api[gevent]` |

## Why This Setup?

We use a dual-repository approach:
- **GitHub** → Better visibility, issue tracking, and community engagement
- **GitLab** → Better CI/CD, development workflows, and security features

This is a common pattern used by many successful open source projects.

## 🚀 Quick Start

```bash
# Install from PyPI
pip install enrichlayer-api[gevent]

# Or with asyncio
pip install enrichlayer-api[asyncio]
```

```python
from enrichlayer_client.gevent import EnrichLayer

client = EnrichLayer(api_key="your-api-key")
person = client.person.get(linkedin_profile_url="https://linkedin.com/in/example")
```

## 📖 Full Documentation

For complete documentation, API reference, and examples, visit the [main README](README.md).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](.github/CONTRIBUTING.md) for details.

**Remember:**
- 🐛 Issues → GitHub (here)
- 🔧 Code → GitLab (merge requests)

Thank you for your understanding and support! 🙏