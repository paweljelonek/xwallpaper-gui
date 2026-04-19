import unittest
from unittest.mock import patch
import src.xrandr as xrandr

class TestXwallpaper(unittest.TestCase):
    @patch('subprocess.check_output')
    def test_get_monitors(self, mock_subp):
        mock_subp.return_value = "Screen 0: minimum 320 x 200, current 1920 x 1080, maximum 16384 x 16384\n" \
                                 "eDP-1 connected primary 1920x1080+0+0\n" \
                                 "DP-1 disconnected\n" \
                                 "HDMI-1 connected 1920x1080+1920+0\n"
        
        monitors = xrandr.get_monitors()
        self.assertEqual(len(monitors), 2)
        self.assertEqual(monitors[0]["name"], "eDP-1")
        self.assertEqual(monitors[0]["resolution"], "1920x1080")
        self.assertEqual(monitors[1]["name"], "HDMI-1")
        self.assertEqual(monitors[1]["resolution"], "1920x1080")

    def test_build_command(self):
        configs = [
            {"monitor": "HDMI-1", "image_path": "img1.jpg", "style": "zoom"},
            {"monitor": "eDP-1", "image_path": "img2.png", "style": "center"}
        ]
        
        cmd = xrandr.build_xwallpaper_command(configs)
        self.assertEqual(cmd, [
            "xwallpaper", 
            "--output", "HDMI-1", "--zoom", "img1.jpg",
            "--output", "eDP-1", "--center", "img2.png"
        ])

    def test_build_command_empty(self):
        self.assertEqual(xrandr.build_xwallpaper_command([]), [])

    @patch('subprocess.check_output')
    def test_get_monitors_none_connected(self, mock_subp):
        mock_subp.return_value = "Screen 0: minimum 320 x 200, current 0 x 0, maximum 16384 x 16384\n" \
                                 "DP-1 disconnected\n" \
                                 "HDMI-1 disconnected\n"
        self.assertEqual(xrandr.get_monitors(), [])

    @patch('subprocess.run')
    def test_apply_wallpapers(self, mock_run):
        configs = [{"monitor": "eDP-1", "image_path": "bg.png", "style": "zoom"}]
        xrandr.apply_wallpapers(configs)
        mock_run.assert_called_once_with(
            ["xwallpaper", "--output", "eDP-1", "--zoom", "bg.png"],
            check=True
        )

if __name__ == "__main__":
    unittest.main()
