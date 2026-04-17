import traceback
from kivymd.uix.screen    import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card      import MDCard
from kivymd.uix.label     import MDLabel
from kivymd.uix.toolbar   import MDTopAppBar
from kivy.uix.scrollview  import ScrollView
from kivy.metrics         import dp

from database import Database

SCREEN = "ExamsScreen"

class ExamsScreen(MDScreen):
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
            root = MDBoxLayout(orientation="vertical", md_bg_color=(0.98, 0.98, 1.0, 1))

            root.add_widget(MDTopAppBar(
                title="Exams & Time Tables",
                anchor_title="center",
                left_action_items=[["arrow-left", lambda x: self.go_back()]],
                md_bg_color=(0.15, 0.35, 0.7, 1),
                elevation=2,
            ))

            scroll = ScrollView(do_scroll_x=False, bar_width=dp(2))
            content = MDBoxLayout(orientation="vertical", adaptive_height=True,
                                  padding=dp(16), spacing=dp(15))

            # Student academic summary card
            summary_card = MDCard(
                orientation="horizontal",
                padding=dp(15),
                size_hint=(1, None),
                height=dp(85),
                radius=[20],
                md_bg_color=(0.15, 0.35, 0.7, 1),
                elevation=3,
            )
            for title, value in [("REGULATION","R18"),("YEAR","III-II"),
                                  ("CGPA","8.12"),("TYPE","REGULAR")]:
                box = MDBoxLayout(orientation="vertical")
                box.add_widget(MDLabel(text=title, halign="center",
                    theme_text_color="Custom", text_color=(1,1,1,0.6), font_style="Overline"))
                box.add_widget(MDLabel(text=value, halign="center",
                    theme_text_color="Custom", text_color=(1,1,1,1),
                    font_style="Subtitle2", bold=True))
                summary_card.add_widget(box)
            content.add_widget(summary_card)

            content.add_widget(MDLabel(text="JNTUH Notifications & Results",
                font_style="Subtitle1", bold=True, adaptive_height=True))

            jntuh_data = [
                ("B.Tech III-II Regular Exams",  "May/June 2024", "R18", "TIME TABLE"),
                ("B.Tech IV-I Supply Exams",      "June 2024",     "R18", "TIME TABLE"),
                ("B.Tech II-II Regular Results",  "April 2024",    "R22", "RESULT"),
                ("B.Tech I-II Supply Results",    "April 2024",    "R22", "RESULT"),
                ("B.Tech III-I Regular Results",  "March 2024",    "R18", "RESULT"),
                ("B.Tech IV-II Advanced Supply",  "July 2024",     "R18", "SCHEDULE"),
                ("B.Tech II-I Regular Results",   "Feb 2024",      "R22", "RESULT"),
                ("Mid-Term II Examinations",      "May 2024",      "R18", "SCHEDULE"),
                ("B.Tech III-II Supply Results",  "Jan 2024",      "R18", "RESULT"),
                ("External Lab Examinations",     "June 2024",     "R18", "SCHEDULE"),
            ]

            for title, month, reg, category in jntuh_data:
                try:
                    if category == "RESULT":
                        cat_color = (0.1, 0.6, 0.2, 1)
                        icon = "file-check-outline"
                    elif category == "TIME TABLE":
                        cat_color = (0.15, 0.35, 0.7, 1)
                        icon = "calendar-clock"
                    else:
                        cat_color = (1, 0.5, 0, 1)
                        icon = "alert-circle-outline"

                    card = MDCard(
                        orientation="horizontal",
                        size_hint=(1, None),
                        height=dp(90),
                        radius=[15],
                        elevation=1,
                        md_bg_color=(1, 1, 1, 1),
                        padding=[0, 0, dp(15), 0],
                    )
                    card.add_widget(MDBoxLayout(
                        size_hint_x=None, width=dp(6),
                        md_bg_color=cat_color, radius=[15,0,0,15]))
                    info = MDBoxLayout(orientation="vertical", padding=dp(12),
                                       pos_hint={"center_y": 0.5})
                    info.add_widget(MDLabel(text=title, bold=True, font_style="Subtitle2"))
                    info.add_widget(MDLabel(text=f"{month} | Regulation: {reg}",
                        theme_text_color="Secondary", font_style="Caption"))
                    badge = MDBoxLayout(orientation="vertical", size_hint_x=0.3,
                                        pos_hint={"center_y":0.5}, spacing=dp(2))
                    badge.add_widget(MDLabel(text=category, halign="center",
                        theme_text_color="Custom", text_color=cat_color,
                        bold=True, font_style="Overline"))
                    badge.add_widget(MDLabel(text="VIEW", halign="center",
                        theme_text_color="Secondary", font_style="Caption"))
                    card.add_widget(info)
                    card.add_widget(badge)
                    content.add_widget(card)
                except Exception as exc:
                    self.db.log_error(SCREEN, "_build_ui_card_loop", exc)

            scroll.add_widget(content)
            root.add_widget(scroll)
            self.add_widget(root)
        except Exception as exc:
            self.db.log_error(SCREEN, "_build_ui", exc)
            traceback.print_exc()

    def go_back(self):
        try:
            if self.manager:
                self.manager.transition.direction = "right"
                self.manager.current = "dashboard"
        except Exception as exc:
            self.db.log_error(SCREEN, "go_back", exc)
