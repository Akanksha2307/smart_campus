"""
issues_monitor_screen.py – Smart Campus
========================================
Displays all application exceptions that were captured by try/except
blocks across every screen.  Only ERRORS are stored — normal activity
is never recorded here.

Features
--------
* Summary stat cards (Total bugs / Last 24 h / Most-affected screen)
* Scrollable list of error cards (newest first)
* Tap any card to view the full stack-trace detail
* "Clear All Logs" button (admin clean-up)
* Refresh button on the toolbar
"""

import traceback

from kivy.metrics        import dp
from kivy.uix.scrollview import ScrollView
from kivy.clock          import Clock

from kivymd.uix.screen    import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card      import MDCard
from kivymd.uix.label     import MDLabel
from kivymd.uix.button    import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.toolbar   import MDTopAppBar
from kivymd.uix.dialog    import MDDialog
from kivymd.uix.snackbar  import MDSnackbar

from database import Database


# ─────────────────────────────────────────────────────────────────────────────
# Helper: colour for severity badge
# ─────────────────────────────────────────────────────────────────────────────
_SEVERITY_COLORS = {
    "AttributeError":    (0.85, 0.2,  0.1,  1),
    "TypeError":         (0.85, 0.2,  0.1,  1),
    "ValueError":        (0.9,  0.5,  0.0,  1),
    "ImportError":       (0.9,  0.5,  0.0,  1),
    "ModuleNotFoundError":(0.9, 0.5,  0.0,  1),
    "KeyError":          (0.7,  0.1,  0.5,  1),
    "IndexError":        (0.7,  0.1,  0.5,  1),
    "Exception":         (0.35, 0.35, 0.35, 1),
}

def _error_color(error_type: str):
    return _SEVERITY_COLORS.get(error_type, (0.35, 0.35, 0.35, 1))


# ─────────────────────────────────────────────────────────────────────────────
class IssuesMonitorScreen(MDScreen):
    """
    Page: Issues / Bug Monitor
    Route name registered in router.py: "issues_monitor"
    """

    SCREEN = "IssuesMonitorScreen"   # used when this screen itself logs errors

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.db     = Database()
            self.dialog = None          # holds the detail dialog instance
            self._build_ui()
        except Exception as exc:
            print(f"[{self.SCREEN}] __init__ error: {exc}")
            traceback.print_exc()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        try:
            root = MDBoxLayout(orientation="vertical", md_bg_color=(0.95, 0.95, 1.0, 1))

            # 1. TOP APP BAR
            root.add_widget(MDTopAppBar(
                title="Issues Monitor",
                anchor_title="center",
                left_action_items=[["arrow-left", lambda x: self.go_back()]],
                right_action_items=[
                    ["refresh", lambda x: self.refresh()],
                    ["delete-sweep-outline", lambda x: self.confirm_clear()],
                ],
                md_bg_color=(0.6, 0.1, 0.15, 1),   # dark-red toolbar for "alert" feel
                elevation=2,
            ))

            # 2. STATS STRIP
            self.stats_strip = MDBoxLayout(
                orientation="horizontal",
                size_hint=(1, None),
                height=dp(80),
                padding=[dp(12), dp(6), dp(12), dp(6)],
                spacing=dp(8),
                md_bg_color=(0.9, 0.1, 0.2, 0.08),
            )
            root.add_widget(self.stats_strip)

            # 3. SCROLLABLE LOG LIST
            scroll = ScrollView(do_scroll_x=False, bar_width=dp(2))
            self.log_container = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                padding=[dp(12), dp(8), dp(12), dp(16)],
                spacing=dp(10),
            )
            scroll.add_widget(self.log_container)
            root.add_widget(scroll)

            self.add_widget(root)
        except Exception as exc:
            self.db.log_error(self.SCREEN, "_build_ui", exc)
            print(f"[{self.SCREEN}] _build_ui error: {exc}")

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_pre_enter(self, *args):
        """Refresh data every time the screen is shown."""
        try:
            self.refresh()
        except Exception as exc:
            self.db.log_error(self.SCREEN, "on_pre_enter", exc)

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh(self):
        """Reload stats + log list from the database."""
        try:
            self._load_stats()
            self._load_logs()
        except Exception as exc:
            self.db.log_error(self.SCREEN, "refresh", exc)

    def _load_stats(self):
        try:
            # Clear previous stat cards
            self.stats_strip.clear_widgets()

            stats = self.db.get_error_stats()

            stat_items = [
                ("bug-outline",      str(stats["total"]),      "Total Bugs",     (0.7, 0.1, 0.2, 1)),
                ("clock-alert",      str(stats["last_24h"]),   "Last 24 h",      (0.9, 0.5, 0.0, 1)),
                ("layers-triple",    stats["top_screen"][:12], "Most Affected",  (0.2, 0.4, 0.7, 1)),
            ]

            for icon, value, label, color in stat_items:
                card = MDCard(
                    orientation="vertical",
                    padding=dp(8),
                    radius=[12],
                    elevation=1,
                    size_hint=(1, 1),
                    md_bg_color=(1, 1, 1, 1),
                )
                card.add_widget(MDIconButton(
                    icon=icon,
                    theme_text_color="Custom",
                    text_color=color,
                    pos_hint={"center_x": 0.5},
                ))
                card.add_widget(MDLabel(
                    text=value,
                    bold=True,
                    halign="center",
                    font_style="Subtitle1",
                    theme_text_color="Custom",
                    text_color=color,
                ))
                card.add_widget(MDLabel(
                    text=label,
                    halign="center",
                    font_style="Caption",
                    theme_text_color="Secondary",
                ))
                self.stats_strip.add_widget(card)
        except Exception as exc:
            self.db.log_error(self.SCREEN, "_load_stats", exc)

    def _load_logs(self):
        try:
            self.log_container.clear_widgets()

            logs = self.db.get_error_logs()

            if not logs:
                self.log_container.add_widget(MDCard(
                    orientation="vertical",
                    padding=dp(24),
                    radius=[16],
                    elevation=1,
                    size_hint=(1, None),
                    height=dp(120),
                    md_bg_color=(1, 1, 1, 1),
                ))
                # Re-fetch last added card and put a label in it
                empty_card = self.log_container.children[0]
                empty_card.add_widget(MDIconButton(
                    icon="check-circle-outline",
                    icon_size="40sp",
                    theme_text_color="Custom",
                    text_color=(0.1, 0.7, 0.3, 1),
                    pos_hint={"center_x": 0.5},
                ))
                empty_card.add_widget(MDLabel(
                    text="No issues found. App is running clean!",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="Body1",
                ))
                return

            for row in logs:
                log_id, timestamp, screen, func, err_type, err_msg = row
                self._add_log_card(log_id, timestamp, screen, func, err_type, err_msg)

        except Exception as exc:
            self.db.log_error(self.SCREEN, "_load_logs", exc)

    def _add_log_card(self, log_id, timestamp, screen, func, err_type, err_msg):
        try:
            color = _error_color(err_type or "Exception")

            card = MDCard(
                orientation="vertical",
                padding=[dp(14), dp(10), dp(14), dp(10)],
                radius=[14],
                elevation=1,
                size_hint=(1, None),
                height=dp(140),
                md_bg_color=(1, 1, 1, 1),
                ripple_behavior=True,
                on_release=lambda x, lid=log_id, et=err_type, em=err_msg:
                    self.show_detail(lid, et, em),
            )

            # ── Header row: badge + timestamp ──────────────────────────────
            header = MDBoxLayout(
                orientation="horizontal",
                size_hint=(1, None),
                height=dp(30),
                spacing=dp(6),
            )

            # Error-type badge
            badge = MDCard(
                radius=[8],
                padding=[dp(6), dp(2), dp(6), dp(2)],
                size_hint=(None, None),
                height=dp(26),
                width=dp(130),
                md_bg_color=(*color[:3], 0.12),
                elevation=0,
            )
            badge.add_widget(MDLabel(
                text=err_type or "Exception",
                font_style="Caption",
                bold=True,
                theme_text_color="Custom",
                text_color=color,
                halign="center",
            ))
            header.add_widget(badge)

            header.add_widget(MDLabel(
                text=f"#{log_id}  •  {timestamp}",
                font_style="Caption",
                theme_text_color="Hint",
                halign="right",
            ))
            card.add_widget(header)

            # ── Screen + function ──────────────────────────────────────────
            meta = MDBoxLayout(
                orientation="horizontal",
                size_hint=(1, None),
                height=dp(22),
                spacing=dp(4),
            )
            meta.add_widget(MDIconButton(
                icon="layers-triple",
                icon_size="14sp",
                theme_text_color="Custom",
                text_color=(0.4, 0.4, 0.6, 1),
            ))
            meta.add_widget(MDLabel(
                text=f"{screen}  /  {func or '—'}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.3, 0.3, 0.5, 1),
            ))
            card.add_widget(meta)

            # ── Error message ──────────────────────────────────────────────
            short_msg = (err_msg or "")[:100]
            if len(err_msg or "") > 100:
                short_msg += "…"

            card.add_widget(MDLabel(
                text=short_msg,
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint=(1, None),
                height=dp(50),
            ))

            # ── Tap-to-expand hint ─────────────────────────────────────────
            card.add_widget(MDLabel(
                text="Tap to view full traceback →",
                font_style="Caption",
                theme_text_color="Hint",
                halign="right",
                italic=True,
            ))

            self.log_container.add_widget(card)
        except Exception as exc:
            self.db.log_error(self.SCREEN, "_add_log_card", exc)

    # ── Detail dialog ─────────────────────────────────────────────────────────

    def show_detail(self, log_id, err_type, err_msg):
        try:
            if self.dialog:
                self.dialog.dismiss()

            full_tb = self.db.get_error_log_detail(log_id)

            body = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                spacing=dp(8),
                padding=[dp(4), dp(4), dp(4), dp(4)],
            )
            body.add_widget(MDLabel(
                text=f"[b]Type:[/b] {err_type}",
                markup=True,
                font_style="Body2",
                adaptive_height=True,
            ))
            body.add_widget(MDLabel(
                text=f"[b]Message:[/b] {err_msg}",
                markup=True,
                font_style="Body2",
                adaptive_height=True,
            ))

            scroll = ScrollView(size_hint=(1, None), height=dp(200))
            scroll.add_widget(MDLabel(
                text=full_tb or "No traceback available.",
                font_style="Caption",
                adaptive_height=True,
                theme_text_color="Secondary",
            ))
            body.add_widget(scroll)

            self.dialog = MDDialog(
                title=f"Bug #{log_id} Detail",
                type="custom",
                content_cls=body,
                buttons=[
                    MDFlatButton(
                        text="CLOSE",
                        on_release=lambda x: self.dialog.dismiss(),
                    ),
                ],
            )
            self.dialog.open()
        except Exception as exc:
            self.db.log_error(self.SCREEN, "show_detail", exc)

    # ── Clear logs ────────────────────────────────────────────────────────────

    def confirm_clear(self):
        try:
            if self.dialog:
                self.dialog.dismiss()

            self.dialog = MDDialog(
                title="Clear All Logs?",
                text="This will permanently delete all recorded issues. This cannot be undone.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: self.dialog.dismiss(),
                    ),
                    MDRaisedButton(
                        text="CLEAR",
                        md_bg_color=(0.8, 0.1, 0.1, 1),
                        on_release=lambda x: self._do_clear(),
                    ),
                ],
            )
            self.dialog.open()
        except Exception as exc:
            self.db.log_error(self.SCREEN, "confirm_clear", exc)

    def _do_clear(self):
        try:
            if self.dialog:
                self.dialog.dismiss()
            self.db.clear_error_logs()
            self.refresh()
            MDSnackbar(
                MDLabel(
                    text="All issue logs cleared.",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                ),
                bg_color=(0.2, 0.2, 0.2, 1),
                duration=2,
            ).open()
        except Exception as exc:
            self.db.log_error(self.SCREEN, "_do_clear", exc)

    # ── Navigation ────────────────────────────────────────────────────────────

    def go_back(self):
        try:
            if self.manager:
                self.manager.transition.direction = "right"
                self.manager.current = "dashboard"
        except Exception as exc:
            self.db.log_error(self.SCREEN, "go_back", exc)
