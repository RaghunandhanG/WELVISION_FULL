"""
Database Manager for WelVision System
Handles MySQL database operations with secure authentication using salted password hashing
"""

import mysql.connector
from mysql.connector import Error
import hashlib
import secrets
from datetime import datetime
from config import DB_CONFIG, DEFAULT_OD_DEFECT_THRESHOLDS, DEFAULT_BF_DEFECT_THRESHOLDS, DEFAULT_OD_DEFECT_THRESHOLDS, DEFAULT_BF_DEFECT_THRESHOLDS

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.salt_length = 32  # 32 bytes = 256 bits salt
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_CONFIG['HOST'],
                port=DB_CONFIG['PORT'],
                database=DB_CONFIG['DATABASE'],
                user=DB_CONFIG['USER'],
                password=DB_CONFIG['PASSWORD'],
                autocommit=True
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    def generate_salt(self):
        """Generate a random salt"""
        return secrets.token_hex(self.salt_length)
    
    def hash_password(self, password, salt=None):
        """Hash password with salt using SHA-256"""
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
    
    def authenticate_user(self, employee_id, password, role):
        """
        Authenticate user with employee_id, password, and role
        Returns (success, message, user_data)
        """
        if not self.connection:
            if not self.connect():
                return False, "Database connection failed", None
        
        try:
            cursor = self.connection.cursor()
            
            # Get user data including salt
            query = """
            SELECT employee_id, password_hash, salt, role, is_active, failed_attempts, locked_until
            FROM users 
            WHERE employee_id = %s AND role = %s
            """
            
            cursor.execute(query, (employee_id, role))
            result = cursor.fetchone()
            
            if not result:
                return False, "Invalid employee ID or role", None
            
            emp_id, stored_hash, stored_salt, user_role, is_active, failed_attempts, locked_until = result
            
            # Check if account is locked
            if locked_until and locked_until > datetime.now():
                return False, f"Account locked until {locked_until}", None
            
            if not is_active:
                return False, "Account is deactivated", None
            
            # Verify password
            if self.verify_password(password, stored_hash, stored_salt):
                # Reset failed attempts and update last login
                self.reset_failed_attempts(employee_id)
                self.update_last_login(employee_id)
                
                user_data = {
                    'employee_id': emp_id,
                    'role': user_role
                }
                
                return True, f"Welcome {emp_id}!", user_data
            else:
                # Increment failed attempts
                self.increment_failed_attempts(employee_id)
                return False, "Invalid password", None
                
        except Error as e:
            print(f"Authentication error: {e}")
            return False, f"Authentication error: {e}", None
        finally:
            if cursor:
                cursor.close()
    
    def increment_failed_attempts(self, employee_id):
        """Increment failed login attempts and lock account if necessary"""
        try:
            cursor = self.connection.cursor()
            
            # Get current failed attempts
            cursor.execute("SELECT failed_attempts FROM users WHERE employee_id = %s", (employee_id,))
            result = cursor.fetchone()
            
            if result:
                failed_attempts = result[0] + 1
                
                # Lock account after 5 failed attempts for 30 minutes
                if failed_attempts >= 5:
                    query = """
                    UPDATE users SET 
                        failed_attempts = %s, 
                        locked_until = DATE_ADD(NOW(), INTERVAL 30 MINUTE)
                    WHERE employee_id = %s
                    """
                    cursor.execute(query, (failed_attempts, employee_id))
                else:
                    cursor.execute("UPDATE users SET failed_attempts = %s WHERE employee_id = %s", 
                                 (failed_attempts, employee_id))
                
                self.connection.commit()
                
        except Error as e:
            print(f"Error updating failed attempts: {e}")
    
    def reset_failed_attempts(self, employee_id):
        """Reset failed login attempts after successful login"""
        try:
            cursor = self.connection.cursor()
            query = """
            UPDATE users SET 
                failed_attempts = 0, 
                locked_until = NULL 
            WHERE employee_id = %s
            """
            cursor.execute(query, (employee_id,))
            self.connection.commit()
        except Error as e:
            print(f"Error resetting failed attempts: {e}")
    
    def update_last_login(self, employee_id):
        """Update last login timestamp"""
        try:
            cursor = self.connection.cursor()
            query = "UPDATE users SET last_login = NOW() WHERE employee_id = %s"
            cursor.execute(query, (employee_id,))
            self.connection.commit()
        except Error as e:
            print(f"Error updating last login: {e}")
    
    def create_user(self, employee_id, email, password, role):
        """Create a new user with hashed password"""
        if not self.connection:
            if not self.connect():
                return False, "Database connection failed"
        
        try:
            cursor = self.connection.cursor()
            
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
            self.connection.commit()
            
            return True, f"User {employee_id} created successfully"
            
        except Error as e:
            return False, f"Error creating user: {e}"
        finally:
            if cursor:
                cursor.close()
    
    def log_system_event(self, user_id, action, details=None, level='INFO'):
        """Log system events for audit trail"""
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO system_logs (user_id, action, details, level, timestamp)
            VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (user_id, action, details, level))
            self.connection.commit()
        except Error as e:
            print(f"Error logging system event: {e}")
        finally:
            if cursor:
                cursor.close()
    
    def create_roller_table(self):
        """Create roller_informations table if it doesn't exist"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS roller_informations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                roller_type VARCHAR(50) NOT NULL,
                diameter DECIMAL(10,3) NOT NULL,
                thickness DECIMAL(10,3) NOT NULL,
                length DECIMAL(10,3) NOT NULL,
                status ENUM('Active', 'Inactive', 'Maintenance') DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_by VARCHAR(20),
                INDEX idx_type (roller_type),
                INDEX idx_status (status)
            )
            """
            cursor.execute(create_table_query)
            self.connection.commit()
            cursor.close()
            print("✅ Roller informations table created/verified")
            return True
        except Error as e:
            print(f"❌ Error creating roller table: {e}")
            return False
    
    def create_roller(self, roller_type, diameter, thickness, length, created_by=None):
        """Create a new roller record"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Insert new roller
            insert_query = """
            INSERT INTO roller_informations (roller_type, diameter, thickness, length, created_by)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (roller_type, diameter, thickness, length, created_by))
            self.connection.commit()
            
            roller_id = cursor.lastrowid
            cursor.close()
            
            # Log the creation
            self.log_system_event(created_by or "SYSTEM", "ROLLER_CREATED", f"Roller ID: {roller_id}, Type: {roller_type}")
            
            return True, f"Roller created successfully (ID: {roller_id})"
            
        except Error as e:
            print(f"❌ Error creating roller: {e}")
            return False, f"Database error: {e}"
    
    def get_all_rollers(self):
        """Retrieve all roller records"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT id, roller_type, diameter, thickness, length, 
                   status, created_at, updated_at, created_by
            FROM roller_informations
            ORDER BY id DESC
            """
            cursor.execute(query)
            rollers = cursor.fetchall()
            cursor.close()
            
            return rollers
            
        except Error as e:
            print(f"❌ Error retrieving rollers: {e}")
            return []
    
    def get_roller_by_id(self, roller_id):
        """Retrieve a specific roller by ID"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            query = """
            SELECT id, roller_type, diameter, thickness, length, 
                   status, created_at, updated_at, created_by
            FROM roller_informations WHERE id = %s
            """
            cursor.execute(query, (roller_id,))
            roller = cursor.fetchone()
            cursor.close()
            
            return roller
            
        except Error as e:
            print(f"❌ Error retrieving roller: {e}")
            return None
    
    def update_roller(self, roller_id, roller_type, diameter, thickness, length, updated_by=None):
        """Update an existing roller record"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Check if roller exists
            check_query = "SELECT id FROM roller_informations WHERE id = %s"
            cursor.execute(check_query, (roller_id,))
            result = cursor.fetchone()
            if not result:
                cursor.close()
                return False, f"Roller with ID {roller_id} not found"
            
            # Update the roller
            update_query = """
            UPDATE roller_informations 
            SET roller_type = %s, diameter = %s, thickness = %s, length = %s, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """
            cursor.execute(update_query, (roller_type, diameter, thickness, length, roller_id))
            self.connection.commit()
            
            rows_affected = cursor.rowcount
            cursor.close()
            
            if rows_affected > 0:
                # Log the update
                self.log_system_event(updated_by or "SYSTEM", "ROLLER_UPDATED", f"Roller ID: {roller_id}, Type: {roller_type}")
                return True, f"Roller updated successfully (ID: {roller_id})"
            else:
                return False, "No changes made to roller"
                
        except Error as e:
            print(f"❌ Error updating roller: {e}")
            return False, f"Database error: {e}"
    
    def delete_roller(self, roller_id, deleted_by=None):
        """Delete a roller record"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Get roller info before deletion for logging
            check_query = "SELECT roller_type FROM roller_informations WHERE id = %s"
            cursor.execute(check_query, (roller_id,))
            result = cursor.fetchone()
            if not result:
                cursor.close()
                return False, f"Roller with ID {roller_id} not found"
            
            roller_type = result[0] or "Unknown"
            
            # Delete the roller
            delete_query = "DELETE FROM roller_informations WHERE id = %s"
            cursor.execute(delete_query, (roller_id,))
            self.connection.commit()
            
            rows_affected = cursor.rowcount
            cursor.close()
            
            if rows_affected > 0:
                # Log the deletion
                self.log_system_event(deleted_by or "SYSTEM", "ROLLER_DELETED", f"Roller ID: {roller_id}, Type: {roller_type}")
                return True, f"Roller deleted successfully (ID: {roller_id})"
            else:
                return False, "Roller not found or already deleted"
                
        except Error as e:
            print(f"❌ Error deleting roller: {e}")
            return False, f"Database error: {e}"
    
    def get_roller_types(self):
        """Get unique roller types for dropdown"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            
            cursor = self.connection.cursor()
            query = """
            SELECT DISTINCT roller_type 
            FROM roller_informations 
            WHERE roller_type IS NOT NULL AND roller_type != ''
            ORDER BY roller_type
            """
            cursor.execute(query)
            types = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            return types
            
        except Error as e:
            print(f"❌ Error retrieving roller types: {e}")
            return []
    
    def create_threshold_tables(self):
        """Create threshold tracking tables for OD and BigFace models"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            
            # Create OD Model Threshold Tracking Table
            od_table_query = """
            CREATE TABLE IF NOT EXISTS od_threshold_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(20) NOT NULL,
                rust_threshold INT DEFAULT 50,
                dent_threshold INT DEFAULT 50,
                spherical_mark_threshold INT DEFAULT 50,
                damage_threshold INT DEFAULT 50,
                flat_line_threshold INT DEFAULT 50,
                damage_on_end_threshold INT DEFAULT 50,
                roller_threshold INT DEFAULT 50,
                model_confidence_threshold DECIMAL(5,3) DEFAULT 0.25,
                change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id VARCHAR(100),
                INDEX idx_employee (employee_id),
                INDEX idx_timestamp (change_timestamp)
            )
            """
            cursor.execute(od_table_query)
            
            # Create BigFace Model Threshold Tracking Table
            bf_table_query = """
            CREATE TABLE IF NOT EXISTS bigface_threshold_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                employee_id VARCHAR(20) NOT NULL,
                rust_threshold INT DEFAULT 50,
                dent_threshold INT DEFAULT 50,
                damage_threshold INT DEFAULT 50,
                roller_threshold INT DEFAULT 50,
                model_confidence_threshold DECIMAL(5,3) DEFAULT 0.25,
                change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id VARCHAR(100),
                INDEX idx_employee (employee_id),
                INDEX idx_timestamp (change_timestamp)
            )
            """
            cursor.execute(bf_table_query)
            
            # Create Current Threshold Settings Table (stores latest values)
            current_thresholds_query = """
            CREATE TABLE IF NOT EXISTS current_thresholds (
                id INT AUTO_INCREMENT PRIMARY KEY,
                model_type ENUM('OD', 'BIGFACE') NOT NULL,
                threshold_data JSON NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                updated_by VARCHAR(20),
                UNIQUE KEY unique_model (model_type)
            )
            """
            cursor.execute(current_thresholds_query)
            
            self.connection.commit()
            cursor.close()
            
            # Initialize default threshold values if tables are empty
            self._initialize_default_thresholds()
            
            print("✅ Threshold tracking tables created/verified successfully")
            return True
            
        except Error as e:
            print(f"❌ Error creating threshold tables: {e}")
            return False
    
    def _initialize_default_thresholds(self):
        """Initialize default threshold values in current_thresholds table"""
        try:
            cursor = self.connection.cursor()
            
            # Check if default values exist
            cursor.execute("SELECT COUNT(*) FROM current_thresholds")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert default OD thresholds
                od_data = {
                    'rust': DEFAULT_OD_DEFECT_THRESHOLDS['Rust'],
                    'dent': DEFAULT_OD_DEFECT_THRESHOLDS['Dent'],
                    'spherical_mark': DEFAULT_OD_DEFECT_THRESHOLDS['Spherical Mark'],
                    'damage': DEFAULT_OD_DEFECT_THRESHOLDS['Damage'],
                    'flat_line': DEFAULT_OD_DEFECT_THRESHOLDS['Flat Line'],
                    'damage_on_end': DEFAULT_OD_DEFECT_THRESHOLDS['Damage on End'],
                    'roller': DEFAULT_OD_DEFECT_THRESHOLDS['Roller'],
                    'model_confidence': 0.25
                }
                
                # Insert default BigFace thresholds
                bf_data = {
                    'rust': DEFAULT_BF_DEFECT_THRESHOLDS['Rust'],
                    'dent': DEFAULT_BF_DEFECT_THRESHOLDS['Dent'],
                    'damage': DEFAULT_BF_DEFECT_THRESHOLDS['Damage'],
                    'roller': DEFAULT_BF_DEFECT_THRESHOLDS['Roller'],
                    'model_confidence': 0.25
                }
                
                import json
                
                # Insert OD defaults
                cursor.execute("""
                    INSERT INTO current_thresholds (model_type, threshold_data, updated_by)
                    VALUES (%s, %s, %s)
                """, ('OD', json.dumps(od_data), 'SYSTEM'))
                
                # Insert BigFace defaults
                cursor.execute("""
                    INSERT INTO current_thresholds (model_type, threshold_data, updated_by)
                    VALUES (%s, %s, %s)
                """, ('BIGFACE', json.dumps(bf_data), 'SYSTEM'))
                
                self.connection.commit()
                print("✅ Default threshold values initialized")
            
            cursor.close()
            
        except Error as e:
            print(f"❌ Error initializing default thresholds: {e}")
    
    def save_od_thresholds(self, employee_id, thresholds, session_id=None):
        """Save OD model threshold changes to history and update current values"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Insert into history table
            history_query = """
            INSERT INTO od_threshold_history 
            (employee_id, rust_threshold, dent_threshold, spherical_mark_threshold, 
             damage_threshold, flat_line_threshold, damage_on_end_threshold, 
             roller_threshold, model_confidence_threshold, session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(history_query, (
                employee_id,
                thresholds.get('rust', 50),
                thresholds.get('dent', 50),
                thresholds.get('spherical_mark', 50),
                thresholds.get('damage', 50),
                thresholds.get('flat_line', 50),
                thresholds.get('damage_on_end', 50),
                thresholds.get('roller', 50),
                thresholds.get('model_confidence', 0.25),
                session_id
            ))
            
            # Update current thresholds
            import json
            threshold_data = {
                'rust': thresholds.get('rust', 50),
                'dent': thresholds.get('dent', 50),
                'spherical_mark': thresholds.get('spherical_mark', 50),
                'damage': thresholds.get('damage', 50),
                'flat_line': thresholds.get('flat_line', 50),
                'damage_on_end': thresholds.get('damage_on_end', 50),
                'roller': thresholds.get('roller', 50),
                'model_confidence': thresholds.get('model_confidence', 0.25)
            }
            
            cursor.execute("""
                INSERT INTO current_thresholds (model_type, threshold_data, updated_by)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                threshold_data = VALUES(threshold_data),
                updated_by = VALUES(updated_by)
            """, ('OD', json.dumps(threshold_data), employee_id))
            
            self.connection.commit()
            cursor.close()
            
            # Log the change
            self.log_system_event(employee_id, "OD_THRESHOLDS_UPDATED", f"Session: {session_id}")
            
            return True, "OD thresholds saved successfully"
            
        except Error as e:
            print(f"❌ Error saving OD thresholds: {e}")
            return False, f"Database error: {e}"
    
    def save_bigface_thresholds(self, employee_id, thresholds, session_id=None):
        """Save BigFace model threshold changes to history and update current values"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Insert into history table
            history_query = """
            INSERT INTO bigface_threshold_history 
            (employee_id, rust_threshold, dent_threshold, damage_threshold, 
             roller_threshold, model_confidence_threshold, session_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(history_query, (
                employee_id,
                thresholds.get('rust', 50),
                thresholds.get('dent', 50),
                thresholds.get('damage', 50),
                thresholds.get('roller', 50),
                thresholds.get('model_confidence', 0.25),
                session_id
            ))
            
            # Update current thresholds
            import json
            threshold_data = {
                'rust': thresholds.get('rust', 50),
                'dent': thresholds.get('dent', 50),
                'damage': thresholds.get('damage', 50),
                'roller': thresholds.get('roller', 50),
                'model_confidence': thresholds.get('model_confidence', 0.25)
            }
            
            cursor.execute("""
                INSERT INTO current_thresholds (model_type, threshold_data, updated_by)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                threshold_data = VALUES(threshold_data),
                updated_by = VALUES(updated_by)
            """, ('BIGFACE', json.dumps(threshold_data), employee_id))
            
            self.connection.commit()
            cursor.close()
            
            # Log the change
            self.log_system_event(employee_id, "BIGFACE_THRESHOLDS_UPDATED", f"Session: {session_id}")
            
            return True, "BigFace thresholds saved successfully"
            
        except Error as e:
            print(f"❌ Error saving BigFace thresholds: {e}")
            return False, f"Database error: {e}"
    
    def get_current_thresholds(self, model_type):
        """Retrieve current threshold values for specified model"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT threshold_data, last_updated, updated_by 
                FROM current_thresholds 
                WHERE model_type = %s
            """, (model_type,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                import json
                thresholds = json.loads(result['threshold_data'])
                thresholds['last_updated'] = result['last_updated']
                thresholds['updated_by'] = result['updated_by']
                return thresholds
            else:
                # Return default values if not found
                if model_type == 'OD':
                    return {
                        'rust': DEFAULT_OD_DEFECT_THRESHOLDS['Rust'],
                        'dent': DEFAULT_OD_DEFECT_THRESHOLDS['Dent'],
                        'spherical_mark': DEFAULT_OD_DEFECT_THRESHOLDS['Spherical Mark'],
                        'damage': DEFAULT_OD_DEFECT_THRESHOLDS['Damage'],
                        'flat_line': DEFAULT_OD_DEFECT_THRESHOLDS['Flat Line'],
                        'damage_on_end': DEFAULT_OD_DEFECT_THRESHOLDS['Damage on End'],
                        'roller': DEFAULT_OD_DEFECT_THRESHOLDS['Roller'],
                        'model_confidence': 0.25
                    }
                else:  # BIGFACE
                    return {
                        'rust': DEFAULT_BF_DEFECT_THRESHOLDS['Rust'],
                        'dent': DEFAULT_BF_DEFECT_THRESHOLDS['Dent'],
                        'damage': DEFAULT_BF_DEFECT_THRESHOLDS['Damage'],
                        'roller': DEFAULT_BF_DEFECT_THRESHOLDS['Roller'],
                        'model_confidence': 0.25
                    }
            
        except Error as e:
            print(f"❌ Error retrieving current thresholds: {e}")
            return None
    
    def get_threshold_history(self, model_type, start_date=None, end_date=None, employee_id=None, limit=100):
        """Retrieve threshold change history for specified model"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Build query based on model type
            if model_type == 'OD':
                table_name = 'od_threshold_history'
                columns = """id, employee_id, rust_threshold, dent_threshold, 
                            spherical_mark_threshold, damage_threshold, flat_line_threshold, 
                            damage_on_end_threshold, roller_threshold, model_confidence_threshold, 
                            change_timestamp, session_id"""
            else:  # BIGFACE
                table_name = 'bigface_threshold_history'
                columns = """id, employee_id, rust_threshold, dent_threshold, 
                            damage_threshold, roller_threshold, model_confidence_threshold, 
                            change_timestamp, session_id"""
            
            query = f"SELECT {columns} FROM {table_name} WHERE 1=1"
            params = []
            
            # Add filters
            if start_date:
                query += " AND DATE(change_timestamp) >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(change_timestamp) <= %s"
                params.append(end_date)
            
            if employee_id:
                query += " AND employee_id = %s"
                params.append(employee_id)
            
            query += " ORDER BY change_timestamp DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            history = cursor.fetchall()
            cursor.close()
            
            return history
            
        except Error as e:
            print(f"❌ Error retrieving threshold history: {e}")
            return []
    
    def clear_threshold_history(self, model_type=None, confirm_deletion=False):
        """Clear threshold history records from database
        
        Args:
            model_type: 'OD', 'BIGFACE', or None for both
            confirm_deletion: Must be True to actually delete records
        
        Returns:
            tuple: (success, message, records_deleted)
        """
        try:
            if not confirm_deletion:
                return False, "Deletion not confirmed", 0
            
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed", 0
            
            cursor = self.connection.cursor()
            total_deleted = 0
            
            # Clear OD history
            if model_type is None or model_type == 'OD':
                # Count records before deletion
                cursor.execute("SELECT COUNT(*) FROM od_threshold_history")
                od_count = cursor.fetchone()[0]
                
                # Delete records
                cursor.execute("DELETE FROM od_threshold_history")
                od_deleted = cursor.rowcount
                total_deleted += od_deleted
                
                print(f"🗑️ Cleared {od_deleted} OD threshold history records")
            
            # Clear BigFace history
            if model_type is None or model_type == 'BIGFACE':
                # Count records before deletion
                cursor.execute("SELECT COUNT(*) FROM bigface_threshold_history")
                bf_count = cursor.fetchone()[0]
                
                # Delete records
                cursor.execute("DELETE FROM bigface_threshold_history")
                bf_deleted = cursor.rowcount
                total_deleted += bf_deleted
                
                print(f"🗑️ Cleared {bf_deleted} BigFace threshold history records")
            
            self.connection.commit()
            cursor.close()
            
            # Log the deletion
            if model_type:
                log_message = f"Cleared {model_type} threshold history ({total_deleted} records)"
            else:
                log_message = f"Cleared all threshold history ({total_deleted} records)"
            
            self.log_system_event("SYSTEM", "THRESHOLD_HISTORY_CLEARED", log_message)
            
            return True, f"Successfully cleared {total_deleted} threshold history records", total_deleted
            
        except Error as e:
            print(f"❌ Error clearing threshold history: {e}")
            return False, f"Database error: {e}", 0
    
    def create_model_management_table(self):
        """Create separate tables for OD and BigFace models with simplified schema"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False
            
            cursor = self.connection.cursor()
            
            # Create OD Models table
            od_models_query = """
            CREATE TABLE IF NOT EXISTS od_models (
                id INT AUTO_INCREMENT PRIMARY KEY,
                model_name VARCHAR(255) NOT NULL,
                model_path VARCHAR(1000) NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                uploaded_by VARCHAR(20),
                is_active BOOLEAN DEFAULT FALSE,
                INDEX idx_upload_date (upload_date),
                INDEX idx_active (is_active)
            )
            """
            cursor.execute(od_models_query)
            
            # Create BigFace Models table
            bf_models_query = """
            CREATE TABLE IF NOT EXISTS bigface_models (
                id INT AUTO_INCREMENT PRIMARY KEY,
                model_name VARCHAR(255) NOT NULL,
                model_path VARCHAR(1000) NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                uploaded_by VARCHAR(20),
                is_active BOOLEAN DEFAULT FALSE,
                INDEX idx_upload_date (upload_date),
                INDEX idx_active (is_active)
            )
            """
            cursor.execute(bf_models_query)
            
            self.connection.commit()
            cursor.close()
            
            print("✅ OD and BigFace model tables created/verified successfully")
            return True
            
        except Error as e:
            print(f"❌ Error creating model tables: {e}")
            return False
    
    def upload_od_model(self, model_name, model_path, uploaded_by, set_active=False):
        """Upload an OD model to database"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Check if model with same name already exists
            cursor.execute("SELECT id FROM od_models WHERE model_name = %s", (model_name,))
            if cursor.fetchone():
                cursor.close()
                return False, f"OD model '{model_name}' already exists"
            
            # If set_active, deactivate other models first
            if set_active:
                cursor.execute("UPDATE od_models SET is_active = FALSE")
            
            # Insert new model
            cursor.execute("""
                INSERT INTO od_models (model_name, model_path, uploaded_by, is_active)
                VALUES (%s, %s, %s, %s)
            """, (model_name, model_path, uploaded_by, set_active))
            
            model_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            
            # Log the upload
            self.log_system_event(uploaded_by, "OD_MODEL_UPLOADED", f"Model: {model_name}")
            
            print(f"✅ OD model '{model_name}' uploaded successfully (ID: {model_id})")
            return True, f"OD model uploaded successfully with ID: {model_id}"
            
        except Error as e:
            print(f"❌ Error uploading OD model: {e}")
            return False, f"Database error: {e}"
    
    def upload_bigface_model(self, model_name, model_path, uploaded_by, set_active=False):
        """Upload a BigFace model to database"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Check if model with same name already exists
            cursor.execute("SELECT id FROM bigface_models WHERE model_name = %s", (model_name,))
            if cursor.fetchone():
                cursor.close()
                return False, f"BigFace model '{model_name}' already exists"
            
            # If set_active, deactivate other models first
            if set_active:
                cursor.execute("UPDATE bigface_models SET is_active = FALSE")
            
            # Insert new model
            cursor.execute("""
                INSERT INTO bigface_models (model_name, model_path, uploaded_by, is_active)
                VALUES (%s, %s, %s, %s)
            """, (model_name, model_path, uploaded_by, set_active))
            
            model_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            
            # Log the upload
            self.log_system_event(uploaded_by, "BIGFACE_MODEL_UPLOADED", f"Model: {model_name}")
            
            print(f"✅ BigFace model '{model_name}' uploaded successfully (ID: {model_id})")
            return True, f"BigFace model uploaded successfully with ID: {model_id}"
            
        except Error as e:
            print(f"❌ Error uploading BigFace model: {e}")
            return False, f"Database error: {e}"
    
    def get_od_models(self):
        """Retrieve all OD models from database"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, model_name, model_path, upload_date, uploaded_by, is_active
                FROM od_models 
                ORDER BY upload_date DESC
            """)
            models = cursor.fetchall()
            cursor.close()
            return models
            
        except Error as e:
            print(f"❌ Error retrieving OD models: {e}")
            return []
    
    def get_bigface_models(self):
        """Retrieve all BigFace models from database"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return []
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, model_name, model_path, upload_date, uploaded_by, is_active
                FROM bigface_models 
                ORDER BY upload_date DESC
            """)
            models = cursor.fetchall()
            cursor.close()
            return models
            
        except Error as e:
            print(f"❌ Error retrieving BigFace models: {e}")
            return []
    
    def delete_od_model(self, model_id, deleted_by):
        """Delete an OD model from database"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Get model info before deletion
            cursor.execute("SELECT * FROM od_models WHERE id = %s", (model_id,))
            model = cursor.fetchone()
            
            if not model:
                cursor.close()
                return False, "OD model not found"
            
            # Delete from database
            cursor.execute("DELETE FROM od_models WHERE id = %s", (model_id,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False, "OD model not found or already deleted"
            
            self.connection.commit()
            cursor.close()
            
            # Log the deletion
            self.log_system_event(deleted_by, "OD_MODEL_DELETED", f"Model: {model['model_name']}")
            
            print(f"✅ OD model '{model['model_name']}' deleted from database")
            return True, f"OD model '{model['model_name']}' deleted successfully"
            
        except Error as e:
            print(f"❌ Error deleting OD model: {e}")
            return False, f"Database error: {e}"
    
    def delete_bigface_model(self, model_id, deleted_by):
        """Delete a BigFace model from database"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor(dictionary=True)
            
            # Get model info before deletion
            cursor.execute("SELECT * FROM bigface_models WHERE id = %s", (model_id,))
            model = cursor.fetchone()
            
            if not model:
                cursor.close()
                return False, "BigFace model not found"
            
            # Delete from database
            cursor.execute("DELETE FROM bigface_models WHERE id = %s", (model_id,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False, "BigFace model not found or already deleted"
            
            self.connection.commit()
            cursor.close()
            
            # Log the deletion
            self.log_system_event(deleted_by, "BIGFACE_MODEL_DELETED", f"Model: {model['model_name']}")
            
            print(f"✅ BigFace model '{model['model_name']}' deleted from database")
            return True, f"BigFace model '{model['model_name']}' deleted successfully"
            
        except Error as e:
            print(f"❌ Error deleting BigFace model: {e}")
            return False, f"Database error: {e}"
    
    def set_active_od_model(self, model_id, activated_by):
        """Set an OD model as active"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Deactivate all OD models
            cursor.execute("UPDATE od_models SET is_active = FALSE")
            
            # Activate selected model
            cursor.execute("UPDATE od_models SET is_active = TRUE WHERE id = %s", (model_id,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False, "OD model not found"
            
            self.connection.commit()
            cursor.close()
            
            # Log the activation
            self.log_system_event(activated_by, "OD_MODEL_ACTIVATED", f"Model ID: {model_id}")
            
            print(f"✅ OD model ID {model_id} set as active")
            return True, "OD model activated successfully"
            
        except Error as e:
            print(f"❌ Error activating OD model: {e}")
            return False, f"Database error: {e}"
    
    def set_active_bigface_model(self, model_id, activated_by):
        """Set a BigFace model as active"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return False, "Database connection failed"
            
            cursor = self.connection.cursor()
            
            # Deactivate all BigFace models
            cursor.execute("UPDATE bigface_models SET is_active = FALSE")
            
            # Activate selected model
            cursor.execute("UPDATE bigface_models SET is_active = TRUE WHERE id = %s", (model_id,))
            
            if cursor.rowcount == 0:
                cursor.close()
                return False, "BigFace model not found"
            
            self.connection.commit()
            cursor.close()
            
            # Log the activation
            self.log_system_event(activated_by, "BIGFACE_MODEL_ACTIVATED", f"Model ID: {model_id}")
            
            print(f"✅ BigFace model ID {model_id} set as active")
            return True, "BigFace model activated successfully"
            
        except Error as e:
            print(f"❌ Error activating BigFace model: {e}")
            return False, f"Database error: {e}"
    
    def get_active_od_model(self):
        """Get the currently active OD model"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM od_models WHERE is_active = TRUE LIMIT 1")
            model = cursor.fetchone()
            cursor.close()
            return model
            
        except Error as e:
            print(f"❌ Error getting active OD model: {e}")
            return None
    
    def get_active_bigface_model(self):
        """Get the currently active BigFace model"""
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM bigface_models WHERE is_active = TRUE LIMIT 1")
            model = cursor.fetchone()
            cursor.close()
            return model
            
        except Error as e:
            print(f"❌ Error getting active BigFace model: {e}")
            return None

# Global database manager instance
db_manager = DatabaseManager() 