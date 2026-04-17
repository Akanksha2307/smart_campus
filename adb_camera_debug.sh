# Android Camera Debugging Guide
# ================================
# For SmartCampus app on Android 15 (vivo T3x 5G)

## STEP 1: Enable USB Debugging on your device
# Settings → About Phone → tap "Build Number" 7 times
# Settings → Developer Options → enable USB Debugging

## STEP 2: Connect phone + verify ADB sees it
adb devices
# Expected output: <serial>    device

## STEP 3: Install the APK
adb install -r SmartCampus-debug.apk

## STEP 4: Clear logcat buffer before testing
adb logcat -c

## STEP 5: Watch ONLY relevant logs (Python + Camera + Permissions)
adb logcat -s python:V Camera2:E CameraManager:E AndroidRuntime:E PermissionController:W

## STEP 6: Capture full session log to file
adb logcat > campus_debug.log &
# ... run your app, reproduce the bug ...
# Then press Ctrl+C to stop

## ─── WHAT TO LOOK FOR ────────────────────────────────────────────────────────

# PERMISSION DENIED → Look for:
#   W PermissionController: CAMERA permission denied
#   E CameraManager: Camera device open failed
# FIX: Grant camera permission manually:
#   adb shell pm grant org.college.smartcampus android.permission.CAMERA

# CAMERA OPEN FAILED → Look for:
#   E Camera2: Unable to open camera: CAMERA_DISCONNECTED
# FIX: Another app is using the camera. Close it.

# KIVY CAMERA NOT STARTING → Look for:
#   I python: [Nav] Kivy Camera widget not available
# FIX: Confirm kivy==2.3.0 in requirements (not 2.2.x which had camera bugs)

# BLACK FRAMES (cv2 issue) → Look for:
#   I python: [Nav] cv2 camera opened at index 0
#   (followed by no AR rendering despite cap.isOpened() = True)
# FIX: This is the root cause — cv2 VideoCapture returns black frames on Android.
#      The fixed code uses Kivy Camera instead. Rebuild APK with fixed code.

# IMPORT ERROR → Look for:
#   E python: ModuleNotFoundError: No module named 'cv2'
# This is EXPECTED on Android — cv2 is optional. The app handles it gracefully.

## ─── GRANT PERMISSIONS VIA ADB (for testing) ────────────────────────────────
adb shell pm grant org.college.smartcampus android.permission.CAMERA
adb shell pm grant org.college.smartcampus android.permission.ACCESS_FINE_LOCATION
adb shell pm grant org.college.smartcampus android.permission.READ_EXTERNAL_STORAGE
adb shell pm grant org.college.smartcampus android.permission.READ_MEDIA_IMAGES

## ─── CHECK WHICH PERMISSIONS ARE GRANTED ─────────────────────────────────────
adb shell dumpsys package org.college.smartcampus | grep -A2 "CAMERA\|LOCATION\|STORAGE"

## ─── VERIFY CAMERA HARDWARE ─────────────────────────────────────────────────
adb shell "dumpsys media.camera | head -50"
# Should show: "Camera 0", "Camera 1" (front + back)

## ─── PYTHON PRINT LOGS ───────────────────────────────────────────────────────
# All [Nav] print() calls go to logcat under tag "python"
# grep for your specific messages:
adb logcat -s python:V | grep -E "\[Nav\]|\[GPS\]|\[AR\]"
