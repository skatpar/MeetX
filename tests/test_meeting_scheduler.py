import unittest
from meeting_scheduler import MeetingScheduler
from user import User
from location import Location
from meeting_time import MeetingTime

class TestMeetingScheduler(unittest.TestCase):

    def setUp(self):
        loc1 = Location("Place 1", 40.7128, -74.0060)  # New York City
        loc2 = Location("Place 2", 40.730610, -73.935242)  # Brooklyn
        loc3 = Location("Place 3", 40.748817, -73.985428)  # Empire State Building
        
        self.user1 = User("User 1", loc1, [MeetingTime("Monday", "10:00", "12:00", "America/New_York")], [loc1])
        self.user2 = User("User 2", loc2, [MeetingTime("Monday", "11:00", "13:00", "America/New_York")], [loc2])
        self.user3 = User("User 3", loc3, [MeetingTime("Monday", "10:30", "12:30", "America/New_York")], [loc3])
        
        self.scheduler = MeetingScheduler([self.user1, self.user2, self.user3])

    def test_find_common_times(self):
        common_times = self.scheduler.find_common_times()
        self.assertIn("Monday", common_times)
        self.assertEqual(len(common_times["Monday"]), 1)  # Expecting one overlapping time slot

    def test_calculate_distances_to_meeting_point(self):
        meeting_point = self.user1.current_location
        distances = self.scheduler.calculate_distances_to_meeting_point(meeting_point)
        self.assertEqual(len(distances), 3)
        for distance in distances.values():
            self.assertGreater(distance, 0)  # Distances should be positive

    def test_suggest_meeting_places(self):
        common_times = self.scheduler.find_common_times()
        suggestions = self.scheduler.suggest_meeting_places(common_times)
        
        # Check if the "Monday" key is in suggestions and if it's not empty
        self.assertIn("Monday", suggestions)
        self.assertTrue(len(suggestions["Monday"]) > 0)

if __name__ == "__main__":
    unittest.main()
