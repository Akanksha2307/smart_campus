[app]

# ─── App Identity ───────────────────────────────────────────────────────────
title = SmartCampus
package.name = smartcampus
package.domain = org.college

# ─── Source ─────────────────────────────────────────────────────────────────
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xlsx,json,ttf,otf

# Include the College_Db.xlsx data file in the APK assets
source.include_patterns = assets/*,data/*,*.xlsx,*.json

version = 1.0

# ─── Entry Point ────────────────────────────────────────────────────────────
entrypoint = main.py

# ─── Python Requirements ────────────────────────────────────────────────────
# CRITICAL NOTES:
# 1. Do NOT include opencv-python here — it does NOT work on Android.
#    The cv2 camera (VideoCapture) requires V4L2 which Android does not expose.
#    The code handles ImportError gracefully (CV2_AVAILABLE = False).
#
# 2. kivy includes the Camera widget which uses Android Camera2 API — this IS
#    the correct camera provider for Android.
#
# 3. openpyxl is included for reading College_Db.xlsx.
#
# 4. kivymd must match your KivyMD version (check: pip show kivymd).
requirements =
    python3,
    kivy==2.3.0,
    kivymd==1.2.0,
    openpyxl,
    Pillow,
    plyer,
    requests,
    certifi

# ─── Presplash & Icon ───────────────────────────────────────────────────────
#presplash.filename = %(source.dir)s/assets/presplash.png
#icon.filename = %(source.dir)s/assets/icon.png

# ─── Android Permissions ────────────────────────────────────────────────────
# ANDROID 15 (API 35) REQUIRED PERMISSIONS:
# • CAMERA              — for camera hardware access via Camera2 API
# • ACCESS_FINE_LOCATION — GPS positioning for AR navigation
# • ACCESS_COARSE_LOCATION — network-based location fallback
# • INTERNET            — for any network features
# • READ_EXTERNAL_STORAGE — for reading Excel file (pre-API 33 devices)
# • READ_MEDIA_IMAGES   — replaces READ_EXTERNAL_STORAGE on API 33+
# • WRITE_EXTERNAL_STORAGE — for saving route logs (if needed)
# • VIBRATE             — for haptic feedback on arrival
android.permissions =
    CAMERA,
    ACCESS_FINE_LOCATION,
    ACCESS_COARSE_LOCATION,
    INTERNET,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE,
    READ_MEDIA_IMAGES,
    VIBRATE

# ─── Android API Versions ───────────────────────────────────────────────────
# IMPORTANT FOR ANDROID 15:
# • android.api = 35 targets Android 15 (vivo T3x 5G runs API 35)
# • android.minapi = 26 (Android 8.0) — Camera2 API stable from API 21,
#   but setting 26 ensures modern permission handling works correctly
# • android.ndk = 25b — stable NDK for Python 3.11 ARM builds
android.api = 35
android.minapi = 26
android.ndk = 25b
android.sdk = 35

# ─── Android Architecture ───────────────────────────────────────────────────
# Your device: Snapdragon 6 Gen 1 (ARM64)
# arm64-v8a = 64-bit ARM — correct for your vivo T3x 5G
android.archs = arm64-v8a

# ─── Android Build Extras ───────────────────────────────────────────────────
android.add_jars =

# FIX: Removed inline comment from gradle_dependencies value.
# Buildozer's INI parser treats any text after '=' as a dependency string.
# An inline comment like '# No extra deps' gets passed to Gradle and breaks
# the build. Keep the value empty or list real deps only.
android.gradle_dependencies =

# Enable Camera2 API features
android.features = android.hardware.camera,android.hardware.camera.autofocus

# ─── Camera Provider (CRITICAL FIX) ─────────────────────────────────────────
# NOTE: android.meta_data below writes a <meta-data> tag into AndroidManifest.xml.
# This is read by the Java/Android layer ONLY — Python and Kivy never see it.
# The KIVY_CAMERA env var is now correctly set in main.py before kivy imports.
# This entry is kept as documentation / future use only.
android.meta_data =
    kivy.camera_provider=android

# ─── Orientation ────────────────────────────────────────────────────────────
orientation = portrait

# ─── Fullscreen ─────────────────────────────────────────────────────────────
fullscreen = 0

# ─── Build Options ──────────────────────────────────────────────────────────
android.accept_sdk_license = True

# Enable debug keystore for test builds
android.debug_artifact = apk
android.release_artifact = aab

# ─── Buildozer Internals ────────────────────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1
