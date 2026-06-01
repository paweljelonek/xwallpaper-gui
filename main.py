import os
import sys
from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "src"))

import xrandr
from gui import AppWindow, ensure_single_instance, setup_ipc_server
from tray import start_tray


def apply_saved_wallpapers(app):
    configs = []
    for monitor_name, data in app.saved_config.items():
        if monitor_name == "_last_directory":
            continue
        image_path = data.get("image_path", "")
        if os.path.exists(image_path):
            configs.append({
                "monitor": monitor_name,
                "image_path": image_path,
                "style": data.get("style", "stretch"),
            })
    if configs:
        xrandr.apply_wallpapers(configs)


class XWallpaperApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.xwallpaper.gui")
        self._window = None
        self._server = None
        self._startup_mode = "--startup" in sys.argv

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        if self._window is None:
            self._server = ensure_single_instance()
            self._window = AppWindow(self)
            setup_ipc_server(self._server, self._window)

            # Prevent GTK from quitting when the window is hidden
            self.hold()

            start_tray(self._window)

            if self._startup_mode:
                self._window.hide_window()
                if self._window.saved_config.get("_apply_on_startup", True):
                    GLib.timeout_add(3000, lambda: apply_saved_wallpapers(self._window) or False)
            else:
                self._window.show_window()
        else:
            self._window.show_window()


def main():
    app = XWallpaperApp()
    try:
        app.run(sys.argv)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
