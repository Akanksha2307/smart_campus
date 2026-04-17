import sqlite3
import os
import traceback
from datetime import datetime


def _get_writable_dir():
    """
    Return a writable directory for the database file.
    On Android the APK bundle is read-only, so we must use the app's
    private files directory.  On desktop we fall back to the script dir.
    """
    try:
        from android.storage import app_storage_path   # type: ignore
        d = app_storage_path()
        os.makedirs(d, exist_ok=True)
        return d
    except Exception:
        pass
    # Desktop fallback
    return os.path.dirname(os.path.abspath(__file__))


class Database:
    def __init__(self):
        base_dir     = _get_writable_dir()
        self.db_path = os.path.join(base_dir, "campus.db")

        self.conn   = sqlite3.connect(self.db_path, timeout=20,
                                      check_same_thread=False)
        self.cursor = self.conn.cursor()

        try:
            self.cursor.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError:
            pass

        self._create_tables()
        self._fix_migrations()

    def _create_tables(self):
        tables = {
            "users":      "id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT DEFAULT 'student'",
            "faculty":    "id INTEGER PRIMARY KEY, name TEXT, room TEXT, department TEXT",
            "events":     "id INTEGER PRIMARY KEY, title TEXT, date TEXT",
            "emergency":  "id INTEGER PRIMARY KEY, message TEXT",
            "exams":      "id INTEGER PRIMARY KEY, subject TEXT, code TEXT, grade TEXT, result TEXT",
            "notices":    "id INTEGER PRIMARY KEY, title TEXT, date TEXT",
            "placements": "id INTEGER PRIMARY KEY, company TEXT, role TEXT, package TEXT",
            "forms":      "id INTEGER PRIMARY KEY, form_name TEXT, link TEXT",
        }
        for table_name, schema in tables.items():
            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
            )

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp     TEXT    NOT NULL,
                screen        TEXT    NOT NULL,
                function_name TEXT,
                error_type    TEXT,
                error_message TEXT,
                traceback     TEXT
            )
        """)
        self.conn.commit()
        self._seed_data()

    def _fix_migrations(self):
        try:
            self.cursor.execute("SELECT department FROM faculty LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute(
                "ALTER TABLE faculty ADD COLUMN department TEXT DEFAULT 'General'"
            )
            self.conn.commit()
        try:
            self.cursor.execute("SELECT role FROM users LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute(
                "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'"
            )
            self.conn.commit()

    def _seed_data(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            new_users = [
                ("Meghana", "123", "admin"),
                ("Navya",   "123", "student"),
                ("Akansha", "123", "student"),
            ]
            self.cursor.executemany(
                "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                new_users,
            )

        seed_configs = {
            "faculty": ("INSERT INTO faculty (name, room, department) VALUES (?, ?, ?)", [
                ("P Sumalatha",    "S-102", "Computer Science"),
                ("R Dinesh Kumar", "S-105", "Computer Science"),
                ("M Vinod",        "S-203", "Computer Science"),
                ("P Deepthi",      "S-204", "Computer Science"),
                ("B Shireesha",    "S-305", "Computer Science"),
            ]),
            "exams": ("INSERT INTO exams (subject, code, grade, result) VALUES (?, ?, ?, ?)", [
                ("Data Structures", "CS301", "A+", "PASS"),
                ("Maths III",       "MA201", "B",  "PASS"),
                ("Microprocessors", "EC402", "F",  "FAIL"),
                ("Python",          "IT101", "O",  "PASS"),
                ("OS",              "CS405", "B+", "PASS"),
            ]),
            "notices": ("INSERT INTO notices (title, date) VALUES (?, ?)", [
                ("Mid-term Schedule", "2024-10-05"),
                ("Annual Day",        "2024-10-12"),
                ("Library Notice",    "2024-10-14"),
                ("Fee Deadline",      "2024-10-20"),
                ("Hackathon 2024",    "2024-11-01"),
            ]),
            "placements": ("INSERT INTO placements (company, role, package) VALUES (?, ?, ?)", [
                ("Google",    "SDE",       "45 LPA"),
                ("Accenture", "Associate", "6.5 LPA"),
                ("Microsoft", "Analyst",   "18 LPA"),
                ("TCS",       "Ninja",     "3.6 LPA"),
                ("Amazon",    "SDE-1",     "32 LPA"),
            ]),
            "events": ("INSERT INTO events (title, date) VALUES (?, ?)", [
                ("Tech Symposium", "Oct 25"),
                ("AI Workshop",    "Nov 02"),
                ("Sports Meet",    "Nov 15"),
                ("Music Night",    "Dec 05"),
                ("Alumni Meet",    "Dec 20"),
            ]),
            "emergency": ("INSERT INTO emergency (message) VALUES (?)", [
                ("Security: +91 9876543210",),
                ("Health Center: Block A",),
                ("Fire Station: 101",),
                ("Ambulance: 108",),
                ("Police: 100",),
            ]),
            "forms": ("INSERT INTO forms (form_name, link) VALUES (?, ?)", [
                ("Scholarship", "http://link.com"),
                ("Leave Form",  "http://link.com"),
                ("Bus Pass",    "http://link.com"),
                ("ID Card",     "http://link.com"),
                ("Hostel",      "http://link.com"),
            ]),
        }

        for table, (query, data) in seed_configs.items():
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.executemany(query, data)

        self.conn.commit()

    # ── GETTERS ───────────────────────────────────────────────────────────────

    def validate_login(self, username, password):
        self.cursor.execute(
            "SELECT 1 FROM users WHERE username=? AND password=?",
            (username, password),
        )
        return self.cursor.fetchone() is not None

    def get_user_role(self, username):
        self.cursor.execute("SELECT role FROM users WHERE username=?", (username,))
        row = self.cursor.fetchone()
        return row[0] if row else "student"

    # ── USER MANAGEMENT ───────────────────────────────────────────────────────

    def get_all_users(self):
        self.cursor.execute("SELECT id, username, role FROM users ORDER BY id")
        return self.cursor.fetchall()

    def add_user(self, username, password, role="student"):
        if not username.strip() or not password.strip():
            return False, "Username and password cannot be empty."
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username.strip(), password.strip(), role),
            )
            self.conn.commit()
            return True, ""
        except sqlite3.IntegrityError:
            return False, f"Username '{username}' already exists."
        except Exception as e:
            return False, str(e)

    def username_exists(self, username):
        self.cursor.execute(
            "SELECT 1 FROM users WHERE username=?", (username.strip(),)
        )
        return self.cursor.fetchone() is not None

    def delete_user(self, user_id):
        try:
            self.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            self.conn.commit()
            return True
        except Exception:
            return False

    def update_user_password(self, user_id, new_password):
        try:
            self.cursor.execute(
                "UPDATE users SET password=? WHERE id=?", (new_password, user_id)
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_faculty(self):
        self.cursor.execute("SELECT name, room, department FROM faculty")
        return self.cursor.fetchall()

    def get_events(self):
        self.cursor.execute("SELECT title, date FROM events")
        return [f"{row[0]} - {row[1]}" for row in self.cursor.fetchall()]

    def get_exam_results(self):
        self.cursor.execute("SELECT subject, code, grade, result FROM exams")
        return self.cursor.fetchall()

    def get_notices(self):
        self.cursor.execute("SELECT title, date FROM notices")
        return self.cursor.fetchall()

    def get_placements(self):
        self.cursor.execute("SELECT company, role, package FROM placements")
        return self.cursor.fetchall()

    def get_emergency_info(self):
        self.cursor.execute("SELECT message FROM emergency")
        return [row[0] for row in self.cursor.fetchall()]

    def get_forms(self):
        self.cursor.execute("SELECT form_name, link FROM forms")
        return self.cursor.fetchall()

    # ── ERROR LOGS ────────────────────────────────────────────────────────────

    def log_error(self, screen: str, function_name: str, exc: Exception,
                  tb_str: str = None):
        try:
            timestamp     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_type    = type(exc).__name__
            error_message = str(exc)
            tb            = tb_str if tb_str else traceback.format_exc()
            self.cursor.execute(
                """INSERT INTO error_logs
                       (timestamp, screen, function_name, error_type, error_message, traceback)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (timestamp, screen, function_name, error_type, error_message, tb),
            )
            self.conn.commit()
        except Exception as inner:
            print(f"[ErrorLogger] Failed to write log: {inner}")

    def get_error_logs(self):
        self.cursor.execute(
            "SELECT id, timestamp, screen, function_name, error_type, error_message "
            "FROM error_logs ORDER BY id DESC"
        )
        return self.cursor.fetchall()

    def get_error_log_detail(self, log_id: int):
        self.cursor.execute("SELECT traceback FROM error_logs WHERE id=?", (log_id,))
        row = self.cursor.fetchone()
        return row[0] if row else "No detail available."

    def clear_error_logs(self):
        self.cursor.execute("DELETE FROM error_logs")
        self.conn.commit()

    def get_error_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM error_logs")
        total = self.cursor.fetchone()[0]
        self.cursor.execute(
            "SELECT COUNT(*) FROM error_logs WHERE timestamp >= date('now','-1 day')"
        )
        last_24h = self.cursor.fetchone()[0]
        self.cursor.execute(
            "SELECT screen, COUNT(*) as cnt FROM error_logs "
            "GROUP BY screen ORDER BY cnt DESC LIMIT 1"
        )
        row = self.cursor.fetchone()
        top_screen = row[0] if row else "—"
        return {"total": total, "last_24h": last_24h, "top_screen": top_screen}
