import os
import sys
import json
import socket
import threading
import tkinter as tk
from tkinter import filedialog, ttk
import webbrowser
from PIL import Image, ImageTk

import xrandr
import info

CONFIG_PATH = os.path.expanduser("~/.config/xwallpaper-gui/config.json")
AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")
DESKTOP_FILE = os.path.join(AUTOSTART_DIR, "xwallpaper-gui.desktop")

def is_autostart_enabled():
    return os.path.exists(DESKTOP_FILE)

def toggle_autostart(enable):
    if enable:
        os.makedirs(AUTOSTART_DIR, exist_ok=True)
        main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
        exec_cmd = f"{sys.executable} {main_py} --startup"
        content = f"[Desktop Entry]\nType=Application\nName=xwallpaper gui\nComment=Wallpaper Manager\nExec={exec_cmd}\nTerminal=false\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\n"
        with open(DESKTOP_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        os.chmod(DESKTOP_FILE, 0o755)
    else:
        if os.path.exists(DESKTOP_FILE):
            os.remove(DESKTOP_FILE)

SOCKET_PATH = os.path.expanduser("~/.config/xwallpaper-gui/app.sock")

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
                    app.after(0, app.show_window)
                conn.close()
            except Exception:
                pass
    t = threading.Thread(target=listen, daemon=True)
    t.start()

class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"xwallpaper gui ({info.VERSION})")
        self.geometry("950x700")
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        self.saved_config = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.saved_config = json.load(f)
            except Exception:
                pass
                
        self.last_directory = self.saved_config.get("_last_directory", os.path.expanduser("~"))

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.icon_image = ImageTk.PhotoImage(Image.open(icon_path))
            self.wm_iconphoto(True, self.icon_image)

        self.monitor_rows = {}
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        
        self._setup_ui()
        self._load_monitors()

    def _setup_ui(self):
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Close Application", command=self.quit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)

        prefs_menu = tk.Menu(menu_bar, tearoff=0)
        prefs_menu.add_checkbutton(label="Run on System Startup", variable=self.autostart_var, command=lambda: toggle_autostart(self.autostart_var.get()))
        menu_bar.add_cascade(label="Preferences", menu=prefs_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

        tk.Label(self, text="Wallpaper Configuration", font=("Helvetica", 16, "bold")).pack(pady=10)
        self.monitors_frame = tk.Frame(self)
        self.monitors_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(self, text="Apply", command=self._apply_wallpapers, font=("Helvetica", 12)).pack(pady=10)

    def _load_monitors(self):
        try:
            monitors = xrandr.get_monitors()
        except Exception as e:
            print(f"Error loading monitors: {e}")
            return
        
        for monitor in monitors:
            m_name = monitor["name"]
            row_frame = tk.Frame(self.monitors_frame, pady=5)
            row_frame.pack(fill=tk.X)

            disp_text = f"Display: {m_name}\n{monitor['resolution']}"
            tk.Label(row_frame, text=disp_text, width=20, anchor="w", justify="left").pack(side=tk.LEFT)

            saved = self.saved_config.get(m_name, {})
            def_path = saved.get("image_path", "")
            def_style = saved.get("style", "stretch")

            path_var = tk.StringVar(value=def_path)

            tk.Entry(row_frame, textvariable=path_var, width=30).pack(side=tk.LEFT, padx=5)
            tk.Button(row_frame, text="Browse Image", command=lambda v=path_var: self._browse_image(v)).pack(side=tk.LEFT, padx=5)

            style_var = tk.StringVar(value=def_style)
            ttk.Combobox(row_frame, textvariable=style_var, values=["stretch", "zoom", "center", "tile", "max"], state="readonly", width=10).pack(side=tk.LEFT, padx=5)

            preview_frame = tk.Frame(row_frame, width=256, height=144, bg="lightgray", highlightbackground="gray", highlightcolor="gray", highlightthickness=1)
            preview_frame.pack_propagate(False)

            preview_lbl = tk.Label(preview_frame, text="No Preview", bg="lightgray")
            preview_lbl.pack(expand=True, fill=tk.BOTH)

            def clear_row(pv=path_var, lbl=preview_lbl):
                pv.set("")
                lbl.config(image="", text="No Preview")
                lbl.image = None

            tk.Button(row_frame, text="Clear", command=clear_row).pack(side=tk.LEFT, padx=5)
            preview_frame.pack(side=tk.LEFT, padx=10)

            self.monitor_rows[m_name] = {"path_var": path_var, "style_var": style_var, "preview_lbl": preview_lbl}

            def update_preview(var=path_var, lbl=preview_lbl):
                p = var.get()
                if os.path.exists(p) and os.path.isfile(p):
                    try:
                        img = Image.open(p)
                        img.thumbnail((256, 144), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        lbl.config(image=photo, text="")
                        lbl.image = photo
                    except Exception:
                        lbl.config(image="", text="Error")
                else:
                    lbl.config(image="", text="No Preview")

            path_var.trace_add("write", lambda *args, f=update_preview: f())
            update_preview()

    def _browse_image(self, path_var):
        filepath = filedialog.askopenfilename(title="Select wallpaper", initialdir=self.last_directory, filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")])
        if filepath:
            path_var.set(filepath)
            self.last_directory = os.path.dirname(filepath)

    def _apply_wallpapers(self):
        configs = []
        config_to_save = {"_last_directory": self.last_directory}
        
        for m_name, widgets in self.monitor_rows.items():
            path = widgets["path_var"].get()
            style = widgets["style_var"].get()
            config_to_save[m_name] = {"image_path": path, "style": style}
            if path:
                configs.append({"monitor": m_name, "image_path": path, "style": style})

        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=4)

        if configs:
            try:
                xrandr.apply_wallpapers(configs)
                print("Wallpapers applied.")
            except Exception as e:
                print(f"Error applying wallpapers: {e}")

    def hide_window(self):
        self.withdraw()

    def show_window(self):
        self.deiconify()
        self.lift()
        self.attributes('-topmost', 1)
        self.attributes('-topmost', 0)

    def _show_about(self):
        win = tk.Toplevel(self)
        win.title("About")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text=f"{info.NAME} ({info.VERSION})", font=("Helvetica", 13, "bold")).pack(padx=20, pady=(16, 4))
        tk.Label(win, text=info.DESCRIPTION, wraplength=320, justify="center").pack(padx=20)

        xwp_label = tk.Label(win, text=info.XWALLPAPER_URL, fg="blue", cursor="hand2", font=("Helvetica", 9, "underline"))
        xwp_label.pack(padx=20)
        xwp_label.bind("<Button-1>", lambda e: webbrowser.open(info.XWALLPAPER_URL))

        tk.Label(win, text=f"Author: {info.AUTHOR}").pack(padx=20, pady=(8, 0))
        url_label = tk.Label(win, text=info.URL, fg="blue", cursor="hand2", font=("Helvetica", 9, "underline"))
        url_label.pack(padx=20)
        url_label.bind("<Button-1>", lambda e: webbrowser.open(info.URL))
        tk.Label(win, text=f"License: {info.LICENSE}").pack(padx=20, pady=(4, 0))
        tk.Button(win, text="OK", width=8, command=win.destroy).pack(pady=12)

    def quit_app(self):
        self.destroy()

