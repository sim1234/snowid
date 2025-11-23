import sdl2.ext
from context import MyContext
from gamepart import SimpleScene
from gamepart.gui import Console, GUISystem
from gamepart.render import GfxRenderer


class MyBaseScene(SimpleScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gui: GUISystem = None
        self.console: Console = None

    def init(self):
        super().init()
        self.gui = GUISystem(
            self.game.renderer,
            self.game.font_manager,
            self.game.sprite_factory,
            self.game.width,
            self.game.height,
        )
        self.system.add(self.gui)
        self.key_event.on_down(sdl2.SDLK_F1, self.toggle_console)
        self.key_event.on_up(sdl2.SDLK_F1, self.key_event.stop)
        self.key_event.on_up(sdl2.SDLK_F3, self.toggle_fps)
        self.event.chain(self.gui.event)

    def every_frame(self, renderer: GfxRenderer):
        self.gui.draw()

    def toggle_console(self, _=None):
        if self.console.visible:
            self.console.visible = False
            self.console.enabled = False
            self.gui.change_focus(None)
        else:
            self.console.visible = True
            self.console.enabled = True
            self.gui.change_focus(self.console)
        return True

    def toggle_fps(self, _=None):
        self.game.show_fps = not self.game.show_fps

    def stop(self):
        context = super().stop()
        context.console = self.console
        return context

    def start(self, context: MyContext):  # TODO: fix mypy
        super().start(context)
        if context.console is None:
            self.console = Console({"game": self.game})
            self.console.visible = False
            self.console.enabled = False
            self.gui.add(self.console)
        else:
            self.console = context.console
            if self.console not in self.gui.objects:
                self.gui.add(self.console)
