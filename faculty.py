from __future__ import annotations   # enables str | None on Python 3.9
import traceback
from dataclasses import dataclass
from kivymd.uix.screen    import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card      import MDCard
from kivymd.uix.label     import MDLabel
from kivymd.uix.button    import MDIconButton
from kivymd.uix.toolbar   import MDTopAppBar
from kivy.uix.scrollview  import ScrollView
from kivy.metrics         import dp

from database import Database

SCREEN = "FacultyScreen"

@dataclass
class Faculty:
    id: int
    name: str
    department: str
    room: str
    email: str | None = None

    @staticmethod
    def from_db(row):
        # DB stores 4 cols (id, name, room, department); email is optional col 5.
        # Guard against both orderings: treat col[2] as room, col[3] as dept.
        email = row[4] if len(row) > 4 else None
        return Faculty(id=row[0], name=row[1], department=row[3],
                       room=row[2], email=email)


class FacultyScreen(MDScreen):
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
            layout = MDBoxLayout(orientation="vertical", md_bg_color=(0.98,0.98,1,1))
            layout.add_widget(MDTopAppBar(
                title="Department & Faculty",
                anchor_title="center",
                left_action_items=[["arrow-left", lambda x: self.go_back()]],
                md_bg_color=(0.15,0.35,0.7,1),
                elevation=2,
            ))

            scroll   = ScrollView(do_scroll_x=False, bar_width=dp(2))
            content  = MDBoxLayout(orientation="vertical", adaptive_height=True,
                                   padding=dp(16), spacing=dp(15))

            faculty_data = [
                (1,"P Sumalatha",  "S-102","Computer Science",       "Sumalatha.p@bhojreddy.ac.in"),
                (2,"R Dinesh Kumar","S-105","Computer Science",       "Dinesh.p@bhojreddy.ac.in"),
                (3,"M Vinod",      "S-203","Computer Science",       "Vinod.p@bhojreddy.ac.in"),
                (4,"P Deepthi",    "S-204","Computer Science",       "Deepthi.p@bhojreddy.ac.in"),
                (5,"B Shireesha",  "S-305","Computer Science",       "Shireesha.p@bhojreddy.ac.in"),
                (6,"Dr. P. Madhavi","Room 401","Computer Science",   "madhavi.p@bhojreddy.ac.in"),
                (7,"Prof. K. Ramesh","Room 302","Information Technology","ramesh.k@bhojreddy.ac.in"),
                (8,"Dr. S. Anitha","Room 215","Electronics & Comm",  "anitha.s@bhojreddy.ac.in"),
                (9,"Mr. V. Suresh","Room 105","Mechanical Eng",      "suresh.v@bhojreddy.ac.in"),
                (10,"Dr. M. Lakshmi","Room 208","Electrical Eng",    "lakshmi.m@bhojreddy.ac.in"),
            ]

            for row in faculty_data:
                try:
                    fac = Faculty.from_db(row)
                    card = MDCard(
                        orientation="horizontal", padding=dp(15),
                        size_hint=(1, None), height=dp(110),
                        radius=[20], elevation=1, md_bg_color=(1,1,1,1),
                        ripple_behavior=True,
                    )
                    card.add_widget(MDIconButton(
                        icon="account-tie-circle", icon_size="48sp",
                        theme_text_color="Custom", text_color=(0.15,0.35,0.7,1),
                        pos_hint={"center_y":.5},
                    ))
                    info = MDBoxLayout(orientation="vertical",
                                       pos_hint={"center_y":.5},
                                       padding=[dp(10),0,0,0])
                    info.add_widget(MDLabel(text=fac.name, bold=True, font_style="Subtitle1"))
                    info.add_widget(MDLabel(text=fac.department, font_style="Caption",
                        theme_text_color="Secondary"))
                    info.add_widget(MDLabel(text=f"Location: {fac.room}",
                        font_style="Caption", theme_text_color="Hint"))
                    card.add_widget(info)
                    card.add_widget(MDIconButton(
                        icon="email-fast-outline",
                        theme_text_color="Custom",
                        text_color=(0.15,0.35,0.7,0.6),
                        pos_hint={"center_y":.5},
                        on_release=lambda x, e=fac.email: self.contact_faculty(e),
                    ))
                    content.add_widget(card)
                except Exception as exc:
                    self.db.log_error(SCREEN, "_build_ui_card_loop", exc)

            scroll.add_widget(content)
            layout.add_widget(scroll)
            self.add_widget(layout)
        except Exception as exc:
            self.db.log_error(SCREEN, "_build_ui", exc)
            traceback.print_exc()

    def contact_faculty(self, email):
        try:
            print(f"Opening email client for: {email}")
        except Exception as exc:
            self.db.log_error(SCREEN, "contact_faculty", exc)

    def go_back(self):
        try:
            self.manager.transition.direction = "right"
            self.manager.current = "dashboard"
        except Exception as exc:
            self.db.log_error(SCREEN, "go_back", exc)
