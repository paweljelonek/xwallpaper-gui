# xwallpaper-gui 🖼️

A modern, lightweight Python GUI for [xwallpaper](https://github.com/stoeckmann/xwallpaper). Easily manage different wallpapers across multiple monitors with persistence and system tray support.

## 📖 About

This project was created due to the lack of a simple tool for setting different wallpapers across multiple monitors. I use **Linux Mint 21.3 Cinnamon**, and none of the previously available solutions worked correctly on this specific distribution. The only effective tool turned out to be [xwallpaper](https://github.com/stoeckmann/xwallpaper), which is a command-line utility.

While changing wallpapers via the terminal is fast, it has its downsides. That is why I decided to create a graphical user interface (GUI) for this excellent tool.


- **Multi-Monitor Support**: Automatically detects all connected displays via XRandR.
- **Per-Monitor Styling**: Set individual wallpapers with different scaling modes (stretch, zoom, center, tile, max).
- **Live Preview**: See a thumbnail of your wallpaper before applying.
- **System Tray Integration**: Runs in the background with an XApp-compatible tray icon (native on Cinnamon/Linux Mint).
- **Persistence**: Remembers your wallpaper paths and settings between reboots.
- **Autostart**: Built-in option to launch minimized to tray when your system starts.
- **Single Instance**: Prevents multiple windows; clicking the tray or launching again brings the existing window to focus.

## 🚀 Installation

### 1. System Dependencies

You need `xwallpaper` itself and the Python GObject introspection libraries for the tray icon.

```bash
sudo apt update
sudo apt install xwallpaper python3-tk python3-gi gir1.2-xapp-1.0
```

### 2. Python Environment

```bash
git clone https://github.com/paweljelonek/xwallpaper-gui
# or via SSH:
git clone git@github.com:paweljelonek/xwallpaper-gui.git
cd xwallpaper-gui
pip install -r requirements.txt
```

#### Virtual Environment

If you use a `venv`, link the system `gi` package so Python can find it:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "/usr/lib/python3/dist-packages" > "$(python -c 'import site; print(site.getsitepackages()[0])')/system-gi.pth"
```

## 🛠 Usage

Run the application:
```bash
python main.py
```

### Command Line Arguments
- `--startup`: Starts the application minimized to the system tray. This is used by the autostart feature.

### Configuration
Settings are stored in `~/.config/xwallpaper-gui/config.json`.

## 🗺️ Roadmap

- [ ] Support for all Linux Mint desktop environments (MATE, XFCE).
- [ ] Ubuntu/Gnome specific optimizations.
- [ ] Flatpak/Snap packaging for easier installation.
- [ ] Drag-and-drop support for images.

## 🤝 Contributing

Contributions are welcome! If you have ideas for improvements or find a bug:
1. Open an Issue to discuss the change.
2. Fork the repo and submit a Pull Request.

## 📄 License

ISC

Copyright (c) 2026 Pawel Jelonek (pawel dot jelonek at gmail dot com)

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

---
Created with ❤️ for the Linux Mint community.