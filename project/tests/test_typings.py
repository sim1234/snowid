"""Test that sdl2 typings are properly picked up by mypy."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Get the project root (where typings/ is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent
TYPINGS_DIR = PROJECT_ROOT / "typings"


def run_mypy_on_code(code: str) -> tuple[int, str]:
    """Run mypy on a code snippet and return (exit_code, output)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        temp_path = Path(f.name)

    try:
        # Use MYPYPATH environment variable to point to typings
        env = {**os.environ, "MYPYPATH": str(TYPINGS_DIR)}
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mypy",
                "--no-error-summary",
                "--no-incremental",
                str(temp_path),
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        return result.returncode, result.stdout + result.stderr
    finally:
        temp_path.unlink()


class TestSdl2Typings:
    """Test that sdl2 typings are available and work correctly."""

    def test_sdl2_has_types(self) -> None:
        """Test that basic sdl2 imports are typed."""
        code = """
import sdl2

# These should be recognized as valid types
event: sdl2.SDL_Event
rect: sdl2.SDL_Rect

# SDL_Init should be a callable
result: int = sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

# These should be available at sdl2.* level
get_clip = sdl2.SDL_RenderGetClipRect
set_clip = sdl2.SDL_RenderSetClipRect
create = sdl2.SDL_CreateRenderer

rect = sdl2.SDL_Rect()
x: int = rect.x
y: int = rect.y
w: int = rect.w
h: int = rect.h

event = sdl2.SDL_Event()
pos_x: int = event.button.x
"""
        exit_code, output = run_mypy_on_code(code)
        assert exit_code == 0, f"mypy failed: {output}"

    def test_union_type_error_is_caught(self) -> None:
        """Test that type errors are properly caught."""
        code = """
import sdl2

event = sdl2.SDL_Event()
# This should fail - x is an int, not a string
x: str = event.button.x
"""
        exit_code, output = run_mypy_on_code(code)
        # This should fail because rect.x is int, not str
        assert exit_code != 0, "mypy should have caught the type error"
        assert "Incompatible types" in output or "incompatible type" in output.lower()
