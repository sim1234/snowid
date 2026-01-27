import logging
import os
import sys


def setup() -> None:
    # logging
    logging.basicConfig(
        level=int(os.environ.get("LOG_LEVEL", "0")),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.info("Starting...")

    # PySDL2
    # On Windows, set DLL path; on macOS/Linux, SDL2 should be installed system-wide
    if sys.platform == "win32":
        project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ.setdefault("PYSDL2_DLL_PATH", os.path.join(project, "lib"))
    import sdl2

    logging.info("Python %s", sys.version)
    logging.info("PySDL2 %s", sdl2.__version__)


def main() -> None:
    setup()
    from game import MyGame

    game = MyGame()
    game.main_loop()


if __name__ == "__main__":
    main()
