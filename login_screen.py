import traceback
from kivymd.uix.screen    import MDScreen
from kivymd.uix.card      import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button    import MDRaisedButton, MDFlatButton
from kivymd.uix.label     import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.snackbar  import MDSnackbar
from kivy.core.window     import Window
from kivy.metrics         import dp

from database import Database

SCREEN = "LoginScreen"

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.db = Database()
            self.layout = MDFloatLayout(md_bg_color=(0.98, 0.98, 1.0, 1))

            # 1. HEADER SECTION
            header = MDBoxLayout(
                orientation="vertical",
                size_hint=(1, 0.35),
                pos_hint={"top": 1},
                padding=[dp(20), dp(30), dp(20), 0],
                spacing=dp(5),
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
            self.layout.add_widget(header)

            # 2. LOGIN PANEL
            card_width = min(Window.width * 0.85, dp(310))
            self.login_card = MDCard(
                orientation="vertical",
                padding=dp(20),
                spacing=dp(12),
                size_hint=(None, None),
                size=(card_width, dp(320)),
                pos_hint={"center_x": .5, "center_y": .42},
                elevation=2,
                radius=[20],
                md_bg_color=(1, 1, 1, 1),
                line_color=(0.9, 0.9, 0.9, 1),
            )
            self.login_card.add_widget(MDLabel(
                text="SIGN IN",
                font_style="Button",
                halign="center",
                bold=True,
                theme_text_color="Secondary",
            ))
            self.username = MDTextField(
                hint_text="Username",
                icon_left="account-circle",
                mode="rectangle",
                size_hint_y=None,
                height=dp(40),
            )
            self.password = MDTextField(
                hint_text="Password",
                icon_left="lock",
                password=True,
                mode="rectangle",
                size_hint_y=None,
                height=dp(40),
            )
            self.login_card.add_widget(self.username)
            self.login_card.add_widget(self.password)
            login_btn = MDRaisedButton(
                text="LOGIN",
                size_hint_x=1,
                height=dp(45),
                md_bg_color=(0.15, 0.35, 0.7, 1),
                on_release=self.validate_login,
            )
            register_btn = MDFlatButton(
                text="New here? Create an account",
                size_hint_x=1,
                theme_text_color="Custom",
                text_color=(0.3, 0.3, 0.7, 1),
                on_release=self.go_register,
            )
            self.login_card.add_widget(login_btn)
            self.login_card.add_widget(register_btn)
            self.layout.add_widget(self.login_card)

            # 3. FOOTER
            self.layout.add_widget(MDLabel(
                text="Build for Bhoj Reddy Engineering College for Women",
                halign="center",
                font_style="Caption",
                pos_hint={"center_y": 0.05},
                theme_text_color="Secondary",
                italic=True,
            ))
            self.add_widget(self.layout)
        except Exception as exc:
            self.db.log_error(SCREEN, "__init__", exc)
            traceback.print_exc()

    def go_register(self, *args):
        self.manager.transition.direction = "left"
        self.manager.current = "register"

    def validate_login(self, *args):
        try:
            user = self.username.text.strip()
            pwd  = self.password.text.strip()
            if not user or not pwd:
                self.show_error("Fields cannot be empty")
                return
            if self.db.validate_login(user, pwd):
                self.manager.logged_user_name = user
                self.manager.transition.direction = "left"
                self.manager.current = "dashboard"
                self.username.text = ""
                self.password.text = ""
            else:
                self.show_error("Invalid Credentials")
                self.username.error = True
                self.password.error = True
        except Exception as exc:
            self.db.log_error(SCREEN, "validate_login", exc)
            self.show_error("Login error. Please try again.")

    def show_error(self, text):
        try:
            MDSnackbar(
                MDLabel(text=text, theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=(0.2, 0.2, 0.2, 1),
                duration=2,
            ).open()
        except Exception as exc:
            print(f"[{SCREEN}] show_error: {exc}")
