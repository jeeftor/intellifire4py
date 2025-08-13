# Development Guide - Using UV

This guide outlines how to use UV for Python dependency management as a replacement for Poetry in the intellifire4py project.

## Installation

UV can be installed in several ways:

```bash
# Using pip
pip install uv

# Using brew (on macOS)
brew install uv

# Using the Nix flake in this repository (recommended)
nix develop
```

## Nix Integration

This project uses a Nix flake for reproducible development environments. The flake.nix file has been configured to use UV instead of Poetry.

### Using the Nix Development Shell

```bash
# Enter the development environment
nix develop

# This automatically:
# 1. Creates a virtual environment with UV
# 2. Installs the project dependencies
# 3. Activates the environment
```

### Nix Flake Structure

The flake.nix file sets up a development environment with:

- Python 3.13
- UV package manager
- Python LSP server
- Pytest

The shellHook in the flake.nix file:

1. Creates a virtual environment using UV
2. Installs the project in development mode
3. Activates the environment

### Benefits of Using UV with Nix

- Reproducible environments across all development machines
- Automatic Python version management
- Faster dependency installation compared to Poetry
- Minimal configuration requirements

## Environment Setup

### Creating a virtual environment

```bash
# Create a new virtual environment
uv venv

# With specific Python version
uv venv --python-version 3.13
```

### Activating the environment

```bash
source .venv/bin/activate
```

## Dependency Management

### Installing the project & dependencies

```bash
# Install the project in development mode
uv pip install -e .

# Install all dependencies
uv pip install -e ".[dev]"
```

### Adding dependencies

```bash
# Add a new dependency
uv pip install package_name

# Add a specific version
uv pip install "package_name==1.0.0"

# Add to development dependencies
uv pip install --dev package_name
```

### Updating dependencies

```bash
# Update a specific package
uv pip install --upgrade package_name

# List outdated packages
uv pip list --outdated
```

### Creating/updating requirements.txt

```bash
# Generate requirements.txt
uv pip freeze > requirements.txt

# For development dependencies
uv pip freeze --dev > requirements-dev.txt
```

## Project Management

### Initializing a new project

```bash
uv init
```

### Managing Python versions

```bash
# Create .python-version file
echo "3.13" > .python-version

# UV will automatically use this version when creating environments
```

## Testing & Building

### Running tests

```bash
# Run tests using pytest
uv run pytest

# With coverage
uv run pytest --cov
```

### Building the package

```bash
# Build the package
uv run build
```

## Publishing

### Building and publishing to PyPI

```bash
# Build the distribution
python -m build

# Upload to PyPI
uv run twine upload dist/*
```

## Comparing with Poetry Commands

| Task                 | Poetry Command                   | UV Equivalent                            | Nix+UV Command                                    |
| -------------------- | -------------------------------- | ---------------------------------------- | ------------------------------------------------- |
| Initialize a project | `poetry init`                    | `uv init`                                | `nix develop && uv init`                          |
| Install dependencies | `poetry install`                 | `uv pip install -e .`                    | Automatic in `nix develop`                        |
| Add a package        | `poetry add package`             | `uv pip install package`                 | `nix develop && uv pip install package`           |
| Add dev dependency   | `poetry add --group dev package` | `uv pip install --dev package`           | `nix develop && uv pip install --dev package`     |
| Update a package     | `poetry update package`          | `uv pip install --upgrade package`       | `nix develop && uv pip install --upgrade package` |
| Run command          | `poetry run command`             | `uv run command`                         | `nix develop && uv run command`                   |
| Build package        | `poetry build`                   | Need to use `python -m build`            | `nix develop && python -m build`                  |
| Publish to PyPI      | `poetry publish`                 | Need to use `uv run twine upload dist/*` | `nix develop && uv run twine upload dist/*`       |

## CI/CD Integration

To update the GitHub Actions workflows, replace calls to Poetry with the UV equivalents. For example:

```yaml
# Before
- run: poetry install
- run: poetry run pytest

# After
- run: uv pip install -e .
- run: uv run pytest
```

### Python Version Management

UV excels at Python version management, which is one of its major advantages over Poetry by storing the Python version in your git repo to automatically install and use the same Python version in production environments.

1. Create a `.python-version` file at the project root:

   ```
   3.13
   ```

2. UV will automatically detect and use this version when creating environments and running commands with `uv run`.

3. Changing Python versions is as simple as updating the `.python-version` file and running UV commands again.

4. For CI/CD environments, the `.python-version` file ensures consistent Python versions across all environments.

### Version Locking

UV uses lock files to ensure reproducible builds:

1. Generate a lock file:
   ```bash
   uv lock
   ```

## Managing Dependencies with UV

UV provides several ways to manage your project dependencies:

### Updating Dependencies

#### Update a specific package

To update a specific package to the latest version:

```bash
uv pip install --upgrade <package>
```

For example:

```bash
uv pip install --upgrade pydantic
```

#### Update all dependencies

To update all dependencies to their latest versions:

```bash
uv pip install --upgrade -e .
```

#### Update by editing pyproject.toml

1. Edit the version constraints in pyproject.toml
2. Run `uv lock` to regenerate the lock file
3. Run `uv sync` to install the updated dependencies

For example, if you want to update pydantic to version 2.0 or higher:

1. Change `"pydantic>=1.10.8"` to `"pydantic>=2.0.0"` in pyproject.toml
2. Run:
   ```bash
   uv lock
   uv sync
   ```

### Adding New Dependencies

To add a new dependency:

1. Add it to pyproject.toml under the `dependencies` section
2. Run `uv lock` to update the lock file
3. Run `uv sync` to install the dependency

### Development Dependencies

For development, you can install all dev dependencies using:

```bash
uv pip install -e ".[dev]"
```

To add a new development dependency:

1. Add it to pyproject.toml under the `project.optional-dependencies.dev` section
2. Run `uv lock` to update the lock file
3. Run `uv sync` to install the dependency

4. This creates a `uv.lock` file that locks all dependency versions.

5. Install dependencies from lock file:

   ```bash
   uv sync
   ```

6. When migrating from Poetry, you might want to preserve the exact versions from poetry.lock by first hardcoding dependency versions in pyproject.toml, then generating uv.lock, and finally reverting to version ranges.

### Project Structure

UV works with the standard Python project structure and pyproject.toml format. Your existing pyproject.toml will need some adjustments to work optimally with UV.

For example:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "intellifire4py"
version = "4.1.11"
description = "Intellifire4Py"
authors = [
    {name = "Jeff Stein", email = "jeffstein@gmail.com"}
]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=1.10.8",
    "aenum>=3.1.11",
    "rich>=10.0.0",
    "aiohttp>=3.9.1"
]

[project.urls]
Homepage = "https://github.com/jeeftor/intellifire4py"
Repository = "https://github.com/jeeftor/intellifire4py"
Documentation = "https://intellifire4py.readthedocs.io"
"Bug Tracker" = "https://github.com/jeeftor/intellifire4py/issues"
Changelog = "https://github.com/jeeftor/intellifire4py/releases"

[project.optional-dependencies]
dev = [
    "mypy>=1.5.1",
    "black>=23.9.1,<25.0.0",
    "pytest>=7.4.2",
    "sphinx>=7.2.6",
    "pre-commit>=3.4.0",
    "pre-commit-hooks==4.5.0",
    "pyupgrade>=3.13.0",
    "nox>=2023.4.22",
    "nox-poetry>=1.0.3",
    "pytest-asyncio>=0.21.1",
    "sphinx-copybutton>=0.5.2",
    "myst-parser>=2.0.0",
    "sphinx-click>=5.0.1",
    "sphinx-autobuild>=2021.3.14",
    "typeguard>=4.1.5",
    "xdoctest>=1.1.1",
    "pytest-cov>=4.1.0",
    "ruff==0.1.4",
    "aioresponses>=0.7.6",
    "pytest-xdist>=3.5.0",
    "safety>=3.3.1",
    "pytest-timeout>=2.3.1",
    "furo>=2024.8.6",
    "pytest-mock>=3.14.0"
]

[project.scripts]
intellifire4py = "intellifire4py.__main__:main"
```

## Best Practices

1. Use `.python-version` file to manage Python versions
2. Use requirements.txt for pinning exact dependencies when needed
3. Keep pyproject.toml for metadata and general dependency specifications
4. Consider using uv lock/uv.lock for reproducible environments

## Troubleshooting

- If you encounter issues with dependency resolution, try using `uv pip install --no-deps` followed by `uv pip install -e .`
- For version conflicts, consider using `uv lock` to create a lockfile
- When using Nix and encountering environment issues:
  - Try removing the `.venv` directory and running `nix develop` again
  - Make sure your flake.nix is properly configured for your Python version
  - Check that the `shellHook` in your flake.nix properly activates the environment

## Nix-Specific Workflows

### Updating Dependencies in flake.nix

If you need to add tools or dependencies to the development environment:

```nix
# In flake.nix
devShells.default = pkgs.mkShell {
  packages = [
    python
    pkgs.uv
    # Add new tools here
    python.pkgs.python-lsp-server
    python.pkgs.pytest
  ];
};
```

### Updating Python Version

To update the Python version:

1. Update the Python version in flake.nix:

```nix
python = pkgs.python313; # Change as needed
```

2. Update .python-version file:

```bash
echo "3.13" > .python-version
```

3. Reload the Nix environment:

```bash
nix develop
```

### Creating Reproducible Builds

To ensure reproducible builds with UV and Nix:

1. Create and commit both pyproject.toml and uv.lock files
2. Make sure flake.nix pins dependencies correctly
3. Use `nix develop` before any build operations
