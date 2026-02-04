import typing


class Context:
    """Object passed between scenes using start and stop methods"""

    def __init__(self, last_scene: typing.Any) -> None:
        self.last_scene = last_scene

    def __repr__(self) -> str:
        args = [
            f"{name}={value!r}"
            for name, value in self.__dict__.items()
            if not name.startswith("_")
        ]
        return f"{self.__class__.__name__}({', '.join(args)})"
