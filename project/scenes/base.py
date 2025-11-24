import typing

import sdl2.ext
from context import MyContext
from gamepart import SimpleScene
from gamepart.context import Context
from gamepart.gui import Console, GUISystem
from gamepart.render import GfxRenderer


class MyBaseScene(SimpleScene):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.gui: GUISystem | None = None
        self.console: Console | None = None

    def init(self) -> None:
        super().init()
        if (
            self.game.renderer is None
            or self.game.font_manager is None
            or self.game.sprite_factory is None
        ):
            return
        self.gui = GUISystem(
            self.game.renderer,
            self.game.font_manager,
            self.game.sprite_factory,
            self.game.width,
            self.game.height,
        )
        if self.system is not None:
            self.system.add(self.gui)
        if self.key_event is not None:
            self.key_event.on_down(sdl2.SDLK_F1, self.toggle_console)
            self.key_event.on_up(sdl2.SDLK_F1, self.key_event.stop)
            self.key_event.on_up(sdl2.SDLK_F3, self.toggle_fps)
        if (
            hasattr(self, "_event_dispatcher")
            and self._event_dispatcher is not None
            and self.gui is not None
        ):
            self._event_dispatcher.chain(self.gui.event)

    def every_frame(self, renderer: GfxRenderer) -> None:
        if self.gui is None:
            return
        self.gui.draw()

    def toggle_console(self, _: typing.Any = None) -> bool:
        if self.console is None or self.gui is None:
            return False
        if self.console.visible:
            self.console.visible = False
            self.console.enabled = False
            self.gui.change_focus(None)
        else:
            self.console.visible = True
            self.console.enabled = True
            self.gui.change_focus(self.console)
        return True

    def toggle_fps(self, _: typing.Any = None) -> None:
        self.game.show_fps = not self.game.show_fps

    def stop(self) -> MyContext:
        context = super().stop()
        assert isinstance(context, MyContext)
        context.console = self.console
        return context

    def start(self, context: Context) -> None:
        super().start(context)
        if not isinstance(context, MyContext):
            return
        if self.gui is None:
            return
        if context.console is None:
            self.console = Console({"game": self.game})
            self.console.visible = False
            self.console.enabled = False
            self.gui.add(self.console)
        else:
            self.console = context.console
            if self.console is not None and self.console not in self.gui.objects:
                self.gui.add(self.console)
