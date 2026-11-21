import re
import hashlib
import os
from datetime import datetime
import event_organizer
import venue_manager
import participant
import admin

# 🗂️ File paths for storing data
USERS_FILE = "users.txt"
VENUES_FILE = "venues.txt"
EVENTS_FILE = "events.txt"
BLOCKED_DATES_FILE = "blocked_dates.txt"

# 🎭 Role definitions
BASE_ROLES = ["Student", "Lecturer"]
FUNCTIONAL_ROLES = {
    "Student": ["Participant", "Event Organizer"],
    "Lecturer": ["Venue Manager", "Administrator"]
}

def hash_password(password):
    """🔐 Securely hash the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    """✅ Check if email looks valid (e.g., user@example.com)"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """🛡️ Check password strength: at least 8 chars, letter, and number"""
    if len(password) < 8:
        return False, "⚠️ Your password needs to be at least 8 characters long for security"
    if not re.search(r'[A-Za-z]', password):
        return False, "⚠️ Please include at least one letter in your password"
    if not re.search(r'[0-9]', password):
        return False, "⚠️ Please include at least one number in your password"
    return True, "✅ Perfect! Your password meets all requirements"

def read_users():
    """📂 Read user details from file and return them as a list"""
    users = []
    try:
        with open(USERS_FILE, 'r') as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) == 6:
                        users.append({
                            'username': parts[0],
                            'email': parts[1],
                            'password': parts[2],
                            'base_role': parts[3],
                            'functional_role': parts[4],
                            'created_date': parts[5]
                        })
    except FileNotFoundError:
        pass  # No users yet!
    return users

def write_user(username, email, password_hash, base_role, functional_role):
    """📝 Save a new user to file"""
    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_data = f"{username}|{email}|{password_hash}|{base_role}|{functional_role}|{created_date}\n"
    with open(USERS_FILE, 'a') as file:
        file.write(user_data)

def check_username_exists(username):
    """🔎 Check if username is already taken (case-insensitive)"""
    users = read_users()
    return any(user['username'].lower() == username.lower() for user in users)

def check_email_exists(email):
    """🔎 Check if email is already registered (case-insensitive)"""
    users = read_users()
    return any(user['email'].lower() == email.lower() for user in users)

def signup():
    """🎉 Handle user sign-up process with friendly prompts"""
    print("\n=== 📝 SIGN UP FOR SMART CAMPUS EVENT SYSTEM ===")
    print("👉 Let's get you started with an account!")

    # 💡 Get username
    while True:
        username = input("👤 Username: ").strip()
        if not username:
            print("⚠️ Username cannot be empty.")
            continue
        if len(username) < 3:
            print("⚠️ Username must be at least 3 characters long.")
            continue
        if check_username_exists(username):
            print("⚠️ Username already exists. Please choose another one.")
            continue
        break

    # 💡 Get email
    while True:
        email = input("📧 Email: ").strip()
        if not email:
            print("⚠️ Email cannot be empty.")
            continue
        if not validate_email(email):
            print("⚠️ Please enter a valid email address (e.g., user@example.com).")
            continue
        if check_email_exists(email):
            print("⚠️ Email already registered. Please use another email.")
            continue
        break

    # 💡 Get password
    while True:
        password = input("🔑 Password: ").strip()
        if not password:
            print("⚠️ Password cannot be empty.")
            continue
        is_valid, message = validate_password(password)
        if not is_valid:
            print(message)
            continue

        confirm_password = input("🔑 Confirm Password: ").strip()
        if password != confirm_password:
            print("⚠️ Passwords do not match.")
            continue
        break

    # 💡 Default all new users to Student/Participant
    base_role = "Student"
    functional_role = "Participant"

    # 💡 Save user data
    password_hash = hash_password(password)
    write_user(username, email, password_hash, base_role, functional_role)

    print("\n🎉 Your account has been created successfully!")
    print(f"👤 Username: {username}")
    print(f"📧 Email: {email}")
    print(f"🎭 Base Role: {base_role}")
    print(f"🛠️ Functional Role: {functional_role}")
    print("🎫 You're all set as a Participant! Start exploring events!")
    print("✨ Welcome to Smart Campus! Let the adventures begin!")

def login():
    """🔑 Handle user login process"""
    print("\n=== 🔑 LOGIN TO SMART CAMPUS ===")
    username = input("👤 Username: ").strip()
    password = input("🔑 Password: ").strip()

    if not username or not password:
        print("⚠️ Username and password cannot be empty.")
        return None

    users = read_users()
    password_hash = hash_password(password)

    for user in users:
        if user['username'].lower() == username.lower() and user['password'] == password_hash:
            print(f"\n✅ Login successful! Welcome back, {user['username']}! 🎉")
            # 🎉 Personalized message
            role = user['functional_role']
            if role == "Event Organizer":
                print("🎪 Ready to create some amazing events?")
            elif role == "Participant":
                print("🎫 Let’s find you some exciting events to join!")
            elif role == "Venue Manager":
                print("🏢 Time to manage those campus spaces!")
            elif role == "Administrator":
                print("⚙️ Ready to oversee the campus event ecosystem?")
            return user

    print("❌ Invalid username or password.")
    return None


def main_menu(user_data):
    """📜 Show main menu based on the user's functional role"""
    while True:
        role = user_data['functional_role']
        print(f"\n=== 🏠 MAIN MENU - {role.upper()} ===")
        print("1️⃣ 👤 View Profile")
        print("2️⃣ ⚙️ Access Role Features")
        print("3️⃣ 🚪 Logout")

        choice = input("\n🔢 Select an option (1-3): ").strip()

        if choice == "1":
            print("\n=== 👤 USER PROFILE ===")
            print(f"👤 Username: {user_data['username']}")
            print(f"📧 Email: {user_data['email']}")
            print(f"🎭 Base Role: {user_data['base_role']}")
            print(f"🛠️ Functional Role: {user_data['functional_role']}")

        elif choice == "2":
            # 🏢 Access features based on functional role
            if role == "Venue Manager":
                print("🏢 Loading your venue tools and booking system... ✨")
                venue_manager.main_menu()
            elif role == "Participant":
                print("🎫 Opening event discovery portal... 🔍")
                participant.main_menu(user_data)
                
            elif role == "Event Organizer":
                # Role selection for Event Organizer
                while True:
                    print("\n🎭 As an Event Organizer, you have access to multiple roles:")
                    print("1️⃣ 🎫 Participant - Browse and join events")
                    print("2️⃣ 🎪 Event Organizer - Create and manage events")

                    choice2 = input(
                        "\n🔢 Please select your role to continue: Participant or Event Organizer (1-2): ").strip()

                    if choice2 == "1":
                        print("🎫 Opening event discovery portal... 🔍")
                        participant.main_menu(user_data)
                        break
                    elif choice2 == "2":
                        print("🎪 Loading event creation and management tools... ✨")
                        event_organizer.main_menu(user_data)
                        break
                    else:
                        print("⚠️ Invalid option. Please select 1 or 2.")

            elif role == "Administrator":
                print("⚙️ Accessing administrative control panel... 🛡️")
                admin.admin_menu()
            else:
                print(f"🛠️ Features for {role} are coming soon! Stay tuned!")

        elif choice == "3":
            print("👋 Logging out... Thanks for using Smart Campus! 🌟")
            break

        else:
            print("⚠️ Invalid option. Please select 1-3.")

def main():
    """🚀 Main entry point of the application"""
    system_pic = r"""
 __      __       .__                                  __             _________                      __    _________                                      ___________                    __       _____                                                             __      _________               __                  
/  \    /  \ ____ |  |   ____  ____   _____   ____   _/  |_  ____    /   _____/ _____ _____ ________/  |_  \_   ___ \_____    _____ ______  __ __  ______ \_   _____/__  __ ____   _____/  |_    /     \ _____    ____ _____     ____   ____   _____   ____   _____/  |_   /   _____/__.__. _______/  |_  ____   _____  
\   \/\/   // __ \|  | _/ ___\/  _ \ /     \_/ __ \  \   __\/  _ \   \_____  \ /     \\__  \\_  __ \   __\ /    \  \/\__  \  /     \\____ \|  |  \/  ___/  |    __)_\  \/ // __ \ /    \   __\  /  \ /  \\__  \  /    \\__  \   / ___\_/ __ \ /     \_/ __ \ /    \   __\  \_____  <   |  |/  ___/\   __\/ __ \ /     \ 
 \        /\  ___/|  |_\  \__(  <_> )  Y Y  \  ___/   |  | (  <_> )  /        \  Y Y  \/ __ \|  | \/|  |   \     \____/ __ \|  Y Y  \  |_> >  |  /\___ \   |        \\   /\  ___/|   |  \  |   /    Y    \/ __ \|   |  \/ __ \_/ /_/  >  ___/|  Y Y  \  ___/|   |  \  |    /        \___  |\___ \  |  | \  ___/|  Y Y  \
  \__/\  /  \___  >____/\___  >____/|__|_|  /\___  >  |__|  \____/  /_______  /__|_|  (____  /__|   |__|    \______  (____  /__|_|  /   __/|____//____  > /_______  / \_/  \___  >___|  /__|   \____|__  (____  /___|  (____  /\___  / \___  >__|_|  /\___  >___|  /__|   /_______  / ____/____  > |__|  \___  >__|_|  /
       \/       \/          \/            \/     \/                         \/      \/     \/                      \/     \/      \/|__|              \/          \/           \/     \/               \/     \/     \/     \//_____/      \/      \/     \/     \/               \/\/         \/            \/      \/     
"""
    print(system_pic)
    print("🌟 Welcome to your Smart Campus Event Hub! 🌟")

    while True:
        print("\n🌟 What would you like to do today?")
        print("1️⃣ 📝 Create a new account")
        print("2️⃣ 🔑 Sign into existing account")
        print("3️⃣ 🚪 Exit")

        choice = input("\n🔢 Select an option (1-3): ").strip()

        if choice == "1":
            signup()
        elif choice == "2":
            user_data = login()
            if user_data:
                main_menu(user_data)
        elif choice == "3":
            print("\n🌟 Thank you for using Smart Campus! See you again soon! 👋")
            break
        else:
            print("⚠️ Invalid option. Please select 1-3.")

if __name__ == "__main__":
    main()