import traceback
from kivymd.uix.screen     import MDScreen
from kivymd.uix.boxlayout  import MDBoxLayout
from kivymd.uix.toolbar    import MDTopAppBar
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.textfield  import MDTextField
from kivy.metrics          import dp
from database import Database

class NoticesScreen(MDScreen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.db = Database()
            # Store static data for filtering
            self.raw_notices = [
                ("1","23 Jan 2026","Final List of Gold Medal Recipients of XIV Convocation"),
                ("2","09 Jan 2026","Six Months Online Certificate Courses - JAN 2026 (DILT)"),
                ("3","03 Jan 2026","Six Months Online Certificate Courses - DILT, JNTUH"),
                ("4","29 Dec 2025","Workshop: Defend the Digital Frontier (Blue Team Security)"),
                ("5","29 Oct 2025","M.Tech Spot Admissions-2025-26"),
                ("6","28 Oct 2025","Searching & Sorting Coding Interviews Bootcamp"),
                ("7","26 Oct 2025","Spot Admissions B.Pharmacy / B.Tech Biotechnology"),
                ("8","23 Aug 2025","Counselling Notification: International Integrated Masters"),
            ]
            self._build_ui()
        except Exception as exc:
            self.db.log_error("NoticesScreen", "__init__", exc)

    def _build_ui(self):
        layout = MDBoxLayout(orientation="vertical", md_bg_color=(0.98,0.98,1,1))
        layout.add_widget(MDTopAppBar(
            title="Notifications", anchor_title="center",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            md_bg_color=(0.15,0.35,0.7,1),
        ))

        container = MDBoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        
        self.search_input = MDTextField(
            hint_text="Search Title or Date...",
            mode="round", icon_left="magnify",
        )
        # Binds the search logic to the text input
        self.search_input.bind(text=self._filter_data)
        container.add_widget(self.search_input)

        self.data_table = MDDataTable(
            size_hint=(1, 1),
            use_pagination=True,
            column_data=[("S.No.",dp(15)),("Date",dp(30)),("Title",dp(100))],
            row_data=self.raw_notices,
        )
        container.add_widget(self.data_table)
        layout.add_widget(container)
        self.add_widget(layout)

    def _filter_data(self, instance, value):
        query = value.lower().strip()
        # Filters based on Title (Index 2) or Date (Index 1)
        filtered = [row for row in self.raw_notices if query in row[2].lower() or query in row[1].lower()]
        self.data_table.row_data = filtered

    def go_back(self):
        self.manager.current = "dashboard"