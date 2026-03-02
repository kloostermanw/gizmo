# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gizmo is a Python 3 CLI tool for managing multiple Celery-related repositories. It provides commands for health monitoring, remote SSH execution, git operations, and self-updating.

## Running

```bash
# Install (creates venv at ~/venvs/gizmo)
./install.sh

# Run via venv
~/venvs/gizmo/venv/bin/python gizmo

# Run a specific command
python3 gizmo <command>          # e.g. python3 gizmo celery:health
```

There are no automated tests in this project.

## Architecture

### Command Plugin System

The entry point `gizmo` dynamically discovers commands from `Commands/*.py`:
1. Scans `Commands/` for `.py` files (excluding `__init__.py` and `command.py`)
2. Converts snake_case filenames to PascalCase class names via `Base.snakeCaseToPascalCase()`
3. Instantiates each class and registers it

**To add a new command**: Create `Commands/my_command.py` with a class `MyCommand` that extends `Command`. Override `configure()` to set `self.name` (e.g. `"category:action"`) and `self.description`, then implement `handle(args)`.

### Key Classes

- **`Commands/command.py: Command`** — Base class. Provides config loading (`getConfig()`), subprocess execution (`runCommand()`, `runCmdRealTime()`), and command registration (`getCommand()`, `getListItem()`).
- **`Lib/base.py: Base`** — Static utilities: `snakeCaseToPascalCase()`, string helpers, `getVersion()` (reads `VERSION` file).
- **`Lib/termcolor.py`** — Bundled terminal color library (not a pip dependency).

### Configuration Pattern

INI-format configs in `config/<service>/`:
- `conf.default` — Tracked in git, provides defaults
- `conf` — Gitignored local overrides

`Command.getConfig()` reads both files, with local `conf` values overriding defaults. Current config groups: `health`, `composer`, `github`.

### Command Naming Convention

Commands use `category:action` naming (e.g. `celery:health`, `update:check`). The category prefix is used to group commands in the help output.

## Git Workflow

- **Development branch**: `develop` (default, PR target)
- **Release branch**: `main`
- Releases managed via `.gitrelease` config (source: develop → target: main, updates `VERSION` file)
- Single dependency: `gitpython` (in `requirements.txt`)
