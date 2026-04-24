import os

NAME = "xwallpaper-gui"
VERSION = "public preview"
DESCRIPTION = (
    "A modern, lightweight graphical user interface designed for seamlessly "
    "managing wallpapers across multiple displays in X11 desktop environments.\n"
    "It provides a user-friendly way to configure individual screens, scaling modes, "
    "and autostart behaviors.\n\n"
    "────────────────────────────────────────────────────────\n\n"
    "This application serves as a frontend overlay for the fantastic command-line "
    "utility 'xwallpaper' developed by Tobias Stoeckmann. Without the core backend, "
    "this GUI would not be possible."
)
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