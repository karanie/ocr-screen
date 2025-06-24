from time import sleep
import pystray
import core
import PIL
import core.context

class Systray():
    def __init__(self, ctx: core.context.MainContext):
        self._ctx = ctx
        self._menu = pystray.Menu(
            pystray.MenuItem("Settings", self._handle_settings_menu),
            pystray.MenuItem("Restart", self._handle_restart_menu),
            pystray.MenuItem("Quit", self._handle_quit_menu),
        )
        self.tray_icon = pystray.Icon(
            'ScreenOCR',
            icon=self._icon(),
            menu=self._menu
        )
        
    def _icon(self):
        image = PIL.Image.open("./icon.png")
        return image
    
    def _handle_quit_menu(self):
        print("Quitting..")
        with self._ctx.signal_cond:
            self._ctx.signal.value = core.context.SignalState.QUIT
            self._ctx.signal_cond.notify_all()
        self.tray_icon.stop()

    def _handle_restart_menu(self):
        print("Restarting..")
        with self._ctx.signal_cond:
            self._ctx.signal.value = core.context.SignalState.RESTART
            self._ctx.signal_cond.notify_all()

    def _handle_settings_menu(self):
        print("Opening the setting window..")
        with self._ctx.signal_cond:
            self._ctx.signal.value = core.context.SignalState.OPEN_SETTINGS
            self._ctx.signal_cond.notify_all()

    def run(self):
        self.tray_icon.run()

def main(ctx):
    s = Systray(ctx)
    s.run()