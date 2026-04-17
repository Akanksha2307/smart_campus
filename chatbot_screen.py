"""
chatbot_screen.py  –  SmartCampus
==================================
1. API key read from shared api_key_store (api_settings_screen.py).
2. Settings icon in toolbar opens the API Settings page.
3. All methods wrapped with try/except – exceptions logged to DB.
"""

import csv
import os
import traceback
import threading
import requests

from kivy.metrics        import dp
from kivy.clock          import Clock
from kivy.uix.scrollview import ScrollView

from kivymd.uix.screen    import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button    import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label     import MDLabel
from kivymd.uix.toolbar   import MDTopAppBar

from api_settings_screen import api_key_store

from database import Database

SCREEN = "ChatbotScreen"


class ChatbotScreen(MDScreen):

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.db       = Database()
            # On Android, files are copied to writable storage by main.py bootstrap
            try:
                from android.storage import app_storage_path  # type: ignore
                _base = app_storage_path()
            except Exception:
                _base = os.path.dirname(os.path.abspath(__file__))
            self.csv_path = os.path.join(_base, "Smart_Campus_Chatbot_QA_Extended.csv")
            # fallback to same-dir if writable copy not found
            if not os.path.exists(self.csv_path):
                self.csv_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "Smart_Campus_Chatbot_QA_Extended.csv"
                )
            self._build_ui()
            self.knowledge_base = self._prepare_knowledge_base()
        except Exception as exc:
            self.db.log_error(SCREEN, "__init__", exc)
            traceback.print_exc()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        try:
            main_layout = MDBoxLayout(orientation="vertical",
                                      md_bg_color=(0.95, 0.95, 0.97, 1))
            main_layout.add_widget(MDTopAppBar(
                title="Campus AI Chatbot",
                left_action_items=[["robot", lambda x: None]],
                right_action_items=[
                    ["cog",        lambda x: self._open_settings()],
                    ["arrow-left", lambda x: self.go_back()],
                ],
                elevation=2,
                md_bg_color=(0.12, 0.45, 0.9, 1),
            ))

            self.scroll    = ScrollView()
            self.chat_list = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding=dp(15),
                spacing=dp(12),
            )
            self.scroll.add_widget(self.chat_list)
            main_layout.add_widget(self.scroll)

            input_bar = MDBoxLayout(
                size_hint_y=None, height=dp(72),
                padding=[dp(10), dp(8)], spacing=dp(8),
                md_bg_color=(1, 1, 1, 1),
            )
            self.query = MDTextField(
                hint_text="Ask me anything about campus...",
                mode="round",
                fill_color_normal=(0.92, 0.94, 0.96, 1),
                size_hint_x=0.85,
            )
            send_btn = MDIconButton(
                icon="send-circle", icon_size="32sp",
                theme_text_color="Custom",
                text_color=(0.12, 0.45, 0.9, 1),
                on_release=lambda x: self.handle_send(),
            )
            input_bar.add_widget(self.query)
            input_bar.add_widget(send_btn)
            main_layout.add_widget(input_bar)
            self.add_widget(main_layout)
        except Exception as exc:
            self.db.log_error(SCREEN, "_build_ui", exc)
            traceback.print_exc()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_pre_enter(self, *args):
        try:
            self.chat_list.clear_widgets()
            self.query.text = ""
            self.add_message(
                "Assistant",
                "Yo! I'm your Campus Robot!\nAsk me anything about BRECW! 🤖✨",
            )
        except Exception as exc:
            self.db.log_error(SCREEN, "on_pre_enter", exc)

    # ── Knowledge base ────────────────────────────────────────────────────────

    def _prepare_knowledge_base(self):
        try:
            if not os.path.exists(self.csv_path):
                return None
            context = ""
            with open(self.csv_path, newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    context += f"Q: {row['Question']} | A: {row['Answer']}\n"
            return context or None
        except Exception as exc:
            self.db.log_error(SCREEN, "_prepare_knowledge_base", exc)
            return None

    # ── Send / receive ────────────────────────────────────────────────────────

    def handle_send(self):
        try:
            user_text = self.query.text.strip()
            if not user_text:
                return
            self.add_message("You", user_text)
            self.query.text = ""
            threading.Thread(
                target=self._get_ai_answer,
                args=(user_text,),
                daemon=True,
            ).start()
        except Exception as exc:
            self.db.log_error(SCREEN, "handle_send", exc)

    def _get_ai_answer(self, question):
        bot_text = ""
        try:
            if not self.knowledge_base:
                bot_text = "My database is empty. Please check the CSV file."
            else:
                api_url = api_key_store.api_url
                prompt  = (
                    "You are the Bhoj Reddy Engineering College Assistant. "
                    "Answer ONLY from the DATABASE below. "
                    "If the answer is missing, say 'no answer found from CSV file'.\n\n"
                    f"DATABASE:\n{self.knowledge_base}\n\n"
                    f"USER QUESTION: {question}"
                )
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                try:
                    resp = requests.post(api_url, json=payload, timeout=20)
                    data = resp.json()
                    if resp.status_code != 200:
                        bot_text = (
                            f"API error {resp.status_code}. "
                            "Check your API key in Settings ⚙️"
                        )
                    elif "candidates" in data:
                        bot_text = (
                            data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        )
                    else:
                        bot_text = "I couldn't find an answer in my records."
                except requests.exceptions.Timeout as exc:
                    self.db.log_error(SCREEN, "_get_ai_answer_timeout", exc)
                    bot_text = "Request timed out. Check your internet!"
                except Exception as exc:
                    self.db.log_error(SCREEN, "_get_ai_answer_request", exc)
                    bot_text = f"Error: {exc}"
        except Exception as exc:
            self.db.log_error(SCREEN, "_get_ai_answer", exc)
            bot_text = "Something went wrong. Please try again."

        Clock.schedule_once(lambda dt: self.add_message("Assistant", bot_text))

    # ── UI helpers ────────────────────────────────────────────────────────────

    def add_message(self, sender, text):
        try:
            is_user = sender == "You"
            card = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding=dp(12),
                radius=[15, 15, (0 if is_user else 15), (15 if is_user else 0)],
                md_bg_color=(0.12, 0.45, 0.9, 1) if is_user else (1, 1, 1, 1),
                size_hint_x=0.82,
                pos_hint={"right": 1} if is_user else {"left": 1},
            )
            card.add_widget(MDLabel(
                text=text,
                theme_text_color="Custom",
                text_color=(1,1,1,1) if is_user else (0.1,0.1,0.15,1),
                adaptive_height=True,
            ))
            self.chat_list.add_widget(card)
            Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0))
        except Exception as exc:
            self.db.log_error(SCREEN, "add_message", exc)

    def _open_settings(self):
        try:
            if self.manager:
                self.manager._api_settings_caller = self.name
                self.manager.current = "api_settings"
        except Exception as exc:
            self.db.log_error(SCREEN, "_open_settings", exc)

    def go_back(self):
        try:
            if self.manager:
                self.manager.current = "dashboard"
        except Exception as exc:
            self.db.log_error(SCREEN, "go_back", exc)
