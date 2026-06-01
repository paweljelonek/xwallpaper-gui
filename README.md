# xwallpaper-gui 🖼️

A modern, lightweight Python GUI for [xwallpaper](https://github.com/stoeckmann/xwallpaper). Easily manage different wallpapers across multiple monitors with persistence and system tray support.

## 📖 About

This project was created due to the lack of a simple tool for setting different wallpapers across multiple monitors. I use **Linux Mint 21.3 Cinnamon**, and none of the previously available solutions worked correctly on this specific distribution. The only effective tool turned out to be [xwallpaper](https://github.com/stoeckmann/xwallpaper), which is a command-line utility.

While changing wallpapers via the terminal is fast, it has its downsides. That is why I decided to create a graphical user interface (GUI) for this excellent tool.

### ✨ Features
- **Native GTK3 Interface**: Beautiful, fast, and fully integrated with your desktop theme.
- **Multi-Monitor Support**: Automatically detects all connected displays via XRandR.
- **Per-Monitor Styling**: Set individual wallpapers with different scaling modes (stretch, zoom, center, tile, max).
- **Live Preview**: See a thumbnail of your wallpaper before applying.
- **System Tray Integration**: Runs quietly in the background using a pure GTK3 native tray icon.
- **Persistence**: Remembers your wallpaper paths and settings between reboots.
- **Autostart**: Built-in option to launch minimized to tray when your system starts, with a separate toggle to automatically apply your saved wallpapers on startup.
- **Single Instance**: Prevents multiple windows; clicking the tray or launching again brings the existing window to focus.

## 🚀 Installation

### 1. System Dependencies

You need `xwallpaper` itself and the Python GObject introspection libraries for the GTK3 interface. There are **no pip dependencies** — everything is provided by system packages.

```bash
sudo apt update
sudo apt install xwallpaper python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gdkpixbuf-2.0
```

### 2. Clone the repository

```bash
git clone https://github.com/paweljelonek/xwallpaper-gui
# or via SSH:
git clone git@github.com:paweljelonek/xwallpaper-gui.git
cd xwallpaper-gui
```

#### Virtual Environment

If you use a `venv` or `pyenv`, you must link the system `gi` package so Python can find the GTK3 libraries:

```bash
python3 -m venv venv
source venv/bin/activate
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
Created with ❤️ for the Linux Mint community.