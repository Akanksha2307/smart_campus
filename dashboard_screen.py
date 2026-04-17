import traceback
from kivymd.uix.boxlayout  import MDBoxLayout
from kivy.uix.scrollview   import ScrollView
from kivymd.uix.screen     import MDScreen
from kivymd.uix.label      import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card       import MDCard
from kivymd.uix.button     import MDIconButton
from kivymd.uix.toolbar    import MDTopAppBar
from kivy.core.window      import Window
from kivy.metrics          import dp

from database import Database

SCREEN = "DashboardScreen"

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.db = Database()
            self._build_ui()
        except Exception as exc:
            print(f"[{SCREEN}] __init__ error: {exc}")
            traceback.print_exc()

    def _build_ui(self):
        try:
            layout = MDBoxLayout(orientation="vertical", md_bg_color=(0.98, 0.98, 1.0, 1))

            # 1. TOP APP BAR
            layout.add_widget(MDTopAppBar(
                title="Bhoj Reddy Engineering College",
                elevation=1,
                md_bg_color=(0.15, 0.35, 0.7, 1),
                right_action_items=[["logout", lambda x: self.logout()]],
            ))

            scroll = ScrollView(do_scroll_x=False, bar_width=0)
            container = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding=[dp(18), dp(10), dp(18), dp(20)],
                spacing=dp(10),
            )

            # 2. WELCOME SECTION
            welcome_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(55),
                padding=[dp(5), 0, 0, 0],
                spacing=dp(8),
            )
            welcome_box.add_widget(MDIconButton(
                icon="account-circle-outline",
                icon_size="38sp",
                theme_text_color="Custom",
                text_color=(0.15, 0.35, 0.7, 1),
                pos_hint={"center_y": .5},
            ))
            text_box = MDBoxLayout(orientation="vertical", adaptive_height=True,
                                   pos_hint={"center_y": .5})
            self.welcome_label = MDLabel(
                text="Welcome, User",
                font_style="Subtitle1",
                bold=True,
                theme_text_color="Primary",
            )
            text_box.add_widget(self.welcome_label)
            text_box.add_widget(MDLabel(
                text="Smart Campus using AI",
                font_style="Caption",
                theme_text_color="Secondary",
            ))
            welcome_box.add_widget(text_box)
            container.add_widget(welcome_box)

            # 3. MODULE GRID
            grid = MDGridLayout(cols=2, spacing=dp(18), adaptive_height=True)
            tile_width = (Window.width - dp(18 * 3)) / 2

            modules = [
                ("NOTICES",       "bell-outline",        "notices",        (0,    0.6,  0.6,  1)),
                ("EVENTS",        "calendar-star",       "events",         (1,    0.4,  0.2,  1)),
                ("EXAMS",         "file-document-edit",  "exams",          (0.8,  0,    0.4,  1)),
                ("FORMS",         "folder-account",      "forms",          (0.9,  0.7,  0,    1)),
                ("DEPT & FACULTY","school",               "faculty",        (0.1,  0.7,  0.3,  1)),
                ("PLACEMENTS",    "briefcase-check",     "placements",     (0.3,  0.3,  0.3,  1)),
                ("AI CHATBOT",    "robot-outline",       "chatbot",        (0.5,  0.3,  0.9,  1)),
                ("NAVIGATE",      "near-me",             "navigation",     (0.15, 0.35, 0.7,  1)),
                # ── NEW: Issues Monitor tile ────────────────────────────────
                ("ISSUES MONITOR","bug-outline",         "issues_monitor", (0.7,  0.1,  0.15, 1)),
                ("MANAGE USERS",  "account-group",       "manage_users",   (0.2,  0.5,  0.7,  1)),
            ]

            for title, icon, sn, color in modules:
                card = MDCard(
                    orientation="vertical",
                    padding=dp(12),
                    radius=[20],
                    elevation=1,
                    size_hint=(None, None),
                    size=(tile_width, dp(125)),
                    ripple_behavior=True,
                    md_bg_color=(1, 1, 1, 1),
                    on_release=lambda x, screen=sn: self.change_screen(screen),
                )
                card.add_widget(MDIconButton(
                    icon=icon,
                    pos_hint={"center_x": .5},
                    icon_size="34sp",
                    theme_text_color="Custom",
                    text_color=color,
                    on_release=lambda x, screen=sn: self.change_screen(screen),
                ))
                card.add_widget(MDLabel(
                    text=title,
                    halign="center",
                    font_style="Caption",
                    bold=True,
                    theme_text_color="Primary",
                ))
                grid.add_widget(card)

            container.add_widget(grid)
            scroll.add_widget(container)
            layout.add_widget(scroll)
            self.add_widget(layout)
        except Exception as exc:
            self.db.log_error(SCREEN, "_build_ui", exc)
            traceback.print_exc()

    def on_pre_enter(self, *args):
        try:
            if hasattr(self.manager, "logged_user_name") and self.manager.logged_user_name:
                self.welcome_label.text = f"Welcome, {self.manager.logged_user_name}"
            else:
                self.welcome_label.text = "Welcome, Student"
        except Exception as exc:
            self.db.log_error(SCREEN, "on_pre_enter", exc)

    def change_screen(self, screen_name):
        try:
            if self.manager:
                self.manager.transition.direction = "left"
                self.manager.current = screen_name
        except Exception as exc:
            self.db.log_error(SCREEN, "change_screen", exc)
            print(f"[{SCREEN}] Error switching to {screen_name}: {exc}")

    def logout(self):
        try:
            if self.manager:
                self.manager.logged_user_name = ""
                self.manager.transition.direction = "right"
                self.manager.current = "login"
        except Exception as exc:
            self.db.log_error(SCREEN, "logout", exc)
