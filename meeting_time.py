# meeting_time.py

class MeetingTime:
    def __init__(self, day, start_time, end_time, timezone):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.timezone = timezone

    def __repr__(self):
        return f"{self.day}: {self.start_time}-{self.end_time} ({self.timezone})"
