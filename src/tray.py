import os
import threading
from PIL import Image

ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
TRAY_ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "tray_icon.png")


def start_tray(app):
    try:
        import gi
        gi.require_version('XApp', '1.0')
        gi.require_version('Gtk', '3.0')
        from gi.repository import XApp, Gtk, GLib

        menu = Gtk.Menu()
        item_open = Gtk.MenuItem(label="Open")
        item_open.connect("activate", lambda w: app.after(0, app.show_window))
        menu.append(item_open)

        item_about = Gtk.MenuItem(label="About")
        item_about.connect("activate", lambda w: app.after(0, app._show_about))
        menu.append(item_about)

        item_exit = Gtk.MenuItem(label="Exit")
        item_exit.connect("activate", lambda w: [GLib.idle_add(Gtk.main_quit), app.after(0, app.quit_app)])
        menu.append(item_exit)
        menu.show_all()

        _icon_ref = []

        def _create_icon():
            icon = XApp.StatusIcon()
            icon_to_use = TRAY_ICON_PATH if os.path.exists(TRAY_ICON_PATH) else ICON_PATH
            icon.set_icon_name(icon_to_use if os.path.exists(icon_to_use) else "preferences-desktop-wallpaper")
            icon.set_tooltip_text("xwallpaper gui")
            icon.set_secondary_menu(menu)
            icon.set_visible(True)
            icon.connect("activate", lambda i, b, t: app.after(0, app.show_window))
            _icon_ref.append(icon)
            return False

        def _gtk_thread():
            GLib.idle_add(_create_icon)
            Gtk.main()

        threading.Thread(target=_gtk_thread, daemon=True).start()
        return
    except (ImportError, ValueError):
        pass
    except Exception as e:
        print(f"[tray] XApp failed: {e}")


    # pystray as fallback
    try:
        import pystray
        icon_to_use = TRAY_ICON_PATH if os.path.exists(TRAY_ICON_PATH) else ICON_PATH
        if os.path.exists(icon_to_use):
            image = Image.open(icon_to_use).convert("RGBA")
            image = image.resize((22, 22), Image.Resampling.LANCZOS)
        else:
            image = Image.new('RGBA', (22, 22), color=(0, 0, 0, 0))

        def on_exit(icon, item):
            icon.stop()
            app.after(0, app.quit_app)

        menu = pystray.Menu(
            pystray.MenuItem('Open', lambda i, it: app.after(0, app.show_window), default=True),
            pystray.MenuItem('Exit', on_exit)
        )
        ic = pystray.Icon("xwallpaper-gui", image, "xwallpaper gui", menu)
        threading.Thread(target=ic.run, daemon=True).start()
    except ImportError:
        print("[tray] No tray backend found, install pystray or python3-gi")