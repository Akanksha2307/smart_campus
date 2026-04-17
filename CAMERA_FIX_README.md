# Camera Fix – Root Cause Analysis & How to Apply

## Root Causes Found (and Fixed)

### 🔴 Root Cause 1 — `request_permissions` called WITHOUT a callback (critical)
**File:** `navigation_screen.py` (original, lines 388–396)

Android 6+ (API 23+) requires **runtime permissions**. The original code called:
```python
request_permissions([Permission.CAMERA, ...])   # ← NO callback!
```
On Android, `request_permissions` is **asynchronous**. Without a callback the OS shows the dialog but your app never knows if it was granted. Worse, when called at module-load time (before the Activity window is ready), the OS **silently drops the request entirely** — the user never sees the dialog and the camera is always denied.

**Fix applied:** Permission is now requested with a proper `_on_permissions_result` callback. The grant state is tracked in `_CAMERA_GRANTED`. Permission is also re-requested inside `on_enter()` (when the screen is visible) so the dialog appears at the right moment.

---

### 🔴 Root Cause 2 — `cv2.VideoCapture(0)` always uses index 0 (front camera on many devices)
**File:** `navigation_screen.py`, `_start_camera()` and `_start_camera_view()`

On most Android phones, camera index `0` is the **front-facing camera**. Your AR navigation needs the **back camera**. The correct index varies by device (`0`, `1`, or `-1` for system default).

**Fix applied:** Both camera-open methods now try indices `0 → 1 → -1` in sequence and use the first one that opens successfully. Resolution is also set to 1280×720 for better AR quality.

---

### 🔴 Root Cause 3 — Camera accessed before permission granted (race condition)
Even with a callback, `_start_camera()` was called the moment the user taps "START NAVIGATION" — which may be before the permission dialog was answered. The code then falls through silently with `self.cap = None`.

**Fix applied:** Both `_start_camera()` and `_start_camera_view()` now check `_CAMERA_GRANTED` before calling `VideoCapture`. If not granted, they re-request and gracefully fall back to the Kivy AR compass panel instead of a black screen.

---

## 📋 Required: buildozer.spec Changes

The Python-level fixes are necessary but **not sufficient**. You must also declare permissions in your `buildozer.spec` so they appear in the APK `AndroidManifest.xml`:

```ini
# In your buildozer.spec — find the 'android.permissions' line and update it:
android.permissions = CAMERA, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE

# Also add these features so Android knows the app uses the camera:
android.features = android.hardware.camera, android.hardware.camera.autofocus

# Make sure you are targeting API 21+ (required for runtime permissions):
android.minapi = 21
android.api = 33

# Required packages — make sure opencv is included:
requirements = python3, kivy, kivymd, opencv, openpyxl, numpy
```

> **Important:** After editing `buildozer.spec`, do a **clean rebuild**:
> ```bash
> buildozer android clean
> buildozer android debug deploy run logcat
> ```

---

## 📱 How to Verify the Fix Works

1. Build the APK and install it.
2. Open the app and navigate to the **Campus Navigation** screen.
3. You should immediately see a **"Allow app to take pictures and record video?"** dialog.
4. Tap **Allow**.
5. Select Source and Destination and tap **START NAVIGATION**.
6. The camera should open and show the live back-camera feed with the AR overlay.

If you still see only the Kivy compass panel (no camera feed), check `adb logcat` for:
```
[Nav] Camera opened at index 0    ← success
[Nav] Camera permission not yet granted  ← permission still denied
[Nav] No camera available  ← all indices failed (hardware/driver issue)
```

---

## Files Changed
| File | Changes |
|------|---------|
| `navigation_screen.py` | Permission callback system, `_CAMERA_GRANTED` guard, multi-index VideoCapture, `on_enter` permission request |
| `navigation_controller.py` | No changes needed — camera logic is entirely in the screen file |
