# AI Assistant Guide for WelVision Setup

This guide provides AI assistants with comprehensive information to help users set up and troubleshoot the WelVision system.

## System Overview

**WelVision** is an AI-powered roller inspection system with the following components:
- **Frontend**: Python Tkinter GUI application
- **Backend**: MySQL database with comprehensive table structure
- **AI Models**: YOLO-based OD (Object Detection) and BigFace models
- **User Management**: Role-based access (Admin, Super Admin, Operator)
- **Roller Management**: Global validation limits system

## Quick Setup Checklist

### Prerequisites Check
```bash
# Check Python version (3.7+ required)
python --version

# Check MySQL installation
mysql --version

# Check required Python packages
pip list | grep -E "(mysql-connector-python|tkinter|opencv|ultralytics)"
```

### Setup Steps
1. **Database Setup**: Run `python init_database.py`
2. **Configuration**: Update `config.py` with database credentials
3. **First Run**: Execute `python main.py`
4. **Initial Login**: Use default Super Admin (ADMIN001/WelVision2025!)

## File Structure Guide

### Core Application Files
- `main.py` - Main application entry point
- `config.py` - Database and system configuration
- `database.py` - Database manager with all table operations

### Tab Modules
- `inference_tab.py` - AI inspection interface
- `data_tab.py` - Roller management and global limits
- `settings_tab.py` - System settings and thresholds
- `diagnosis_tab.py` - System diagnostics and reports
- `model_management_tab.py` - AI model upload/management
- `model_preview_tab.py` - Model testing interface
- `user_management_tab.py` - User account management
- `system_check_tab.py` - System health monitoring

### Helper Modules
- `password_manager.py` - Secure password handling
- `prediction_tracker.py` - AI prediction logging
- `roller_inspection_logger.py` - Inspection session tracking

### Setup Files
- `init_database.py` - Database initialization script
- `DATABASE_SETUP.md` - Complete setup documentation
- `SETUP_COMPLETE.md` - System status summary

## Database Schema

### Core Tables (10+ tables)
1. **users** - Authentication and user management
2. **system_logs** - Audit trail
3. **roller_informations** - Roller data
4. **global_roller_limits** - Universal validation limits
5. **od_models/bigface_models** - AI model storage
6. **od_threshold_history/bigface_threshold_history** - Threshold tracking
7. **od_inspection_sessions/bf_inspection_sessions** - Session data
8. **od_predictions/bf_predictions** - Individual predictions

## Common Issues and Solutions

### Database Connection Issues
```python
# Check config.py format
DB_CONFIG = {
    'HOST': 'localhost',
    'PORT': 3306,
    'DATABASE': 'welvision_db',
    'USER': 'welvision_user',
    'PASSWORD': 'your_password'
}
```

**Troubleshooting Steps:**
1. Verify MySQL service is running
2. Test connection: `mysql -u username -p`
3. Check database exists: `SHOW DATABASES;`
4. Verify user permissions: `SHOW GRANTS FOR 'username'@'localhost';`

### Application Launch Issues
```bash
# Common error patterns and solutions:

# ImportError: No module named 'mysql.connector'
pip install mysql-connector-python

# ImportError: No module named 'cv2'
pip install opencv-python

# ImportError: No module named 'ultralytics'
pip install ultralytics

# tkinter not found (Linux)
sudo apt-get install python3-tk
```

### Global Limits System Issues
- **Problem**: Rollers not validating against limits
- **Solution**: Check `global_roller_limits` table exists and has data
- **Verification**: Query `SELECT * FROM global_roller_limits;`

### User Authentication Issues
- **Default Admin**: EMP003/password (existing) or ADMIN001/WelVision2025! (new)
- **Password Reset**: Update directly in database or recreate user
- **Role Issues**: Verify role enum values: 'Admin', 'Super Admin', 'Operator'

## Diagnostic Commands

### Database Health Check
```sql
-- Check all tables exist
SHOW TABLES;

-- Verify key tables have data
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM roller_informations;
SELECT * FROM global_roller_limits;

-- Check recent activity
SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 10;
```

### Application Health Check
```python
# Test database connection
python -c "from database import DatabaseManager; db = DatabaseManager(); print('✅ Connected' if db.connect() else '❌ Failed')"

# Check configuration
python -c "from config import DB_CONFIG; print(f'Database: {DB_CONFIG[\"DATABASE\"]} on {DB_CONFIG[\"HOST\"]}')"
```

## User Roles and Permissions

### Super Admin
- **Access**: All features including user management, global limits
- **Key Functions**: Set global roller limits, manage users, system configuration
- **Default Account**: ADMIN001 (if created during setup)

### Admin
- **Access**: Roller management, model management, inspection
- **Restrictions**: Cannot modify global limits or manage users
- **Key Functions**: Create/edit rollers (within limits), upload models

### Operator
- **Access**: Inspection interface only
- **Restrictions**: Read-only access to most features
- **Key Functions**: Run inspections, view results

## Global Roller Limits System

### How It Works
1. **Super Admin** sets global min/max values for diameter, thickness, length
2. **All users** (including Super Admin) must create rollers within these limits
3. **Validation** occurs on create/update operations
4. **Database**: Stored in `global_roller_limits` table

### Key Methods
```python
# In database.py
create_global_limits_table()
save_global_limits(limits_data)
get_global_limits()
validate_roller_against_global_limits(roller_data)
```

## AI Model Management

### Supported Models
- **OD Models**: Object Detection (7 defect types)
- **BigFace Models**: Face detection (4 defect types)

### Model Upload Process
1. Navigate to Model Management tab
2. Select model type (OD/BigFace)
3. Choose .pt file
4. Set as active if desired
5. Model stored in database with metadata

## Inspection Session Flow

### Session Lifecycle
1. **Start**: User selects roller type and begins inspection
2. **Processing**: AI models analyze images/video
3. **Tracking**: Predictions logged to database
4. **Results**: Statistics updated in real-time
5. **End**: Session completed and stored

### Data Flow
```
Image/Video → AI Model → Predictions → Database → Statistics → Reports
```

## Configuration Files

### config.py Structure
```python
# Database Configuration
DB_CONFIG = {...}

# AI Model Thresholds
DEFAULT_OD_DEFECT_THRESHOLDS = {...}
DEFAULT_BF_DEFECT_THRESHOLDS = {...}

# Application Settings
APP_BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4CAF50"
# ... other UI settings
```

## Troubleshooting Workflow

### Step 1: Environment Check
1. Python version compatibility
2. Required packages installed
3. MySQL server running
4. Database exists and accessible

### Step 2: Configuration Verification
1. config.py has correct database credentials
2. Database user has proper permissions
3. All required tables exist

### Step 3: Application Testing
1. Database connection test
2. User authentication test
3. Basic functionality test (create roller, etc.)

### Step 4: Advanced Diagnostics
1. Check system logs for errors
2. Verify AI model files exist
3. Test inspection workflow

## Helper Scripts Usage

### Database Initialization
```bash
# Full setup with prompts
python init_database.py

# Check if tables exist
python -c "from database import DatabaseManager; db = DatabaseManager(); db.connect(); cursor = db.connection.cursor(); cursor.execute('SHOW TABLES'); print([table[0] for table in cursor.fetchall()])"
```

### System Health Check
```bash
# Quick application test
python main.py --test-mode  # (if implemented)

# Database connectivity
python -c "from database import DatabaseManager; print('DB OK' if DatabaseManager().connect() else 'DB FAIL')"
```

## Common User Questions and Answers

### Q: "The application won't start"
**A**: Check Python version, install dependencies, verify MySQL is running

### Q: "Can't login with default credentials"
**A**: Try EMP003/password or ADMIN001/WelVision2025!, check users table

### Q: "Global limits not working"
**A**: Verify global_roller_limits table exists and has data, check validation logic

### Q: "AI models not loading"
**A**: Check model files exist, verify database model entries, check file permissions

### Q: "Database connection failed"
**A**: Verify MySQL running, check config.py credentials, test manual connection

## Advanced Setup Scenarios

### Multi-Machine Deployment
1. Copy entire project folder
2. Install MySQL on target machine
3. Update config.py for local database
4. Run init_database.py
5. Copy AI model files if needed

### Network Database Setup
1. Configure MySQL for network access
2. Update config.py with network host
3. Ensure firewall allows MySQL port (3306)
4. Test connection from client machine

### Backup and Migration
```bash
# Create backup
mysqldump -u username -p welvision_db > backup.sql

# Restore backup
mysql -u username -p welvision_db < backup.sql

# Copy application files
cp -r welvision_project/ /new/location/
```

## Performance Optimization

### Database Optimization
- Regular ANALYZE TABLE commands
- Monitor slow query log
- Optimize indexes for large datasets

### Application Optimization
- Monitor memory usage during AI inference
- Optimize image processing pipeline
- Consider caching for frequently accessed data

---

**Last Updated**: 2025-06-13  
**Version**: 1.0  
**For AI Assistant Use**: This guide provides comprehensive information for helping users with WelVision setup and troubleshooting. 