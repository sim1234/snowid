import logging
import sys
import os


def main():
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault("PYSDL2_DLL_PATH", os.path.join(project, "lib"))
    logging.basicConfig(level=int(os.environ.get("LOG_LEVEL", "0")))
    import sdl2
    import sdl2.sdlgfx

    logging.info("Python %s", sys.version)
    logging.info("PySDL2 %s", sdl2.__version__)

    from game import MyGame

    game = MyGame()
    game.main_loop()


if __name__ == "__main__":
    main()
