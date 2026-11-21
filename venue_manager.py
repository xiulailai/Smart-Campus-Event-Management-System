import os
import datetime
from datetime import datetime, timedelta

# File paths for data storage
VENUES_FILE = "venues.txt"
EVENTS_FILE = "events.txt"
BLOCKED_DATES_FILE = "blocked_dates.txt"


def check_venue_availability_for_approval(venue_name, date_str, event_title):
    """Check if venue is available before allowing approval"""
    try:
        check_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        if is_venue_blocked(venue_name, check_date):
            print(f"❌ Cannot approve - venue '{venue_name}' is blocked on {date_str}")
            return False

        existing_event = get_event_on_date(venue_name, check_date)
        if existing_event and existing_event['title'] != event_title:
            print(f"❌ Cannot approve - venue has conflicting approved event: {existing_event['title']}")
            return False

        return True
    except ValueError:
        print("❌ Cannot approve - invalid date format!")
        return False


def get_event_on_date(venue_name, date, allowed_statuses=None):
    """
    Get event for a venue on a specific date, optionally filtering by allowed statuses.

    Parameters:
        venue_name (str): Name of the venue
        date (datetime.date): The date to check
        allowed_statuses (list or None): Statuses to match. If None, match all approved/pending.

    Returns:
        dict or None: Event details if found, else None
    """
    # Default approved + pending statuses if none provided
    if allowed_statuses is None:
        allowed_statuses = [
            "fully_approved", "approved", "venue_manager_approved",
            "admin_approved", "pending"
        ]

    try:
        with open(EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 6 and parts[1] == venue_name:
                        status = parts[4].split('|')[0]
                        if status in allowed_statuses:
                            try:
                                event_date = datetime.strptime(parts[2], "%Y-%m-%d").date()
                                if event_date == date:
                                    return {
                                        'title': parts[0],
                                        'venue': parts[1],
                                        'date': parts[2],
                                        'time': parts[3],
                                        'status': status,
                                        'organizer': parts[-1]  # safest last-field access
                                    }
                            except ValueError:
                                continue  # skip invalid dates
    except FileNotFoundError:
        pass
    return None



def show_venue_availability_info(venue_name, date_str):
    """Show venue availability info during review - Enhanced conflict detection"""
    is_available, reason = is_venue_available(venue_name, date_str)

    if not is_available:
        print(f"   ⚠️  Venue Status: {reason}")
    else:
        # Check for any pending events on the same date for additional info
        try:
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            pending_events = get_pending_events_on_date(venue_name, check_date)
            if pending_events:
                print(f"   ⚠️  Venue Status: ⏳ {len(pending_events)} PENDING EVENT(S) for this date")
            else:
                print(f"   ✅ Venue Status: Available")
        except ValueError:
            print(f"   ❓ Venue Status: Invalid date format")


def get_pending_events_on_date(venue_name, date):
    """Get list of pending events for a venue on a specific date"""
    pending_events = []
    try:
        with open(EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 6:
                        if parts[1] == venue_name:
                            status = parts[4].split('|')[0]
                            if status == "pending":
                                event_date = datetime.strptime(parts[2], "%Y-%m-%d").date()
                                if event_date == date:
                                    pending_events.append({
                                        'title': parts[0],
                                        'time': parts[3],
                                        'organizer': parts[len(parts)-1]
                                    })
    except FileNotFoundError:
        pass
    return pending_events


def display_bookings_for_venue_manager(bookings):
    """Display bookings with venue-specific information in enhanced format - FIXED ALIGNMENT"""
    print("📋 === VENUE MANAGER: BOOKING REVIEW === 📋")
    print("🎯" + "=" * 110 + "🎯")
    # Fixed header alignment to match the actual column widths used in data rows
    print("📋 #  🆔 Event ID  🏷️ Title                         📅 Date        📊 Status                 ")
    print("🎯" + "=" * 110 + "🎯")

    # Count statistics
    total_events = len(bookings)
    pending_count = 0
    approved_count = 0
    rejected_count = 0

    for j, (line_index, parts) in enumerate(bookings, 1):
        # Handle the correct field positions based on the format:
        # title|venue|date|time|status|timestamp|email|event_id|description|max_participants|organizer (11 fields)
        booking_id = parts[7] if len(parts) > 7 else "N/A"  # event_id is at index 7
        current_status = parts[4].split('|')[0]
        organizer = parts[10] if len(parts) > 10 else "N/A"  # organizer is at index 10

        # Count status types
        if current_status == "pending":
            pending_count += 1
        elif "approved" in current_status.lower():
            approved_count += 1
        elif "rejected" in current_status.lower():
            rejected_count += 1

        # Status display with icons
        status_display = {
            "pending": "⏳ Pending",
            "admin_approved": "✅ Admin Approved",
            "venue_manager_approved": "✅ Venue Manager Approved",
            "fully_approved": "✅ Fully Approved",
            "rejected_by_admin": "❌ Rejected by Admin",
            "rejected_by_venue_manager": "❌ Rejected by Venue Manager"
        }.get(current_status, current_status.replace('_', ' ').title())

        # Alternating row colors (using different bullet points)
        row_icon = "🔹" if j % 2 == 1 else "🔸"

        # Truncate title to fit in 30 characters and pad properly
        title = parts[0][:29] if len(parts[0]) > 29 else parts[0]

        # Format the row with proper spacing - FIXED ALIGNMENT
        # The format is: icon + number + event_id + title + date + status
        print(f"{row_icon} {j:<2} {booking_id:<10} {title:<30} {parts[2]:<12} {status_display:<25}")

    print("🎯" + "=" * 110 + "🎯")
    print(f"📊 Total Events: {total_events}")
    print(f"⏳ Pending: {pending_count} | ✅ Approved: {approved_count} | ❌ Rejected: {rejected_count}")
    print("🎯" + "=" * 110 + "🎯")

def get_user_choice(max_choice):
    """Get valid user choice"""
    try:
        choice = int(input(f"🔢 Enter number to review (1-{max_choice}): "))
        if 1 <= choice <= max_choice:
            return choice
        else:
            print("❌ Invalid choice!")
            return None
    except ValueError:
        print("❌ Please enter a valid number!")
        return None


def get_approval_decision(role):
    """Get approval/rejection decision from user"""
    print(f"\n📝 {role.title()} Decision:")
    print("1. ✅ Approve")
    print("2. ❌ Reject")
    print("3. 🔙 Cancel")

    action = input("🔢 Enter your decision (1-3): ").strip()

    if action == "1":
        return "approve"
    elif action == "2":
        return "reject"
    elif action == "3":
        return None
    else:
        print("❌ Invalid choice!")
        return None

def initialize_files():
    """Create data files if they don't exist"""
    files = [VENUES_FILE, EVENTS_FILE, BLOCKED_DATES_FILE]
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                pass

def add_venue():
    """Add a new venue to the system"""
    print("\n🏢 === Add New Venue ===")
    venue_name = input("📝 Enter venue name: ").strip()

    # Get and validate capacity
    while True:
        capacity_input = input("👥 Enter venue capacity: ").strip()
        try:
            capacity = int(capacity_input)
            if capacity <= 0:
                print("❌ Capacity must be greater than 0!")
                continue
            break
        except ValueError:
            print("❌ Capacity must be a valid number!")

    location = input("📍 Enter venue location: ").strip()
    description = input("📋 Enter venue description: ").strip()

    if not venue_name:
        print("❌ Venue name cannot be empty!")
        return

    # Check if venue already exists
    if venue_exists(venue_name):
        print(f"⚠️ Venue '{venue_name}' already exists!")
        return

    # Add venue to file
    with open(VENUES_FILE, 'a') as f:
        f.write(f"{venue_name}|{capacity}|{location}|{description}\n")

    print(f"✅ Venue '{venue_name}' added successfully! 🎉")

def venue_exists(venue_name):
    """Check if a venue exists"""
    try:
        with open(VENUES_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if parts[0] == venue_name:
                        return True
    except FileNotFoundError:
        pass
    return False


def get_all_venues():
    """Get list of all venues"""
    venues = []
    try:
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
    except FileNotFoundError:
        pass
    return venues


def delete_venue():
    """Delete a venue from the system"""
    print("\n🗑️ === Delete Venue ===")
    venues = get_all_venues()

    if not venues:
        print("🔍 No venues found!")
        return

    print("🏢 Available venues:")
    for i, venue in enumerate(venues, 1):
        print(f"{i}. {venue['name']} - 📍 {venue['location']}")

    try:
        choice = int(input("🔢 Enter venue number to delete: "))
        if 1 <= choice <= len(venues):
            venue_to_delete = venues[choice - 1]['name']

            # Remove venue from file
            remaining_venues = [v for v in venues if v['name'] != venue_to_delete]

            with open(VENUES_FILE, 'w') as f:
                for venue in remaining_venues:
                    f.write(f"{venue['name']}|{venue['capacity']}|{venue['location']}|{venue['description']}\n")

            # Also remove any events for this venue
            remove_events_for_venue(venue_to_delete)

            # Remove blocked dates for this venue
            remove_blocked_dates_for_venue(venue_to_delete)

            print(f"✅ Venue '{venue_to_delete}' deleted successfully! 🧹")
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Please enter a valid number!")


def remove_events_for_venue(venue_name):
    """Remove all events for a specific venue"""
    try:
        events = []
        with open(EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 6 and parts[1] != venue_name:
                        events.append(line)

        with open(EVENTS_FILE, 'w') as f:
            f.writelines(events)
    except FileNotFoundError:
        pass


def remove_blocked_dates_for_venue(venue_name):
    """Remove all blocked dates for a specific venue"""
    try:
        blocked_dates = []
        with open(BLOCKED_DATES_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[0] != venue_name:
                        blocked_dates.append(line)

        with open(BLOCKED_DATES_FILE, 'w') as f:
            f.writelines(blocked_dates)
    except FileNotFoundError:
        pass


def view_venue_availability():
    """View venue availability by date"""
    print("\n📅 === View Venue Availability ===")
    date_str = input("📆 Enter date (YYYY-MM-DD): ").strip()

    try:
        check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ Invalid date format! Please use YYYY-MM-DD")
        return

    venues = get_all_venues()
    if not venues:
        print("🔍 No venues found!")
        return

    print(f"\n📊 Venue availability for {date_str}:")
    print("-" * 50)

    for venue in venues:
        venue_name = venue['name']
        is_available, reason = is_venue_available(venue_name, date_str)

        if is_available:
            status = "✅ Available"
        else:
            status = f"❌ Not Available ({reason})"

        print(f"🏢 {venue_name}: {status}")


def is_venue_available(venue_name, event_date, exclude_event_id=None):
    """Check if venue is available on a specific date"""
    try:
        target_date = datetime.strptime(event_date, '%Y-%m-%d').date()
    except ValueError:
        return False, "❌ Invalid date format"

    # Check if venue is blocked
    if os.path.exists(BLOCKED_DATES_FILE):
        with open(BLOCKED_DATES_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[0] == venue_name:
                        blocked_date = datetime.strptime(parts[1], "%Y-%m-%d").date()
                        if blocked_date == target_date:
                            return False, "🚫 Venue is blocked on this date"

    # Check if venue has ANY active event (pending, approved) on this date
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 7:
                        # Skip if this is the event we're updating
                        if exclude_event_id and len(parts) > 7 and parts[7] == exclude_event_id:
                            continue

                        # Check for events that make venue unavailable
                        if parts[1] == venue_name:
                            status = parts[4].split('|')[0]  # Handle status|timestamp format
                            active_statuses = ["pending", "approved", "admin_approved", "venue_manager_approved",
                                               "fully_approved"]

                            if status in active_statuses:
                                event_date_obj = datetime.strptime(parts[2], '%Y-%m-%d').date()
                                if event_date_obj == target_date:
                                    event_name = parts[0]
                                    if status == "pending":
                                        return False, f"⏳ Venue has a pending event: {event_name}"
                                    else:
                                        return False, f"✅ Venue has an approved event: {event_name}"

    return True, "✅ Available"

def is_venue_blocked(venue_name, date):
    """Check if venue is blocked on a specific date"""
    try:
        with open(BLOCKED_DATES_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 2 and parts[0] == venue_name:
                        blocked_date = datetime.strptime(parts[1], "%Y-%m-%d").date()
                        if blocked_date == date:
                            return True
    except FileNotFoundError:
        pass
    return False


def view_venue_calendar():
    """View venue calendar for a specific month"""
    print("\n🗓️ === View Venue Calendar ===")
    venues = get_all_venues()

    if not venues:
        print("🔍 No venues found!")
        return

    print("🏢 Available venues:")
    for i, venue in enumerate(venues, 1):
        print(f"{i}. {venue['name']}")

    try:
        choice = int(input("🔢 Enter venue number: "))
        if 1 <= choice <= len(venues):
            venue_name = venues[choice - 1]['name']

            month_str = input("📅 Enter month (YYYY-MM): ").strip()
            try:
                year, month = map(int, month_str.split('-'))
                show_venue_calendar(venue_name, year, month)
            except ValueError:
                print("❌ Invalid month format! Please use YYYY-MM")
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Please enter a valid number!")


def show_venue_calendar(venue_name, year, month):
    """Display calendar for a specific venue and month - Enhanced version"""
    import calendar

    print(f"\n📊 Calendar for 🏢 {venue_name} - {calendar.month_name[month]} {year}")
    print("=" * 80)

    # Get number of days in month
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)

    days_in_month = (next_month - datetime(year, month, 1)).days

    # Categorize days
    available_days = []
    blocked_days = []
    event_days = []
    pending_days = []

    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day).date()
        date_str = date.strftime("%Y-%m-%d")

        is_available, reason = is_venue_available(venue_name, date_str)

        if is_available:
            available_days.append(day)
        elif "blocked" in reason.lower():
            blocked_days.append(day)
        elif "pending" in reason.lower():
            pending_days.append((day, reason))
        else:
            # Extract event name from reason
            event_name = reason.split(": ")[-1] if ": " in reason else "Event"
            event_days.append((day, event_name))

    # Display summary
    print(f"📈 SUMMARY:")
    print(f"   ✅ Available days: {len(available_days)}")
    print(f"   🎪 Days with events: {len(event_days)}")
    print(f"   ⏳ Days with pending events: {len(pending_days)}")
    print(f"   🚫 Blocked days: {len(blocked_days)}")
    print("-" * 80)

    # Display calendar in a more organized way
    print(f"📅 DETAILED CALENDAR:")

    # Group days by week for better readability
    current_week = []
    week_num = 1

    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day).date()
        date_str = date.strftime("%Y-%m-%d")
        weekday = date.strftime("%a")

        is_available, reason = is_venue_available(venue_name, date_str)

        if is_available:
            status = "✅ Available"
            status_color = ""
        elif "blocked" in reason.lower():
            status = "🚫 BLOCKED"
            status_color = ""
        elif "pending" in reason.lower():
            event_name = reason.split(": ")[-1] if ": " in reason else "Pending Event"
            status = f"⏳ PENDING: {event_name}"
            status_color = ""
        else:
            event_name = reason.split(": ")[-1] if ": " in reason else "Event"
            status = f"🎪 EVENT: {event_name}"
            status_color = ""

        current_week.append((day, weekday, status))

        # Display week when we have 7 days or reach end of month
        if len(current_week) == 7 or day == days_in_month:
            print(f"\n🗓️  WEEK {week_num}:")
            for d, wd, st in current_week:
                # Truncate long event names for better display
                if len(st) > 60:
                    st = st[:57] + "..."
                print(f"   {d:2d} ({wd}): {st}")
            current_week = []
            week_num += 1

    # Show detailed event information if there are events
    if event_days or pending_days:
        print("\n" + "=" * 80)
        print("📋 EVENT DETAILS:")

        if event_days:
            print("\n🎪 CONFIRMED EVENTS:")
            for day, event_name in event_days:
                date = datetime(year, month, day).date()
                weekday = date.strftime("%A")
                print(f"   📅 {day:2d} ({weekday}): {event_name}")

        if pending_days:
            print("\n⏳ PENDING EVENTS:")
            for day, reason in pending_days:
                date = datetime(year, month, day).date()
                weekday = date.strftime("%A")
                event_name = reason.split(": ")[-1] if ": " in reason else "Pending Event"
                print(f"   📅 {day:2d} ({weekday}): {event_name}")

    # Show blocked dates if any
    if blocked_days:
        print("\n🚫 BLOCKED DATES:")
        for day in blocked_days:
            date = datetime(year, month, day).date()
            weekday = date.strftime("%A")
            print(f"   📅 {day:2d} ({weekday}): Venue unavailable")

    print("\n" + "=" * 80)


def show_venue_calendar_compact(venue_name, year, month):
    """Display calendar for a specific venue and month - Compact version"""
    import calendar

    print(f"\n📊 Calendar for 🏢 {venue_name} - {calendar.month_name[month]} {year}")
    print("=" * 60)

    # Get number of days in month
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)

    days_in_month = (next_month - datetime(year, month, 1)).days

    # Display in grid format (like a real calendar)
    print("   Mon  Tue  Wed  Thu  Fri  Sat  Sun")
    print("   " + "-" * 32)

    # Get first day of month and its weekday
    first_day = datetime(year, month, 1).date()
    first_weekday = first_day.weekday()  # 0=Monday, 6=Sunday

    # Print leading spaces for first week
    print("   ", end="")
    for i in range(first_weekday):
        print("     ", end="")

    # Print days
    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day).date()
        date_str = date.strftime("%Y-%m-%d")

        is_available, reason = is_venue_available(venue_name, date_str)

        if is_available:
            symbol = f"{day:2d}✅"
        elif "blocked" in reason.lower():
            symbol = f"{day:2d}🚫"
        elif "pending" in reason.lower():
            symbol = f"{day:2d}⏳"
        else:
            symbol = f"{day:2d}🎪"

        print(f"{symbol:>4} ", end="")

        # New line after Sunday or last day
        current_weekday = (first_weekday + day - 1) % 7
        if current_weekday == 6 or day == days_in_month:
            print()
            if day != days_in_month:
                print("   ", end="")

    print("\n" + "=" * 60)
    print("Legend: ✅ Available | 🎪 Event | ⏳ Pending | 🚫 Blocked")
    print("=" * 60)


def view_upcoming_events():
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

# Alternative cleaner version without icons
def view_upcoming_events_clean():
    """View upcoming events (not expired) - Clean version"""
    print("\n🔍 === Upcoming Events ===")
    today = datetime.now().date()
    upcoming_events = []

    try:
        with open(EVENTS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 7:
                        event_date = datetime.strptime(parts[2], "%Y-%m-%d").date()
                        if event_date >= today:
                            upcoming_events.append({
                                'event_id': parts[6] if len(parts) > 6 else 'N/A',
                                'title': parts[0],
                                'venue': parts[1],
                                'date': parts[2],
                                'time': parts[3],
                                'status': parts[4],
                                'organizer': parts[5]
                            })
    except FileNotFoundError:
        print("📂 No events found!")
        return

    if not upcoming_events:
        print("📅 No upcoming events found!")
        return

    # Display with proper column widths
    print(f"{'Event ID':<15} {'Title':<20} {'Venue':<15} {'Date':<12} {'Time':<8} {'Status':<30} {'Organizer':<20}")
    print("=" * 120)

    for event in upcoming_events:
        # Format status for better readability
        status_clean = event['status'].replace('_', ' ').replace('by', 'by').title()

        print(
            f"{event['event_id']:<15} {event['title']:<20} {event['venue']:<15} {event['date']:<12} {event['time']:<8} {status_clean:<30} {event['organizer']:<20}")

def mark_venue_unavailable():
    """Mark venue as unavailable on specific date"""
    print("\n🚫 === Mark Venue as Unavailable ===")
    venues = get_all_venues()

    if not venues:
        print("🔍 No venues found!")
        return

    print("🏢 Available venues:")
    for i, venue in enumerate(venues, 1):
        print(f"{i}. {venue['name']}")

    try:
        choice = int(input("🔢 Enter venue number: "))
        if 1 <= choice <= len(venues):
            venue_name = venues[choice - 1]['name']
            date_str = input("📅 Enter date to block (YYYY-MM-DD): ").strip()

            try:
                block_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                # Check if already blocked
                if is_venue_blocked(venue_name, block_date):
                    print(f"⚠️ Venue '{venue_name}' is already blocked on {date_str}")
                    return

                # Check if has event on that date
                event = get_event_on_date(venue_name, block_date)
                if event:
                    print(f"❌ Cannot block venue - it has an event: 🎪 {event['title']}")
                    return

                # Add to blocked dates
                with open(BLOCKED_DATES_FILE, 'a') as f:
                    f.write(f"{venue_name}|{date_str}\n")

                print(f"✅ Venue '{venue_name}' marked as unavailable on {date_str} 🚫")
            except ValueError:
                print("❌ Invalid date format! Please use YYYY-MM-DD")
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Please enter a valid number!")


def unblock_venue_date():
    """Unblock venue date"""
    print("\n🔓 === Unblock Venue Date ===")

    # Get all blocked dates
    blocked_dates = []
    try:
        with open(BLOCKED_DATES_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        blocked_dates.append((parts[0], parts[1]))
    except FileNotFoundError:
        print("🔍 No blocked dates found!")
        return

    if not blocked_dates:
        print("🔍 No blocked dates found!")
        return

    print("🚫 Blocked dates:")
    for i, (venue, date) in enumerate(blocked_dates, 1):
        print(f"{i}. 🏢 {venue} - 📅 {date}")

    try:
        choice = int(input("🔢 Enter number to unblock: "))
        if 1 <= choice <= len(blocked_dates):
            venue_to_unblock, date_to_unblock = blocked_dates[choice - 1]

            # Remove from blocked dates
            remaining_blocks = [(v, d) for v, d in blocked_dates if
                                not (v == venue_to_unblock and d == date_to_unblock)]

            with open(BLOCKED_DATES_FILE, 'w') as f:
                for venue, date in remaining_blocks:
                    f.write(f"{venue}|{date}\n")

            print(f"✅ Unblocked 🏢 {venue_to_unblock} on 📅 {date_to_unblock} 🎉")
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Please enter a valid number!")


def approve_reject_booking_requests():
    """✅❌ Approve or Reject Venue Booking Requests - Enhanced with two-stage approval"""
    print("\n🏢 === VENUE MANAGER: Review Bookings ===")

    # Get bookings that need venue manager review
    bookings_for_vm = []
    all_events_lines = []

    try:
        with open(EVENTS_FILE, 'r') as f:
            all_events_lines = f.readlines()
    except FileNotFoundError:
        print("📂 No bookings found!")
        return

    for i, line in enumerate(all_events_lines):
        line = line.strip()
        if line:
            parts = line.split('|')
            if len(parts) >= 7:
                status = parts[4].split('|')[0]  # Get status without timestamp
                # Venue manager can review: pending bookings or admin_approved bookings
                if status in ["pending", "admin_approved"]:
                    bookings_for_vm.append((i, parts))

    if not bookings_for_vm:
        print("🔍 No bookings need venue manager review!")
        return

    # Display bookings with enhanced format
    display_bookings_for_venue_manager(bookings_for_vm)

    # Show detailed venue information for selected booking
    choice = get_user_choice(len(bookings_for_vm))
    if choice is None:
        return

    line_index, booking_parts = bookings_for_vm[choice - 1]
    current_status = booking_parts[4].split('|')[0]

    # Display selected booking details
    print("\n" + "=" * 80)
    print("📋 SELECTED BOOKING DETAILS:")
    print("=" * 80)
    print(f"🆔 Event ID: {booking_parts[7] if len(booking_parts) > 7 else 'N/A'}")
    print(f"🎪 Event: {booking_parts[0]}")
    print(f"🏢 Venue: {booking_parts[1]}")
    print(f"📅 Date: {booking_parts[2]} | ⏰ Time: {booking_parts[3]}")
    print(f"👤 Organizer: {booking_parts[10] if len(booking_parts) > 10 else 'N/A'}")
    print(f"📧 Email: {booking_parts[6] if len(booking_parts) > 6 else 'N/A'}")

    # Show venue availability
    venue_name = booking_parts[1]
    date_str = booking_parts[2]
    show_venue_availability_info(venue_name, date_str)
    print("=" * 80)

    # Check venue availability before allowing approval
    if not check_venue_availability_for_approval(venue_name, date_str, booking_parts[0]):
        return

    decision = get_approval_decision("venue manager")
    if decision is None:
        return

    if decision == "approve":
        if current_status == "pending":
            new_status = "venue_manager_approved"
            print("✅ Booking approved by venue manager! Waiting for admin approval...")
        elif current_status == "admin_approved":
            new_status = "fully_approved"
            print("🎉 Booking FULLY APPROVED! Both admin and venue manager approved!")
    else:  # reject
        new_status = "rejected_by_venue_manager"
        print("❌ Booking rejected by venue manager!")

    # Update status with new timestamp - FIXED: Replace only the status field, keep original timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    booking_parts[4] = new_status  # Only update status, don't add timestamp here
    booking_parts[5] = timestamp  # Update the timestamp field (index 5)

    # Save changes
    all_events_lines[line_index] = '|'.join(booking_parts) + '\n'
    with open(EVENTS_FILE, 'w') as f:
        f.writelines(all_events_lines)

    print(f"\n🎯 Status updated successfully! 🎯")


def suggest_alternative_venues():
    """Suggest alternative venues for a date"""
    print("\n💡 === Suggest Alternative Venues ===")
    date_str = input("📅 Enter date (YYYY-MM-DD): ").strip()

    try:
        check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ Invalid date format! Please use YYYY-MM-DD")
        return

    venues = get_all_venues()
    available_venues = []
    unavailable_venues = []

    for venue in venues:
        venue_name = venue['name']
        is_available, reason = is_venue_available(venue_name, date_str)

        if is_available:
            available_venues.append(venue)
        else:
            unavailable_venues.append({
                'venue': venue,
                'reason': reason
            })

    if available_venues:
        print(f"\n✅ Available venues for 📅 {date_str}:")
        print("-" * 60)
        for venue in available_venues:
            print(f"🏢 Name: {venue['name']}")
            print(f"📍 Location: {venue['location']}")
            print(f"👥 Capacity: {venue['capacity']}")
            print(f"📋 Description: {venue['description']}")
            print("-" * 60)
    else:
        print(f"🔍 No venues available on 📅 {date_str}")

    # Show unavailable venues with reasons
    if unavailable_venues:
        print(f"\n❌ Unavailable venues for 📅 {date_str}:")
        print("-" * 60)
        for item in unavailable_venues:
            venue = item['venue']
            reason = item['reason']
            print(f"🏢 Name: {venue['name']} - {reason}")
            print(f"📍 Location: {venue['location']}")
            print(f"👥 Capacity: {venue['capacity']}")
            print("-" * 60)


def export_booking_report():
    """Export venue booking report"""
    print("\n📄 === Export Venue Booking Report ===")

    # Get date range
    start_date_str = input("📅 Enter start date (YYYY-MM-DD): ").strip()
    end_date_str = input("📅 Enter end date (YYYY-MM-DD): ").strip()

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("❌ Invalid date format! Please use YYYY-MM-DD")
        return

    if start_date > end_date:
        print("❌ Start date cannot be after end date!")
        return

    # Generate report
    report_filename = f"booking_report_{start_date}_{end_date}.txt"

    with open(report_filename, 'w', encoding='utf-8') as report_file:
        report_file.write(f"📄 Venue Booking Report\n")
        report_file.write(f"📅 Period: {start_date} to {end_date}\n")
        report_file.write(f"🕒 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_file.write("=" * 60 + "\n\n")

        venues = get_all_venues()

        for venue in venues:
            venue_name = venue['name']
            report_file.write(f"🏢 Venue: {venue_name}\n")
            report_file.write(f"📍 Location: {venue['location']}\n")
            report_file.write(f"👥 Capacity: {venue['capacity']}\n")
            report_file.write("-" * 40 + "\n")

            # Get events for this venue in date range
            venue_events = []
            try:
                with open(EVENTS_FILE, 'r') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split('|')
                            # Updated to handle new format with event_id
                            if len(parts) >= 7 and parts[1] == venue_name:
                                event_date = datetime.strptime(parts[2], "%Y-%m-%d").date()
                                if start_date <= event_date <= end_date:
                                    venue_events.append({
                                        'title': parts[0],
                                        'date': parts[2],
                                        'time': parts[3],
                                        'status': parts[4],
                                        'organizer': parts[5],
                                        'event_id': parts[6] if len(parts) > 6 else 'N/A'
                                    })
            except FileNotFoundError:
                pass

            if venue_events:
                venue_events.sort(key=lambda x: x['date'])
                report_file.write("🎪 Events:\n")
                for event in venue_events:
                    status_emoji = {'approved': '✅', 'pending': '⏳', 'rejected': '❌'}.get(event['status'], '❓')
                    report_file.write(
                        f"  📅 {event['date']} ⏰ {event['time']} - 🎪 {event['title']} (🆔 ID: {event['event_id']}) ({status_emoji} Status: {event['status']}) - 👤 Organizer: {event['organizer']}\n")
            else:
                report_file.write("🔍 No events in this period.\n")

            # Get blocked dates for this venue in date range
            blocked_dates = []
            try:
                with open(BLOCKED_DATES_FILE, 'r') as f:
                    for line in f:
                        if line.strip():
                            parts = line.strip().split('|')
                            if len(parts) >= 2 and parts[0] == venue_name:
                                block_date = datetime.strptime(parts[1], "%Y-%m-%d").date()
                                if start_date <= block_date <= end_date:
                                    blocked_dates.append(parts[1])
            except FileNotFoundError:
                pass

            if blocked_dates:
                blocked_dates.sort()
                report_file.write("🚫 Blocked dates:\n")
                for block_date in blocked_dates:
                    report_file.write(f"  📅 {block_date}\n")

            report_file.write("\n" + "=" * 60 + "\n\n")

    print(f"✅ Report exported to: 📄 {report_filename} 🎉")


def main_menu():
    """Display main menu and handle user choices"""
    initialize_files()

    while True:
        print("\n" + "=" * 50)
        print("         🏢 VENUE MANAGER SYSTEM 🏢")
        print("=" * 50)
        print("1.  📅 View Venue Availability by Date")
        print("2.  🗓️ View Venue Calendar")
        print("3.  🔍 View Upcoming Events")
        print("4.  ➕ Add New Venue")
        print("5.  🗑️ Delete Venue")
        print("6.  🚫 Mark Venue as Unavailable")
        print("7.  🔓 Unblock Venue Date")
        print("8.  ✅❌ Approve or Reject Venue Booking Requests")
        print("9.  💡 Suggest Alternative Venues")
        print("10. 📄 Export Venue Booking Report")
        print("11. 🚪 Exit")
        print("=" * 50)

        choice_1 = input("🔢 Enter your choice (1-11): ").strip()
        valid_action = True

        if choice_1 == '1':
            view_venue_availability()
        elif choice_1 == '2':
            view_venue_calendar()
        elif choice_1 == '3':
            view_upcoming_events()
        elif choice_1 == '4':
            add_venue()
        elif choice_1 == '5':
            delete_venue()
        elif choice_1 == '6':
            mark_venue_unavailable()
        elif choice_1 == '7':
            unblock_venue_date()
        elif choice_1 == '8':
            approve_reject_booking_requests()
        elif choice_1 == '9':
            suggest_alternative_venues()
        elif choice_1 == '10':
            export_booking_report()
        elif choice_1 == '11':
            print("👋 Thank you for using Venue Manager System! Have a great day! 🌟")
            break
        else:
            print("❌ Invalid choice! Please try again. 🔄")

        input("\n⏎ Press Enter to continue...")

        if valid_action and choice_1 != "11":  # Fixed condition - should be "11" for exit
            choice_2 = input("\n🤔 Do you want to perform another action? (yes/no): ").strip().lower()
            if choice_2 not in ["yes", "y"]:
                print("👋 Exiting Venue Manager system. Goodbye! 🌟")
                break

if __name__ == "__main__":
    initialize_files()
    main_menu()