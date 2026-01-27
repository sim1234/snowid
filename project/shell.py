import IPython
from main import setup


def main() -> None:
    setup()
    IPython.start_ipython(argv=[])


if __name__ == "__main__":
    main()
