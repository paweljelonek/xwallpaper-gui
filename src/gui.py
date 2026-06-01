import os
import sys
import json
import socket
import threading
import webbrowser

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GLib, GdkPixbuf

import xrandr
import info

CONFIG_PATH = os.path.expanduser("~/.config/xwallpaper-gui/config.json")
AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")
DESKTOP_FILE = os.path.join(AUTOSTART_DIR, "xwallpaper-gui.desktop")
SOCKET_PATH = os.path.expanduser("~/.config/xwallpaper-gui/app.sock")


def is_autostart_enabled():
    return os.path.exists(DESKTOP_FILE)


def toggle_autostart(enable):
    if enable:
        os.makedirs(AUTOSTART_DIR, exist_ok=True)
        main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        exec_cmd = f"{sys.executable} {main_py} --startup"
        content = (
            "[Desktop Entry]\nType=Application\nName=xwallpaper gui\n"
            "Comment=Wallpaper Manager\nExec={}\nTerminal=false\n"
            "Hidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\n"
        ).format(exec_cmd)
        with open(DESKTOP_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(DESKTOP_FILE, 0o644)
    else:
        if os.path.exists(DESKTOP_FILE):
            os.remove(DESKTOP_FILE)


def ensure_single_instance():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    if os.path.exists(SOCKET_PATH):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(SOCKET_PATH)
            try:
                client.sendall(b"show")
                client.close()
                print("Another instance is running. Waking it up and exiting.")
                sys.exit(0)
            except OSError:
                client.close()
        except socket.error:
            pass
        try:
            os.remove(SOCKET_PATH)
        except OSError:
            pass

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)
    return server


def setup_ipc_server(server, app):
    def listen():
        while True:
            try:
                conn, _ = server.accept()
                data = conn.recv(1024)
                if data == b"show":
                    GLib.idle_add(app.show_window)
                conn.close()
            except Exception:
                pass

    threading.Thread(target=listen, daemon=True).start()


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, gtk_app):
        super().__init__(application=gtk_app, title=f"xwallpaper gui ({info.VERSION})")
        self.set_default_size(950, 700)
        self.connect("delete-event", self._on_delete)

        self.saved_config = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.saved_config = json.load(f)
            except Exception:
                pass

        self.last_directory = self.saved_config.get("_last_directory", os.path.expanduser("~"))

        # Window icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            try:
                # Menedżery okien często odrzucają duże obrazki (600x600).
                # Skalujemy bezpiecznie do 128x128 przez GdkPixbuf.
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 128, 128, True)
                self.set_icon(pb)
                Gtk.Window.set_default_icon_list([pb])
            except Exception as e:
                print(f"Failed to load window icon: {e}")

        self.monitor_rows = {}
        self._setup_ui()
        self._load_monitors()
        self.show_all()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _setup_ui(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # ---- Menu bar ----
        menubar = Gtk.MenuBar()

        file_item = Gtk.MenuItem(label="File")
        file_menu = Gtk.Menu()
        quit_item = Gtk.MenuItem(label="Close Application")
        quit_item.connect("activate", lambda w: self.quit_app())
        file_menu.append(quit_item)
        file_item.set_submenu(file_menu)
        menubar.append(file_item)

        prefs_item = Gtk.MenuItem(label="Preferences")
        prefs_menu = Gtk.Menu()

        self._autostart_item = Gtk.CheckMenuItem(label="Run on System Startup")
        self._autostart_item.set_active(is_autostart_enabled())
        self._autostart_item.connect("toggled", self._on_autostart_toggled)
        prefs_menu.append(self._autostart_item)

        self._apply_on_startup_item = Gtk.CheckMenuItem(label="Apply wallpapers on startup")
        self._apply_on_startup_item.set_active(self.saved_config.get("_apply_on_startup", True))
        self._apply_on_startup_item.set_sensitive(is_autostart_enabled())
        self._apply_on_startup_item.connect("toggled", self._on_apply_on_startup_toggled)
        prefs_menu.append(self._apply_on_startup_item)

        prefs_item.set_submenu(prefs_menu)
        menubar.append(prefs_item)

        help_item = Gtk.MenuItem(label="Help")
        help_menu = Gtk.Menu()
        about_item = Gtk.MenuItem(label="About")
        about_item.connect("activate", lambda w: self._show_about())
        help_menu.append(about_item)
        help_item.set_submenu(help_menu)
        menubar.append(help_item)

        vbox.pack_start(menubar, False, False, 0)

        # ---- Title ----
        title_label = Gtk.Label()
        title_label.set_markup("<span font='16' weight='bold'>Wallpaper Configuration</span>")
        title_label.set_margin_top(10)
        title_label.set_margin_bottom(6)
        vbox.pack_start(title_label, False, False, 0)

        # ---- Scrollable monitor area ----
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_margin_start(10)
        scroll.set_margin_end(10)
        scroll.set_margin_bottom(6)

        self.monitors_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scroll.add(self.monitors_box)
        vbox.pack_start(scroll, True, True, 0)

        # ---- Action buttons ----
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        action_box.set_halign(Gtk.Align.CENTER)
        action_box.set_margin_top(10)
        action_box.set_margin_bottom(16)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.set_size_request(120, 36)
        cancel_btn.connect("clicked", lambda w: self.hide_window())
        action_box.pack_start(cancel_btn, False, False, 0)

        apply_btn = Gtk.Button(label="Apply")
        apply_btn.set_size_request(120, 36)
        apply_btn.get_style_context().add_class("suggested-action")
        apply_btn.connect("clicked", lambda w: self._apply_wallpapers())
        action_box.pack_start(apply_btn, False, False, 0)

        vbox.pack_start(action_box, False, False, 0)

    # ------------------------------------------------------------------
    # Monitor rows
    # ------------------------------------------------------------------

    def _load_monitors(self):
        try:
            monitors = xrandr.get_monitors()
        except Exception as e:
            print(f"Error loading monitors: {e}")
            return

        for monitor in monitors:
            m_name = monitor["name"]
            saved = self.saved_config.get(m_name, {})
            def_path = saved.get("image_path", "")
            def_style = saved.get("style", "stretch")

            # Outer frame for visual grouping
            frame = Gtk.Frame()
            frame.set_margin_bottom(4)

            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row.set_margin_start(8)
            row.set_margin_end(8)
            row.set_margin_top(6)
            row.set_margin_bottom(6)
            frame.add(row)

            # Monitor label (name + resolution)
            lbl = Gtk.Label()
            lbl.set_markup(f"<b>{m_name}</b>\n{monitor['resolution']}")
            lbl.set_xalign(0.0)
            lbl.set_valign(Gtk.Align.CENTER)
            lbl.set_width_chars(20)
            row.pack_start(lbl, False, False, 0)

            # Path entry
            path_entry = Gtk.Entry()
            path_entry.set_text(def_path)
            path_entry.set_placeholder_text("Select image…")
            path_entry.set_valign(Gtk.Align.CENTER)
            row.pack_start(path_entry, True, True, 0)

            # Browse button
            browse_btn = Gtk.Button(label="Browse Image")
            browse_btn.set_valign(Gtk.Align.CENTER)
            browse_btn.connect("clicked", lambda _w, e=path_entry: self._browse_image(e))
            row.pack_start(browse_btn, False, False, 0)

            # Style combobox
            styles = ["stretch", "zoom", "center", "tile", "max"]
            style_combo = Gtk.ComboBoxText()
            style_combo.set_valign(Gtk.Align.CENTER)
            for s in styles:
                style_combo.append_text(s)
            style_combo.set_active(styles.index(def_style) if def_style in styles else 0)
            row.pack_start(style_combo, False, False, 0)

            # Clear button
            clear_btn = Gtk.Button(label="Clear")
            clear_btn.set_valign(Gtk.Align.CENTER)
            row.pack_start(clear_btn, False, False, 0)

            # Preview (fixed size box)
            preview_frame = Gtk.Frame()
            preview_frame.set_size_request(256, 144)
            preview_image = Gtk.Image()
            preview_image.set_size_request(256, 144)
            preview_frame.add(preview_image)
            row.pack_start(preview_frame, False, False, 0)

            # Wire up preview update
            def _update_preview(entry, img):
                p = entry.get_text()
                if p and os.path.isfile(p):
                    try:
                        pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(p, 256, 144, True)
                        img.set_from_pixbuf(pb)
                    except Exception:
                        img.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
                else:
                    img.clear()

            path_entry.connect("changed", lambda e, img=preview_image: _update_preview(e, img))

            def _clear(_w, e=path_entry, img=preview_image):
                e.set_text("")
                img.clear()

            clear_btn.connect("clicked", _clear)
            _update_preview(path_entry, preview_image)

            self.monitors_box.pack_start(frame, False, False, 0)
            self.monitor_rows[m_name] = {
                "path_entry": path_entry,
                "style_combo": style_combo,
                "styles": styles,
            }

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_autostart_toggled(self, widget):
        enabled = widget.get_active()
        toggle_autostart(enabled)
        self._apply_on_startup_item.set_sensitive(enabled)

    def _on_apply_on_startup_toggled(self, widget):
        self.saved_config["_apply_on_startup"] = widget.get_active()
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.saved_config, f, indent=4)

    def _browse_image(self, path_entry):
        dialog = Gtk.FileChooserDialog(
            title="Select wallpaper",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )
        dialog.set_current_folder(self.last_directory)

        img_filter = Gtk.FileFilter()
        img_filter.set_name("Image files")
        for pat in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif"]:
            img_filter.add_pattern(pat)
        dialog.add_filter(img_filter)

        all_filter = Gtk.FileFilter()
        all_filter.set_name("All files")
        all_filter.add_pattern("*")
        dialog.add_filter(all_filter)

        if dialog.run() == Gtk.ResponseType.OK:
            path_entry.set_text(dialog.get_filename())
            self.last_directory = os.path.dirname(dialog.get_filename())
        dialog.destroy()

    def _apply_wallpapers(self):
        configs = []
        config_to_save = {
            "_last_directory": self.last_directory,
            "_apply_on_startup": self._apply_on_startup_item.get_active(),
        }

        for m_name, widgets in self.monitor_rows.items():
            path = widgets["path_entry"].get_text()
            idx = widgets["style_combo"].get_active()
            style = widgets["styles"][idx] if 0 <= idx < len(widgets["styles"]) else "stretch"
            config_to_save[m_name] = {"image_path": path, "style": style}
            if path:
                configs.append({"monitor": m_name, "image_path": path, "style": style})

        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=4)
        self.saved_config = config_to_save

        if configs:
            try:
                xrandr.apply_wallpapers(configs)
                print("Wallpapers applied.")
            except Exception as e:
                print(f"Error applying wallpapers: {e}")

    # ------------------------------------------------------------------
    # Window management
    # ------------------------------------------------------------------

    def _on_delete(self, _window, _event):
        self.hide_window()
        return True  # Block destruction — just hide

    def hide_window(self):
        self.hide()

    def show_window(self):
        self.present()

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------

    def _show_about(self):
        dialog = Gtk.Dialog(title="About", transient_for=self, modal=True)
        dialog.set_default_size(500, -1)
        dialog.set_border_width(10)
        
        vbox = dialog.get_content_area()
        vbox.set_spacing(10)

        # Logo
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 64, 64, True)
                img = Gtk.Image.new_from_pixbuf(pb)
                vbox.pack_start(img, False, False, 10)
            except Exception:
                pass

        # Tytuł
        title_label = Gtk.Label()
        title_label.set_markup(f"<span font='16' weight='bold'>{info.NAME}</span>\n<span font='10'>{info.VERSION}</span>")
        title_label.set_justify(Gtk.Justification.CENTER)
        vbox.pack_start(title_label, False, False, 0)
        
        # Copyright
        copyright_label = Gtk.Label(label=f"© 2026 {info.AUTHOR}")
        vbox.pack_start(copyright_label, False, False, 0)

        # Treść główna (wyśrodkowana)
        markup = (
            f"A modern, lightweight graphical user interface designed for seamlessly "
            f"managing wallpapers across multiple displays in X11 desktop environments. "
            f"It provides a user-friendly way to configure individual screens, scaling modes, "
            f"and autostart behaviors. The application runs smoothly in the background with a "
            f"dedicated system tray icon, ensuring quick access and minimal resource usage.\n\n"
            f"<a href='{info.URL}'>{info.URL}</a>\n\n"
            f"────────────────────────────────────────\n\n"
            f"This application serves as a frontend overlay for the excellent command-line tool 'xwallpaper'.\n"
            f"Without this core backend, this GUI would not be possible.\n"
            f"<a href='{info.XWALLPAPER_URL}'>{info.XWALLPAPER_URL}</a>"
        )
        
        custom_label = Gtk.Label()
        custom_label.set_markup(markup)
        custom_label.set_justify(Gtk.Justification.CENTER)
        custom_label.set_line_wrap(True)
        custom_label.set_max_width_chars(65)
        vbox.pack_start(custom_label, False, False, 10)
        
        # Przyciski
        dialog.add_button("License", 1)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)

        vbox.show_all()
        
        while True:
            response = dialog.run()
            if response == 1:
                # Pokazanie licencji w czystym okienku z suwakiem (bez dziwnego wysuwania GTK)
                lic_dialog = Gtk.Dialog(title="MIT License", transient_for=dialog, modal=True)
                lic_dialog.set_default_size(550, 450)
                
                lic_scroll = Gtk.ScrolledWindow()
                lic_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
                
                lic_label = Gtk.Label(label=info.LICENSE_TEXT)
                lic_label.set_margin_start(15)
                lic_label.set_margin_end(15)
                lic_label.set_margin_top(15)
                lic_label.set_margin_bottom(15)
                lic_label.set_xalign(0.0)
                
                lic_scroll.add(lic_label)
                lic_dialog.get_content_area().pack_start(lic_scroll, True, True, 0)
                lic_dialog.add_button("Close", Gtk.ResponseType.CLOSE)
                lic_dialog.show_all()
                lic_dialog.run()
                lic_dialog.destroy()
            else:
                break
                
        dialog.destroy()

    # ------------------------------------------------------------------
    # Quit
    # ------------------------------------------------------------------

    def quit_app(self):
        gtk_app = self.get_application()
        if gtk_app:
            gtk_app.release()   # balance the hold() from do_activate
            gtk_app.quit()
        else:
            Gtk.main_quit()
