import traceback
from kivymd.uix.screen     import MDScreen
from kivymd.uix.boxlayout  import MDBoxLayout
from kivymd.uix.toolbar    import MDTopAppBar
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.label      import MDLabel
from kivy.uix.scrollview   import ScrollView
from kivy.metrics          import dp

from database import Database

SCREEN = "PlacementsScreen"

class PlacementsScreen(MDScreen):
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
                title="Placement Details",
                anchor_title="center",
                left_action_items=[["arrow-left", lambda x: self.go_back()]],
                md_bg_color=(0.15,0.35,0.7,1),
                elevation=2,
            ))
            scroll = ScrollView()
            content = MDBoxLayout(orientation="vertical", adaptive_height=True,
                                  padding=dp(10), spacing=dp(20))

            def add_ay_section(year_text, table_data):
                try:
                    content.add_widget(MDLabel(
                        text=year_text, bold=True, font_style="H6",
                        padding=[dp(10), dp(10)],
                    ))
                    content.add_widget(MDDataTable(
                        size_hint=(1, None), height=dp(160),
                        use_pagination=False,
                        column_data=[
                            ("S.No",dp(15)),("Course",dp(25)),("Registered",dp(25)),
                            ("Placed",dp(20)),("Offers",dp(20)),("Highest",dp(20)),
                            ("Median",dp(20)),("Avg",dp(20)),("%",dp(15)),
                        ],
                        row_data=table_data,
                    ))
                except Exception as exc:
                    self.db.log_error(SCREEN, "add_ay_section", exc)

            add_ay_section("A.Y 2024-25", [
                ("1","MBA","46","12","21","6.6L","6.6L","6.6L","26%"),
                ("Total","","46","12","21","","","","26%"),
            ])
            add_ay_section("A.Y 2023-24",
                [("1","MBA","50","30","45","7.0L","5.5L","6.0L","60%")])
            add_ay_section("A.Y 2022-23",
                [("1","MBA","48","35","50","8.0L","6.0L","6.5L","72%")])
            add_ay_section("A.Y 2021-22",
                [("1","MBA","45","40","55","7.5L","5.8L","6.2L","88%")])

            scroll.add_widget(content)
            layout.add_widget(scroll)
            self.add_widget(layout)
        except Exception as exc:
            self.db.log_error(SCREEN, "_build_ui", exc)
            traceback.print_exc()

    def go_back(self):
        try:
            self.manager.transition.direction = "right"
            self.manager.current = "dashboard"
        except Exception as exc:
            self.db.log_error(SCREEN, "go_back", exc)
