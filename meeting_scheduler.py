from collections import defaultdict
from datetime import datetime
from location import Location
from math import radians, sin, cos, sqrt, atan2


class MeetingScheduler:
    def __init__(self, users):
        self.users = users

    def find_common_times(self):
        common_times = defaultdict(list)

        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            # Collect all available times for this day from all users
            day_availability = [user for user in self.users if any(mt.day == day for mt in user.availability)]
            if len(day_availability) < len(self.users):
                continue  # Skip if not all users are available on this day

            # Start with the first user's availability as the initial common time
            initial_times = [
                (datetime.strptime(mt.start_time, "%H:%M"), datetime.strptime(mt.end_time, "%H:%M"))
                for mt in self.users[0].availability if mt.day == day
            ]

            for start1, end1 in initial_times:
                overlap_start = start1
                overlap_end = end1

                for user in day_availability[1:]:
                    user_times = [
                        (datetime.strptime(mt.start_time, "%H:%M"), datetime.strptime(mt.end_time, "%H:%M"))
                        for mt in user.availability if mt.day == day
                    ]

                    # Find the overlap with the current user's availability
                    for start2, end2 in user_times:
                        overlap_start = max(overlap_start, start2)
                        overlap_end = min(overlap_end, end2)

                        if overlap_start >= overlap_end:
                            break  # No overlap, skip to the next time slot

                if overlap_start < overlap_end:
                    common_times[day].append((overlap_start.strftime("%H:%M"), overlap_end.strftime("%H:%M")))

        print(f"Common times: {common_times}")  # Debug statement
        return common_times

    def haversine(self, loc1, loc2):
        R = 6371.0  # Earth radius in kilometers

        lat1, lon1 = radians(loc1.latitude), radians(loc1.longitude)
        lat2, lon2 = radians(loc2.latitude), radians(loc2.longitude)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    def calculate_distances_to_meeting_point(self, meeting_point):
        distances = {}
        for user in self.users:
            distance = self.haversine(user.current_location, meeting_point)
            distances[user.name] = distance
        return distances

    def suggest_meeting_places(self, common_times):
        suggestions = defaultdict(list)

        for day, times in common_times.items():
            for start, end in times:
                for user in self.users:
                    meeting_point = user.current_location
                    distances = self.calculate_distances_to_meeting_point(meeting_point)
                    suggestions[day].append((start, end, meeting_point, distances))

        print(f"Suggestions: {suggestions}")  # Debug statement
        return suggestions

    def display_suggestions(self, suggestions):
        if not suggestions:
            print("No common meeting times and locations found.")
            return

        print("\n--- Suggested Meeting Times and Locations ---")
        for day, options in suggestions.items():
            if options:
                for start, end, meeting_point, distances in options:
                    print(f"On {day}, from {start} to {end}:")
                    print(f"  - Meet at {meeting_point.name} ({meeting_point.latitude}, {meeting_point.longitude})")
                    for user_name, distance in distances.items():
                        print(f"    - {user_name} is {distance:.2f} km away")

