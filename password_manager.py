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
            
            # Check if user exists
            cursor.execute("SELECT employee_id FROM users WHERE employee_id = %s", (employee_id,))
            if not cursor.fetchone():
                return False, f"User {employee_id} not found"
            
            # Update user
            query = """
            UPDATE users 
            SET email = %s, role = %s, is_active = %s 
            WHERE employee_id = %s
            """
            
            cursor.execute(query, (email, role, is_active, employee_id))
            connection.commit()
            
            return True, f"User {employee_id} updated successfully"
            
        except Error as e:
            return False, f"Error updating user: {e}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    def delete_user(self, employee_id):
        """Delete user (admin function)"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Check if user exists
            cursor.execute("SELECT employee_id FROM users WHERE employee_id = %s", (employee_id,))
            if not cursor.fetchone():
                return False, f"User {employee_id} not found"
            
            # Delete user
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
    
    def admin_change_password(self, admin_id, target_employee_id, new_password):
        """Admin function to change another user's password"""
        connection = self.connect_db()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Verify admin has permission (Admin or Super Admin)
            cursor.execute("SELECT role FROM users WHERE employee_id = %s", (admin_id,))
            admin_result = cursor.fetchone()
            
            if not admin_result or admin_result[0] not in ['Admin', 'Super Admin']:
                return False, "Access denied: Admin privileges required"
            
            # Check if target user exists
            cursor.execute("SELECT employee_id FROM users WHERE employee_id = %s", (target_employee_id,))
            if not cursor.fetchone():
                return False, f"User {target_employee_id} not found"
            
            # Hash new password
            new_hash, new_salt = self.hash_password(new_password)
            
            # Update password
            query = "UPDATE users SET password_hash = %s, salt = %s WHERE employee_id = %s"
            cursor.execute(query, (new_hash, new_salt, target_employee_id))
            connection.commit()
            
            return True, f"Password changed successfully for {target_employee_id}"
            
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