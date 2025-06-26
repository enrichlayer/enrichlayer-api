# Contributing to enrichlayer-py

Thank you for your interest in contributing to enrichlayer-py! 🎉

## 🏠 Important: This is a Mirror Repository

**This GitHub repository is a read-only mirror.** All development happens on GitLab:

🔗 **Primary Repository**: [gitlab.com/enrichlayer/enrichlayer-py](https://gitlab.com/enrichlayer/enrichlayer-py)

### What This Means:
- ✅ **Report issues** here on GitHub - we actively monitor them!
- ❌ **Pull requests** on GitHub will be automatically closed
- ✅ **Submit code changes** as Merge Requests on GitLab

## 🐛 Reporting Issues

We use GitHub Issues for bug reports and feature requests. When reporting an issue:

1. **Search existing issues** first to avoid duplicates
2. **Use issue templates** when available
3. **Provide reproducible examples** with code snippets
4. **Include environment details** (Python version, OS, etc.)

## 🔧 Contributing Code

### Prerequisites

- Python 3.8 or higher
- Poetry for dependency management
- Git configured with your GitLab account

### Development Workflow

1. **Fork the GitLab repository** (not this GitHub mirror):
   ```bash
   # Visit: https://gitlab.com/enrichlayer/enrichlayer-py
   # Click "Fork" button
   ```

2. **Clone your fork**:
   ```bash
   git clone https://gitlab.com/YOUR_USERNAME/enrichlayer-py.git
   cd enrichlayer-py
   ```

3. **Set up development environment**:
   ```bash
   # Install poetry if you haven't
   pip install poetry
   
   # Install dependencies
   poetry install --all-extras
   
   # Activate virtual environment
   poetry shell
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

5. **Make your changes**:
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

6. **Run tests and checks**:
   ```bash
   # Run tests
   pytest tests/
   
   # Run linting
   ruff check .
   
   # Run type checking
   mypy enrichlayer_client/
   ```

7. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature" # or "fix: resolve bug"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring

8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create a Merge Request**:
   - Go to [GitLab](https://gitlab.com/enrichlayer/enrichlayer-py)
   - Click "Create merge request"
   - Fill in the template
   - Link any related GitHub issues

### Code Style Guidelines

- Use type hints for all function parameters and returns
- Follow PEP 8 style guide (enforced by ruff)
- Write docstrings for all public functions/classes
- Keep functions focused and single-purpose
- Prefer clarity over cleverness

### Testing Guidelines

- Write tests for all new functionality
- Maintain or improve code coverage
- Use meaningful test names that describe what's being tested
- Test edge cases and error conditions
- Mock external API calls in tests

### Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update type hints
- Include usage examples for new features

## 📝 Commit Message Format

We use conventional commits for clear history:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Examples:
```
feat(client): add retry logic for rate limits

Implement exponential backoff when hitting rate limits.
Max retries configurable via constructor.

Closes #123
```

## 🔄 Review Process

1. A maintainer will review your Merge Request on GitLab
2. Address any feedback or requested changes
3. Once approved, your changes will be merged
4. The changes will automatically sync to this GitHub mirror

## 📦 Release Process

Releases are handled by maintainers:

1. Version bumped in `pyproject.toml`
2. Changelog updated
3. Tagged in GitLab
4. Automatically published to PyPI
5. GitHub mirror updated with new tag

## 💬 Getting Help

- **Questions about usage**: Open a GitHub issue
- **Development questions**: Use GitLab merge request comments
- **General discussions**: GitHub Discussions
- **Security issues**: Email security@enrichlayer.com

## 🙏 Recognition

Contributors are recognized in:
- Release notes
- Contributors file
- Project documentation

Thank you for helping make enrichlayer-py better! 🚀