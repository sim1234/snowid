# SnowID

A simple 2D game engine built on top of PySDL2 with physics simulation using pymunk.

## Quick Start

Get up and running in 3 steps:

1. **Install dependencies:**
   ```bash
   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install SDL2 libraries
   # macOS:
   brew install sdl2 sdl2_gfx sdl2_ttf sdl2_image
   
   # Linux (Ubuntu/Debian):
   sudo apt-get install libsdl2-dev libsdl2-gfx-dev libsdl2-ttf-dev libsdl2-image-dev
   ```

2. **Set up the project:**
   ```bash
   git clone <repository-url>
   cd snowid
   uv sync
   ```

3. **Run the game:**
   ```bash
   uv run python project/main.py
   ```

That's it! You should see the Balls physics demo scene. Use **A/D** to move, **W** to jump, and **Left Click** to create balls.

For more details, see the [Installation](#installation) and [Usage](#usage) sections below.

## Overview

SnowID is a lightweight game framework that provides:
- **Game Engine**: Core game loop, scene management, and rendering
- **Physics Engine**: Integration with pymunk for 2D physics simulation
- **GUI System**: Built-in GUI components and console
- **Viewport System**: Camera and viewport management
- **Scene System**: Modular scene-based game architecture

## Requirements

- **Python 3.11** (required - project uses Python 3.11 features)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- SDL2 libraries (SDL2, SDL2_gfx, SDL2_ttf, SDL2_image)

### Installing SDL2

**macOS:**
```bash
brew install sdl2 sdl2_gfx sdl2_ttf sdl2_image
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install libsdl2-dev libsdl2-gfx-dev libsdl2-ttf-dev libsdl2-image-dev
```

**Windows:**
SDL2 DLL files should be placed in the `lib/` directory. The project includes `SDL2_gfx.dll` as an example. You'll need to download SDL2, SDL2_gfx, SDL2_ttf, and SDL2_image DLLs and place them in the `lib/` directory.

## Installation

### Prerequisites

1. Install `uv` if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or via pip:

```bash
pip install uv
```

2. Install SDL2 libraries (see Requirements section above)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd snowid
```

2. Install dependencies using uv:
```bash
uv sync
```

This will create a virtual environment and install all dependencies.

3. Activate the virtual environment:
```bash
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

## Usage

### Running the Game

You can run the game in several ways:

```bash
# Using uv (recommended)
uv run python project/main.py

# Or as a module
uv run python -m project.main

# Or activate the virtual environment first
source .venv/bin/activate  # On macOS/Linux
python project/main.py
```

### Interactive Shell

For debugging and development, you can use the interactive IPython shell:

```bash
uv run python -m project.shell
```

## Project Structure

```
snowid/
├── lib/                    # SDL2 DLL files (Windows)
├── project/                # Main application code
│   ├── gamepart/          # Core game engine framework
│   │   ├── gui/           # GUI system components
│   │   ├── physics/       # Physics engine integration
│   │   └── viewport/      # Viewport and camera system
│   ├── scenes/            # Game scenes
│   │   └── balls/         # Example physics scene
│   ├── resources/         # Game assets (fonts, images)
│   ├── main.py            # Entry point
│   └── game.py            # Main game class
├── pyproject.toml         # Project configuration and dependencies
├── mypy.ini               # Type checking configuration
└── README.md              # This file
```

## Development

### Code Quality Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatter (line length: 88)
- **mypy**: Static type checking
- **Ruff**: Fast Python linter (replaces flake8)
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting

**First, install dev dependencies:**
```bash
uv sync --extra dev
```

### Running Code Quality Checks

```bash
# Format code (check what would be changed)
uv run black --check project/

# Format code (apply changes)
uv run black project/

# Type checking
uv run mypy project/

# Linting (check)
uv run ruff check project/

# Linting (check and show fixes)
uv run ruff check --output-format=concise project/

# Linting (auto-fix)
uv run ruff check --fix project/

# Format imports (ruff can also format imports)
uv run ruff check --select I --fix project/

# Run all checks (format check, type check, lint)
uv run black --check project/ && uv run mypy project/ && uv run ruff check project/
```

### Adding Dependencies

To add a new dependency:

```bash
uv add <package-name>
```

For development dependencies:

```bash
uv add --dev <package-name>
```

### Environment Variables

- `LOG_LEVEL`: Set logging level (default: 0). Use standard Python logging levels (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)
- `PYSDL2_DLL_PATH`: Path to SDL2 DLL files (automatically set to `lib/` directory on Windows)

## Troubleshooting

### SDL2 Library Not Found

**macOS/Linux**: Make sure SDL2 libraries are installed via Homebrew/apt and are in your library path. You can verify with:
```bash
brew list sdl2  # macOS
dpkg -l | grep sdl2  # Linux
```

**Windows**: Ensure all required SDL2 DLL files are in the `lib/` directory.

### pymunk Compatibility

This project uses pymunk 7.x. If you encounter API compatibility issues, ensure you're using pymunk 7.0 or later. The project has been updated to work with pymunk 7.2.0.

## Architecture

### Game Engine (`gamepart`)

The core game engine provides:

- **Game**: Main game loop and initialization
- **Scene**: Base class for game scenes with lifecycle management
- **Context**: Game context and state management
- **SubSystem**: Base class for game subsystems
- **Time**: FPS counter and time management

### Physics (`gamepart.physics`)

Physics integration using pymunk:

- **World**: Physics world and space management
- **PhysicalObject**: Base class for physics-enabled objects
- **Vector**: 2D vector utilities
- **Category**: Collision category management

### Rendering (`gamepart.render`)

- **GfxRenderer**: SDL2 graphics renderer wrapper

### Viewport (`gamepart.viewport`)

- **ViewPort**: Camera and viewport management
- **GraphicalObject**: Base class for renderable objects

### GUI (`gamepart.gui`)

- **System**: GUI system manager
- **GUIObject**: Base class for GUI elements
- **Console**: Debug console implementation

## Examples

The project includes example scenes:

- **Test Scene**: Basic scene template (press F2 to switch)
- **Balls Scene**: Physics simulation with balls, player, and boundaries

### Balls Scene Controls

- **A/D**: Move player left/right
- **W**: Jump
- **E**: Shoot
- **Left Click**: Create a ball at mouse position with velocity
- **Right Click**: Delete ball at mouse position
- **Mouse Wheel**: Zoom in/out
- **F1**: Toggle debug console
- **F2**: Switch to test scene
- **F3**: Toggle FPS display

## License

[Add your license here]

## Author

Szymon Zmilczak

