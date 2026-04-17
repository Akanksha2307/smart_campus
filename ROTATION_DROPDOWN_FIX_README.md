# Rotation & Dropdown Fix – Root Cause Analysis

## Bugs Fixed in This Update

---

### 🔴 Bug 1 — App rotates (screen orientation not locked)

**Root cause:** Nothing in the original code locked the screen to portrait. Android defaults to allowing free rotation based on the device sensor. When the screen rotates:
- The Kivy coordinate system flips (x/y swap)
- The popup card positions are calculated from the old window dimensions
- Camera frames get the wrong texture orientation
- All `Window.width` / `Window.height` references are stale until the next rebuild

**Fix applied in `navigation_screen.py`:**
```python
# Locks Android Activity to portrait via Java API (immediate, no rebuild needed)
from jnius import autoclass
ActivityInfo   = autoclass("android.content.pm.ActivityInfo")
PythonActivity = autoclass("org.kivy.android.PythonActivity")
PythonActivity.mActivity.setRequestedOrientation(
    ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
)
# Kivy keyboard mode — doesn't resize window, pushes content up instead
Window.softinput_mode = "below_target"
```

**Also required in `buildozer.spec`** (Python code alone is not enough for the APK manifest):
```ini
android.orientation = portrait
```

---

### 🔴 Bug 2 — Dropdown items not tappable on mobile

**Root cause (3 sub-issues):**

**2a. `FloatLayout(size=Window.size)` — static snapshot**
The outer container of the popup was created with `size=Window.size`, which is a fixed tuple captured at the moment `_build()` runs. After rotation (or if the window size changes for any reason), this container no longer matches the screen, so touch coordinates inside it are wrong — taps land outside the bounds of the card.

**Fix:** Changed to `FloatLayout(size_hint=(1, 1))` so it always fills the live window.

**2b. Manual `on_touch_down` / `on_touch_up` binding**
Row widgets used raw `on_touch_down` callbacks with `row.collide_point(*touch.pos)`. This approach is fragile on Android because:
- Touch events are dispatched in Kivy's tree from parent → child; a parent can consume the event before it reaches the row
- The ModalView intercepts some touches for `auto_dismiss`, breaking propagation
- `collide_point` checks use parent-relative coordinates but `touch.pos` is window-absolute

**Fix:** Replaced all rows with `ButtonBehavior + BoxLayout` mixins. `ButtonBehavior` uses Kivy's standard, tested touch dispatch (`on_press` / `on_release`) which works correctly inside ModalViews.

**2c. Row heights too small for finger taps**

| Widget | Before | After | Material spec |
|--------|--------|-------|---------------|
| Building header row | `dp(36)` | `dp(48)` | ≥ 48 dp |
| Room row | `dp(28)` | `dp(44)` | ≥ 48 dp |
| NavDropBtn | `dp(44)` | `dp(52)` | ≥ 48 dp |

Rows smaller than ~48 dp are routinely missed by adult fingertips on a phone.

---

### 🔴 Bug 3 — Popup position wrong after rotation

**Root cause:** `_build()` captured the caller button's screen position at open time. After rotation the button has a different position and the popup card appears off-screen or overlapping the toolbar.

**Fix:** Added `Window.bind(on_resize=self._on_window_resize)` so whenever the window dimensions change the popup clears and rebuilds itself with freshly calculated coordinates. The binding is unregistered in `on_dismiss` to avoid memory leaks.

---

### ✅ Bonus: Search filter added to dropdown

A text input search bar is now shown at the top of the dropdown. Typing filters the visible building/room rows in real time, making it much faster to find a destination on a small phone screen.

---

## Required `buildozer.spec` entries

```ini
# Lock portrait — REQUIRED in addition to the Python-level lock
android.orientation = portrait

# Permissions (from previous fix)
android.permissions = CAMERA, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE

# Camera features
android.features = android.hardware.camera, android.hardware.camera.autofocus

# pyjnius must be in requirements for the orientation lock to work
requirements = python3, kivy, kivymd, pyjnius, opencv, openpyxl, numpy

android.minapi = 21
android.api = 33
```

After editing `buildozer.spec`, always do a clean rebuild:
```bash
buildozer android clean
buildozer android debug deploy run logcat
```
