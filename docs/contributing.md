# Contributing to fme-mcp-ultra

Thank you for your interest in contributing to `fme-mcp-ultra`! We welcome contributions from geospatial specialists, software engineers, security researchers, and data practitioners worldwide.

## Code Standards & Guidelines

1. **Code & Comments**: Please write documentation, commit messages, and docstrings in clear English.
2. **Type Annotations**: Python code should be type-hinted and pass `mypy`.
3. **Linting & Formatting**: We use `ruff` for formatting and linting.
4. **Testing**: Add unit tests in `tests/unit/` for new tools and fixes.
5. **Security**: Validate inputs using the existing path and command security guards.

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

