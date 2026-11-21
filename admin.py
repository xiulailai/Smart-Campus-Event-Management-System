from datetime import datetime


def admin_menu():
    while True:
        print("\n--- Admin Menu ---")
        print("1. Approve/Reject Event")
        print("2. View System Statistics")
        print("3. Generate Report")
        print("4. Manage User Roles")
        print("5. Logout")

        choice = input("Enter choice: ")
        if choice == "1":
            approve_or_reject_event()
        elif choice == "2":
            view_statistics()
        elif choice == "3":
            generate_report()
        elif choice == "4":
            manage_roles()
        elif choice == "5":
            logout()
            break
        else:
            print("Invalid choice.")


def approve_or_reject_event():
    """Admin Approve or Reject Event Requests - Enhanced with two-stage approval"""
    print("\n=== ADMIN: Review Events ===")

    # Get events that need admin review
    events_for_admin = []
    all_events_lines = []

    try:
        with open("events.txt", "r") as f:
            all_events_lines = f.readlines()
    except FileNotFoundError:
        print("No events found!")
        return

    for i, line in enumerate(all_events_lines):
        line = line.strip()
        if line:
            parts = line.split('|')
            if len(parts) >= 7:
                status = parts[4].split('|')[0] if '|' in parts[4] else parts[4]  # Get status without timestamp
                # Admin can review: pending events or venue_manager_approved events
                if status.lower() in ["pending", "venue_manager_approved", "approved_by_venue_manager"]:
                    events_for_admin.append((i, parts))

    if not events_for_admin:
        print("No events need admin review!")
        return

    # Display events for admin review
    display_events_for_admin(events_for_admin)

    # Show detailed view of selected event
    choice = get_admin_choice(len(events_for_admin))
    if choice is None:
        return

    line_index, event_parts = events_for_admin[choice - 1]

    # Display detailed event information
    display_event_details(event_parts)

    current_status = event_parts[4].split('|')[0] if '|' in event_parts[4] else event_parts[4]

    decision = get_admin_decision()
    if decision is None:
        return

    if decision == "approve":
        if current_status.lower() == "pending":
            new_status = "admin_approved"
            print("\n✅ Event approved by admin! Waiting for venue manager approval...")
        elif current_status.lower() in ["venue_manager_approved", "approved_by_venue_manager"]:
            new_status = "fully_approved"
            print("\n🎉 Event FULLY APPROVED! Both admin and venue manager approved!")
    else:  # reject
        new_status = "rejected_by_admin"
        print("\n❌ Event rejected by admin!")

    # Update status with new timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event_parts[4] = new_status  # Only update status
    event_parts[5] = timestamp  # Update the timestamp field (index 5)

    # Save changes
    all_events_lines[line_index] = '|'.join(event_parts) + '\n'

    try:
        with open("events.txt", "w") as f:
            f.writelines(all_events_lines)
        print("✅ Event status updated successfully.")
    except Exception as e:
        print(f"❌ Failed to write back to 'events.txt': {e}")


def display_events_for_admin(events_list):
    """Display events in a formatted way for admin review"""
    print("\nEvents Pending Admin Review:")
    print("=" * 90)
    print(f"{'#':<3}{'Event ID':<8}{'Title':<35}{'Date':<12}{'Status':<20}")
    print("=" * 90)

    for i, (line_index, parts) in enumerate(events_list):
        # Get the actual event ID (should be at index 7, not 6)
        event_id = parts[7] if len(parts) > 7 else "N/A"

        # If event_id is still showing email, try to extract from different position
        if "@" in event_id:
            # Look for a proper event ID pattern (EV001, EV002, etc.)
            for part in parts:
                if part.startswith("EV") and len(part) <= 10:
                    event_id = part
                    break
            else:
                event_id = f"EV{i + 1:03d}"  # Fallback to generated ID

        title = parts[0]
        # Truncate title if too long
        if len(title) > 32:
            title = title[:32] + "..."

        date = parts[2]
        status = parts[4].split('|')[0] if '|' in parts[4] else parts[4]

        # Format status for better readability
        status_display = status.replace('_', ' ').title()

        print(f"{i + 1:<3}{event_id:<8}{title:<35}{date:<12}{status_display:<20}")

    print("=" * 90)


def display_event_details(event_parts):
    """Display detailed information about a specific event"""
    print("\n" + "=" * 60)
    print("📋 EVENT DETAILS")
    print("=" * 60)

    if len(event_parts) >= 11:
        title = event_parts[0]
        venue = event_parts[1]
        date = event_parts[2]
        time = event_parts[3]
        status = event_parts[4]
        timestamp = event_parts[5]
        email = event_parts[6]
        event_id = event_parts[7]
        description = event_parts[8] if len(event_parts) > 8 else "No description available"
        capacity = event_parts[9] if len(event_parts) > 9 else "Not specified"
        organizer = event_parts[10] if len(event_parts) > 10 else "Unknown"

        print(f"🎯 Event ID      : {event_id}")
        print(f"📝 Title         : {title}")
        print(f"🏢 Venue         : {venue}")
        print(f"📅 Date          : {date}")
        print(f"🕐 Time          : {time}")
        print(f"📊 Status        : {status.replace('_', ' ').title()}")
        print(f"📧 Contact       : {email}")
        print(f"👥 Capacity      : {capacity}")
        print(f"👨‍💼 Organizer     : {organizer}")
        print(f"🕒 Last Updated  : {timestamp}")
        print(f"\n📄 Description:")
        print(f"   {description}")
    else:
        print("⚠️ Event data appears to be incomplete.")

    print("=" * 60)


def get_admin_choice(max_events):
    """Get admin's choice of which event to review"""
    try:
        choice = input(f"\n🔢 Enter event number to review (1-{max_events}) or 'b' to go back: ").strip().lower()
        if choice == 'b':
            return None

        choice_num = int(choice)
        if 1 <= choice_num <= max_events:
            return choice_num
        else:
            print(f"⚠️ Invalid choice. Please enter a number between 1 and {max_events}.")
            return None
    except ValueError:
        print("⚠️ Invalid input. Please enter a valid number.")
        return None


def get_admin_decision():
    """Get admin's approval/rejection decision"""
    while True:
        decision = input("\n🤔 Decision: [A]pprove or [R]eject? (a/r/b to go back): ").strip().lower()
        if decision == 'b':
            return None
        elif decision in ['a', 'approve']:
            return "approve"
        elif decision in ['r', 'reject']:
            return "reject"
        else:
            print("⚠️ Invalid choice. Please enter 'a' to approve, 'r' to reject, or 'b' to go back.")


def view_statistics():
    """Admin view: Show comprehensive system-wide statistics."""
    event_file = "events.txt"
    registration_file = "registrations.txt"
    users_file = "users.txt"

    # Initialize counters
    total_events = 0
    status_counts = {
        'fully_approved': 0,
        'admin_approved': 0,
        'venue_manager_approved': 0,
        'approved_by_venue_manager': 0,
        'pending': 0,
        'rejected_by_admin': 0,
        'rejected_by_venue_manager': 0,
        'rejected': 0,
        'other': 0
    }

    event_registration_count = {}
    event_details = {}  # Store event details for better reporting

    # Read events
    try:
        with open(event_file, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 7:
                    total_events += 1
                    title = parts[0]
                    venue = parts[1]
                    date = parts[2]
                    time = parts[3]
                    status = parts[4].lower().strip()
                    event_id = parts[7]
                    organizer = parts[-1] if len(parts) > 10 else "Unknown"

                    # Count status occurrences
                    if status in status_counts:
                        status_counts[status] += 1
                    else:
                        status_counts['other'] += 1

                    # Store event details
                    event_details[event_id] = {
                        'title': title,
                        'venue': venue,
                        'date': date,
                        'time': time,
                        'status': status,
                        'organizer': organizer,
                        'registrations': 0
                    }

                    event_registration_count[event_id] = 0
    except FileNotFoundError:
        print("❌ events.txt not found.")
        return

    # Count participants per event
    try:
        with open('registrations.txt', 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 4:  # registration: username|event_id|timestamp|status
                    event_id = parts[1].strip()
                    status = parts[3].strip().lower()
                    if event_id in event_registration_count and status == "active":
                        event_registration_count[event_id] += 1
                        if event_id in event_details:
                            event_details[event_id]['registrations'] += 1
    except FileNotFoundError:
        pass  # It's okay if registrations.txt doesn't exist yet

    # Calculate approval statistics
    total_approved = status_counts['fully_approved'] + status_counts['admin_approved'] + status_counts[
        'venue_manager_approved'] + status_counts['approved_by_venue_manager']
    total_rejected = status_counts['rejected_by_admin'] + status_counts['rejected_by_venue_manager'] + status_counts[
        'rejected']
    total_pending = status_counts['pending']

    # Find most popular event
    if event_registration_count and max(event_registration_count.values()) > 0:
        most_popular_id = max(event_registration_count, key=event_registration_count.get)
        most_popular_count = event_registration_count[most_popular_id]
        most_popular_title = event_details[most_popular_id]['title'] if most_popular_id in event_details else "Unknown"
        most_popular = f"{most_popular_title} ({most_popular_count} registrations)"
    else:
        most_popular = "N/A"

    # Count user roles
    role_counts = {"participant": 0, "event organizer": 0, "venue manager": 0, "administrator": 0}
    total_users = 0

    try:
        with open(users_file, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 5:
                    role = parts[4].strip().lower()
                    total_users += 1
                    if role in role_counts:
                        role_counts[role] += 1
    except FileNotFoundError:
        print("❌ users.txt not found.")

    # Display comprehensive statistics
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE SYSTEM STATISTICS")
    print("=" * 60)

    print(f"\n📅 EVENT OVERVIEW:")
    print(f"   📁 Total Events        : {total_events}")
    print(f"   ✅ Total Approved      : {total_approved}")
    print(f"   ⏳ Pending Review      : {total_pending}")
    print(f"   ❌ Total Rejected      : {total_rejected}")

    print(f"\n📋 DETAILED EVENT STATUS:")
    print(f"   🎯 Fully Approved      : {status_counts['fully_approved']}")
    print(f"   👨‍💼 Admin Approved      : {status_counts['admin_approved']}")
    print(
        f"   🏢 Venue Mgr Approved  : {status_counts['venue_manager_approved'] + status_counts['approved_by_venue_manager']}")
    print(f"   ⏳ Pending Review      : {status_counts['pending']}")
    print(f"   ❌ Rejected by Admin   : {status_counts['rejected_by_admin']}")
    print(f"   🚫 Rejected by Venue   : {status_counts['rejected_by_venue_manager']}")
    print(f"   ❌ Other Rejections    : {status_counts['rejected']}")
    if status_counts['other'] > 0:
        print(f"   ❓ Other Status        : {status_counts['other']}")

    print(f"\n🌟 POPULAR EVENTS:")
    print(f"   Most Popular Event     : {most_popular}")

    # Show top 3 events by registration (only with registrations > 0)
    if event_registration_count:
        # Sort and filter events with count > 0
        sorted_events = sorted(
            [(eid, cnt) for eid, cnt in event_registration_count.items() if cnt > 0],
            key=lambda x: x[1], reverse=True
        )
        print(f"📄 Top Events by Registration:")
        if sorted_events:
            for i, (event_id, count) in enumerate(sorted_events[:3], 1):
                title = event_details[event_id]['title'] if event_id in event_details else event_id
                print(f"   {i}. {title[:40]}{'...' if len(title) > 40 else ''} ({count})")
        else:
            print("   Stay tuned for upcoming events!")
    else:
        print("   Stay tuned for upcoming events!")

    # Show user statistics
    print(f"\n👥 USER STATISTICS:")
    print(f"   Total Users            : {total_users}")
    for role, count in role_counts.items():
        percentage = (count / total_users * 100) if total_users > 0 else 0
        print(f"   - {role.title():<15}: {count:>3} ({percentage:>5.1f}%)")

    # Event status distribution
    if total_events > 0:
        print(f"\n📊 EVENT STATUS DISTRIBUTION:")
        approved_pct = (total_approved / total_events * 100)
        pending_pct = (total_pending / total_events * 100)
        rejected_pct = (total_rejected / total_events * 100)

        print(f"   ✅ Approved Events     : {approved_pct:>5.1f}%")
        print(f"   ⏳ Pending Events      : {pending_pct:>5.1f}%")
        print(f"   ❌ Rejected Events     : {rejected_pct:>5.1f}%")

    # Show events needing attention
    events_needing_review = []
    for event_id, details in event_details.items():
        if details['status'] in ['pending', 'admin_approved', 'venue_manager_approved', 'approved_by_venue_manager']:
            events_needing_review.append((event_id, details))

    if events_needing_review:
        print(f"\n⚠️  EVENTS NEEDING ATTENTION ({len(events_needing_review)}):")
        for event_id, details in events_needing_review[:5]:  # Show max 5
            status_emoji = {"pending": "⏳", "admin_approved": "👨‍💼", "venue_manager_approved": "🏢",
                            "approved_by_venue_manager": "🏢"}
            emoji = status_emoji.get(details['status'], "❓")
            print(
                f"   {emoji} {details['title'][:35]}{'...' if len(details['title']) > 35 else ''} - {details['status'].replace('_', ' ').title()}")

        if len(events_needing_review) > 5:
            print(f"   ... and {len(events_needing_review) - 5} more events")

    print("=" * 60)


def generate_report():
    events_file = "events.txt"
    registration_file = "registrations.txt"
    report_file = "report.txt"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_events = 0
    approved = 0
    pending = 0
    rejected = 0
    event_data = {}  # event_id: {'title': ..., 'status': ..., 'count': 0}

    # Load events
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 7:
                    title = parts[8].strip()
                    status = parts[4].strip().lower()
                    event_id = parts[7].strip()

                    event_data[event_id] = {
                        'title': title,
                        'status': status,
                        'count': 0
                    }

                    total_events += 1
                    if status == 'approved':
                        approved += 1
                    elif status == 'pending':
                        pending += 1
                    elif status == 'rejected':
                        rejected += 1
    except FileNotFoundError:
        print("❌ Error: events.txt not found.")
        return

    # Count registrations from registrations.txt
    try:
        with open(registration_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 1:
                    event_id = parts[1].strip()
                    if event_id in event_data:
                        event_data[event_id]['count'] += 1
    except FileNotFoundError:
        print("⚠️ Warning: registrations.txt not found, skipping registration count.")

    # Write report with UTF-8 encoding
    try:
        with open(report_file, 'w', encoding='utf-8') as report:
            report.write("📄 Event Report\n")
            report.write("=========================================\n")
            report.write(f"🕒 Generated on: {now}\n\n")
            report.write(f"{'Event ID':<10}{'Title':<50}{'Status':<32}{'Registrations'}\n")
            report.write("-" * 110 + "\n")

            for event_id, info in event_data.items():
                report.write(f"{event_id:<10}{info['title']:<50}{info['status']:<32}{info['count']}\n")

            report.write("\n📊 Summary:\n")
            report.write(f"Total Events   : {total_events}\n")
            report.write(f"Approved       : {approved}\n")
            report.write(f"Pending        : {pending}\n")
            report.write(f"Rejected       : {rejected}\n")

        print("✅ Report successfully generated as 'report.txt'.")
    except Exception as e:
        print("❌ Error writing to report.txt:", e)


def manage_roles():
    users_file = "users.txt"

    # Available roles that can be managed
    manageable_roles = ["Participant", "Event Organizer", "Venue Manager"]
    # Roles that can be changed (excludes Venue Manager and Administrator)
    changeable_roles = ["Participant", "Event Organizer"]

    try:
        with open(users_file, 'r') as f:
            user_lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ Error: 'users.txt' not found.")
        return

    while True:
        print("\n=== 🔧 Role Management ===")
        print("Available roles to manage:")
        print("1. Participants")
        print("2. Event Organizers")
        print("3. Venue Managers")
        print("4. View All Users (Read-only)")
        print("b. Back to Menu")

        choice = input("Select option (1-4, b): ").strip().lower()

        if choice == "b":
            break
        elif choice == "4":
            # View all users
            print("\n--- All Users ---")
            print(f"{'#':<3}{'Username':<20}{'Email':<25}{'Base Role':<12}{'System Role':<15}")
            print("-" * 75)
            for i, line in enumerate(user_lines):
                parts = line.split('|')
                if len(parts) >= 6:
                    username, email, _, base_role, system_role, _ = parts
                    # Truncate email if too long
                    display_email = email[:22] + "..." if len(email) > 25 else email
                    print(f"{i + 1:<3}{username:<20}{display_email:<25}{base_role:<12}{system_role:<15}")
            input("\nPress Enter to continue...")
            continue
        elif choice not in ["1", "2", "3"]:
            print("⚠️ Invalid selection.")
            continue

        # Map choice to role
        role_mapping = {
            "1": "Participant",
            "2": "Event Organizer",
            "3": "Venue Manager"
        }
        selected_role = role_mapping[choice]

        # Filter users by selected role
        filtered_users = []
        print(f"\n--- Users with Role: {selected_role} ---")
        print(f"{'#':<3}{'Username':<20}{'Email':<25}{'Base Role':<12}")
        print("-" * 60)

        for index, line in enumerate(user_lines):
            parts = line.split('|')
            if len(parts) >= 6:
                username, email, pwd_hash, base_role, system_role, created = parts
                if system_role.strip() == selected_role:
                    filtered_users.append((index, parts))
                    # Truncate email if too long
                    display_email = email[:22] + "..." if len(email) > 25 else email
                    print(f"{len(filtered_users):<3}{username:<20}{display_email:<25}{base_role:<12}")

        if not filtered_users:
            print("No users found with this role.")
            input("Press Enter to continue...")
            continue

        # User modification loop
        while True:
            print(f"\nModifying {selected_role} users:")

            # Check if this role can be modified
            if selected_role not in changeable_roles:
                print(f"⚠️ {selected_role} roles cannot be modified.")
                input("Press Enter to continue...")
                break

            user_choice = input("Enter user number to modify role (or 'b' to go back): ").strip().lower()

            if user_choice == "b":
                break

            if not user_choice.isdigit() or int(user_choice) < 1 or int(user_choice) > len(filtered_users):
                print("⚠️ Invalid selection.")
                continue

            selected_index = int(user_choice) - 1
            file_line_index, user_data = filtered_users[selected_index]

            username = user_data[0]
            current_role = user_data[4].strip()

            print(f"\nSelected User: {username}")
            print(f"Current Role: {current_role}")
            print("\nAvailable roles to change to:")

            # Get user's base role (Student/Lecturer)
            base_role = user_data[3].strip()

            # Determine available roles based on base role
            if base_role.lower() == "student":
                # Students can only be Participant or Event Organizer
                student_roles = ["Participant", "Event Organizer"]
                available_roles = [role for role in student_roles if role != current_role]
            else:
                # Lecturers can have any changeable role
                available_roles = [role for role in changeable_roles if role != current_role]
            # Show available roles
            if not available_roles:
                if base_role.lower() == "student" and current_role in ["Venue Manager", "Administrator"]:
                    print("⚠️ Students cannot be assigned higher-level roles.")
                else:
                    print("⚠️ No other roles available for this user.")
                input("Press Enter to continue...")
                continue

            for i, role in enumerate(available_roles, 1):
                print(f"{i}. {role}")

            print(f"\nNote: {base_role}s can only have certain roles.")

            role_choice = input(f"Select new role (1-{len(available_roles)}) or 'c' to cancel: ").strip().lower()

            if role_choice == "c":
                continue

            if not role_choice.isdigit() or int(role_choice) < 1 or int(role_choice) > len(available_roles):
                print("⚠️ Invalid selection.")
                continue

            new_role = available_roles[int(role_choice) - 1]

            # Confirm change
            confirm = input(f"Change {username}'s role from '{current_role}' to '{new_role}'? (y/n): ").strip().lower()
            if confirm != "y":
                print("❌ Cancelled.")
                continue

            # Update the role
            user_data[4] = new_role
            user_lines[file_line_index] = "|".join(user_data)

            # Save to file
            try:
                with open(users_file, 'w') as f:
                    for line in user_lines:
                        f.write(line + '\n')
                print(f"✅ Successfully changed {username}'s role to {new_role}.")

                # Update the filtered_users list to reflect the change
                # Remove from current list since role changed
                filtered_users.pop(selected_index)
                if not filtered_users:
                    print("No more users with this role.")
                    break

            except Exception as e:
                print(f"❌ Error writing to file: {e}")

            break


def logout():
    print("\nLogging out... Returning to main menu.\n")


if __name__ == "__main__":
    admin_menu()