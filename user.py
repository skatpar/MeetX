# user.py

from location import Location
from meeting_time import MeetingTime

class User:
    def __init__(self, name, current_location, availability=None, meeting_points=None):
        self.name = name
        self.current_location = current_location  # Location object
        self.availability = availability if availability else []  # List of MeetingTime objects
        self.meeting_points = meeting_points if meeting_points else [current_location]  # List of Location objects

    def add_availability(self, meeting_time):
        self.availability.append(meeting_time)

    def add_meeting_point(self, location):
        self.meeting_points.append(location)

    def __repr__(self):
        return f"User: {self.name}, Location: {self.current_location}, Availability: {self.availability}, Meeting Points: {self.meeting_points}"
