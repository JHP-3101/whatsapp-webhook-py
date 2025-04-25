from threading import Timer
from datetime import datetime

class Session:
    def __init__(self, phone_number, on_timeout):
        self.phone_number = phone_number
        self.last_interaction = datetime.now()
        self.timeout_task = None
        self.on_timeout = on_timeout

    def refresh(self):
        self.last_interaction = datetime.now()
        self.cancel_timeout()
        self.schedule_timeout()

    def schedule_timeout(self):
        self.timeout_task = Timer(300, self.timeout)
        self.timeout_task.start()

    def cancel_timeout(self):
        if self.timeout_task:
            self.timeout_task.cancel()

    def timeout(self):
        self.on_timeout(self.phone_number)

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def start_or_refresh_session(self, phone_number, on_timeout):
        if phone_number not in self.sessions:
            self.sessions[phone_number] = Session(phone_number, on_timeout)
        self.sessions[phone_number].refresh()

    def end_session(self, phone_number):
        session = self.sessions.pop(phone_number, None)
        if session:
            session.cancel_timeout()

session_manager = SessionManager()
