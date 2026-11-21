import os
from datetime import datetime

# 🗂️ File paths for storing data
EVENTS_FILE = "events.txt"
REGISTRATIONS_FILE = "registrations.txt"


def read_events():
    """📂 Read all events from file and return them as a list"""
    events = []
    try:
        with open(EVENTS_FILE, 'r') as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 11:  # Updated to match actual format (11 fields)
                        events.append({
                            'event_id': parts[7],      # Event ID is at index 7
                            'title': parts[0],         # Title is at index 0
                            'date': parts[2],          # Date is at index 2
                            'location': parts[1],      # Location is at index 1
                            'description': parts[8],   # Description is at index 8
                            'capacity': int(parts[9]), # Capacity is at index 9
                            'organizer': parts[10],    # Organizer is at index 10
                            'status': parts[4],        # Status is at index 4
                            'time': parts[3],          # Time is at index 3 (additional field)
                            'created_date': parts[5],  # Created date is at index 5 (additional field)
                            'email': parts[6]          # Email is at index 6 (additional field)
                        })
    except FileNotFoundError:
        print("📄 No events found. The events file doesn't exist yet.")
    except Exception as e:
        print(f"⚠️ Error reading events: {e}")
    return events


def read_registrations():
    """📂 Read all registrations from file and return them as a list"""
    registrations = []
    try:
        with open(REGISTRATIONS_FILE, 'r') as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 4:
                        registrations.append({
                            'username': parts[0],
                            'event_id': parts[1],
                            'registration_date': parts[2],
                            'status': parts[3]
                        })
    except FileNotFoundError:
        pass  # No registrations yet
    except Exception as e:
        print(f"⚠️ Error reading registrations: {e}")
    return registrations

def read_users():
    """📂 Read all users from file and return them as a list"""
    users = []
    try:
        with open("users.txt", 'r') as file:  # Assuming your users file is named users.txt
            for line in file:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) >= 6:
                        users.append({
                            'username': parts[0],
                            'email': parts[1],
                            'password': parts[2],
                            'position': parts[3],
                            'role': parts[4],
                            'registration_date': parts[5]
                        })
    except FileNotFoundError:
        print("📄 No users found. The users file doesn't exist yet.")
    except Exception as e:
        print(f"⚠️ Error reading users: {e}")
    return users


def is_event_organizer(username, event_id):
    """🔎 Check if user is the organizer of an event"""
    events = read_events()
    users = read_users()

    # Get user's email from username
    user_email = None
    for user in users:
        if user['username'] == username:
            user_email = user['email']
            break

    if not user_email:
        return False

    # Check if user's email matches event's organizer email
    for event in events:
        if event['event_id'] == event_id:
            return event['email'] == user_email

    return False

def write_registration(username, event_id):
    """📝 Save a new registration to file"""
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registration_data = f"{username}|{event_id}|{registration_date}|Active\n"
    try:
        with open(REGISTRATIONS_FILE, 'a') as file:
            file.write(registration_data)
        return True
    except Exception as e:
        print(f"⚠️ Error saving registration: {e}")
        return False


def update_registrations(registrations):
    """📝 Update the entire registrations file"""
    try:
        with open(REGISTRATIONS_FILE, 'w') as file:
            for reg in registrations:
                line = f"{reg['username']}|{reg['event_id']}|{reg['registration_date']}|{reg['status']}\n"
                file.write(line)
        return True
    except Exception as e:
        print(f"⚠️ Error updating registrations: {e}")
        return False


def is_user_registered(username, event_id):
    """🔎 Check if user is already registered for an event"""
    registrations = read_registrations()
    for reg in registrations:
        if reg['username'] == username and reg['event_id'] == event_id and reg['status'] == 'Active':
            return True
    return False


def get_event_registration_count(event_id):
    """📊 Count active registrations for an event"""
    registrations = read_registrations()
    count = 0
    for reg in registrations:
        if reg['event_id'] == event_id and reg['status'] == 'Active':
            count += 1
    return count


def validate_date_format(date_str):
    """✅ Validate if date is in correct format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_future_date(date_str):
    """🗓️ Check if the event date is in the future"""
    try:
        event_date = datetime.strptime(date_str, "%Y-%m-%d")
        current_date = datetime.now()
        return event_date.date() >= current_date.date()
    except ValueError:
        return False


def browse_upcoming_events():
    """🔍 Browse and display all upcoming approved events"""
    print("\n=== 🎪 UPCOMING EVENTS ===")
    events = read_events()

    if not events:
        print("📭 No events available at the moment.")
        print("🌟 Check back later for exciting campus events!")
        return

    # Filter for fully approved and upcoming events
    upcoming_events = []
    for event in events:
        if event['status'].lower() == 'fully_approved' and is_future_date(event['date']):
            upcoming_events.append(event)

    if not upcoming_events:
        print("📭 No upcoming fully approved events found.")
        print("🌟 Stay tuned for new events!")
        return

    print(f"📅 Found {len(upcoming_events)} upcoming events:")
    print("-" * 80)

    for i, event in enumerate(upcoming_events, 1):
        registered_count = get_event_registration_count(event['event_id'])
        available_spots = event['capacity'] - registered_count

        print(f"\n🎯 Event #{i}")
        print(f"🆔 ID: {event['event_id']}")
        print(f"📝 Title: {event['title']}")
        print(f"📅 Date: {event['date']}")
        print(f"📍 Location: {event['location']}")
        print(f"📖 Description: {event['description']}")
        print(f"👥 Capacity: {event['capacity']} | Registered: {registered_count} | Available: {available_spots}")
        print(f"👤 Organizer: {event['organizer']}")

        if available_spots <= 0:
            print("🚫 FULLY BOOKED")
        elif available_spots <= 5:
            print("⚠️ LIMITED SPOTS AVAILABLE!")

        print("-" * 40)


def search_events():
    """🔎 Search events by title, date, or location"""
    print("\n=== 🔍 SEARCH EVENTS ===")
    print("🎯 Search by:")
    print("1️⃣ Event Title")
    print("2️⃣ Event Date (YYYY-MM-DD)")
    print("3️⃣ Location")
    print("4️⃣ Go Back")

    choice = input("\n🔢 Select search option (1-4): ").strip()

    if choice == "4":
        return

    if choice not in ["1", "2", "3"]:
        print("⚠️ Invalid option. Please select 1-4.")
        return

    search_term = input("🔍 Enter search term: ").strip().lower()
    if not search_term:
        print("⚠️ Search term cannot be empty.")
        return

    events = read_events()
    if not events:
        print("📭 No events available to search.")
        return

    # Filter for fully approved and upcoming events
    matching_events = []
    for event in events:
        if event['status'].lower() != 'fully_approved' or not is_future_date(event['date']):
            continue

        match_found = False
        if choice == "1":  # Search by title
            match_found = search_term in event['title'].lower()
        elif choice == "2":  # Search by date
            match_found = search_term in event['date']
        elif choice == "3":  # Search by location
            match_found = search_term in event['location'].lower()

        if match_found:
            matching_events.append(event)

    if not matching_events:
        print(f"🔍 No matching events found for '{search_term}'.")
        print("💡 Try different search terms or browse all events.")
        return

    print(f"\n🎯 Found {len(matching_events)} matching events:")
    print("-" * 80)

    for i, event in enumerate(matching_events, 1):
        registered_count = get_event_registration_count(event['event_id'])
        available_spots = event['capacity'] - registered_count

        print(f"\n🎪 Event #{i}")
        print(f"🆔 ID: {event['event_id']}")
        print(f"📝 Title: {event['title']}")
        print(f"📅 Date: {event['date']}")
        print(f"📍 Location: {event['location']}")
        print(f"📖 Description: {event['description']}")
        print(f"👥 Capacity: {event['capacity']} | Registered: {registered_count} | Available: {available_spots}")
        print(f"👤 Organizer: {event['organizer']}")

        if available_spots <= 0:
            print("🚫 FULLY BOOKED")
        elif available_spots <= 5:
            print("⚠️ LIMITED SPOTS AVAILABLE!")

        print("-" * 40)


def register_for_event(username):
    """🎫 Register user for an event"""
    print("\n=== 🎫 EVENT REGISTRATION ===")

    # First show available events
    events = read_events()
    if not events:
        print("📭 No events available for registration.")
        return

    # Filter for fully approved and upcoming events with available spots
    available_events = []
    for event in events:
        if (event['status'].lower() == 'fully_approved' and
                is_future_date(event['date']) and
                not is_user_registered(username, event['event_id']) and
                not is_event_organizer(username, event['event_id'])):  # NEW: Check if user is organizer

            registered_count = get_event_registration_count(event['event_id'])
            if registered_count < event['capacity']:
                available_events.append(event)

    if not available_events:
        print("📭 No events available for registration.")
        print("💡 You might already be registered for all available events,")
        print("   all events are fully booked, or you are the organizer of available events.")
        return

    print(f"🎪 Available events for registration ({len(available_events)} found):")
    print("-" * 80)

    for i, event in enumerate(available_events, 1):
        registered_count = get_event_registration_count(event['event_id'])
        available_spots = event['capacity'] - registered_count

        print(f"\n{i}. 🎯 {event['title']}")
        print(f"   🆔 ID: {event['event_id']}")
        print(f"   📅 Date: {event['date']}")
        print(f"   📍 Location: {event['location']}")
        print(f"   📖 Description: {event['description']}")
        print(f"   👥 Available Spots: {available_spots}/{event['capacity']}")

        if available_spots <= 5:
            print("   ⚠️ LIMITED SPOTS!")

    print(f"\n{len(available_events) + 1}. 🔙 Go Back")

    while True:
        try:
            choice = input(f"\n🔢 Select event to register (1-{len(available_events) + 1}): ").strip()
            choice_num = int(choice)

            if choice_num == len(available_events) + 1:
                return

            if 1 <= choice_num <= len(available_events):
                selected_event = available_events[choice_num - 1]
                break
            else:
                print(f"⚠️ Please select a number between 1 and {len(available_events) + 1}.")
        except ValueError:
            print("⚠️ Please enter a valid number.")

    # Confirm registration
    print(f"\n🎯 You selected: {selected_event['title']}")
    print(f"📅 Date: {selected_event['date']}")
    print(f"📍 Location: {selected_event['location']}")

    confirm = input("\n✅ Confirm registration? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Registration cancelled.")
        return

    # Double-check availability, registration status, and organizer status
    current_registrations = get_event_registration_count(selected_event['event_id'])
    if current_registrations >= selected_event['capacity']:
        print("😔 Sorry! This event just became fully booked.")
        return

    if is_user_registered(username, selected_event['event_id']):
        print("⚠️ You are already registered for this event!")
        return

    # NEW: Double-check organizer status
    if is_event_organizer(username, selected_event['event_id']):
        print("⚠️ You cannot register for your own event as the organizer!")
        return

    # Register the user
    if write_registration(username, selected_event['event_id']):
        print("🎉 Registration successful!")
        print(f"✅ You are now registered for '{selected_event['title']}'")
        print(f"📅 Event Date: {selected_event['date']}")
        print(f"📍 Location: {selected_event['location']}")
        print("💡 Don't forget to mark your calendar!")
    else:
        print("❌ Registration failed. Please try again.")


def cancel_registration(username):
    """❌ Cancel user's event registration"""
    print("\n=== ❌ CANCEL REGISTRATION ===")

    # Get user's active registrations
    registrations = read_registrations()
    events = read_events()

    user_registrations = []
    for reg in registrations:
        if reg['username'] == username and reg['status'] == 'Active':
            # Find the corresponding event
            for event in events:
                if event['event_id'] == reg['event_id']:
                    user_registrations.append({
                        'registration': reg,
                        'event': event
                    })
                    break

    if not user_registrations:
        print("📭 You have no active event registrations.")
        print("🎫 Register for some exciting events first!")
        return

    print(f"🎫 Your active registrations ({len(user_registrations)} found):")
    print("-" * 80)

    for i, reg_info in enumerate(user_registrations, 1):
        event = reg_info['event']
        reg = reg_info['registration']

        print(f"\n{i}. 🎯 {event['title']}")
        print(f"   🆔 Event ID: {event['event_id']}")
        print(f"   📅 Date: {event['date']}")
        print(f"   📍 Location: {event['location']}")
        print(f"   📝 Registered on: {reg['registration_date']}")

        # Check if event is soon
        try:
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")
            days_until = (event_date.date() - datetime.now().date()).days
            if days_until <= 3:
                print(f"   ⚠️ EVENT IS IN {days_until} DAYS!")
        except:
            pass

    print(f"\n{len(user_registrations) + 1}. 🔙 Go Back")

    while True:
        try:
            choice = input(f"\n🔢 Select registration to cancel (1-{len(user_registrations) + 1}): ").strip()
            choice_num = int(choice)

            if choice_num == len(user_registrations) + 1:
                return

            if 1 <= choice_num <= len(user_registrations):
                selected_reg = user_registrations[choice_num - 1]
                break
            else:
                print(f"⚠️ Please select a number between 1 and {len(user_registrations) + 1}.")
        except ValueError:
            print("⚠️ Please enter a valid number.")

    # Confirm cancellation
    event = selected_reg['event']
    print(f"\n❌ You selected to cancel: {event['title']}")
    print(f"📅 Date: {event['date']}")
    print(f"📍 Location: {event['location']}")

    # Warning for events happening soon
    try:
        event_date = datetime.strptime(event['date'], "%Y-%m-%d")
        days_until = (event_date.date() - datetime.now().date()).days
        if days_until <= 7:
            print(f"⚠️ WARNING: This event is happening in {days_until} days!")
    except:
        pass

    confirm = input("\n❌ Are you sure you want to cancel? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("✅ Cancellation aborted. Your registration remains active.")
        return

    # Cancel the registration
    all_registrations = read_registrations()
    for reg in all_registrations:
        if (reg['username'] == username and
                reg['event_id'] == selected_reg['registration']['event_id'] and
                reg['status'] == 'Active'):
            reg['status'] = 'Cancelled'
            break

    if update_registrations(all_registrations):
        print("✅ Registration cancelled successfully!")
        print(f"❌ You are no longer registered for '{event['title']}'")
        print("🎫 You can register for other events anytime!")
    else:
        print("❌ Failed to cancel registration. Please try again.")


def view_personal_calendar(username):
    """📅 View user's personal event calendar"""
    print("\n=== 📅 MY EVENT CALENDAR ===")

    # Get user's active registrations
    registrations = read_registrations()
    events = read_events()

    user_events = []
    for reg in registrations:
        if reg['username'] == username and reg['status'] == 'Active':
            # Find the corresponding event
            for event in events:
                if event['event_id'] == reg['event_id']:
                    user_events.append({
                        'event': event,
                        'registration_date': reg['registration_date']
                    })
                    break

    if not user_events:
        print("📭 Your calendar is empty!")
        print("🎫 Register for some exciting events to get started!")
        return

    # Sort events by date
    try:
        user_events.sort(key=lambda x: datetime.strptime(x['event']['date'], "%Y-%m-%d"))
    except:
        pass  # If date parsing fails, show unsorted

    # Separate upcoming and past events
    upcoming_events = []
    past_events = []

    for event_info in user_events:
        if is_future_date(event_info['event']['date']):
            upcoming_events.append(event_info)
        else:
            past_events.append(event_info)

    print(f"🎯 Total Events: {len(user_events)}")

    # Show upcoming events
    if upcoming_events:
        print(f"\n🔮 UPCOMING EVENTS ({len(upcoming_events)}):")
        print("-" * 80)

        for i, event_info in enumerate(upcoming_events, 1):
            event = event_info['event']

            print(f"\n🎪 Event #{i}")
            print(f"📝 Title: {event['title']}")
            print(f"📅 Date: {event['date']}")
            print(f"📍 Location: {event['location']}")
            print(f"📖 Description: {event['description']}")
            print(f"👤 Organizer: {event['organizer']}")
            print(f"🎫 Registered on: {event_info['registration_date']}")

            # Show days until event
            try:
                event_date = datetime.strptime(event['date'], "%Y-%m-%d")
                days_until = (event_date.date() - datetime.now().date()).days
                if days_until == 0:
                    print("🔥 TODAY!")
                elif days_until == 1:
                    print("⚡ TOMORROW!")
                elif days_until <= 7:
                    print(f"⏰ In {days_until} days")
                else:
                    print(f"📆 In {days_until} days")
            except:
                pass

            print("-" * 40)

    # Show past events
    if past_events:
        print(f"\n📚 PAST EVENTS ({len(past_events)}):")
        print("-" * 80)

        for i, event_info in enumerate(past_events, 1):
            event = event_info['event']

            print(f"\n🕰️ Event #{i}")
            print(f"📝 Title: {event['title']}")
            print(f"📅 Date: {event['date']}")
            print(f"📍 Location: {event['location']}")
            print(f"🎫 Registered on: {event_info['registration_date']}")
            print("-" * 40)

    # Show calendar summary
    print(f"\n📊 CALENDAR SUMMARY:")
    print(f"🔮 Upcoming Events: {len(upcoming_events)}")
    print(f"📚 Past Events: {len(past_events)}")
    print(f"📅 Total Events: {len(user_events)}")


def main_menu(user_data):
    """📜 Main menu for participants"""
    username = user_data['username']

    while True:
        print(f"\n=== 🎫 PARTICIPANT MENU - Welcome {username}! ===")
        print("1️⃣ 🔍 Browse/Search Upcoming Events")
        print("2️⃣ 🎫 Register for an Event")
        print("3️⃣ ❌ Cancel Registration")
        print("4️⃣ 📅 View My Event Calendar")
        print("5️⃣ 🔙 Back to Main Menu")

        choice = input("\n🔢 Select an option (1-5): ").strip()

        if choice == "1":
            print("\n🔍 EVENT DISCOVERY")
            print("1️⃣ 📋 Browse All Upcoming Events")
            print("2️⃣ 🔎 Search Specific Events")
            print("3️⃣ 🔙 Go Back")

            sub_choice = input("\n🔢 Select option (1-3): ").strip()

            if sub_choice == "1":
                browse_upcoming_events()
            elif sub_choice == "2":
                search_events()
            elif sub_choice == "3":
                continue
            else:
                print("⚠️ Invalid option. Please select 1-3.")

            input("\n🔙 Press Enter to continue...")

        elif choice == "2":
            register_for_event(username)
            input("\n🔙 Press Enter to continue...")

        elif choice == "3":
            cancel_registration(username)
            input("\n🔙 Press Enter to continue...")

        elif choice == "4":
            view_personal_calendar(username)
            input("\n🔙 Press Enter to continue...")

        elif choice == "5":
            print("🔙 Returning to main menu...")
            break

        else:
            print("⚠️ Invalid option. Please select 1-5.")


if __name__ == "__main__":
    # Run tests when module is executed directly
    main_menu()