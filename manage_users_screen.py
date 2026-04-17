"""
manage_users_screen.py  –  SmartCampus
========================================
Admin-only screen: view all users, add new users, delete users,
and reset passwords.
"""
import traceback

from kivymd.uix.screen      import MDScreen
from kivymd.uix.toolbar     import MDTopAppBar
from kivymd.uix.card        import MDCard
from kivymd.uix.label       import MDLabel
from kivymd.uix.button      import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.textfield   import MDTextField
from kivymd.uix.boxlayout   import MDBoxLayout
from kivymd.uix.dialog      import MDDialog
from kivymd.uix.snackbar    import MDSnackbar
from kivy.uix.scrollview    import ScrollView as KScrollView
from kivy.metrics           import dp
from kivy.clock             import Clock

from database import Database

SCREEN = "ManageUsersScreen"

# Role badge colours
ROLE_COLORS = {
    "admin":   (0.15, 0.35, 0.7,  1),
    "student": (0.1,  0.6,  0.35, 1),
}


class _UserRow(MDCard):
    """One row in the user list."""

    def __init__(self, user_id, username, role, on_delete, on_reset, **kwargs):
        super().__init__(**kwargs)
        self.user_id  = user_id
        self.username = username
        self.role     = role

        self.orientation  = "horizontal"
        self.size_hint_y  = None
        self.height       = dp(56)
        self.padding      = [dp(12), dp(6), dp(6), dp(6)]
        self.spacing      = dp(6)
        self.elevation    = 1
        self.radius       = [10]
        self.md_bg_color  = (1, 1, 1, 1)

        # Avatar letter
        avatar = MDLabel(
            text=username[0].upper(),
            size_hint=(None, None),
            size=(dp(38), dp(38)),
            halign="center",
            valign="middle",
            bold=True,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            md_bg_color=ROLE_COLORS.get(role, (0.5, 0.5, 0.5, 1)),
        )

        # Name + role
        info = MDBoxLayout(orientation="vertical", spacing=dp(2))
        info.add_widget(MDLabel(
            text=username,
            font_style="Subtitle2",
            bold=True,
            theme_text_color="Primary",
            halign="left",
        ))
        info.add_widget(MDLabel(
            text=role.capitalize(),
            font_style="Caption",
            theme_text_color="Custom",
            text_color=ROLE_COLORS.get(role, (0.5, 0.5, 0.5, 1)),
            halign="left",
        ))

        # Action buttons
        btn_reset = MDIconButton(
            icon="lock-reset",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.8, 1),
            on_release=lambda *a: on_reset(user_id, username),
        )
        btn_del = MDIconButton(
            icon="trash-can-outline",
            theme_text_color="Custom",
            text_color=(0.85, 0.2, 0.2, 1),
            on_release=lambda *a: on_delete(user_id, username),
        )

        self.add_widget(avatar)
        self.add_widget(info)
        self.add_widget(btn_reset)
        self.add_widget(btn_del)


class _AddUserContent(MDBoxLayout):
    """Dialog body for adding a new user."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing     = dp(10)
        self.size_hint_y = None
        self.height      = dp(230)
        self.padding     = [dp(4), dp(4), dp(4), dp(4)]

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

        self._role = "student"
        role_label = MDLabel(
            text="Role",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(20),
        )
        role_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10),
        )
        self.btn_student = MDRaisedButton(
            text="Student",
            size_hint_x=0.5,
            md_bg_color=(0.15, 0.35, 0.7, 1),
            on_release=lambda *a: self._set_role("student"),
        )
        self.btn_admin = MDFlatButton(
            text="Admin",
            size_hint_x=0.5,
            theme_text_color="Custom",
            text_color=(0.15, 0.35, 0.7, 1),
            on_release=lambda *a: self._set_role("admin"),
        )
        role_row.add_widget(self.btn_student)
        role_row.add_widget(self.btn_admin)

        for w in (self.username, self.password, role_label, role_row):
            self.add_widget(w)

    def _set_role(self, role):
        self._role = role
        if role == "student":
            self.btn_student.md_bg_color  = (0.15, 0.35, 0.7, 1)
            self.btn_admin.md_bg_color    = (0.85, 0.85, 0.85, 1)
        else:
            self.btn_admin.md_bg_color    = (0.15, 0.35, 0.7, 1)
            self.btn_student.md_bg_color  = (0.85, 0.85, 0.85, 1)


class _ResetPwdContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing     = dp(10)
        self.size_hint_y = None
        self.height      = dp(90)
        self.padding     = [dp(4), dp(4), dp(4), dp(4)]

        self.new_pwd = MDTextField(
            hint_text="New Password",
            icon_left="lock",
            password=True,
            mode="rectangle",
            size_hint_y=None,
            height=dp(42),
        )
        self.add_widget(self.new_pwd)


# ─────────────────────────────────────────────────────────────────────────────

class ManageUsersScreen(MDScreen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.db      = Database()
            self._dialog = None

            root = MDBoxLayout(orientation="vertical")

            # ── Toolbar ───────────────────────────────────────────────────────
            self.toolbar = MDTopAppBar(
                title="Manage Users",
                left_action_items=[["arrow-left", lambda *a: self._go_back()]],
                right_action_items=[["account-plus", lambda *a: self._open_add_dialog()]],
                md_bg_color=(0.15, 0.35, 0.7, 1),
            )
            root.add_widget(self.toolbar)

            # ── Stats bar ─────────────────────────────────────────────────────
            self.stats_bar = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(46),
                padding=[dp(16), dp(6), dp(16), dp(6)],
                spacing=dp(16),
                md_bg_color=(0.95, 0.96, 1.0, 1),
            )
            self.lbl_total  = MDLabel(text="Total: 0",   font_style="Caption", theme_text_color="Secondary")
            self.lbl_admin  = MDLabel(text="Admins: 0",  font_style="Caption", theme_text_color="Secondary")
            self.lbl_stud   = MDLabel(text="Students: 0",font_style="Caption", theme_text_color="Secondary")
            for l in (self.lbl_total, self.lbl_admin, self.lbl_stud):
                self.stats_bar.add_widget(l)
            root.add_widget(self.stats_bar)

            # ── Search bar ────────────────────────────────────────────────────
            search_box = MDBoxLayout(
                size_hint_y=None, height=dp(52),
                padding=[dp(12), dp(6), dp(12), dp(6)],
                md_bg_color=(1, 1, 1, 1),
            )
            self.search_field = MDTextField(
                hint_text="Search users…",
                icon_left="magnify",
                mode="rectangle",
                size_hint_y=None,
                height=dp(40),
                on_text=self._on_search,
            )
            search_box.add_widget(self.search_field)
            root.add_widget(search_box)

            # ── User list ─────────────────────────────────────────────────────
            self.scroll = KScrollView()
            self.list_box = MDBoxLayout(
                orientation="vertical",
                spacing=dp(6),
                padding=[dp(10), dp(8), dp(10), dp(8)],
                size_hint_y=None,
            )
            self.list_box.bind(minimum_height=self.list_box.setter("height"))
            self.scroll.add_widget(self.list_box)
            root.add_widget(self.scroll)

            self.add_widget(root)

        except Exception as exc:
            traceback.print_exc()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_enter(self):
        self.search_field.text = ""
        Clock.schedule_once(lambda dt: self._refresh_list(), 0.05)

    # ── Data helpers ──────────────────────────────────────────────────────────

    def _refresh_list(self, filter_text=""):
        try:
            users = self.db.get_all_users()          # [(id, username, role), ...]
            ft = filter_text.lower().strip()
            if ft:
                users = [u for u in users if ft in u[1].lower() or ft in u[2].lower()]

            self.list_box.clear_widgets()

            for uid, uname, role in users:
                row = _UserRow(
                    user_id=uid,
                    username=uname,
                    role=role,
                    on_delete=self._confirm_delete,
                    on_reset=self._open_reset_dialog,
                )
                self.list_box.add_widget(row)

            if not users:
                self.list_box.add_widget(MDLabel(
                    text="No users found." if ft else "No users yet.",
                    halign="center",
                    theme_text_color="Secondary",
                    size_hint_y=None,
                    height=dp(60),
                ))

            # Update stats
            all_users = self.db.get_all_users()
            admins   = sum(1 for u in all_users if u[2] == "admin")
            students = sum(1 for u in all_users if u[2] == "student")
            self.lbl_total.text  = f"Total: {len(all_users)}"
            self.lbl_admin.text  = f"Admins: {admins}"
            self.lbl_stud.text   = f"Students: {students}"

        except Exception as exc:
            self.db.log_error(SCREEN, "_refresh_list", exc)
            traceback.print_exc()

    def _on_search(self, instance, value):
        self._refresh_list(filter_text=value)

    # ── Add user dialog ───────────────────────────────────────────────────────

    def _open_add_dialog(self):
        try:
            self._add_content = _AddUserContent()
            self._dialog = MDDialog(
                title="Add New User",
                type="custom",
                content_cls=self._add_content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        text_color=(0.5, 0.5, 0.5, 1),
                        on_release=lambda *a: self._dialog.dismiss(),
                    ),
                    MDRaisedButton(
                        text="ADD USER",
                        md_bg_color=(0.15, 0.35, 0.7, 1),
                        on_release=self._do_add_user,
                    ),
                ],
            )
            self._dialog.open()
        except Exception as exc:
            self.db.log_error(SCREEN, "_open_add_dialog", exc)

    def _do_add_user(self, *args):
        try:
            uname = self._add_content.username.text.strip()
            pwd   = self._add_content.password.text.strip()
            role  = self._add_content._role

            if not uname or not pwd:
                self._snack("Username and password are required.")
                return
            if len(pwd) < 3:
                self._snack("Password must be at least 3 characters.")
                return
            if self.db.username_exists(uname):
                self._snack(f"'{uname}' already exists.")
                return

            ok, msg = self.db.add_user(uname, pwd, role)
            if ok:
                self._dialog.dismiss()
                self._snack(f"User '{uname}' added as {role}.")
                self._refresh_list()
            else:
                self._snack(msg or "Could not add user.")
        except Exception as exc:
            self.db.log_error(SCREEN, "_do_add_user", exc)

    # ── Delete user ───────────────────────────────────────────────────────────

    def _confirm_delete(self, user_id, username):
        try:
            self._pending_delete_id = user_id
            self._dialog = MDDialog(
                title="Delete User",
                text=f"Are you sure you want to delete '{username}'?\nThis cannot be undone.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda *a: self._dialog.dismiss(),
                    ),
                    MDRaisedButton(
                        text="DELETE",
                        md_bg_color=(0.85, 0.2, 0.2, 1),
                        on_release=self._do_delete,
                    ),
                ],
            )
            self._dialog.open()
        except Exception as exc:
            self.db.log_error(SCREEN, "_confirm_delete", exc)

    def _do_delete(self, *args):
        try:
            ok = self.db.delete_user(self._pending_delete_id)
            self._dialog.dismiss()
            if ok:
                self._snack("User deleted.")
                self._refresh_list()
            else:
                self._snack("Could not delete user.")
        except Exception as exc:
            self.db.log_error(SCREEN, "_do_delete", exc)

    # ── Reset password ────────────────────────────────────────────────────────

    def _open_reset_dialog(self, user_id, username):
        try:
            self._pending_reset_id = user_id
            self._reset_content = _ResetPwdContent()
            self._dialog = MDDialog(
                title=f"Reset Password — {username}",
                type="custom",
                content_cls=self._reset_content,
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda *a: self._dialog.dismiss(),
                    ),
                    MDRaisedButton(
                        text="SAVE",
                        md_bg_color=(0.15, 0.35, 0.7, 1),
                        on_release=self._do_reset_pwd,
                    ),
                ],
            )
            self._dialog.open()
        except Exception as exc:
            self.db.log_error(SCREEN, "_open_reset_dialog", exc)

    def _do_reset_pwd(self, *args):
        try:
            new_pwd = self._reset_content.new_pwd.text.strip()
            if len(new_pwd) < 3:
                self._snack("Password must be at least 3 characters.")
                return
            ok = self.db.update_user_password(self._pending_reset_id, new_pwd)
            self._dialog.dismiss()
            self._snack("Password updated." if ok else "Could not update password.")
        except Exception as exc:
            self.db.log_error(SCREEN, "_do_reset_pwd", exc)

    # ── Navigation ────────────────────────────────────────────────────────────

    def _go_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "dashboard"

    def _snack(self, text):
        try:
            MDSnackbar(
                MDLabel(text=text, theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=(0.2, 0.2, 0.35, 1),
                duration=2.5,
            ).open()
        except Exception:
            print(f"[ManageUsersScreen] snack: {text}")
