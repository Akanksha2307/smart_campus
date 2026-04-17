"""
api_settings_screen.py  -  SmartCampus
=======================================
Shared Gemini API key store + Settings UI page.
All methods wrapped with try/except – exceptions logged to DB.
"""

# ── Shared singleton ──────────────────────────────────────────────────────────

class _APIKeyStore:
    _DEFAULT = "AIzaSyBUjcqPDO1at9c9qr0zoWLRexl2K42nM1U"

    def __init__(self):
        self._key = self._DEFAULT

    def get(self) -> str:
        return self._key

    def set(self, key: str):
        self._key = key.strip()

    def reset(self):
        self._key = self._DEFAULT

    @property
    def api_url(self) -> str:
        return (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={self._key}"
        )


api_key_store = _APIKeyStore()

# ── KivyMD UI ────────────────────────────────────────────────────────────────

import traceback
from kivy.metrics         import dp, sp
from kivy.uix.scrollview  import ScrollView
from kivymd.uix.screen    import MDScreen
from kivymd.uix.toolbar   import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card      import MDCard
from kivymd.uix.label     import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button    import MDRaisedButton, MDFlatButton

from database import Database

SCREEN = "APISettingsScreen"


class APISettingsScreen(MDScreen):

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.db = Database()
            self._build_ui()
        except Exception as exc:
            self.db.log_error(SCREEN, "__init__", exc)
            traceback.print_exc()

    def _build_ui(self):
        try:
            root = MDBoxLayout(orientation="vertical", md_bg_color=(0.95,0.95,0.97,1))
            root.add_widget(MDTopAppBar(
                title="API Settings",
                left_action_items=[["arrow-left", lambda x: self._go_back()]],
                right_action_items=[["restore",   lambda x: self._reset_key()]],
                md_bg_color=(0.10,0.10,0.20,1),
                elevation=3,
            ))

            sv = ScrollView()
            content = MDBoxLayout(orientation="vertical", adaptive_height=True,
                                  padding=[dp(16),dp(16)], spacing=dp(14))
            sv.add_widget(content)
            root.add_widget(sv)

            # Info card
            info = MDCard(orientation="vertical", padding=dp(16), spacing=dp(6),
                size_hint=(1,None), height=dp(108), radius=[dp(12)], elevation=0,
                md_bg_color=(0.12,0.45,0.9,0.10))
            info.add_widget(MDLabel(text="🔑  Gemini API Key", font_size=sp(14),
                bold=True, theme_text_color="Custom", text_color=(0.10,0.10,0.20,1),
                size_hint_y=None, height=dp(24)))
            info.add_widget(MDLabel(
                text="Used by: Campus AI Chatbot\nGet a free key at: aistudio.google.com",
                font_size=sp(11), theme_text_color="Secondary", adaptive_height=True))
            content.add_widget(info)

            # Input card
            inp = MDCard(orientation="vertical", padding=[dp(16),dp(18)],
                spacing=dp(12), size_hint=(1,None), height=dp(220),
                radius=[dp(12)], elevation=2, md_bg_color=(1,1,1,1))
            inp.add_widget(MDLabel(text="Enter your Gemini API Key",
                font_size=sp(12), bold=True, theme_text_color="Primary",
                size_hint_y=None, height=dp(20)))
            self._key_field = MDTextField(
                hint_text="AIza...", mode="rectangle", password=True,
                helper_text="Paste your full API key here",
                helper_text_mode="on_focus",
                fill_color_normal=(0.96,0.96,0.99,1))
            inp.add_widget(self._key_field)

            toggle_row = MDBoxLayout(orientation="horizontal",
                size_hint=(1,None), height=dp(30))
            self._toggle_btn = MDFlatButton(
                text="👁  Show Key",
                theme_text_color="Custom", text_color=(0.10,0.10,0.20,1),
                on_release=self._toggle_visibility)
            toggle_row.add_widget(self._toggle_btn)
            toggle_row.add_widget(MDBoxLayout())
            inp.add_widget(toggle_row)
            inp.add_widget(MDRaisedButton(
                text="💾  SAVE API KEY",
                size_hint=(1,None), height=dp(44),
                md_bg_color=(0.10,0.10,0.20,1),
                on_release=self._save_key))
            content.add_widget(inp)

            # Status card
            self._status_card = MDCard(orientation="vertical", padding=dp(14),
                spacing=dp(4), size_hint=(1,None), height=dp(90),
                radius=[dp(10)], elevation=0, md_bg_color=(0.95,1.0,0.95,1))
            self._status_title = MDLabel(text="✅  Active Key", font_size=sp(12),
                bold=True, theme_text_color="Custom", text_color=(0.05,0.55,0.25,1),
                size_hint_y=None, height=dp(22))
            self._status_preview = MDLabel(text="", font_size=sp(10),
                theme_text_color="Secondary", adaptive_height=True)
            self._status_card.add_widget(self._status_title)
            self._status_card.add_widget(self._status_preview)
            content.add_widget(self._status_card)

            # Usage card
            usage = MDCard(orientation="vertical", padding=dp(14), spacing=dp(4),
                size_hint=(1,None), height=dp(118), radius=[dp(10)], elevation=0,
                md_bg_color=(1.0,0.98,0.90,1))
            usage.add_widget(MDLabel(text="ℹ️  Where is this key used?",
                font_size=sp(12), bold=True, theme_text_color="Custom",
                text_color=(0.55,0.40,0.0,1), size_hint_y=None, height=dp(22)))
            usage.add_widget(MDLabel(
                text=(
                    "• Campus AI Chatbot  (tap ⚙️ in chatbot toolbar)\n"
                    "• Also accessible from the Main Dashboard page\n"
                    "• One key shared across all AI features automatically"
                ),
                font_size=sp(11), theme_text_color="Secondary", adaptive_height=True))
            content.add_widget(usage)
            self.add_widget(root)
        except Exception as exc:
            self.db.log_error(SCREEN, "_build_ui", exc)
            traceback.print_exc()

    def on_pre_enter(self, *args):
        try:
            current = api_key_store.get()
            self._key_field.text = current
            self._refresh_status(current)
        except Exception as exc:
            self.db.log_error(SCREEN, "on_pre_enter", exc)

    def _save_key(self, *_):
        try:
            key = self._key_field.text.strip()
            if not key:
                self._show_status("⚠️  Key is empty",
                    "Paste your API key before saving.",
                    (1.0,0.93,0.93,1), (0.7,0.1,0.1,1))
                return
            api_key_store.set(key)
            self._show_status("✅  Key saved!", self._mask(key),
                (0.95,1.0,0.95,1), (0.05,0.55,0.25,1))
        except Exception as exc:
            self.db.log_error(SCREEN, "_save_key", exc)

    def _reset_key(self, *_):
        try:
            api_key_store.reset()
            self._key_field.text = api_key_store.get()
            self._show_status("🔄  Reset to default", self._mask(api_key_store.get()),
                (0.93,0.95,1.0,1), (0.10,0.20,0.60,1))
        except Exception as exc:
            self.db.log_error(SCREEN, "_reset_key", exc)

    def _toggle_visibility(self, *_):
        try:
            self._key_field.password = not self._key_field.password
            self._toggle_btn.text = (
                "🙈  Hide Key" if not self._key_field.password else "👁  Show Key"
            )
        except Exception as exc:
            self.db.log_error(SCREEN, "_toggle_visibility", exc)

    def _go_back(self):
        try:
            if self.manager:
                dest = getattr(self.manager, "_api_settings_caller", "dashboard")
                self.manager.current = dest
        except Exception as exc:
            self.db.log_error(SCREEN, "_go_back", exc)

    @staticmethod
    def _mask(key: str) -> str:
        if len(key) <= 8:
            return "*" * len(key)
        return key[:4] + "••••••••" + key[-4:]

    def _refresh_status(self, key: str):
        try:
            self._show_status("✅  Active Key", self._mask(key),
                (0.95,1.0,0.95,1), (0.05,0.55,0.25,1))
        except Exception as exc:
            self.db.log_error(SCREEN, "_refresh_status", exc)

    def _show_status(self, title, preview, bg, title_color):
        try:
            self._status_card.md_bg_color = bg
            self._status_title.text       = title
            self._status_title.text_color = title_color
            self._status_preview.text     = preview
        except Exception as exc:
            self.db.log_error(SCREEN, "_show_status", exc)
