# AdventureGPT User Manual

## Introduction
AdventureGPT is a modern reimagining of the classic "Colossal Cave Adventure" text adventure game. Phase 1 provides the core engine with a classic CLI and a modern TUI interface.

## Prerequisites
- **OS**: Linux (tested), Mac (likely works), Windows (via WSL recommended).
- **Python**: 3.13 or higher.
- **Tooling**: [uv](https://github.com/astral-sh/uv) (Recommended for dependency management).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd AdventureGPT
    ```

2.  **Install dependencies**:
    Using `uv`:
    ```bash
    uv sync
    ```
    Or manually with `pip`:
    ```bash
    pip install .
    ```

## How to Play

## How to Play

Launch the game (TUI mode):

```bash
uv run adventuregpt
```
*   Use `--new` or `-n` to force a start new game (overwrites save).

### New Features (TUI)
- **Autocomplete**: Press `TAB` to see available commands.
- **Slash Commands**:
    - `/help`: Show command assistance.
    - `/learn`: Learn about the project.

### Controls & Commands
Once in the game, you can use natural language commands. The parser currently supports basic two-word commands (Verb + Noun).

*   **Move**: `go north`, `go in`, `south`, `up`, `down`, etc.
*   **Look**: `look`, `l` (Redescribe the current room).
*   **Inventory**: `inventory`, `i` (Check what you are carrying).
*   **Quit**: `quit`, `exit` (Save and close the game).

### Game State & Uninstalling
The game automatically saves your progress to `adventure.db` in your user application directory (e.g., `~/.config/adventuregpt` or `~/.local/share/adventuregpt` on Linux).

**Cleaning up**:
To completely remove all game data (saves, logs), run:
```bash
uv run adventuregpt nuke
```
This is recommended before uninstalling the CLI tool, as `pip uninstall` will not remove these files.
