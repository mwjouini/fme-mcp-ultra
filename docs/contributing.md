# Contributing to fme-mcp-ultra

Thank you for your interest in contributing to `fme-mcp-ultra`! We welcome contributions from geospatial specialists, software engineers, security researchers, and data practitioners worldwide.

## Code Standards & Guidelines

1. **Language & Spelling**: All code comments, docstrings, documentation, commit messages, and PR descriptions must use **British English (en-GB)** (e.g. *optimise*, *serialise*, *colour*, *catalogue*, *behaviour*).
2. **Type Annotations**: Every function and method must be fully type-hinted and pass `mypy --strict`.
3. **Linting & Formatting**: We use `ruff` for formatting and linting.
4. **Testing**: All new tools and security guards must include corresponding unit tests in `tests/unit/` and integration tests where appropriate. Minimum test coverage requirement is 85%.
5. **Security First**: Input validation, path traversal guards (`PathGuard`), and command guards (`CommandGuard`) must be strictly applied on all parameter inputs.

## Development Workflow

1. Fork the repository on GitHub: `https://github.com/mwjouini/fme-mcp-ultra`.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/fme-mcp-ultra.git
   cd fme-mcp-ultra
   ```
3. Install dependencies in an isolated virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev,docs]"
   ```
4. Run the automated test suite:
   ```bash
   pytest tests/ -v
   ```
5. Create a descriptive feature branch:
   ```bash
   git checkout -b feat/add-spatial-cluster-tool
   ```
6. Commit changes with Conventional Commits (e.g. `feat(spatial): add DBSCAN clustering tool`).
7. Push to your branch and submit a Pull Request against `main`.

