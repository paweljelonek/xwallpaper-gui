import re
import subprocess

def get_monitors():
    monitors = []
    output = subprocess.check_output(["xrandr"], text=True)
    for line in output.splitlines():
        if " connected" in line:
            parts = line.split()
            if parts:
                name = parts[0]
                resolution = ""
                for part in parts[1:]:
                    match = re.search(r'^(\d+x\d+)', part)
                    if match:
                        resolution = match.group(1)
                        break
                monitors.append({"name": name, "resolution": resolution})
    return monitors

def build_xwallpaper_command(configs):
    if not configs:
        return []
    command = ["xwallpaper"]
    for config in configs:
        command.extend(["--output", config["monitor"]])
        command.extend([f"--{config['style']}", config["image_path"]])
    return command

def apply_wallpapers(configs):
    cmd = build_xwallpaper_command(configs)
    if cmd:
        subprocess.run(cmd, check=True)
