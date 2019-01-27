from ..subsystem import SubSystemObject


class GUIObject(SubSystemObject):
    def draw(self, manager: "GUISystem"):
        raise NotImplementedError()


from .system import GUISystem  # noqa
