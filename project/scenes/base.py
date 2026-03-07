import typing

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
        self.game.fps_display_config.display = not self.game.fps_display_config.display

    def stop(self) -> MyContext:
        context = super().stop()
        assert isinstance(context, MyContext)
        context.console = self.console
        self.gui.clear()
        return context

    def start(self, context: Context) -> None:
        super().start(context)
        assert isinstance(context, MyContext)
        self.event_dispatcher.chain_before(self.gui.event)
        kb = context.key_binds
        self.keyboard_event.on_down(kb.get("console"), self.toggle_console)
        self.keyboard_event.on_up(kb.get("console"), self.keyboard_event.stop)
        self.keyboard_event.on_up(kb.get("toggle_fps"), self.toggle_fps)
        if context.console is None:
            self.console = Console({"game": self.game})
            self.console.visible = False
            self.console.enabled = False
            self.gui.add(self.console)
        else:
            self.console = context.console
            self.gui.add(self.console)
