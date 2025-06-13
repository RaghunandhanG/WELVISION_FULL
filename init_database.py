#!/usr/bin/env python3
"""
WelVision Database Initialization Script
========================================

This script initializes all required database tables for the WelVision system.
Run this script on new machines to set up the database structure.

Requirements:
- MySQL server running
- Database already created
- Update config.py with correct database credentials

Usage:
    python init_database.py

Author: WelVision Development Team
Date: 2025-06-13
"""

import sys
import os
from datetime import datetime

# Add current directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import DatabaseManager
    from config import DB_CONFIG, DEFAULT_OD_DEFECT_THRESHOLDS, DEFAULT_BF_DEFECT_THRESHOLDS
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Make sure you're running this script from the WelVision directory")
    sys.exit(1)

def print_header():
    """Print script header"""
    print("=" * 60)
    print("WelVision Database Initialization Script")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Database: {DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['DATABASE']}")
    print("=" * 60)

def test_database_connection():
    """Test database connection before proceeding"""
    print("\n🔍 Testing database connection...")
    db_manager = DatabaseManager()
    
    if db_manager.connect():
        print("✅ Database connection successful")
        db_manager.disconnect()
        return True
    else:
        print("❌ Database connection failed")
        print("\nPlease check:")
        print("1. MySQL server is running")
        print("2. Database exists")
        print("3. Credentials in config.py are correct")
        print("4. Network connectivity")
        return False

def create_users_table(db_manager):
    """Create users table for authentication"""
    print("\n📋 Creating users table...")
    try:
        cursor = db_manager.connection.cursor()
        create_users_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            employee_id VARCHAR(20) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(64) NOT NULL,
            salt VARCHAR(64) NOT NULL,
            role ENUM('Admin', 'Super Admin', 'Operator') NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            failed_attempts INT DEFAULT 0,
            locked_until DATETIME NULL,
            last_login DATETIME NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_employee_id (employee_id),
            INDEX idx_email (email),
            INDEX idx_role (role),
            INDEX idx_active (is_active)
        )
        """
        cursor.execute(create_users_query)
        db_manager.connection.commit()
        cursor.close()
        print("✅ Users table created/verified")
        return True
    except Exception as e:
        print(f"❌ Error creating users table: {e}")
        return False

def create_system_logs_table(db_manager):
    """Create system logs table for audit trail"""
    print("\n📋 Creating system logs table...")
    try:
        cursor = db_manager.connection.cursor()
        create_logs_query = """
        CREATE TABLE IF NOT EXISTS system_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(20),
            action VARCHAR(100) NOT NULL,
            details TEXT,
            level ENUM('INFO', 'WARNING', 'ERROR', 'CRITICAL') DEFAULT 'INFO',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_id (user_id),
            INDEX idx_action (action),
            INDEX idx_level (level),
            INDEX idx_timestamp (timestamp)
        )
        """
        cursor.execute(create_logs_query)
        db_manager.connection.commit()
        cursor.close()
        print("✅ System logs table created/verified")
        return True
    except Exception as e:
        print(f"❌ Error creating system logs table: {e}")
        return False

def initialize_all_tables():
    """Initialize all database tables"""
    print_header()
    
    # Test connection first
    if not test_database_connection():
        return False
    
    # Initialize database manager
    db_manager = DatabaseManager()
    if not db_manager.connect():
        print("❌ Failed to connect to database")
        return False
    
    success_count = 0
    total_tables = 0
    
    try:
        # Core system tables
        print("\n🏗️  Creating core system tables...")
        
        # Users table
        total_tables += 1
        if create_users_table(db_manager):
            success_count += 1
        
        # System logs table
        total_tables += 1
        if create_system_logs_table(db_manager):
            success_count += 1
        
        # Roller management tables
        print("\n🏗️  Creating roller management tables...")
        
        # Roller informations table
        total_tables += 1
        if db_manager.create_roller_table():
            success_count += 1
        
        # Roller specifications table
        total_tables += 1
        if db_manager.create_roller_specifications_table():
            success_count += 1
        
        # Global roller limits table
        total_tables += 1
        if db_manager.create_global_limits_table():
            success_count += 1
        
        # Threshold management tables
        print("\n🏗️  Creating threshold management tables...")
        
        # Threshold tracking tables
        total_tables += 1
        if db_manager.create_threshold_tables():
            success_count += 1
        
        # Model management tables
        print("\n🏗️  Creating model management tables...")
        
        # OD and BigFace model tables
        total_tables += 1
        if db_manager.create_model_management_table():
            success_count += 1
        
        # Inspection session tables
        print("\n🏗️  Creating inspection session tables...")
        
        # Inspection session tables
        total_tables += 1
        if db_manager.create_inspection_session_tables():
            success_count += 1
        
        # Import additional table creation functions
        try:
            from prediction_tracker import PredictionTracker
            from roller_inspection_logger import RollerInspectionLogger
            
            # Prediction tracking tables
            print("\n🏗️  Creating prediction tracking tables...")
            total_tables += 1
            try:
                prediction_tracker = PredictionTracker()
                prediction_tracker._create_prediction_tables()
                print("✅ Prediction tracking tables created/verified")
                success_count += 1
            except Exception as e:
                print(f"❌ Error creating prediction tables: {e}")
            
            # Roller inspection logger tables
            print("\n🏗️  Creating roller inspection logger tables...")
            total_tables += 1
            try:
                inspection_logger = RollerInspectionLogger()
                inspection_logger._create_database_tables()
                print("✅ Roller inspection logger tables created/verified")
                success_count += 1
            except Exception as e:
                print(f"❌ Error creating inspection logger tables: {e}")
                
        except ImportError as e:
            print(f"⚠️  Warning: Could not import additional modules: {e}")
            print("Some optional tables may not be created")
        
        # Summary
        print("\n" + "=" * 60)
        print("DATABASE INITIALIZATION SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully created: {success_count}/{total_tables} tables")
        
        if success_count == total_tables:
            print("🎉 All database tables initialized successfully!")
            print("\nNext steps:")
            print("1. Create initial user accounts using the application")
            print("2. Configure global roller limits (Super Admin)")
            print("3. Upload AI models for inspection")
            print("4. Test the application functionality")
            return True
        else:
            print(f"⚠️  {total_tables - success_count} tables failed to initialize")
            print("Please check the error messages above and resolve issues")
            return False
            
    except Exception as e:
        print(f"❌ Critical error during initialization: {e}")
        return False
    
    finally:
        db_manager.disconnect()

def create_default_admin():
    """Create a default Super Admin user for initial setup"""
    print("\n🔐 Creating default Super Admin user...")
    
    db_manager = DatabaseManager()
    if not db_manager.connect():
        print("❌ Failed to connect to database")
        return False
    
    try:
        # Check if any Super Admin exists
        cursor = db_manager.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Super Admin'")
        admin_count = cursor.fetchone()[0]
        cursor.close()
        
        if admin_count > 0:
            print("✅ Super Admin user already exists, skipping creation")
            return True
        
        # Create default Super Admin
        default_employee_id = "ADMIN001"
        default_email = "admin@welvision.com"
        default_password = "WelVision2025!"
        
        success, message = db_manager.create_user(
            employee_id=default_employee_id,
            email=default_email,
            password=default_password,
            role="Super Admin"
        )
        
        if success:
            print("✅ Default Super Admin created successfully!")
            print(f"   Employee ID: {default_employee_id}")
            print(f"   Email: {default_email}")
            print(f"   Password: {default_password}")
            print("\n⚠️  IMPORTANT: Change the default password after first login!")
            return True
        else:
            print(f"❌ Failed to create default admin: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating default admin: {e}")
        return False
    finally:
        db_manager.disconnect()

def main():
    """Main function"""
    try:
        # Initialize all tables
        if initialize_all_tables():
            # Optionally create default admin
            print("\n" + "=" * 60)
            response = input("Create default Super Admin user? (y/n): ").lower().strip()
            
            if response in ['y', 'yes']:
                create_default_admin()
            
            print("\n🎉 Database initialization completed successfully!")
            print("The WelVision system is ready to use.")
            
        else:
            print("\n❌ Database initialization failed!")
            print("Please resolve the errors and run the script again.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 