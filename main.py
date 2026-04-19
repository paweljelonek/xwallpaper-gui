import os
import sys
from pathlib import Path

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
                "style": data.get("style", "stretch")
            })

    if configs:
        xrandr.apply_wallpapers(configs)


def main():
    server = ensure_single_instance()

    app = AppWindow()
    setup_ipc_server(server, app)

    if "--startup" in sys.argv:
        app.withdraw()

        app.after(3000, lambda: apply_saved_wallpapers(app))

    start_tray(app)
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Błąd: {e}")
        sys.exit(1)
