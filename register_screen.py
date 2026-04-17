"""
register_screen.py  –  SmartCampus
=====================================
Self-registration page reachable from the Login screen.
Any visitor can create a 'student' or 'admin' account.

FIXES APPLIED
-------------
FIX-1  btn_admin was MDFlatButton — md_bg_color is silently ignored on
       MDFlatButton (transparent by design in KivyMD).  Role toggle
       appeared to do nothing visually when switching to "Admin".
       → Both role buttons are now MDRaisedButton so md_bg_color renders.

FIX-2  _set_role() used inconsistent property types for the two buttons:
       btn_student used md_bg_color while btn_admin used theme_text_color/
       text_color.  Switching "Student → Admin → Student" left btn_student
       stuck in grey and btn_admin text invisible because neither branch
       fully reset the other button.
       → _set_role() now sets md_bg_color AND text_color on BOTH buttons
         every time it runs, so the active/inactive state is always correct.

FIX-3  Card height dp(370) clipped the bottom button.
       Measured real content: 8 widgets × heights + padding + spacing ≈ dp(420).
       → Card height raised to dp(420).

FIX-4  register_btn had height=dp(46) but no size_hint_y=None, so Kivy
       ignored the explicit height and used the default stretch height.
       → size_hint_y=None added so height=dp(46) is honoured.

FIX-5  go_back() had no try/except and no self.manager guard. Any routing
       failure raised an unhandled AttributeError that crashed the screen.
       → Wrapped in try/except with manager guard and db error logging.

FIX-6  __init__ except block called traceback.print_exc() but could never
       call self.db.log_error() because self.db is only assigned inside the
       try block. If Database() itself raised, self.db did not exist and a
       second AttributeError masked the real error.
       → self.db = None initialised before try; all log_error calls guarded
         with `if self.db:`.

FIX-7  _set_role() did not reset btn_student text_color when switching
       "Student → Admin → Student", leaving btn_student text in wrong colour
       on second toggle.
       → Every _set_role() call now explicitly resets BOTH buttons fully.
"""

import traceback

from kivymd.uix.screen      import MDScreen
from kivymd.uix.card        import MDCard
from kivymd.uix.textfield   import MDTextField
from kivymd.uix.button      import MDRaisedButton, MDFlatButton   # MDFlatButton kept for back_btn only
from kivymd.uix.label       import MDLabel
from kivymd.uix.boxlayout   import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.snackbar    import MDSnackbar
from kivy.metrics           import dp
from kivy.core.window       import Window

from database import Database

SCREEN = "RegisterScreen"

# ── Role-button colour palette ────────────────────────────────────────────────
_ACTIVE_BG    = (0.15, 0.35, 0.70, 1)   # blue fill  — selected role
_ACTIVE_TEXT  = (1.00, 1.00, 1.00, 1)   # white text — selected role
_INACTIVE_BG  = (0.88, 0.88, 0.92, 1)   # grey fill  — unselected role
_INACTIVE_TEXT= (0.40, 0.40, 0.50, 1)   # grey text  — unselected role


class RegisterScreen(MDScreen):

    def __init__(self, **kwargs):
        # FIX-6: assign self.db = None first so that the except block can
        # safely call `if self.db: self.db.log_error(...)` even when
        # Database() itself is what raised the exception.
        self.db = None
        try:
            super().__init__(**kwargs)
            self.db   = Database()
            self._role = "student"
            self._build_ui()
        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "__init__", exc)
            traceback.print_exc()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        try:
            layout = MDFloatLayout(md_bg_color=(0.98, 0.98, 1.0, 1))

            # ── Header ────────────────────────────────────────────────────────
            header = MDBoxLayout(
                orientation="vertical",
                size_hint=(1, 0.28),
                pos_hint={"top": 1},
                padding=[dp(20), dp(28), dp(20), 0],
                spacing=dp(4),
            )
            header.add_widget(MDLabel(
                text="BHOJ REDDY ENGINEERING\nCOLLEGE FOR WOMEN",
                halign="center",
                font_style="Subtitle1",
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.3, 1),
                bold=True,
            ))
            header.add_widget(MDLabel(
                text="SMART CAMPUS USING AI",
                halign="center",
                font_style="H6",
                theme_text_color="Custom",
                text_color=(0.7, 0.5, 0.1, 1),
                bold=True,
            ))
            layout.add_widget(header)

            # ── Registration card ─────────────────────────────────────────────
            card_width = min(Window.width * 0.88, dp(320))

            # FIX-3: height raised from dp(370) to dp(420).
            # Measured content: title(28) + 3 fields(42×3=126) + role_label(22)
            # + role_row(38) + register_btn(46) + back_btn(36) = 296
            # + padding(22×2=44) + spacing(10×7=70) = 410 → rounded up to 420
            card = MDCard(
                orientation="vertical",
                padding=dp(22),
                spacing=dp(10),
                size_hint=(None, None),
                size=(card_width, dp(420)),
                pos_hint={"center_x": .5, "center_y": .45},
                elevation=2,
                radius=[20],
                md_bg_color=(1, 1, 1, 1),
                line_color=(0.88, 0.88, 0.95, 1),
            )

            # Title
            card.add_widget(MDLabel(
                text="CREATE ACCOUNT",
                font_style="Button",
                halign="center",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.15, 0.35, 0.7, 1),
                size_hint_y=None,
                height=dp(28),
            ))

            # Input fields
            self.username = MDTextField(
                hint_text="Username",
                icon_left="account-circle",
                mode="rectangle",
                size_hint_y=None,
                height=dp(42),
            )
            self.password = MDTextField(
                hint_text="Password",
                icon_left="lock",
                password=True,
                mode="rectangle",
                size_hint_y=None,
                height=dp(42),
            )
            self.confirm_pwd = MDTextField(
                hint_text="Confirm Password",
                icon_left="lock-check",
                password=True,
                mode="rectangle",
                size_hint_y=None,
                height=dp(42),
            )
            card.add_widget(self.username)
            card.add_widget(self.password)
            card.add_widget(self.confirm_pwd)

            # Role label
            card.add_widget(MDLabel(
                text="Select Role:",
                size_hint_y=None,
                height=dp(22),
                theme_text_color="Secondary",
                font_style="Caption",
            ))

            # ── Role toggle row ───────────────────────────────────────────────
            # FIX-1 + FIX-2: BOTH buttons are now MDRaisedButton so that
            # md_bg_color is actually rendered. MDFlatButton ignores
            # md_bg_color entirely (transparent by KivyMD design).
            role_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10),
            )

            # Student button — starts ACTIVE (blue)
            self.btn_student = MDRaisedButton(
                text="Student",
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(40),
                md_bg_color=_ACTIVE_BG,
                theme_text_color="Custom",
                text_color=_ACTIVE_TEXT,
                on_release=lambda *a: self._set_role("student"),
            )

            # Admin button — starts INACTIVE (grey)
            # FIX-1: was MDFlatButton; changed to MDRaisedButton
            self.btn_admin = MDRaisedButton(
                text="Admin",
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(40),
                md_bg_color=_INACTIVE_BG,
                theme_text_color="Custom",
                text_color=_INACTIVE_TEXT,
                on_release=lambda *a: self._set_role("admin"),
            )

            role_row.add_widget(self.btn_student)
            role_row.add_widget(self.btn_admin)
            card.add_widget(role_row)

            # Register button
            # FIX-4: added size_hint_y=None so height=dp(46) is honoured by Kivy
            register_btn = MDRaisedButton(
                text="REGISTER",
                size_hint_x=1,
                size_hint_y=None,
                height=dp(46),
                md_bg_color=(0.15, 0.35, 0.7, 1),
                on_release=self.do_register,
            )
            card.add_widget(register_btn)

            # Back button — MDFlatButton is correct here (no background needed)
            back_btn = MDFlatButton(
                text="← Back to Login",
                size_hint_x=1,
                theme_text_color="Custom",
                text_color=(0.4, 0.4, 0.6, 1),
                on_release=self.go_back,
            )
            card.add_widget(back_btn)

            layout.add_widget(card)
            self.add_widget(layout)

        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "_build_ui", exc)
            traceback.print_exc()

    # ── Role toggle ───────────────────────────────────────────────────────────

    def _set_role(self, role):
        """
        Switch the active role and update BOTH button colours.

        FIX-2 + FIX-7: Previous code set md_bg_color on btn_student but
        theme_text_color/text_color on btn_admin, so the two branches used
        completely different property paths.  On a second toggle the inactive
        button's colour was never fully reset.

        This version always sets md_bg_color AND text_color on BOTH buttons
        so the visual state is 100 % correct after every tap.
        """
        try:
            self._role = role

            if role == "student":
                # Student = active (blue), Admin = inactive (grey)
                self.btn_student.md_bg_color = _ACTIVE_BG
                self.btn_student.text_color  = _ACTIVE_TEXT
                self.btn_admin.md_bg_color   = _INACTIVE_BG
                self.btn_admin.text_color    = _INACTIVE_TEXT
            else:
                # Admin = active (blue), Student = inactive (grey)
                self.btn_admin.md_bg_color   = _ACTIVE_BG
                self.btn_admin.text_color    = _ACTIVE_TEXT
                self.btn_student.md_bg_color = _INACTIVE_BG
                self.btn_student.text_color  = _INACTIVE_TEXT

        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "_set_role", exc)

    # ── Actions ───────────────────────────────────────────────────────────────

    def do_register(self, *args):
        try:
            uname = self.username.text.strip()
            pwd   = self.password.text.strip()
            cpwd  = self.confirm_pwd.text.strip()

            if not uname or not pwd:
                self._snack("Username and password are required.")
                return
            if len(pwd) < 3:
                self._snack("Password must be at least 3 characters.")
                return
            if pwd != cpwd:
                self._snack("Passwords do not match.")
                self.confirm_pwd.error = True
                return
            if self.db.username_exists(uname):
                self._snack(f"Username '{uname}' is already taken.")
                self.username.error = True
                return

            ok, msg = self.db.add_user(uname, pwd, self._role)
            if ok:
                self._snack(f"Account created! You can now log in as '{uname}'.")
                self._clear_fields()
                self.go_back()
            else:
                self._snack(msg or "Registration failed.")

        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "do_register", exc)
            traceback.print_exc()

    def go_back(self, *args):
        # FIX-5: added try/except and self.manager guard.  Previously an
        # unguarded AttributeError here would crash the entire screen.
        try:
            if self.manager:
                self.manager.transition.direction = "right"
                self.manager.current = "login"
        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "go_back", exc)

    def _clear_fields(self):
        try:
            self.username.text    = ""
            self.password.text    = ""
            self.confirm_pwd.text = ""
            self.username.error      = False
            self.confirm_pwd.error   = False
            self._set_role("student")
        except Exception as exc:
            if self.db:
                self.db.log_error(SCREEN, "_clear_fields", exc)

    def _snack(self, text):
        try:
            MDSnackbar(
                MDLabel(
                    text=text,
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                ),
                bg_color=(0.2, 0.2, 0.35, 1),
                duration=2.5,
            ).open()
        except Exception:
            print(f"[{SCREEN}] snack: {text}")
