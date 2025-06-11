"""
Command Line Password Management Utility
Provides CLI tools for password operations in WelVision
"""

import sys
import getpass
from password_manager import password_manager

def show_help():
    """Show help information"""
    print("🔐 WelVision Password Management CLI")
    print("=" * 40)
    print("Commands:")
    print("  create   - Create a new user")
    print("  auth     - Test authentication")
    print("  change   - Change password")
    print("  list     - List all users")
    print("  hash     - Hash a password")
    print("  help     - Show this help")
    print("\nExamples:")
    print("  python password_cli.py create")
    print("  python password_cli.py auth EMP001 User")
    print("  python password_cli.py change EMP001")
    print("  python password_cli.py list")
    print("  python password_cli.py hash mypassword")

def create_user():
    """Interactive user creation"""
    print("🆕 Create New User")
    print("-" * 20)
    
    employee_id = input("Employee ID: ").strip()
    if not employee_id:
        print("❌ Employee ID is required")
        return
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email is required")
        return
    
    print("Available roles: User, Admin, Super Admin")
    role = input("Role: ").strip()
    if role not in ['User', 'Admin', 'Super Admin']:
        print("❌ Invalid role. Must be: User, Admin, or Super Admin")
        return
    
    password = getpass.getpass("Password: ")
    if not password:
        print("❌ Password is required")
        return
    
    confirm_password = getpass.getpass("Confirm Password: ")
    if password != confirm_password:
        print("❌ Passwords don't match")
        return
    
    success, message = password_manager.create_user(employee_id, email, password, role)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def test_auth(employee_id=None, role=None):
    """Test authentication"""
    if not employee_id:
        employee_id = input("Employee ID: ").strip()
    if not role:
        role = input("Role: ").strip()
    
    password = getpass.getpass("Password: ")
    
    success, message = password_manager.authenticate_user(employee_id, password, role)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def change_password(employee_id=None):
    """Change user password"""
    if not employee_id:
        employee_id = input("Employee ID: ").strip()
    
    old_password = getpass.getpass("Current Password: ")
    new_password = getpass.getpass("New Password: ")
    confirm_password = getpass.getpass("Confirm New Password: ")
    
    if new_password != confirm_password:
        print("❌ New passwords don't match")
        return
    
    success, message = password_manager.change_password(employee_id, old_password, new_password)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def list_users():
    """List all users"""
    users = password_manager.get_all_users()
    
    print("👥 All Users")
    print("=" * 60)
    
    if not users:
        print("❌ No users found")
        return
    
    for user in users:
        emp_id, email, role, created_at, last_login, is_active = user
        
        status = "🟢 Active" if is_active else "🔴 Inactive"
        last_login_str = str(last_login) if last_login else "Never"
        
        print(f"👤 {emp_id} ({role}) - {status}")
        print(f"   📧 {email}")
        print(f"   📅 Created: {created_at}")
        print(f"   🕐 Last Login: {last_login_str}")
        print("-" * 40)

def hash_password(password=None):
    """Hash a password"""
    if not password:
        password = getpass.getpass("Password to hash: ")
    
    hashed, salt = password_manager.hash_password(password)
    
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    print(f"Salt: {salt}")

def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "create":
        create_user()
    elif command == "auth":
        if len(sys.argv) >= 4:
            test_auth(sys.argv[2], sys.argv[3])
        else:
            test_auth()
    elif command == "change":
        if len(sys.argv) >= 3:
            change_password(sys.argv[2])
        else:
            change_password()
    elif command == "list":
        list_users()
    elif command == "hash":
        if len(sys.argv) >= 3:
            hash_password(sys.argv[2])
        else:
            hash_password()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main() 