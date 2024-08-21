# tests/test_user.py

import unittest
from user import User
from location import Location
from meeting_time import MeetingTime

class TestUser(unittest.TestCase):

    def setUp(self):
        self.location = Location("Test Place", 40.7128, -74.0060)
        self.user = User("Test User", self.location)

    def test_user_creation(self):
        self.assertEqual(self.user.name, "Test User")
        self.assertEqual(self.user.current_location, self.location)

    def test_add_availability(self):
        mt = MeetingTime("Monday", "10:00", "12:00", "America/New_York")
        self.user.add_availability(mt)
        self.assertIn(mt, self.user.availability)

    def test_add_meeting_point(self):
        new_location = Location("New Meeting Point", 40.730610, -73.935242)
        self.user.add_meeting_point(new_location)
        self.assertIn(new_location, self.user.meeting_points)

if __name__ == "__main__":
    unittest.main()
