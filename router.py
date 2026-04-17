import traceback
from kivy.uix.screenmanager import ScreenManager

from login_screen          import LoginScreen
from register_screen       import RegisterScreen
from manage_users_screen   import ManageUsersScreen
from dashboard_screen      import DashboardScreen
from navigation_screen     import NavigationScreen
from faculty               import FacultyScreen
from emergency_screen      import EmergencyScreen
from events_screen         import EventsScreen
from chatbot_screen        import ChatbotScreen
from exams_screen          import ExamsScreen
from forms_screen          import FormsScreen
from placements_screen     import PlacementsScreen
from notices_screen        import NoticesScreen
from api_settings_screen   import APISettingsScreen
from issues_monitor_screen import IssuesMonitorScreen
from database              import Database


class AppRouter(ScreenManager):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self._db = Database()

            # ── Core screens ──────────────────────────────────────────────────
            self.add_widget(LoginScreen(name="login"))
            self.add_widget(RegisterScreen(name="register"))
            self.add_widget(DashboardScreen(name="dashboard"))
            self.add_widget(NavigationScreen(name="navigation"))
            self.add_widget(ManageUsersScreen(name="manage_users"))

            # ── API settings (required for Chatbot & Dashboard) ───────────────
            self.add_widget(APISettingsScreen(name="api_settings"))

            # ── Feature screens ───────────────────────────────────────────────
            self.add_widget(FacultyScreen(name="faculty"))
            self.add_widget(EmergencyScreen(name="emergency"))
            self.add_widget(EventsScreen(name="events"))
            self.add_widget(ChatbotScreen(name="chatbot"))
            self.add_widget(ExamsScreen(name="exams"))
            self.add_widget(FormsScreen(name="forms"))
            self.add_widget(PlacementsScreen(name="placements"))
            self.add_widget(NoticesScreen(name="notices"))

            # ── Issues Monitor ────────────────────────────────────────────────
            self.add_widget(IssuesMonitorScreen(name="issues_monitor"))

            self.logged_user_name = ""   # set by LoginScreen on successful login
            self.current = "login"
        except Exception as exc:
            self._db.log_error("AppRouter", "__init__", exc)
            traceback.print_exc()

    def change_screen(self, screen_name):
        try:
            if self.has_screen(screen_name):
                self.current = screen_name
            else:
                print(f"[AppRouter] Screen '{screen_name}' not found!")
        except Exception as exc:
            self._db.log_error("AppRouter", "change_screen", exc)
