"""
Password Management Utility for WelVision
Handles secure password hashing, verification, and user management
"""

import hashlib
import secrets
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class PasswordManager:
    def __init__(self):
        self.salt_length = 32  # 32 bytes = 256 bits salt
    
    def generate_salt(self):
        """Generate a random salt"""
        return secrets.token_hex(self.salt_length)
    
    def hash_password(self, password, salt=None):
        """Hash password with salt"""
        if salt is None:
            salt = self.generate_salt()
        
        # Combine password and salt
        password_salt = f"{password}{salt}"
        
        # Hash using SHA-256
        hashed = hashlib.sha256(password_salt.encode()).hexdigest()
        
        return hashed, salt
    
    def verify_password(self, password, stored_hash, stored_salt):
        """Verify password against stored hash and salt"""
        hashed, _ = self.hash_password(password, stored_salt)
        return hashed == stored_hash
    
    def connect_db(self):
        """Connect to MySQL database"""
        try:
            connection = mysql.connector.connect(
                host=DB_CONFIG['HOST'],
                port=DB_CONFIG['PORT'],
                database=DB_CONFIG['DATABASE'],
                user=DB_CONFIG['USER'],
                password=DB_CONFIG['PASSWORD']
            )
            return connection
        except Error as e:
            print(f"Database connection error: {e}")
            return None
    
    def get_super_admin_count(self):
        """Get the count of Super Admin users"""
        connection = self.connect_db()
        if not connection:
            return 0
        
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Super Admin' AND is_active = 1")
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            print(f"Error counting Super Admins: {e}")
            return 0
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_super_admin_info(self):
        """Get information about existing Super Admin"""
        connection = self.connect_db()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT employee_id, email, created_at 
                FROM users 
                WHERE role = 'Super Admin' AND is_active = 1
                LIMIT 1
            """)
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error getting Super Admin info: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def create_user(self, employee_id, email, password, role):
        """Create a new user with hashed password"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT employee_id FROM users WHERE employee_id = %s", (employee_id,))
            if cursor.fetchone():
                return False, f"Employee ID {employee_id} already exists"
            
            # Check Super Admin constraint
            if role == 'Super Admin':
                super_admin_count = self.get_super_admin_count()
                if super_admin_count > 0:
                    super_admin_info = self.get_super_admin_info()
                    if super_admin_info:
                        return False, f"Only one Super Admin is allowed. Current Super Admin: {super_admin_info[0]} ({super_admin_info[1]})"
                    else:
                        return False, "Only one Super Admin is allowed in the system"
            
            # Hash the password
            hashed_password, salt = self.hash_password(password)
            
            # Insert new user
            query = """
            INSERT INTO users (employee_id, email, password_hash, salt, role, created_at, is_active)
            VALUES (%s, %s, %s, %s, %s, NOW(), 1)
            """
            
            cursor.execute(query, (employee_id, email, hashed_password, salt, role))
            connection.commit()
            
            return True, f"User {employee_id} created successfully"
            
        except Error as e:
            return False, f"Error creating user: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def authenticate_user(self, employee_id, password, role):
        """Authenticate user with employee_id, password, and role"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Get user data including salt
            query = """
            SELECT employee_id, password_hash, salt, role, is_active 
            FROM users 
            WHERE employee_id = %s AND role = %s
            """
            
            cursor.execute(query, (employee_id, role))
            result = cursor.fetchone()
            
            if not result:
                return False, "Invalid employee ID or role"
            
            emp_id, stored_hash, stored_salt, user_role, is_active = result
            
            if not is_active:
                return False, "Account is deactivated"
            
            # Verify password
            if self.verify_password(password, stored_hash, stored_salt):
                # Update last login
                self.update_last_login(employee_id)
                return True, f"Welcome {emp_id}!"
            else:
                return False, "Invalid password"
                
        except Error as e:
            return False, f"Authentication error: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def update_last_login(self, employee_id):
        """Update last login timestamp"""
        connection = self.connect_db()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            query = "UPDATE users SET last_login = NOW() WHERE employee_id = %s"
            cursor.execute(query, (employee_id,))
            connection.commit()
        except Error as e:
            print(f"Error updating last login: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def change_password(self, employee_id, old_password, new_password):
        """Change user password"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Get current password and salt
            cursor.execute("SELECT password_hash, salt FROM users WHERE employee_id = %s", (employee_id,))
            result = cursor.fetchone()
            
            if not result:
                return False, "User not found"
            
            stored_hash, stored_salt = result
            
            # Verify old password
            if not self.verify_password(old_password, stored_hash, stored_salt):
                return False, "Current password is incorrect"
            
            # Hash new password
            new_hash, new_salt = self.hash_password(new_password)
            
            # Update password
            query = "UPDATE users SET password_hash = %s, salt = %s WHERE employee_id = %s"
            cursor.execute(query, (new_hash, new_salt, employee_id))
            connection.commit()
            
            return True, "Password changed successfully"
            
        except Error as e:
            return False, f"Error changing password: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def get_all_users(self):
        """Get all users for admin management"""
        connection = self.connect_db()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor()
            query = """
            SELECT employee_id, email, role, created_at, last_login, is_active 
            FROM users ORDER BY created_at DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching users: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def update_user(self, employee_id, email, role, is_active):
        """Update user information (admin function)"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Check if user exists and get current role
            cursor.execute("SELECT employee_id, role FROM users WHERE employee_id = %s", (employee_id,))
            user_result = cursor.fetchone()
            if not user_result:
                return False, f"User {employee_id} not found"
            
            current_role = user_result[1]
            
            # Check Super Admin constraint when changing TO Super Admin
            if role == 'Super Admin' and current_role != 'Super Admin':
                super_admin_count = self.get_super_admin_count()
                if super_admin_count > 0:
                    super_admin_info = self.get_super_admin_info()
                    if super_admin_info:
                        return False, f"Only one Super Admin is allowed. Current Super Admin: {super_admin_info[0]} ({super_admin_info[1]})"
                    else:
                        return False, "Only one Super Admin is allowed in the system"
            
            # Prevent deactivating the only Super Admin
            if current_role == 'Super Admin' and not is_active:
                return False, "Cannot deactivate the Super Admin account. System must have an active Super Admin."
            
            # Prevent changing Super Admin role to something else
            if current_role == 'Super Admin' and role != 'Super Admin':
                return False, "Cannot change Super Admin role. Super Admin role is permanent for system security."
            
            # Convert boolean to integer for database compatibility
            is_active_int = 1 if is_active else 0
            
            # Update user
            query = """
            UPDATE users 
            SET email = %s, role = %s, is_active = %s 
            WHERE employee_id = %s
            """
            
            cursor.execute(query, (email, role, is_active_int, employee_id))
            connection.commit()
            
            return True, f"User {employee_id} updated successfully"
            
        except Error as e:
            return False, f"Error updating user: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def delete_user(self, employee_id):
        """Delete user (admin function) with foreign key constraint handling"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Check if user exists and get role
            cursor.execute("SELECT employee_id, role FROM users WHERE employee_id = %s", (employee_id,))
            user_result = cursor.fetchone()
            if not user_result:
                return False, f"User {employee_id} not found"
            
            user_role = user_result[1]
            
            # Prevent deleting Super Admin
            if user_role == 'Super Admin':
                return False, "Cannot delete Super Admin account. Super Admin is required for system security."
            
            # Check for foreign key dependencies
            dependencies = []
            
            # Check inspection_sessions
            cursor.execute("SELECT COUNT(*) FROM inspection_sessions WHERE employee_id = %s", (employee_id,))
            inspection_count = cursor.fetchone()[0]
            if inspection_count > 0:
                dependencies.append(f"inspection_sessions ({inspection_count} records)")
            
            # Check manual_mode_sessions
            cursor.execute("SELECT COUNT(*) FROM manual_mode_sessions WHERE user_id = %s", (employee_id,))
            manual_count = cursor.fetchone()[0]
            if manual_count > 0:
                dependencies.append(f"manual_mode_sessions ({manual_count} records)")
            
            # Check settings_history
            cursor.execute("SELECT COUNT(*) FROM settings_history WHERE user_id = %s", (employee_id,))
            settings_count = cursor.fetchone()[0]
            if settings_count > 0:
                dependencies.append(f"settings_history ({settings_count} records)")
            
            # If there are dependencies, offer options
            if dependencies:
                dependency_list = ", ".join(dependencies)
                return False, f"Cannot delete user {employee_id}. User has dependent records in: {dependency_list}. Please clean up these records first or deactivate the user instead."
            
            # If no dependencies, proceed with deletion
            query = "DELETE FROM users WHERE employee_id = %s"
            cursor.execute(query, (employee_id,))
            connection.commit()
            
            return True, f"User {employee_id} deleted successfully"
            
        except Error as e:
            return False, f"Error deleting user: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def deactivate_user(self, employee_id):
        """Deactivate user instead of deleting (safer option)"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Check if user exists and get role
            cursor.execute("SELECT employee_id, role FROM users WHERE employee_id = %s", (employee_id,))
            user_result = cursor.fetchone()
            if not user_result:
                return False, f"User {employee_id} not found"
            
            user_role = user_result[1]
            
            # Prevent deactivating Super Admin
            if user_role == 'Super Admin':
                return False, "Cannot deactivate Super Admin account. Super Admin is required for system security."
            
            # Deactivate user
            query = "UPDATE users SET is_active = 0 WHERE employee_id = %s"
            cursor.execute(query, (employee_id,))
            connection.commit()
            
            return True, f"User {employee_id} deactivated successfully"
            
        except Error as e:
            return False, f"Error deactivating user: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def admin_change_password(self, admin_id, target_employee_id, new_password):
        """Admin function to change another user's password with role hierarchy"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Get admin role and verify permissions
            cursor.execute("SELECT role FROM users WHERE employee_id = %s", (admin_id,))
            admin_result = cursor.fetchone()
            
            if not admin_result or admin_result[0] not in ['Admin', 'Super Admin']:
                return False, "Access denied: Admin privileges required"
            
            admin_role = admin_result[0]
            
            # Get target user role
            cursor.execute("SELECT employee_id, role FROM users WHERE employee_id = %s", (target_employee_id,))
            target_result = cursor.fetchone()
            
            if not target_result:
                return False, f"User {target_employee_id} not found"
            
            target_role = target_result[1]
            
            # Enforce role hierarchy permissions
            if admin_role == 'Admin':
                # Admin can only change User passwords
                if target_role != 'User':
                    return False, f"Access denied: Admin can only change User passwords, not {target_role} passwords"
            elif admin_role == 'Super Admin':
                # Super Admin can change Admin and User passwords, but not other Super Admin
                if target_role == 'Super Admin' and target_employee_id != admin_id:
                    return False, "Access denied: Cannot change another Super Admin's password"
            
            # Prevent changing own password through admin function
            if admin_id == target_employee_id:
                return False, "Use the regular change password function to change your own password"
            
            # Hash new password
            new_hash, new_salt = self.hash_password(new_password)
            
            # Update password
            query = "UPDATE users SET password_hash = %s, salt = %s WHERE employee_id = %s"
            cursor.execute(query, (new_hash, new_salt, target_employee_id))
            connection.commit()
            
            return True, f"Password changed successfully for {target_employee_id} ({target_role})"
            
        except Error as e:
            return False, f"Error changing password: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

# Global password manager instance
password_manager = PasswordManager()

# Command line utilities
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Password Manager Utilities:")
        print("python password_manager.py create <emp_id> <email> <password> <role>")
        print("python password_manager.py hash <password>")
        print("python password_manager.py test <emp_id> <password> <role>")
        print("python password_manager.py list")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create" and len(sys.argv) == 6:
        emp_id, email, password, role = sys.argv[2:6]
        success, message = password_manager.create_user(emp_id, email, password, role)
        print("✅" if success else "❌", message)
    
    elif command == "hash" and len(sys.argv) == 3:
        password = sys.argv[2]
        hashed, salt = password_manager.hash_password(password)
        print(f"Password: {password}")
        print(f"Hash: {hashed}")
        print(f"Salt: {salt}")
    
    elif command == "test" and len(sys.argv) == 5:
        emp_id, password, role = sys.argv[2:5]
        success, message = password_manager.authenticate_user(emp_id, password, role)
        print("✅" if success else "❌", message)
    
    elif command == "list":
        users = password_manager.get_all_users()
        print(f"Total Users: {len(users)}")
        for user in users:
            print(f"• {user[0]} ({user[2]}) - {user[1]} - Active: {bool(user[5])}")
    
    else:
        print("Invalid command or arguments") 