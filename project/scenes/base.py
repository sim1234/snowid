import typing

import sdl2
from context import MyContext
from gamepart import SimpleScene
from gamepart.context import Context
from gamepart.gui import Console, GUISystem
from gamepart.render import GfxRenderer


class MyBaseScene(SimpleScene):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.gui: GUISystem
        self.console: Console
        self._key_bind_keys: set[tuple[int, int]] = set()

    def init(self) -> None:
        super().init()
        self.gui = GUISystem(
            self.game.renderer,
            self.game.font_manager,
            self.game.sprite_factory,
            self.game.width,
            self.game.height,
        )
        self.system.add(self.gui)
        self.event_dispatcher.chain_before(self.gui.event)

    def every_frame(self, renderer: GfxRenderer) -> None:
        renderer.clear((0, 0, 0, 255))
        self.gui.draw()

    def toggle_console(self, _: typing.Any = None) -> None:
        if self.console.visible:
            self.console.visible = False
            self.console.enabled = False
            self.gui.change_focus(None)
        else:
            self.console.visible = True
            self.console.enabled = True
            self.gui.change_focus(self.console)

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
        for key in self._key_bind_keys:
            self.keyboard_event.remove_key(key)
        self._key_bind_keys.clear()
        kb = context.key_binds
        self.keyboard_event.on_down(kb.get("console"), self.toggle_console)
        self.keyboard_event.on_up(kb.get("console"), self.keyboard_event.stop)
        self.keyboard_event.on_up(kb.get("toggle_fps"), self.toggle_fps)
        self._key_bind_keys.add((sdl2.SDL_KEYDOWN, kb.get("console")))
        self._key_bind_keys.add((sdl2.SDL_KEYUP, kb.get("console")))
        self._key_bind_keys.add((sdl2.SDL_KEYUP, kb.get("toggle_fps")))
        if context.console is None:
            self.console = Console({"game": self.game})
            self.console.visible = False
            self.console.enabled = False
            self.gui.add(self.console)
        else:
            self.console = context.console
            if self.console not in self.gui.objects:
                self.gui.add(self.console)
