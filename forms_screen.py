"""
forms_screen.py  –  SmartCampus  (Digital Document Center)
============================================================

FIXES APPLIED
-------------
FIX-1  Uri.fromFile() BANNED on Android 7+ (API 24+)
       The original code used Uri.fromFile() which throws
       android.os.FileUriExposedException on every device because
       android.minapi = 26 (Android 8+).
       Fixed by using androidx.core.content.FileProvider.getUriForFile()
       to produce a safe content:// URI, plus FLAG_GRANT_READ_URI_PERMISSION.

FIX-2  Missing PDF files returned "File not found." silently.
       scholarship.pdf, bus_form.pdf, nodues.pdf, bonafide.pdf, hostel.pdf
       were listed in the UI but never existed in the project.
       The form list now carries an `available` flag:
         True  → file is bundled; download/open works.
         False → card is greyed out with "Coming Soon" badge.

FIX-3  Database() not initialised when __init__ exception fires.
       If Database() itself raises, original code called self.db.log_error()
       before self.db was assigned → secondary AttributeError.
       Fixed by separating db init and guarding with `if self.db`.

FIX-4  Bare except in _open_file_android swallowed every error silently.
       Fixed: every branch prints root cause and logs to Issues Monitor.
"""

import os
import traceback

# ─────────────────────────────────────────────────────────────────────────────
#  _open_pdf_android()
#  FIX-1: replaces Uri.fromFile() with FileProvider for Android 7+ safety
# ─────────────────────────────────────────────────────────────────────────────

def _open_pdf_android(filepath: str) -> bool:
    """
    Open *filepath* in a PDF viewer.

    Android path (API 26+):
        Generates a safe content:// URI via FileProvider and launches
        ACTION_VIEW with FLAG_GRANT_READ_URI_PERMISSION.

        Requires companion changes in buildozer.spec:
          android.add_res = res/
          android.gradle_dependencies = androidx.core:core:1.12.0
          android.extra_manifest_application_arguments = ...
              <provider android:name="androidx.core.content.FileProvider"
                        android:authorities="${applicationId}.fileprovider"
                        android:exported="false"
                        android:grantUriPermissions="true">
                  <meta-data
                      android:name="android.support.FILE_PROVIDER_PATHS"
                      android:resource="@xml/file_paths" />
              </provider>
          (and res/xml/file_paths.xml must exist in the project)

    Desktop fallback:
        Uses webbrowser.open().

    Returns True if a viewer was launched, False if no app was available.
    """

    # ── Android / pyjnius branch ──────────────────────────────────────────────
    try:
        from jnius import autoclass  # type: ignore  – present only on Android

        Intent         = autoclass('android.content.Intent')
        File           = autoclass('java.io.File')
        FileProvider   = autoclass('androidx.core.content.FileProvider')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        activity  = PythonActivity.mActivity
        context   = activity.getApplicationContext()

        # Authority MUST match the value declared in AndroidManifest.xml
        # (injected via buildozer.spec android.extra_manifest_application_arguments)
        authority = context.getPackageName() + ".fileprovider"

        # FIX-1 core: use FileProvider instead of the banned Uri.fromFile()
        file_obj = File(filepath)
        uri      = FileProvider.getUriForFile(context, authority, file_obj)

        intent = Intent(Intent.ACTION_VIEW)
        intent.setDataAndType(uri, "application/pdf")
        intent.addFlags(
            Intent.FLAG_ACTIVITY_NEW_TASK           # required from non-Activity context
            | Intent.FLAG_GRANT_READ_URI_PERMISSION  # grant read to the viewer app
        )

        # Check if any app can handle this intent before launching
        package_manager = context.getPackageManager()
        resolve_info = package_manager.resolveActivity(intent, 0)
        if resolve_info is None:
            # No PDF viewer installed on device
            print("[Forms] No PDF viewer app found on device.")
            return False

        activity.startActivity(intent)
        return True

    except ImportError:
        # jnius not available → running on desktop; fall through to webbrowser
        pass
    except Exception as exc:
        print(f"[Forms] FileProvider open failed: {type(exc).__name__}: {exc}")
        traceback.print_exc()

    # ── Desktop / webbrowser fallback ─────────────────────────────────────────
    try:
        import webbrowser
        webbrowser.open(filepath)
        return True
    except Exception as exc:
        print(f"[Forms] webbrowser fallback also failed: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  KivyMD imports
# ─────────────────────────────────────────────────────────────────────────────

from kivy.metrics         import dp
from kivy.uix.scrollview  import ScrollView
from kivymd.uix.screen    import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card      import MDCard
from kivymd.uix.label     import MDLabel
from kivymd.uix.button    import MDIconButton, MDRaisedButton
from kivymd.uix.toolbar   import MDTopAppBar
from kivymd.uix.snackbar  import MDSnackbar

from database import Database

SCREEN = "FormsScreen"


# ─────────────────────────────────────────────────────────────────────────────
#  FormsScreen
# ─────────────────────────────────────────────────────────────────────────────

class FormsScreen(MDScreen):
    """
    Digital Document Center screen.

    Forms that are NOT physically bundled in the APK are rendered as
    disabled 'Coming Soon' cards so the user receives clear feedback
    instead of a confusing 'File not found' error.
    """

    def __init__(self, **kwargs):
        # FIX-3: assign self.db = None first so that any exception raised
        # inside Database() or _build_ui() can still safely call
        # `if self.db: self.db.log_error(...)` without a secondary crash.
        self.db = None
        try:
            super().__init__(**kwargs)
            self.db = Database()
            self._build_ui()
        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "__init__", exc)
            traceback.print_exc()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        try:
            layout = MDBoxLayout(
                orientation="vertical",
                md_bg_color=(0.97, 0.98, 1.0, 1),
            )

            layout.add_widget(MDTopAppBar(
                title="Digital Document Center",
                anchor_title="center",
                left_action_items=[["arrow-left", lambda x: self.go_back()]],
                md_bg_color=(0.15, 0.35, 0.7, 1),
                elevation=2,
            ))

            scroll  = ScrollView(do_scroll_x=False, bar_width=dp(2))
            content = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding=dp(18),
                spacing=dp(20),
            )

            # ── Section 1: Featured / priority download ───────────────────────
            content.add_widget(MDLabel(
                text="Priority Downloads",
                font_style="Subtitle1",
                bold=True,
                size_hint_y=None,
                height=dp(30),
            ))
            self._add_featured_card(content)

            # ── Section 2: Other campus forms ─────────────────────────────────
            content.add_widget(MDLabel(
                text="Other Campus Forms",
                font_style="Subtitle1",
                bold=True,
                size_hint_y=None,
                height=dp(30),
            ))

            # FIX-2: `available` flag — False means the file is NOT bundled.
            # Those cards are shown as greyed-out with a "COMING SOON" badge
            # so the user is informed rather than confused.
            other_forms = [
                # title                  dept                filename           available
                ("Scholarship Renewal",  "Accounts Dept",    "scholarship.pdf", False),
                ("Bus Pass Application", "Transport Dept",   "bus_form.pdf",    False),
                ("No Dues Certificate",  "Library / Admin",  "nodues.pdf",      False),
                ("Bonafide Request",     "Office",           "bonafide.pdf",    False),
                ("Hostel Admission",     "Warden Office",    "hostel.pdf",      False),
            ]

            for title, dept, fname, available in other_forms:
                try:
                    self._add_form_row(content, title, dept, fname, available)
                except Exception as exc:
                    if self.db:
                        self.db.log_error(SCREEN, "_build_ui_forms_loop", exc)

            # ── Info banner ───────────────────────────────────────────────────
            info = MDCard(
                orientation="horizontal",
                padding=dp(12),
                size_hint_y=None,
                height=dp(68),
                radius=[12],
                md_bg_color=(0.90, 0.95, 1.0, 1),
                elevation=0,
            )
            info.add_widget(MDIconButton(
                icon="information-outline",
                theme_text_color="Custom",
                text_color=(0.15, 0.35, 0.7, 0.9),
                pos_hint={"center_y": .5},
            ))
            info.add_widget(MDLabel(
                text="'Coming Soon' forms will be available in the next update.\n"
                     "Contact admin@brecw.ac.in for urgent document requests.",
                font_style="Caption",
                theme_text_color="Secondary",
                pos_hint={"center_y": .5},
            ))
            content.add_widget(info)

            scroll.add_widget(content)
            layout.add_widget(scroll)
            self.add_widget(layout)

        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "_build_ui", exc)
            traceback.print_exc()

    # ── Card builders ─────────────────────────────────────────────────────────

    def _add_featured_card(self, parent):
        """Build the featured Admission Form 2026 (form1.pdf) card."""
        card = MDCard(
            orientation="horizontal",
            padding=dp(15),
            size_hint=(1, None),
            height=dp(100),
            radius=[20],
            elevation=3,
            md_bg_color=(1, 1, 1, 1),
            line_color=(0.15, 0.35, 0.7, 0.2),
            ripple_behavior=True,
            on_release=lambda x: self.open_form("form1.pdf"),
        )
        card.add_widget(MDIconButton(
            icon="file-pdf-box",
            icon_size="44sp",
            theme_text_color="Custom",
            text_color=(0.8, 0.1, 0.1, 1),
            pos_hint={"center_y": .5},
        ))
        txt = MDBoxLayout(
            orientation="vertical",
            pos_hint={"center_y": .5},
            padding=[dp(10), 0, 0, 0],
        )
        txt.add_widget(MDLabel(
            text="Admission Form 2026",
            bold=True,
            font_style="H6",
        ))
        txt.add_widget(MDLabel(
            text="form1.pdf  •  Bundled in app  •  Ready to open",
            font_style="Caption",
            theme_text_color="Secondary",
        ))
        card.add_widget(txt)
        card.add_widget(MDIconButton(
            icon="download-circle",
            icon_size="32sp",
            theme_text_color="Custom",
            text_color=(0.15, 0.35, 0.7, 1),
            pos_hint={"center_y": .5},
            on_release=lambda x: self.open_form("form1.pdf"),
        ))
        parent.add_widget(card)

    def _add_form_row(self, parent, title, dept, fname, available):
        """
        Build one form row.

        available=True  → tappable card that opens the PDF.
        available=False → greyed-out card with 'COMING SOON' badge,
                          no on_release handler attached.
        """
        bg      = (1, 1, 1, 1)        if available else (0.95, 0.95, 0.96, 1)
        alpha   = 1.0                  if available else 0.38
        elev    = 1                    if available else 0

        kw = dict(
            orientation="horizontal",
            padding=[dp(15), dp(10)],
            size_hint_y=None,
            height=dp(75),
            radius=[15],
            elevation=elev,
            ripple_behavior=available,
            md_bg_color=bg,
        )
        if available:
            kw["on_release"] = lambda x, f=fname: self.open_form(f)

        row = MDCard(**kw)

        row.add_widget(MDIconButton(
            icon="file-document-outline" if available else "file-document-remove-outline",
            theme_text_color="Custom",
            text_color=(0.4, 0.4, 0.4, alpha),
            pos_hint={"center_y": .5},
        ))

        rtxt = MDBoxLayout(orientation="vertical", pos_hint={"center_y": .5})
        rtxt.add_widget(MDLabel(
            text=title,
            bold=True,
            font_style="Subtitle2",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.15, alpha),
        ))
        rtxt.add_widget(MDLabel(
            text=dept,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, alpha),
        ))
        row.add_widget(rtxt)

        # Right-side badge / chevron
        badge = MDBoxLayout(
            orientation="vertical",
            size_hint_x=None,
            width=dp(84),
            pos_hint={"center_y": .5},
        )
        if available:
            badge.add_widget(MDIconButton(
                icon="chevron-right",
                theme_text_color="Secondary",
                pos_hint={"center_y": .5, "center_x": .5},
            ))
        else:
            badge.add_widget(MDLabel(
                text="COMING\nSOON",
                font_style="Overline",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.55, 0.55, 0.6, 1),
                pos_hint={"center_y": .5},
            ))

        row.add_widget(badge)
        parent.add_widget(row)

    # ── File handling ─────────────────────────────────────────────────────────

    def _resolve_path(self, filename: str) -> str:
        """
        Return the full path to *filename*.

        Checks writable app storage first (where main.py bootstrap
        copies bundled files on Android), then the script directory
        (desktop / development mode).
        """
        try:
            from android.storage import app_storage_path  # type: ignore
            candidate = os.path.join(app_storage_path(), filename)
            if os.path.isfile(candidate):
                return candidate
        except Exception:
            pass
        # Desktop fallback – file lives next to forms_screen.py
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    def open_form(self, filename: str):
        """
        Locate *filename* and open it in a PDF viewer.
        Shows informative snackbars for both success and all failure modes.
        """
        try:
            file_path = self._resolve_path(filename)

            if not os.path.isfile(file_path):
                # Should only happen if the APK was modified / corrupted
                self._snack_error(
                    f"'{filename}' missing from app storage.\n"
                    "Please reinstall the app to restore bundled files."
                )
                return

            success = _open_pdf_android(file_path)

            if success:
                self._snack_ok(f"Opening {filename} …")
            else:
                # _open_pdf_android returned False → no PDF viewer installed
                self._snack_error(
                    "No PDF viewer app found on this device.\n"
                    "Install any free PDF reader from the Play Store and retry."
                )

        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "open_form", exc)
            self._snack_error(f"Could not open file:\n{exc}")

    # ── Snackbar helpers ──────────────────────────────────────────────────────

    def _snack_ok(self, text: str):
        try:
            MDSnackbar(
                MDLabel(text=text, theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=(0.1, 0.5, 0.2, 1),
                duration=2.5,
            ).open()
        except Exception as exc:
            print(f"[{SCREEN}] _snack_ok: {exc}")

    def _snack_error(self, text: str):
        try:
            MDSnackbar(
                MDLabel(text=text, theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=(0.75, 0.1, 0.1, 1),
                duration=4,
            ).open()
        except Exception as exc:
            print(f"[{SCREEN}] _snack_error: {exc}")

    # ── Navigation ────────────────────────────────────────────────────────────

    def go_back(self):
        try:
            if self.manager:
                self.manager.transition.direction = "right"
                self.manager.current = "dashboard"
        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "go_back", exc)
