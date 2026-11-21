import os
import shutil
from datetime import datetime

# File paths for storing data
EVENTS_FILE = "events.txt"
REGISTRATIONS_FILE = "registrations.txt"
CANCELLED_EVENTS_FILE = "cancelled_events.txt"
VENUES_FILE = "venues.txt"  # Added venue file
BLOCKED_DATES_FILE = "blocked_dates.txt"  # Added blocked dates file


def initialize_files():
    """Create data files if they don't exist"""
    files = [EVENTS_FILE, REGISTRATIONS_FILE, CANCELLED_EVENTS_FILE, VENUES_FILE, BLOCKED_DATES_FILE]
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                pass


def validate_date(date_str):
    """Validate date format and check if it's a valid date"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_time(time_str):
    """Validate time format (HH:MM)"""
    try:
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


def validate_email(email):
    """Basic email validation - check if it contains @ and has proper format"""
    if '@' not in email:
        return False

    # Split email into local and domain parts
    parts = email.split('@')
    if len(parts) != 2:
        return False

    local, domain = parts

    # Check if local and domain parts are not empty
    if not local or not domain:
        return False

    # Check if domain has at least one dot
    if '.' not in domain:
        return False

    # Check if domain doesn't start or end with dot
    if domain.startswith('.') or domain.endswith('.'):
        return False

    return True


def get_non_empty_input(prompt):
    """Get input that cannot be empty"""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("❗ This field cannot be empty! Please enter a value.")


def get_valid_date():
    """Get a valid date from user"""
    while True:
        date_str = get_non_empty_input("📅 Enter event date (YYYY-MM-DD): ")
        if validate_date(date_str):
            return date_str
        print("⚠️ Invalid date format or date doesn't exist! Please use YYYY-MM-DD format (e.g., 2024-12-25)")


def get_valid_time():
    """Get a valid time from user"""
    while True:
        time_str = get_non_empty_input("⏰ Enter event time (HH:MM)(e.g., 14:30): ")
        if validate_time(time_str):
            return time_str
        print("⚠️ Invalid time format! Please use HH:MM format (e.g., Jan 14:30)")


def get_valid_email():
    """Get a valid email from user"""
    while True:
        email = get_non_empty_input("📧 Enter organizer email: ")
        if validate_email(email):
            return email
        print("⚠️ Invalid email format! Please enter a valid email address (e.g., user@example.com)")


def get_all_venues():
    """Get list of all venues from venues.txt"""
    venues = []
    if os.path.exists(VENUES_FILE):
        with open(VENUES_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 4:
                        venues.append({
                            'name': parts[0],
                            'capacity': parts[1],
                            'location': parts[2],
                            'description': parts[3]
                        })
    return venues


def is_venue_available(venue_name, event_date, exclude_event_id=None):
    """Check if venue is available on a specific date"""
    target_date = datetime.strptime(event_date, '%Y-%m-%d').date()

    # Check if venue is blocked in blocked_dates.txt
    if os.path.exists(BLOCKED_DATES_FILE):
        with open(BLOCKED_DATES_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[0] == venue_name:
                        blocked_date = datetime.strptime(parts[1], '%Y-%m-%d').date()
                        if blocked_date == target_date:
                            return False, "🚫 Venue is blocked on this date"

    # Check if venue has any active event (pending or approved) on this date
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 8:  # Ensure we have enough fields
                        event_venue = parts[1]
                        event_date_str = parts[2]
                        event_status = parts[4]
                        event_id = parts[7] if len(parts) > 7 else None
                        event_name = parts[0]

                        # Skip if this is the event we're updating
                        if exclude_event_id and event_id == exclude_event_id:
                            continue

                        # Check if same venue and same date
                        if event_venue == venue_name:
                            try:
                                event_date_obj = datetime.strptime(event_date_str, '%Y-%m-%d').date()
                                if event_date_obj == target_date:
                                    # Venue is unavailable if event is pending or approved
                                    # Venue is available if event is rejected
                                    if event_status == "pending":
                                        return False, f"⏳ Venue has a pending event: {event_name} (ID: {event_id})"
                                    elif event_status == "approved" or event_status.endswith("_approved"):
                                        return False, f"✅ Venue has an approved event: {event_name} (ID: {event_id})"
                                    # If status is rejected, we continue checking other events
                                    # (rejected events don't block the venue)
                            except ValueError:
                                # Skip if date format is invalid
                                continue

    return True, "✅ Available"


def show_available_venues(event_date, exclude_event_id=None):
    """Display available venues for a specific date - Enhanced with better status display"""
    venues = get_all_venues()

    if not venues:
        print("❌ No venues found in the system!")
        return []

    print(f"\n📅 Venue availability for {event_date}:")
    print("=" * 80)

    available_venues = []
    unavailable_venues = []

    for venue in venues:
        venue_name = venue['name']
        is_available, reason = is_venue_available(venue_name, event_date, exclude_event_id)

        if is_available:
            available_venues.append(venue)
        else:
            unavailable_venues.append((venue, reason))

    # Show available venues
    if available_venues:
        print("✅ AVAILABLE VENUES:")
        print("-" * 80)
        for i, venue in enumerate(available_venues, 1):
            print(f"{i}. {venue['name']}")
            print(f"   📍 Location: {venue['location']}")
            print(f"   👥 Capacity: {venue['capacity']}")
            print(f"   📝 Description: {venue['description']}")
            print("-" * 80)

    # Show unavailable venues with detailed reasons
    if unavailable_venues:
        print("\n❌ UNAVAILABLE VENUES:")
        print("-" * 80)
        for venue, reason in unavailable_venues:
            print(f"   🏢 {venue['name']}")
            print(f"       {reason}")
            print(f"       📍 Location: {venue['location']}")
        print("-" * 80)

    return available_venues


def debug_venue_status(venue_name, event_date):
    """Debug function to check venue status and all events on a specific date"""
    print(f"\n🔍 === DEBUG VENUE STATUS === 🔍")
    print(f"🏢 Venue: {venue_name}")
    print(f"📅 Date: {event_date}")
    print("-" * 60)

    target_date = datetime.strptime(event_date, '%Y-%m-%d').date()

    # Check blocked dates
    print("🚫 Checking blocked dates...")
    if os.path.exists(BLOCKED_DATES_FILE):
        with open(BLOCKED_DATES_FILE, 'r') as f:
            blocked_found = False
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[0] == venue_name:
                        blocked_date = datetime.strptime(parts[1], '%Y-%m-%d').date()
                        if blocked_date == target_date:
                            print(f"   ❌ Venue is blocked on {event_date}")
                            blocked_found = True
            if not blocked_found:
                print(f"   ✅ No blocked dates found for {venue_name} on {event_date}")
    else:
        print("   📂 No blocked dates file found")

    # Check all events on this date for this venue
    print(f"\n📋 Checking events for {venue_name} on {event_date}...")
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as f:
            events_found = []
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 8:
                        event_venue = parts[1]
                        event_date_str = parts[2]
                        event_status = parts[4]
                        event_id = parts[7] if len(parts) > 7 else "N/A"
                        event_name = parts[0]

                        if event_venue == venue_name:
                            try:
                                event_date_obj = datetime.strptime(event_date_str, '%Y-%m-%d').date()
                                if event_date_obj == target_date:
                                    events_found.append((event_name, event_id, event_status))
                            except ValueError:
                                continue

            if events_found:
                print(f"   📅 Found {len(events_found)} event(s):")
                for event_name, event_id, status in events_found:
                    status_emoji = {
                        "pending": "⏳",
                        "approved": "✅",
                        "rejected": "❌"
                    }.get(status, "❓")
                    print(f"     {status_emoji} {event_name} (ID: {event_id}) - Status: {status}")
                    if status in ["pending", "approved"] or status.endswith("_approved"):
                        print(f"       → This event BLOCKS the venue")
                    elif status == "rejected" or status.startswith("rejected_by"):
                        print(f"       → This event does NOT block the venue (rejected)")
            else:
                print(f"   ✅ No events found for {venue_name} on {event_date}")
    else:
        print("   📂 No events file found")

    # Final availability check
    is_available, reason = is_venue_available(venue_name, event_date)
    print(f"\n🎯 FINAL RESULT:")
    print(f"   Venue {venue_name} on {event_date}: {reason}")
    print("-" * 60)

def get_venue_choice(available_venues):
    """Let user choose from available venues"""
    if not available_venues:
        print("❌ No venues available for this date!")
        return None

    while True:
        try:
            choice = int(input(f"\n🏢 Choose venue (1-{len(available_venues)}): "))
            if 1 <= choice <= len(available_venues):
                return available_venues[choice - 1]['name']
            else:
                print(f"⚠️ Please enter a number between 1 and {len(available_venues)}")
        except ValueError:
            print("⚠️ Please enter a valid number!")


def check_event_name_exists(event_name, exclude_id=None):
    """Check if event name already exists in active or cancelled events"""
    # Check active events
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 7 and parts[0].lower() == event_name.lower() and parts[6] != exclude_id:
                        return True, "active", parts[6]

    # Check cancelled events
    if os.path.exists(CANCELLED_EVENTS_FILE):
        with open(CANCELLED_EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 7 and parts[0].lower() == event_name.lower() and parts[6] != exclude_id:
                        return True, "cancelled", parts[6]

    return False, None, None


def get_unique_event_name(exclude_id=None):
    """Get a unique event name from user"""
    while True:
        event_name = get_non_empty_input("🏷️ Enter event name: ")
        exists, status, existing_id = check_event_name_exists(event_name, exclude_id)

        if exists:
            print(f"⚠️ Event name '{event_name}' already exists as {status} event (ID: {existing_id})!")
            print("Please choose a different name.")
        else:
            return event_name



def search_event_by_name_or_id(search_term):
    """Search for event by name or ID in active events - FIXED to handle correct format"""
    if not os.path.exists(EVENTS_FILE):
        return []

    found_events = []
    with open(EVENTS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split('|')
                # Current format: title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
                if len(parts) >= 11:
                    event_id = parts[7]  # ID at position 7
                    event_name = parts[0]  # Name is always at position 0

                    # Check if search term matches ID or name (case insensitive)
                    if (search_term.upper() == event_id.upper() or
                            search_term.lower() in event_name.lower()):
                        found_events.append((event_id, event_name, parts))

    return found_events

def display_search_results(events):
    """Display search results in a readable format"""
    if not events:
        print("🔍 No events found!")
        return None

    if len(events) == 1:
        return events[0][0]  # Return the event ID directly if only one found

    print("\n🔍 Found multiple events:")
    print("-" * 60)
    for i, (event_id, event_name, parts) in enumerate(events, 1):
        print(f"{i}. {event_id} - {event_name}")
        print(f"   📅 Date: {parts[2]} at {parts[3]}")
        print(f"   🏢 Venue: {parts[1]}")

        # Add emoji based on status
        status = parts[4]
        if status == "pending":
            status_emoji = "⏳"
        elif status == "approved":
            status_emoji = "✅"
        elif status == "rejected":
            status_emoji = "❌"
        else:
            status_emoji = "❓"

        print(f"   {status_emoji} Status: {parts[4]}")
        print()

    while True:
        try:
            choice = int(input(f"🔢 Enter choice (1-{len(events)}): "))
            if 1 <= choice <= len(events):
                return events[choice - 1][0]  # Return selected event ID
            else:
                print(f"⚠️ Please enter a number between 1 and {len(events)}")
        except ValueError:
            print("⚠️ Please enter a valid number!")


def get_valid_max_participants():
    """Get a valid number for maximum participants"""
    while True:
        max_str = get_non_empty_input("👥 Enter maximum participants: ")
        try:
            max_participants = int(max_str)
            if max_participants > 0:
                return max_participants
            else:
                print("⚠️ Maximum participants must be greater than 0!")
        except ValueError:
            print("⚠️ Please enter a valid number!")


def generate_event_id():
    """Generate a unique event ID"""
    if not os.path.exists(EVENTS_FILE):
        return "EV001"

    with open(EVENTS_FILE, 'r') as f:
        lines = f.readlines()

    if not lines:
        return "EV001"

    # Find the highest event ID number
    max_num = 0
    for line in lines:
        line = line.strip()
        if line:
            parts = line.split('|')
            # Fixed: event_id is at position 7 in the format
            if len(parts) >= 8:
                event_id = parts[7]  # ID is at position 7
                # Check if it's a valid event ID format (starts with EV)
                if event_id.startswith('EV') and len(event_id) >= 5:
                    try:
                        num = int(event_id[2:])
                        max_num = max(max_num, num)
                    except ValueError:
                        # Skip invalid event IDs
                        continue

    # Return next event ID
    return f"EV{max_num + 1:03d}"


def view_organizer_events(organizer_username):
    """View events created by specific organizer - FIXED"""
    if not organizer_username or organizer_username == "None":
        print("❌ No organizer specified!")
        return

    if not os.path.exists(EVENTS_FILE):
        print("📂 No events found!")
        return

    with open(EVENTS_FILE, 'r') as f:
        lines = f.readlines()

    if not lines or all(not line.strip() for line in lines):
        print("📂 No active events found!")
        return

    organizer_events = []
    for line in lines:
        if line.strip():
            parts = line.strip().split('|')
            # Current format: title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
            if len(parts) >= 11:
                creator = parts[10]  # Creator at position 10
                if creator == organizer_username:
                    organizer_events.append(parts)

    if not organizer_events:
        print(f"📂 No events found created by {organizer_username}!")
        return

    # Display organizer's events
    print("-" * 80)
    for i, parts in enumerate(organizer_events, 1):
        # Format: title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
        event_id = parts[7]
        name = parts[0]
        date = parts[2]
        time = parts[3]
        venue = parts[1]
        status = parts[4]
        organizer_email = parts[6]
        max_participants = parts[9]

        print(f"{i}. 🔢 Event ID: {event_id}")
        print(f"   🏷️ Name: {name}")
        print(f"   📅 Date: {date} at {time}")
        print(f"   🏢 Venue: {venue}")

        # Add emoji based on status
        if status == "pending":
            status_emoji = "⏳"
        elif status == "approved" or status.endswith("_approved"):
            status_emoji = "✅"
        elif status == "rejected" or status.startswith("rejected_by"):
            status_emoji = "❌"
        else:
            status_emoji = "❓"
        print(f"   {status_emoji} Status: {status}")

        print(f"   📧 Email Organizer: {organizer_email}")
        print(f"   👥 Max Participants: {max_participants}")
        print("-" * 80)


def get_venue_capacity(venue_name):
    """Get the capacity of a specific venue"""
    try:
        with open("venues.txt", 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 4 and parts[0] == venue_name:
                        capacity_str = parts[1].strip()
                        try:
                            return int(capacity_str)
                        except ValueError:
                            print(f"⚠️ Warning: Venue '{venue_name}' has invalid capacity: '{capacity_str}'")
                            return None
    except FileNotFoundError:
        pass
    return None


def get_valid_max_participants(venue_name=None):
    """Get valid max participants number with venue capacity check"""
    venue_capacity = None
    if venue_name:
        venue_capacity = get_venue_capacity(venue_name)
        if venue_capacity:
            print(f"🏢 Venue '{venue_name}' capacity: {venue_capacity}")

    while True:
        try:
            max_participants = int(input("👥 Enter maximum participants: ").strip())
            if max_participants <= 0:
                print("❌ Maximum participants must be greater than 0!")
                continue

            if venue_capacity and max_participants > venue_capacity:
                print(f"❌ Maximum participants ({max_participants}) cannot exceed venue capacity ({venue_capacity})!")
                continue

            return max_participants
        except ValueError:
            print("❌ Please enter a valid number!")


def create_new_event(current_organizer=None):
    """Create a new campus activity with venue availability check"""
    print("\n🌟 === CREATE NEW EVENT === 🌟")
    event_id = generate_event_id()
    # Get event name first
    event_name = get_unique_event_name()
    # Get event date
    event_date = get_valid_date()
    # Show available venues for this date
    available_venues = show_available_venues(event_date)
    if not available_venues:
        retry = input("\n🔄 Would you like to choose a different date? (y/N): ").strip().lower()
        if retry == 'y':
            event_date = get_valid_date()
            available_venues = show_available_venues(event_date)
            if not available_venues:
                print("❌ No venues available. Event creation cancelled.")
                return
        else:
            print("❌ Event creation cancelled.")
            return

    # Get venue choice
    venue = get_venue_choice(available_venues)
    if not venue:
        print("❌ Event creation cancelled.")
        return
    # Get remaining information
    event_time = get_valid_time()
    organizer_email = get_valid_email()
    description = get_non_empty_input("📝 Enter description: ")
    max_participants = get_valid_max_participants(venue)  # Pass venue name for capacity check
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create event record in format:
    # title|venue|date|time|status|timestamp|email|event_id|description|max_participants|creator_username
    event_record = f"{event_name}|{venue}|{event_date}|{event_time}|pending|{timestamp}|{organizer_email}|{event_id}|{description}|{max_participants}|{current_organizer or 'unknown'}\n"

    with open(EVENTS_FILE, 'a') as f:
        f.write(event_record)

    print(f"\n🎉 Event '{event_id}-{event_name}' has been created and is pending approval!")
    print(f"📍 Venue: {venue}")
    print(f"📅 Date: {event_date} at {event_time}")
    print(f"👥 Max Participants: {max_participants}")
    print(f"⚠️ Note: The venue is now reserved for this date until the event is approved or rejected.")


def update_event_details(current_organizer=None):
    """Update existing event details - FIXED to handle organizer properly"""
    print("\n🔄 === UPDATE EVENT DETAILS === 🔄")

    if not current_organizer or current_organizer == "None":
        print("❌ No organizer specified! Please log in properly.")
        return

    if not os.path.exists(EVENTS_FILE):
        print("📂 No events found!")
        return

    # First show only events created by current organizer
    print(f"\n📋 Your events ({current_organizer}):")
    view_organizer_events(current_organizer)

    # Get search term
    search_term = input("\n🔍 Enter event ID or event name to update: ").strip()

    if not search_term:
        print("❌ Search term cannot be empty!")
        return

    # Search for events
    found_events = search_event_by_name_or_id(search_term)

    # Filter events to only show those created by current organizer
    organizer_events = []
    for event_id, event_name, parts in found_events:
        if len(parts) >= 11 and parts[10] == current_organizer:
            organizer_events.append((event_id, event_name, parts))

    if not organizer_events:
        print("❌ No matching events found that you created!")
        return

    event_id = display_search_results(organizer_events)

    if not event_id:
        return

    # Read all events
    with open(EVENTS_FILE, 'r') as f:
        lines = f.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.strip():
            parts = line.strip().split('|')
            # Current format: title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
            if len(parts) >= 11 and parts[7] == event_id:  # event_id is at position 7
                # Check if current organizer owns this event
                creator = parts[10]  # creator is at position 10
                if current_organizer and creator != current_organizer:
                    print(
                        f"❌ Access denied! This event was created by '{creator}'. You can only modify your own events.")
                    return

                # Check if event status allows updates
                status = parts[4]
                if status != "pending":
                    print(f"❌ Cannot update event! Only pending events can be updated.")
                    print(f"Current status: {status}")
                    if status == "approved" or status.endswith("_approved"):
                        print("✅ This event has already been approved and cannot be modified.")
                    elif status == "rejected" or status.startswith("rejected_by"):
                        print("❌ This event has been rejected and cannot be modified.")
                    return

                print(f"\n📌 Current details for {event_id}:")
                print(f"🏷️ Name: {parts[0]}")
                print(f"🏢 Venue: {parts[1]}")
                print(f"📅 Date: {parts[2]}")
                print(f"⏰ Time: {parts[3]}")
                print(f"⏳ Status: {parts[4]} (pending)")
                print(f"📧 Organizer Email: {parts[6]}")
                print(f"📝 Description: {parts[8]}")
                print(f"👥 Max Participants: {parts[9]}")

                print("\n🔄 Which field would you like to update?")
                print("1️⃣ Name")
                print("2️⃣ Venue")
                print("3️⃣ Date")
                print("4️⃣ Time")
                print("5️⃣ Organizer Email")
                print("6️⃣ Description")
                print("7️⃣ Max Participants")
                print("8️⃣ Update all fields")

                choice = input("🔢 Enter your choice (1-8): ").strip()

                new_parts = parts.copy()

                if choice == '1':
                    new_parts[0] = get_unique_event_name(exclude_id=event_id)
                elif choice == '2':
                    # Show available venues for current date
                    current_date = parts[2]
                    available_venues = show_available_venues(current_date, exclude_event_id=event_id)
                    new_venue = get_venue_choice(available_venues)
                    if new_venue:
                        new_parts[1] = new_venue
                        # Check if current max participants exceed new venue capacity
                        current_max_participants = int(parts[9])
                        new_venue_capacity = get_venue_capacity(new_venue)
                        if new_venue_capacity and current_max_participants > new_venue_capacity:
                            print(
                                f"⚠️ Current max participants ({current_max_participants}) exceeds new venue capacity ({new_venue_capacity})")
                            new_max_participants = get_valid_max_participants(new_venue)
                            new_parts[9] = str(new_max_participants)
                    else:
                        print("🚫 Venue update cancelled.")
                        return
                elif choice == '3':
                    new_date = get_valid_date()
                    # Check if current venue is available on new date
                    is_available, reason = is_venue_available(parts[1], new_date, exclude_event_id=event_id)
                    if is_available:
                        new_parts[2] = new_date
                    else:
                        print(f"❌ Current venue '{parts[1]}' is not available on {new_date}: {reason}")
                        print("Please choose a different venue or date.")
                        available_venues = show_available_venues(new_date, exclude_event_id=event_id)
                        new_venue = get_venue_choice(available_venues)
                        if new_venue:
                            new_parts[1] = new_venue
                            new_parts[2] = new_date
                            # Check if current max participants exceed new venue capacity
                            current_max_participants = int(parts[9])
                            new_venue_capacity = get_venue_capacity(new_venue)
                            if new_venue_capacity and current_max_participants > new_venue_capacity:
                                print(
                                    f"⚠️ Current max participants ({current_max_participants}) exceeds new venue capacity ({new_venue_capacity})")
                                new_max_participants = get_valid_max_participants(new_venue)
                                new_parts[9] = str(new_max_participants)
                        else:
                            print("🚫 Update cancelled.")
                            return
                elif choice == '4':
                    new_parts[3] = get_valid_time()
                elif choice == '5':
                    new_parts[6] = get_valid_email()
                elif choice == '6':
                    new_parts[8] = get_non_empty_input("📝 Enter new description: ")
                elif choice == '7':
                    current_venue = parts[1]
                    new_parts[9] = str(get_valid_max_participants(current_venue))
                elif choice == '8':
                    print("🆕 Enter new details:")
                    new_parts[0] = get_unique_event_name(exclude_id=event_id)

                    # Get new date first
                    new_date = get_valid_date()

                    # Show available venues for new date
                    available_venues = show_available_venues(new_date, exclude_event_id=event_id)
                    new_venue = get_venue_choice(available_venues)
                    if not new_venue:
                        print("🚫 Update cancelled.")
                        return

                    new_parts[1] = new_venue
                    new_parts[2] = new_date
                    new_parts[3] = get_valid_time()
                    new_parts[6] = get_valid_email()
                    new_parts[8] = get_non_empty_input("📝 New description: ")
                    new_parts[9] = str(get_valid_max_participants(new_venue))
                else:
                    print("⚠️ Invalid choice!")
                    return

                lines[i] = "|".join(new_parts) + "\n"
                updated = True
                break

    if updated:
        with open(EVENTS_FILE, 'w') as f:
            f.writelines(lines)
        print("✅ Event updated successfully!")
    else:
        print("❌ Event not found!")


def cancel_event(current_organizer=None):
    """Cancel an existing event - UPDATED to handle new registration format"""
    print("\n❌ === CANCEL EVENT === ❌")

    if not current_organizer or current_organizer == "None":
        print("❌ No organizer specified! Please log in properly.")
        return

    if not os.path.exists(EVENTS_FILE):
        print("📂 No events found!")
        return

    # First show only events created by current organizer
    print(f"\n📋 Your events ({current_organizer}):")
    view_organizer_events(current_organizer)

    # Get search term
    search_term = input("\n🔍 Enter event ID or event name to cancel: ").strip()

    if not search_term:
        print("❌ Search term cannot be empty!")
        return

    # Search for events
    found_events = search_event_by_name_or_id(search_term)

    # Filter events to only show those created by current organizer
    organizer_events = []
    for event_id, event_name, parts in found_events:
        if len(parts) >= 11 and parts[10] == current_organizer:
            organizer_events.append((event_id, event_name, parts))

    if not organizer_events:
        print("❌ No matching events found that you created!")
        return

    event_id = display_search_results(organizer_events)

    if not event_id:
        return

    # Read the event details again to check current status
    with open(EVENTS_FILE, 'r') as f:
        event_found = False
        for line in f:
            if line.strip():
                parts = line.strip().split('|')
                if len(parts) >= 11 and parts[7] == event_id:
                    # Check if current organizer owns this event
                    creator = parts[10]
                    if current_organizer and creator != current_organizer:
                        print(
                            f"❌ Access denied! This event was created by '{creator}'. You can only cancel your own events.")
                        return

                    # Check if event status allows cancellation
                    status = parts[4]
                    if status != "pending":
                        print(f"❌ Cannot cancel event! Only pending events can be cancelled.")
                        print(f"Current status: {status}")
                        if status == "approved" or status.endswith("_approved"):
                            print("✅ This event has already been approved.")
                        elif status == "rejected" or status.startswith("rejected_by"):
                            print("❌ This event has already been rejected.")
                        return

                    event_found = True
                    print(f"\n🚫 Event to be cancelled:")
                    print(f"🔢 ID: {parts[7]}")
                    print(f"🏷️ Name: {parts[0]}")
                    print(f"📅 Date: {parts[2]} at {parts[3]}")
                    print(f"🏢 Venue: {parts[1]}")
                    print(f"⏳ Status: {parts[4]} (pending)")
                    break

        if not event_found:
            print("❌ Event not found!")
            return

    # Confirm cancellation
    confirm = input("\n⚠️ Are you sure you want to cancel this event? (y/N): ").strip().lower()
    if confirm != 'y':
        print("🛑 Cancellation aborted.")
        return

    # Read all events
    with open(EVENTS_FILE, 'r') as f:
        lines = f.readlines()

    cancelled = False
    cancelled_venue = None
    cancelled_date = None

    for i, line in enumerate(lines):
        if line.strip():
            parts = line.strip().split('|')
            if len(parts) >= 11 and parts[7] == event_id:
                cancelled_venue = parts[1]
                cancelled_date = parts[2]

                # Move to cancelled events file
                with open(CANCELLED_EVENTS_FILE, 'a') as f:
                    f.write(line)

                # Remove from active events
                lines.pop(i)
                cancelled = True
                break

    if cancelled:
        with open(EVENTS_FILE, 'w') as f:
            f.writelines(lines)

        # Remove participants for this event - UPDATED to use registrations.txt
        if os.path.exists(REGISTRATIONS_FILE):
            with open(REGISTRATIONS_FILE, 'r') as f:
                registration_lines = f.readlines()

            # Filter out registrations for this event (where event_id is at position 1)
            updated_registration_lines = []
            for line in registration_lines:
                if line.strip():
                    parts = line.strip().split('|')
                    # Format: username|event_id|registration_date|status
                    if len(parts) >= 4 and parts[1] != event_id:
                        updated_registration_lines.append(line)
                else:
                    updated_registration_lines.append(line)

            with open(REGISTRATIONS_FILE, 'w') as f:
                f.writelines(updated_registration_lines)

        print("✅ Event cancelled successfully!")
        print(f"🏢 Venue '{cancelled_venue}' is now available again for {cancelled_date}")
        print("👥 All participant registrations for this event have been removed.")
    else:
        print("❌ Event not found!")


def view_all_events():
    """View upcoming events (not expired)"""
    print("\n🔍 === Upcoming Events ===")
    today = datetime.now().date()
    upcoming_events = []

    try:
        with open(EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 10:
                        try:
                            event_date = datetime.strptime(parts[2], "%Y-%m-%d").date()
                            if event_date >= today:
                                # Check if we have timestamp (11 fields) or not (10 fields)
                                if len(parts) == 11:
                                    # Format with timestamp: status might be "status|timestamp" format
                                    status = parts[4].split('|')[0]  # Extract just the status part
                                    upcoming_events.append({
                                        'event_id': parts[7],  # event_id
                                        'title': parts[0],  # title
                                        'venue': parts[1],  # venue
                                        'date': parts[2],  # date
                                        'time': parts[3],  # time
                                        'status': status,  # clean status
                                        'email': parts[6],  # email
                                        'organizer': parts[10]  # organizer
                                    })
                                else:
                                    # Format without timestamp (10 fields)
                                    status = parts[4].split('|')[0]  # Extract just the status part
                                    upcoming_events.append({
                                        'event_id': parts[6],  # event_id
                                        'title': parts[0],  # title
                                        'venue': parts[1],  # venue
                                        'date': parts[2],  # date
                                        'time': parts[3],  # time
                                        'status': status,  # clean status
                                        'email': parts[5],  # email
                                        'organizer': parts[9]  # organizer
                                    })
                        except ValueError:
                            print(f"Error parsing date: {parts[2]}")
                            continue
    except FileNotFoundError:
        print("📂 No events found!")
        return

    if not upcoming_events:
        print("📅 No upcoming events found!")
        return

    # Properly aligned table
    print(
        f"{'Event ID':<10} {'Title':<15} {'Venue':<12} {'Date':<12} {'Time':<8} {'Status':<25} {'Email':<20} {'Organizer':<12}")
    print("=" * 120)

    for event in upcoming_events:
        # Clean up status display with better formatting
        status = event['status'].lower()

        if status == 'pending':
            status_display = "Pending Review"
            status_icon = "⏳"
        elif status == 'admin_approved':
            status_display = "Admin Approved"
            status_icon = "🔸"
        elif status == 'venue_manager_approved':
            status_display = "Venue Mgr Approved"
            status_icon = "🔹"
        elif status == 'fully_approved':
            status_display = "Fully Approved"
            status_icon = "✅"
        elif status == 'rejected_by_admin':
            status_display = "Rejected by Admin"
            status_icon = "❌"
        elif status == 'rejected_by_venue_manager':
            status_display = "Rejected by Venue Mgr"
            status_icon = "❌"
        else:
            status_display = event['status'].replace('_', ' ').title()
            status_icon = "❓"

        # Truncate fields to fit exactly in columns
        event_id = event['event_id'][:9] if len(event['event_id']) > 9 else event['event_id']
        title = event['title'][:14] if len(event['title']) > 14 else event['title']
        venue = event['venue'][:11] if len(event['venue']) > 11 else event['venue']
        email = event['email'][:19] if len(event['email']) > 19 else event['email']
        organizer = event['organizer'][:11] if len(event['organizer']) > 11 else event['organizer']
        status_with_icon = f"{status_icon} {status_display}"[:24]

        print(
            f"{event_id:<10} {title:<15} {venue:<12} {event['date']:<12} {event['time']:<8} {status_with_icon:<25} {email:<20} {organizer:<12}")

def view_event_details():
    """View detailed information about a specific event - FIXED participant counting"""
    print("\n🔍 === VIEW EVENT DETAILS === 🔍")

    if not os.path.exists(EVENTS_FILE):
        print("📂 No events found!")
        return

    # Get search term
    search_term = input("🔍 Enter event ID or event name: ").strip()

    if not search_term:
        print("❌ Search term cannot be empty!")
        return

    # Search for events
    found_events = search_event_by_name_or_id(search_term)
    event_id = display_search_results(found_events)

    if not event_id:
        return

    with open(EVENTS_FILE, 'r') as f:
        event_found = False
        for line in f:
            if line.strip():
                parts = line.strip().split('|')
                # Current format: title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
                if len(parts) >= 11 and parts[7] == event_id:
                    event_found = True
                    print(f"\n📌 Event Details for {event_id}")
                    print("=" * 60)
                    print(f"🏷️ Name: {parts[0]}")
                    print(f"🏢 Venue: {parts[1]}")
                    print(f"📅 Date: {parts[2]}")
                    print(f"⏰ Time: {parts[3]}")

                    # Add emoji based on status
                    status = parts[4]
                    if status == "pending":
                        status_emoji = "⏳"
                    elif status == "approved" or status.endswith("_approved"):
                        status_emoji = "✅"
                    elif status == "rejected" or status.startswith("rejected_by"):
                        status_emoji = "❌"
                    else:
                        status_emoji = "❓"
                    print(f"{status_emoji} Status: {status}")

                    print(f"📧 Organizer Email: {parts[6]}")
                    print(f"📝 Description: {parts[8]}")
                    print(f"👥 Maximum Participants: {parts[9]}")
                    print(f"👤 Created by: {parts[10]}")

                    # Count current participants - FIXED using the improved function
                    current_participants = count_active_participants(event_id)
                    print(f"👥 Current Participants: {current_participants}")
                    max_participants = int(parts[9])
                    available_spots = max_participants - current_participants
                    print(f"🎯 Available Spots: {available_spots}")

                    # Show participants if any - FIXED with better file reading
                    if current_participants > 0:
                        print(f"\n📋 Current Participants:")
                        print("-" * 40)
                        participant_count = 0
                        if os.path.exists(REGISTRATIONS_FILE):
                            try:
                                with open(REGISTRATIONS_FILE, 'r', encoding='utf-8') as pf:
                                    for p_line in pf:
                                        if p_line.strip():
                                            p_parts = p_line.strip().split('|')
                                            # Format: username|event_id|registration_date|status
                                            if len(p_parts) >= 4:
                                                file_event_id = p_parts[1].strip()
                                                status = p_parts[3].strip()
                                                if file_event_id == event_id and status == "Active":
                                                    participant_count += 1
                                                    participant_name = p_parts[0].strip()
                                                    registration_time = p_parts[2].strip()
                                                    print(f"   {participant_count}. {participant_name} (Registered: {registration_time})")
                            except Exception as e:
                                print(f"❌ Error reading participants: {e}")

                    print("=" * 60)
                    return

        if not event_found:
            print("❌ Event not found!")

def view_participants():
    """View participants for a specific event - FIXED to properly read registration file"""
    print("\n👥 === VIEW EVENT PARTICIPANTS === 👥")

    if not os.path.exists(EVENTS_FILE):
        print("📂 No events found!")
        return

    # Get search term
    search_term = input("🔍 Enter event ID or event name: ").strip()

    if not search_term:
        print("❌ Search term cannot be empty!")
        return

    # Search for events
    found_events = search_event_by_name_or_id(search_term)
    event_id = display_search_results(found_events)

    if not event_id:
        return

    # Verify event exists and get event details
    event_found = False
    event_name = ""
    max_participants = 0

    with open(EVENTS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split('|')
                if len(parts) >= 11 and parts[7] == event_id:
                    event_found = True
                    event_name = parts[0]
                    max_participants = int(parts[9])
                    break

    if not event_found:
        print("❌ Event not found!")
        return

    # Count and display participants - FIXED to use registrations.txt
    participants = []

    if os.path.exists(REGISTRATIONS_FILE):
        try:
            with open(REGISTRATIONS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split('|')
                        # Format: username|event_id|registration_date|status
                        if len(parts) >= 4:
                            participant_name = parts[0].strip()
                            file_event_id = parts[1].strip()
                            registration_time = parts[2].strip()
                            status = parts[3].strip()

                            if file_event_id == event_id and status == "Active":
                                participants.append((participant_name, registration_time))
        except Exception as e:
            print(f"❌ Error reading registrations file: {e}")
    else:
        print("📂 No registrations file found!")

    print(f"\n📋 Participants for Event: {event_name} ({event_id})")
    print("=" * 60)
    print(f"👥 Total Participants: {len(participants)}/{max_participants}")
    print(f"🎯 Available Spots: {max_participants - len(participants)}")
    print("-" * 60)

    if participants:
        for i, (name, reg_time) in enumerate(participants, 1):
            print(f"{i:2d}. {name}")
            print(f"     📅 Registered: {reg_time}")
            print()
    else:
        print("   No participants registered yet.")

    print("=" * 60)


def count_active_participants(event_id):
    """Count active participants for an event - FIXED to use registrations.txt"""
    count = 0
    if os.path.exists(REGISTRATIONS_FILE):
        try:
            with open(REGISTRATIONS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split('|')
                        # Format: username|event_id|registration_date|status
                        if len(parts) >= 4:
                            file_event_id = parts[1].strip()
                            status = parts[3].strip()
                            if file_event_id == event_id and status == "Active":
                                count += 1
        except Exception as e:
            print(f"❌ Error reading registrations file: {e}")
    return count


def debug_participants_file():
    """Debug function to examine the participants file"""
    print("\n🔍 === DEBUG PARTICIPANTS FILE === 🔍")
    if not os.path.exists(REGISTRATIONS_FILE):
        print("📂 No participants file found!")
        return

    try:
        with open(REGISTRATIONS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"📊 Total lines in file: {len(lines)}")
        print("\n📋 Raw file contents:")
        print("-" * 60)

        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"Line {i:2d}: '{line.strip()}'")
                parts = line.strip().split('|')
                print(f"         Parts: {parts}")
                print(f"         Length: {len(parts)}")
                if len(parts) >= 4:
                    print(f"         Name: '{parts[0]}'")
                    print(f"         Event ID: '{parts[1]}'")
                    print(f"         Timestamp: '{parts[2]}'")
                    print(f"         Status: '{parts[3]}'")
                print("-" * 40)
            else:
                print(f"Line {i:2d}: (empty line)")

    except Exception as e:
        print(f"❌ Error reading file: {e}")


def view_cancelled_events():
    """📉 View cancelled events - FIXED to use correct field indices"""
    print("\n🚫 === CANCELLED EVENTS ===")

    if not os.path.exists(CANCELLED_EVENTS_FILE):
        print("❌ No cancelled events found!")
        return

    with open(CANCELLED_EVENTS_FILE, 'r') as f:
        lines = f.readlines()

    if not lines or all(not line.strip() for line in lines):
        print("❌ No cancelled events found!")
        return

    # Display in a more friendly and readable format
    print("-" * 80)
    for i, line in enumerate(lines, 1):
        if line.strip():
            parts = line.strip().split('|')
            # Current format: title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
            if len(parts) >= 11:
                event_id = parts[7]  # Event ID at position 7
                name = parts[0]  # Name at position 0
                date = parts[2]  # Date at position 2
                time = parts[3]  # Time at position 3
                venue = parts[1]  # Venue at position 1
                status = parts[4]  # Status at position 4
                organizer_email = parts[6]  # Email at position 6
                max_participants = parts[9]  # Max participants at position 9
                organizer = parts[10]  # Organizer username at position 10

                print(f"🔹 {i}. 🆔 Event ID: {event_id}")
                print(f"   📝 Name: {name}")
                print(f"   📅 Date: {date} 🕒 {time}")
                print(f"   📍 Venue: {venue}")
                print(f"   📌 Status: {status}")
                print(f"   📧 Organizer Email: {organizer_email}")
                print(f"   👤 Created by: {organizer}")
                print(f"   👥 Max Participants: {max_participants}")
                print("-" * 80)


def delete_cancelled_events():
    """🗑️ Delete cancelled events permanently - FIXED to use correct field indices"""
    print("\n🗑️ === DELETE CANCELLED EVENTS ===")

    if not os.path.exists(CANCELLED_EVENTS_FILE):
        print("❌ No cancelled events found!")
        return

    with open(CANCELLED_EVENTS_FILE, 'r') as f:
        lines = f.readlines()

    if not lines or all(not line.strip() for line in lines):
        print("❌ No cancelled events found!")
        return

    print("📋 Current cancelled events:")
    for i, line in enumerate(lines, 1):
        if line.strip():
            parts = line.strip().split('|')
            # Current format: title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
            if len(parts) >= 11:
                event_id = parts[7]  # Event ID at position 7
                name = parts[0]  # Name at position 0
                print(f"   {i}. 🆔 {event_id} - 📝 {name}")

    choice = input(
        "\n🔧 What would you like to do?\n1️⃣ Delete ALL cancelled events\n2️⃣ Delete a specific event\nEnter choice (1-2): ").strip()

    if choice == '1':
        confirm = input("⚠️ Are you absolutely sure you want to delete ALL cancelled events? (y/N): ").strip().lower()
        if confirm == 'y':
            with open(CANCELLED_EVENTS_FILE, 'w') as f:
                pass
            print("✅ All cancelled events have been deleted!")
        else:
            print("❌ Operation cancelled.")
    elif choice == '2':
        event_id = input("🔎 Enter the Event ID to delete: ").strip()
        new_lines = []
        found = False
        for line in lines:
            if line.strip():
                parts = line.strip().split('|')
                # Current format: title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
                if len(parts) >= 11 and parts[7] == event_id:  # Event ID at position 7
                    found = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if found:
            with open(CANCELLED_EVENTS_FILE, 'w') as f:
                f.writelines(new_lines)
            print(f"✅ Event '{event_id}' has been successfully deleted!")
        else:
            print(f"❌ Event ID '{event_id}' not found!")
    else:
        print("⚠️ Invalid choice! Please enter 1 or 2.")


def main_menu(user_data=None):
    """Display main menu and handle user input - FIXED to handle user_data properly"""
    # Ensure we have a proper username
    current_organizer = None
    if user_data and isinstance(user_data, dict) and 'username' in user_data:
        current_organizer = user_data['username']
    elif isinstance(user_data, str):
        current_organizer = user_data

    # If no organizer is provided, ask for one
    if not current_organizer or current_organizer == "None":
        current_organizer = input("Please enter your username: ").strip()
        if not current_organizer:
            print("❌ Username cannot be empty!")
            return

    while True:
        print("\n" + "=" * 50)
        print("         CAMPUS EVENT ORGANIZER")
        print(f"         Welcome, {current_organizer}!")
        print("=" * 50)
        print("📋 What would you like to do?")
        print("1.  ✏️ Create new campus activity")
        print("2.  🛠️ Update event details")
        print("3.  ❌ Cancel existing event")
        print("4.  📅 View all active events")
        print("5.  🔍 View event details")
        print("6.  👥 View participants for an event")
        print("7.  🚫 View cancelled events")
        print("8.  🗑️ Delete cancelled events")
        print("9.  🚪 Exit")
        print("-" * 50)

        choice_1 = input("Enter your choice (1-9): ").strip()

        if choice_1 == '1':
            create_new_event(current_organizer)
        elif choice_1 == '2':
            update_event_details(current_organizer)
        elif choice_1 == '3':
            cancel_event(current_organizer)
        elif choice_1 == '4':
            view_all_events()
        elif choice_1 == '5':
            view_event_details()
        elif choice_1 == '6':
            view_participants()
        elif choice_1 == '7':
            view_cancelled_events()
        elif choice_1 == '8':
            delete_cancelled_events()
        elif choice_1 == '9':
            print("Thank you for using Campus Event Organizer!")
            break
        else:
            print("Invalid choice! Please try again.")

        input("\nPress Enter to continue...")

        if choice_1 != "9":  # Don't ask to continue if exiting
            choice_2 = input("\nDo you want to perform another action? (yes/no): ").strip().lower()
            if choice_2 not in ["yes", "y"]:
                print("👋 Exiting Event Organizer system. Goodbye!")
                break


if __name__ == "__main__":
    initialize_files()
    main_menu()