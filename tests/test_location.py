# tests/test_location.py

import unittest
from location import Location

class TestLocation(unittest.TestCase):

    def test_location_creation(self):
        loc = Location("Test Place", 40.7128, -74.0060)
        self.assertEqual(loc.name, "Test Place")
        self.assertEqual(loc.latitude, 40.7128)
        self.assertEqual(loc.longitude, -74.0060)

if __name__ == "__main__":
    unittest.main()
