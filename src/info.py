import os

NAME = "xwallpaper-gui"
VERSION = "public preview"
DESCRIPTION = "GUI frontend for xwallpaper — wallpaper manager for multi-monitor X11 setups."
AUTHOR = "Pawel Jelonek"
URL = "https://github.com/paweljelonek/xwallpaper-gui"
XWALLPAPER_URL = "https://github.com/stoeckmann/xwallpaper"
LICENSE = "MIT"

LICENSE_PATH = os.path.join(os.path.dirname(__file__), "..", "LICENSE")
if os.path.exists(LICENSE_PATH):
    with open(LICENSE_PATH, "r", encoding="utf-8") as f:
        LICENSE_TEXT = f.read()
else:
    LICENSE_TEXT = "MIT License"