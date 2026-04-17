import sys
import os

# ─────────────────────────────────────────────────────────────────────────────
# CRITICAL FIX #1 — Set KIVY_CAMERA env var BEFORE any kivy/kivymd import.
# android.meta_data in buildozer.spec writes to AndroidManifest.xml (Java layer)
# and is NOT read by Python/Kivy. The env var must be set here in Python.
# Without this, Kivy picks the default 'opencv' provider on Android,
# which fails silently because OpenCV uses V4L2 (Linux-only, not Android).
# ─────────────────────────────────────────────────────────────────────────────
_IS_ANDROID = "ANDROID_ARGUMENT" in os.environ or os.path.exists("/sdcard")
if _IS_ANDROID:
    os.environ["KIVY_CAMERA"] = "android"
    print("[Boot] KIVY_CAMERA set to 'android'")

# ─────────────────────────────────────────────────────────────────────────────

from kivy.config import Config

# -- VERSION CONTROL --
# Increment this whenever you update your Excel files or Database
APP_VERSION = "1.2"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Fixed Window size for consistent mobile-like preview
Config.set('graphics', 'width',     '420')
Config.set('graphics', 'height',    '750')
Config.set('graphics', 'resizable', '0')


def _get_writable_dir():
    """Returns the Android app-specific storage path or local dir for Desktop."""
    try:
        from android.storage import app_storage_path
        d = app_storage_path()
        os.makedirs(d, exist_ok=True)
        return d
    except Exception:
        return ROOT_DIR


def _bootstrap_android_files():
    """Forces an update of local assets if the version has changed."""
    try:
        import shutil
        writable = _get_writable_dir()
        ver_path = os.path.join(writable, "version.txt")

        current_ver = ""
        if os.path.exists(ver_path):
            with open(ver_path, "r") as f:
                current_ver = f.read().strip()

        # If version is new or missing, overwrite writable data
        force_update = current_ver != APP_VERSION

        # Assets to sync
        asset_files = ["campus.db", "Smart_Campus_Chatbot_QA_Extended.csv", "form1.pdf"]
        for fname in asset_files:
            dst = os.path.join(writable, fname)
            if force_update or not os.path.isfile(dst):
                src = os.path.join(ROOT_DIR, fname)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)

        # Sync Data Folder (Excel files)
        dst_data = os.path.join(writable, "data")
        if force_update or not os.path.isdir(dst_data):
            src_data = os.path.join(ROOT_DIR, "data")
            if os.path.isdir(src_data):
                if os.path.exists(dst_data):
                    shutil.rmtree(dst_data)
                shutil.copytree(src_data, dst_data)

        with open(ver_path, "w") as f:
            f.write(APP_VERSION)
    except Exception as e:
        print(f"[Boot] Error: {e}")


_bootstrap_android_files()

from kivymd.app import MDApp
from router import AppRouter


class SmartCampusApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        return AppRouter()


if __name__ == "__main__":
    SmartCampusApp().run()
