import traceback
from kivymd.uix.screen    import MDScreen
from kivymd.uix.toolbar   import MDTopAppBar
from kivymd.uix.label     import MDLabel
from kivymd.uix.card      import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button    import MDIconButton
from kivy.uix.scrollview  import ScrollView
from kivy.metrics         import dp

from database import Database

SCREEN = "EventsScreen"

class EventsScreen(MDScreen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.db = Database()
            layout = MDBoxLayout(orientation="vertical")

            layout.add_widget(MDTopAppBar(
                title="Campus Events",
                elevation=4,
                left_action_items=[["arrow-left", lambda x: self.go_back()]],
                right_action_items=[["refresh", lambda x: self.refresh_events()]],
            ))

            scroll = ScrollView(do_scroll_x=False)
            self.container = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding="16dp",
                spacing="12dp",
            )
            self.load_events()
            scroll.add_widget(self.container)
            layout.add_widget(scroll)
            self.add_widget(layout)
        except Exception as exc:
            self.db.log_error(SCREEN, "__init__", exc)
            traceback.print_exc()

    def load_events(self):
        try:
            self.container.clear_widgets()
            events = self.db.get_events()
            if not events:
                self.container.add_widget(MDLabel(
                    text="No upcoming events found.",
                    halign="center",
                    font_style="Subtitle1",
                    theme_text_color="Secondary",
                    padding=(0, dp(100)),
                ))
            else:
                for event in events:
                    event_card = MDCard(
                        orientation="horizontal",
                        padding="12dp",
                        size_hint=(1, None),
                        height="80dp",
                        radius=[15],
                        elevation=1,
                        ripple_behavior=True,
                    )
                    icon_box = MDBoxLayout(size_hint=(None, 1), width="50dp")
                    icon_box.add_widget(MDIconButton(
                        icon="calendar-star",
                        theme_text_color="Custom",
                        text_color=(0.1, 0.5, 0.8, 1),
                    ))
                    content_box = MDBoxLayout(orientation="vertical", spacing="4dp")
                    content_box.add_widget(MDLabel(
                        text=event,
                        font_style="H6",
                        bold=True,
                        shorten=True,
                        shorten_from="right",
                    ))
                    content_box.add_widget(MDLabel(
                        text="Bhoj Reddy Campus • Tap for details",
                        font_style="Caption",
                        theme_text_color="Secondary",
                    ))
                    event_card.add_widget(icon_box)
                    event_card.add_widget(content_box)
                    self.container.add_widget(event_card)
        except Exception as exc:
            self.db.log_error(SCREEN, "load_events", exc)

    def refresh_events(self):
        try:
            self.load_events()
        except Exception as exc:
            self.db.log_error(SCREEN, "refresh_events", exc)

    def go_back(self):
        try:
            self.manager.current = "dashboard"
        except Exception as exc:
            self.db.log_error(SCREEN, "go_back", exc)
