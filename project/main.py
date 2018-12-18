import logging
import sys
import os


def setup():
    # logging
    logging.basicConfig(
        level=int(os.environ.get("LOG_LEVEL", "0")),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.info("Starting...")

    # PySDL2
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault("PYSDL2_DLL_PATH", os.path.join(project, "lib"))
    import sdl2

    logging.info("Python %s", sys.version)
    logging.info("PySDL2 %s", sdl2.__version__)


def main():
    setup()
    from game import MyGame

    game = MyGame()
    game.main_loop()


if __name__ == "__main__":
    main()
