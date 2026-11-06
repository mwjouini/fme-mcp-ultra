# Contributing to `fme-mcp-ultra`

Thank you for your interest in contributing to **`fme-mcp-ultra`**. We welcome community contributions, bug reports, feature requests, and documentation improvements.

Documentation and code comments are maintained in English. Contributions in any clear, standard English are warmly welcomed.

---

## Code of Conduct

All contributors and maintainers must abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Development Setup

### Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- `pip` or `uv`
- Git

### Initialising the Environment
```bash
git clone https://github.com/mwjouini/fme-mcp-ultra.git
cd fme-mcp-ultra
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev,docs]"
```

---

## Quality & Security Standards

Before submitting any Pull Request, ensure all checks pass:

```bash
# Linting & Formatting
ruff check .
ruff format --check .

# Static Type Checking
mypy src/fme_mcp_ultra

# Security Scans
bandit -r src/fme_mcp_ultra

# Test Suite Execution
pytest tests/ -v --cov=src/fme_mcp_ultra
```

---

## Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

- `feat:` A new feature or MCP tool
- `fix:` A bug fix
- `docs:` Documentation updates
- `sec:` Security enhancements or CVE remediations
- `refactor:` Code restructuring without functional changes
- `test:` Adding or updating tests
- `chore:` Dependency bumps, CI updates

---

## Pull Request Process

1. Fork the repository and create a feature branch (`feat/your-feature-name`).
2. Implement your changes with corresponding unit and security tests.
3. Verify that all automated CI checks pass.
4. Ensure documentation is updated.
5. Submit your Pull Request using the [PR template](.github/PULL_REQUEST_TEMPLATE.md).

