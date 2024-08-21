from datetime import datetime
import pytz
from collections import defaultdict
import requests
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in kilometers

def calculate_midpoint(locations):
    avg_lat = sum(loc.latitude for loc in locations) / len(locations)
    avg_lon = sum(loc.longitude for loc in locations) / len(locations)
    return Location("Midpoint", avg_lat, avg_lon)


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



class MeetingTime:
    def __init__(self, day, start_time, end_time, timezone):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time
        self.timezone = pytz.timezone(timezone)

    def convert_to_timezone(self, target_timezone):
        target_timezone = pytz.timezone(target_timezone)
        start_time_converted = self.timezone.localize(datetime.strptime(self.start_time, "%H:%M")).astimezone(target_timezone)
        end_time_converted = self.timezone.localize(datetime.strptime(self.end_time, "%H:%M")).astimezone(target_timezone)
        return MeetingTime(self.day, start_time_converted.strftime("%H:%M"), end_time_converted.strftime("%H:%M"), target_timezone.zone)

    def __repr__(self):
        return f"{self.day}: {self.start_time}-{self.end_time} ({self.timezone})"

class Location:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class MeetingScheduler:
    def __init__(self, users, api):
        self.users = users
        self.api = api

    def find_common_times(self):
        common_times = defaultdict(list)

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            day_availability = []

            for user in self.users:
                available_times = [(mt.start_time, mt.end_time) for mt in user.availability if mt.day == day]
                if available_times:
                    day_availability.append(available_times)

            if len(day_availability) > 1:
                for i in range(len(day_availability[0])):
                    common_start, common_end = day_availability[0][i]
                    overlap = True
                    for j in range(1, len(day_availability)):
                        overlap_found = False
                        for start, end in day_availability[j]:
                            overlap, latest_start, earliest_end = self.time_overlap(common_start, common_end, start, end)
                            if overlap:
                                common_start, common_end = latest_start, earliest_end
                                overlap_found = True
                                break
                        if not overlap_found:
                            overlap = False
                            break
                    if overlap:
                        common_times[day].append((common_start, common_end))

        return common_times

    def time_overlap(self, start1, end1, start2, end2):
        start1 = datetime.strptime(start1, "%H:%M")
        end1 = datetime.strptime(end1, "%H:%M")
        start2 = datetime.strptime(start2, "%H:%M")
        end2 = datetime.strptime(end2, "%H:%M")

        latest_start = max(start1, start2)
        earliest_end = min(end1, end2)

        return (earliest_end > latest_start), latest_start.strftime("%H:%M"), earliest_end.strftime("%H:%M")

    def calculate_distances(self):
        distances = {}
        for i, user1 in enumerate(self.users):
            for j, user2 in enumerate(self.users):
                if i < j:
                    distance = haversine(user1.current_location.latitude, user1.current_location.longitude,
                                         user2.current_location.latitude, user2.current_location.longitude)
                    distances[(user1.name, user2.name)] = distance
        return distances

    def find_midpoint(self):
        all_locations = [user.current_location for user in self.users]
        return calculate_midpoint(all_locations)

    def find_best_meeting_place(self, midpoint):
        return self.api.find_nearby(midpoint.latitude, midpoint.longitude)

    def suggest_meeting_points(self, common_times):
        suggestions = defaultdict(list)

        for day, times in common_times.items():
            for start, end in times:
                locations = set(self.users[0].meeting_points)
                for user in self.users[1:]:
                    locations &= set(user.meeting_points)

                if locations:
                    suggestions[day].append((start, end, list(locations)))

        return suggestions

    def display_suggestions(self, suggestions, distances, midpoint, best_places):
        if not suggestions:
            print("No common meeting times and locations found.")
            return

        print("\n--- Suggested Meeting Times and Locations ---")
        for day, options in suggestions.items():
            if options:
                print(f"On {day}, you can meet:")
                for start, end, locations in options:
                    print(f"  - From {start} to {end} at one of the following locations: {', '.join([loc.name for loc in locations])}")
            else:
                print(f"No common times on {day}.")

        print("\n--- Distances Between Users ---")
        for (user1, user2), distance in distances.items():
            print(f"Distance between {user1} and {user2}: {distance:.2f} km")

        print(f"\n--- Midpoint Location ---\nMidpoint: {midpoint}")

        print("\n--- Nearby Meeting Places ---")
        for place in best_places:
            print(f"Place: {place.name} ({place.latitude}, {place.longitude})")


import requests

class OpenCageAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.opencagedata.com/geocode/v1/json"
        self.places_url = "https://api.opencagedata.com/geosearch/v1"

    def get_coordinates(self, place_name):
        params = {
            "q": place_name,
            "key": self.api_key,
            "limit": 1,  # Limit results to the top one
            "format": "json"
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            data = response.json()

            if data['results']:
                location = data['results'][0]['geometry']  # Get the first result's geometry
                return Location(name=place_name, latitude=float(location['lat']), longitude=float(location['lng']))
            else:
                raise ValueError(f"No results found for {place_name}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except requests.exceptions.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def find_nearby(self, latitude, longitude, amenity="cafe"):
        params = {
            "q": amenity,
            "key": self.api_key,
            "proximity": f"{latitude},{longitude}",
            "radius": 5000,  # Radius in meters
            "limit": 5  # Limit to the top 5 results
        }
        try:
            response = requests.get(self.places_url, params=params)
            response.raise_for_status()
            data = response.json()

            if data['features']:
                places = []
                for feature in data['features']:
                    geometry = feature['geometry']
                    properties = feature['properties']
                    places.append(
                        Location(
                            name=properties.get('name', 'Unknown Place'),
                            latitude=geometry['coordinates'][1],
                            longitude=geometry['coordinates'][0]
                        )
                    )
                return places
            else:
                print(f"No nearby places found for amenity: {amenity}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except requests.exceptions.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return []

# Initialize OpenCage API with your API key
api_key = "29bfeb3ef71440b6986504215fbd852a"  # Replace with your actual API key
opencage = OpenCageAPI(api_key)

# Create some users and their availability
alice_location = opencage.get_coordinates("Central Park, New York")
if alice_location is None:
    raise RuntimeError("Failed to get coordinates for Alice's location.")

bob_location = opencage.get_coordinates("Downtown, New York")
if bob_location is None:
    raise RuntimeError("Failed to get coordinates for Bob's location.")

charlie_location = opencage.get_coordinates("Uptown, New York")
if charlie_location is None:
    raise RuntimeError("Failed to get coordinates for Charlie's location.")

david_location = opencage.get_coordinates("Brooklyn, New York")
if david_location is None:
    raise RuntimeError("Failed to get coordinates for David's location.")

eve_location = opencage.get_coordinates("Harlem, New York")
if eve_location is None:
    raise RuntimeError("Failed to get coordinates for Eve's location.")



alice = User(
    name="Alice",
    current_location=alice_location,
    availability=[
        MeetingTime("Monday", "10:00", "12:00", "America/New_York"),
        MeetingTime("Wednesday", "14:00", "16:00", "America/New_York")
    ],
    meeting_points=[alice_location, opencage.get_coordinates("Coffee Shop, New York")]
)

bob = User(
    name="Bob",
    current_location=bob_location,
    availability=[
        MeetingTime("Monday", "11:00", "12:00", "America/New_York"),
        MeetingTime("Wednesday", "14:00", "15:00", "America/New_York")
    ],
    meeting_points=[bob_location, opencage.get_coordinates("Library, New York")]
)

charlie = User(
    name="Charlie",
    current_location=charlie_location,
    availability=[
        MeetingTime("Monday", "10:30", "11:30", "America/New_York"),
        MeetingTime("Wednesday", "14:00", "16:00", "America/New_York")
    ],
    meeting_points=[charlie_location, opencage.get_coordinates("Uptown Café, New York")]
)

david = User(
    name="David",
    current_location=david_location,
    availability=[
        MeetingTime("Monday", "09:00", "10:00", "America/New_York"),
        MeetingTime("Wednesday", "15:00", "17:00", "America/New_York")
    ],
    meeting_points=[david_location, opencage.get_coordinates("Brooklyn Bridge Park, New York")]
)

eve = User(
    name="Eve",
    current_location=eve_location,
    availability=[
        MeetingTime("Monday", "12:00", "14:00", "America/New_York"),
        MeetingTime("Wednesday", "13:00", "15:00", "America/New_York")
    ],
    meeting_points=[eve_location, opencage.get_coordinates("Harlem Café, New York")]
)
# Create the scheduler
scheduler = MeetingScheduler(users=[alice, bob, charlie, david, eve], api=opencage)

# Find common times
common_times = scheduler.find_common_times()

# Calculate distances between users
distances = scheduler.calculate_distances()

# Find the midpoint location
midpoint = scheduler.find_midpoint()

# Find the best meeting places near the midpoint
best_places = scheduler.find_best_meeting_place(midpoint)

# Suggest meeting points
suggestions = scheduler.suggest_meeting_points(common_times)

# Display the suggestions, distances, and best places
scheduler.display_suggestions(suggestions, distances, midpoint, best_places)