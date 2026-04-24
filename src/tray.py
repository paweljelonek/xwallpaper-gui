import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
TRAY_SVG_PATH = os.path.join(os.path.dirname(__file__), "assets", "tray_icon.svg")

# Przechowujemy referencje na poziomie modułu by GC nie usunął ikony i menu
_tray_icon = None
_tray_menu = None


def start_tray(app):
    global _tray_icon, _tray_menu

    # Menu pod prawym przyciskiem myszy
    _tray_menu = Gtk.Menu()

    item_open = Gtk.MenuItem(label="Open")
    item_open.connect("activate", lambda w: app.show_window())
    _tray_menu.append(item_open)

    item_about = Gtk.MenuItem(label="About")
    item_about.connect("activate", lambda w: app._show_about())
    _tray_menu.append(item_about)

    _tray_menu.append(Gtk.SeparatorMenuItem())

    item_exit = Gtk.MenuItem(label="Exit")
    item_exit.connect("activate", lambda w: app.quit_app())
    _tray_menu.append(item_exit)

    _tray_menu.show_all()

    # Wybór ikony (najpierw SVG, potem główna ikona aplikacji)
    if os.path.exists(TRAY_SVG_PATH):
        icon_to_use = TRAY_SVG_PATH
    elif os.path.exists(ICON_PATH):
        icon_to_use = ICON_PATH
    else:
        icon_to_use = "preferences-desktop-wallpaper"

    # Tworzenie standardowej ikony zasobnika z GTK3 (Gtk.StatusIcon)
    _tray_icon = Gtk.StatusIcon()
    
    if icon_to_use.endswith(".svg") or icon_to_use.endswith(".png"):
        _tray_icon.set_from_file(icon_to_use)
    else:
        _tray_icon.set_from_icon_name(icon_to_use)

    _tray_icon.set_tooltip_text("xwallpaper gui")
    _tray_icon.set_visible(True)

    # Obsługa zdarzeń
    _tray_icon.connect("activate", lambda icon: app.show_window())
    
    def on_right_click(icon, button, time):
        _tray_menu.popup(None, None, Gtk.StatusIcon.position_menu, icon, button, time)
        
    _tray_icon.connect("popup-menu", on_right_click)

    print("[tray] Uruchomiono czysty Gtk.StatusIcon")