from location import Location
from meeting_time import MeetingTime
from user import User
from meeting_scheduler import MeetingScheduler

# Define locations directly with lat/lon values
alice_location = Location("Alice's Place", 40.785091, -73.968285)  # Central Park
bob_location = Location("Bob's Place", 40.712776, -74.005974)  # Downtown NYC
charlie_location = Location("Charlie's Place", 40.748817, -73.985428)  # Empire State Building
david_location = Location("David's Place", 40.730610, -73.935242)  # Brooklyn
eve_location = Location("Eve's Place", 40.706446, -73.996705)  # Wall Street

# Define users with their respective locations and availabilities
alice = User(
    name="Alice",
    current_location=alice_location,
    availability=[
        MeetingTime("Monday", "10:00", "12:00", "America/New_York"),
        MeetingTime("Wednesday", "14:00", "16:00", "America/New_York")
    ],
    meeting_points=[alice_location]
)

bob = User(
    name="Bob",
    current_location=bob_location,
    availability=[
        MeetingTime("Monday", "11:00", "12:00", "America/New_York"),
        MeetingTime("Wednesday", "14:00", "15:00", "America/New_York")
    ],
    meeting_points=[bob_location]
)

charlie = User(
    name="Charlie",
    current_location=charlie_location,
    availability=[
        MeetingTime("Monday", "10:30", "11:30", "America/New_York"),
        MeetingTime("Wednesday", "14:00", "16:00", "America/New_York")
    ],
    meeting_points=[charlie_location]
)

david = User(
    name="David",
    current_location=david_location,
    availability=[
        MeetingTime("Monday", "09:00", "10:00", "America/New_York"),
        MeetingTime("Wednesday", "15:00", "17:00", "America/New_York")
    ],
    meeting_points=[david_location]
)

eve = User(
    name="Eve",
    current_location=eve_location,
    availability=[
        MeetingTime("Monday", "12:00", "14:00", "America/New_York"),
        MeetingTime("Wednesday", "13:00", "15:00", "America/New_York")
    ],
    meeting_points=[eve_location]
)

# Create the scheduler
scheduler = MeetingScheduler(users=[alice, bob, charlie, david, eve])

# Find common times
common_times = scheduler.find_common_times()

# Suggest meeting places (which will also calculate distances to each user's location)
suggestions = scheduler.suggest_meeting_places(common_times)

# Display the suggestions
scheduler.display_suggestions(suggestions)
