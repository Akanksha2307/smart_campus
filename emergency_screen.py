import traceback
from kivymd.uix.screen    import MDScreen
from kivymd.uix.toolbar   import MDTopAppBar
from kivymd.uix.label     import MDLabel
from kivymd.uix.card      import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button    import MDIconButton, MDRaisedButton
from kivy.uix.scrollview  import ScrollView
from kivy.metrics         import dp

from database import Database

SCREEN = "EmergencyScreen"

class EmergencyScreen(MDScreen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.db = Database()
            layout = MDBoxLayout(orientation="vertical", md_bg_color=(1, 0.95, 0.95, 1))

            layout.add_widget(MDTopAppBar(
                title="Emergency Services",
                elevation=4,
                md_bg_color=(0.8, 0, 0, 1),
                left_action_items=[["arrow-left", lambda x: self.go_back()]],
            ))

            scroll = ScrollView(do_scroll_x=False)
            container = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding="20dp",
                spacing="15dp",
            )

            # Status banner
            status_card = MDCard(
                orientation="horizontal",
                padding="15dp",
                size_hint=(1, None),
                height="70dp",
                radius=[15],
                md_bg_color=(0.9, 0, 0, 1),
                elevation=2,
            )
            status_card.add_widget(MDIconButton(
                icon="alert-decagram",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
            ))
            status_card.add_widget(MDLabel(
                text="EMERGENCY MODE ACTIVE",
                bold=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                halign="center",
            ))
            container.add_widget(status_card)

            container.add_widget(MDLabel(
                text="Nearest Safety Points",
                font_style="H6",
                bold=True,
            ))

            locations = [
                ("Nearest Exit", "East Gate (40m)", "exit-run"),
                ("Medical Room", "Health Center (100m)", "medical-bag"),
            ]
            for title, desc, icon in locations:
                loc_card = MDCard(
                    orientation="horizontal",
                    padding="12dp",
                    size_hint=(1, None),
                    height="85dp",
                    radius=[15],
                    elevation=1,
                )
                loc_card.add_widget(MDIconButton(icon=icon, icon_size="32sp"))
                info = MDBoxLayout(orientation="vertical", padding=["10dp", 0, 0, 0])
                info.add_widget(MDLabel(text=title, font_style="Subtitle1", bold=True))
                info.add_widget(MDLabel(text=desc, font_style="Caption",
                                        theme_text_color="Secondary"))
                loc_card.add_widget(info)
                container.add_widget(loc_card)

            container.add_widget(MDLabel(text="Immediate Contact", font_style="H6", bold=True))
            container.add_widget(MDRaisedButton(
                text="CALL SECURITY: +91 98765 43210",
                md_bg_color=(0.8, 0, 0, 1),
                size_hint_x=1,
                height="50dp",
                font_style="Button",
            ))

            scroll.add_widget(container)
            layout.add_widget(scroll)
            self.add_widget(layout)
        except Exception as exc:
            self.db.log_error(SCREEN, "__init__", exc)
            traceback.print_exc()

    def go_back(self):
        try:
            self.manager.current = "dashboard"
        except Exception as exc:
            self.db.log_error(SCREEN, "go_back", exc)
