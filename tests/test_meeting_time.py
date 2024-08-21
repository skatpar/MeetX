# tests/test_meeting_time.py

import unittest
from meeting_time import MeetingTime

class TestMeetingTime(unittest.TestCase):

    def test_meeting_time_creation(self):
        mt = MeetingTime("Monday", "10:00", "12:00", "America/New_York")
        self.assertEqual(mt.day, "Monday")
        self.assertEqual(mt.start_time, "10:00")
        self.assertEqual(mt.end_time, "12:00")
        self.assertEqual(mt.timezone, "America/New_York")

if __name__ == "__main__":
    unittest.main()
