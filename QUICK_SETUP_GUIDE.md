# WelVision Quick Setup Guide for AI Assistants

This is a streamlined guide for AI assistants to help users quickly set up WelVision.

## 🚀 Quick Setup (5 Steps)

### Step 1: Prerequisites Check
```bash
# Check Python version (3.7+ required)
python --version

# Check if MySQL is installed
mysql --version
```

### Step 2: Install Dependencies
```bash
# Install required Python packages
pip install mysql-connector-python opencv-python ultralytics Pillow numpy
```

### Step 3: Database Setup
```bash
# Connect to MySQL and create database
mysql -u root -p
```
```sql
CREATE DATABASE welvision_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'welvision_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON welvision_db.* TO 'welvision_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 4: Configure Application
Update `config.py`:
```python
DB_CONFIG = {
    'HOST': 'localhost',
    'PORT': 3306,
    'DATABASE': 'welvision_db',
    'USER': 'welvision_user',
    'PASSWORD': 'secure_password'
}
```

### Step 5: Initialize Database
```bash
# Run database initialization
python init_database.py

# Start the application
python main.py
```

## 🔧 Troubleshooting Commands

### Quick Diagnostics
```bash
# Run system diagnostics
python system_diagnostics.py

# Test database connection
python -c "from database import DatabaseManager; print('✅ OK' if DatabaseManager().connect() else '❌ FAIL')"
```

### Common Issues

#### "ImportError: No module named 'mysql.connector'"
```bash
pip install mysql-connector-python
```

#### "Can't connect to MySQL server"
```bash
# Windows
net start mysql

# Linux
sudo systemctl start mysql
```

#### "Access denied for user"
- Check username/password in `config.py`
- Verify user exists: `SELECT User FROM mysql.user;`

#### "Database doesn't exist"
```sql
CREATE DATABASE welvision_db;
```

## 📋 Default Login Credentials

After running `init_database.py`:
- **Employee ID**: ADMIN001
- **Password**: WelVision2025!
- **Role**: Super Admin

**⚠️ Change password after first login!**

## 🎯 First-Time Setup Tasks

1. **Login** with default Super Admin account
2. **Set Global Limits** in Data tab (required for roller validation)
3. **Create Users** in User Management tab
4. **Upload AI Models** in Model Management tab
5. **Test System** by creating a roller in Data tab

## 🔍 System Health Check

### Database Tables Check
```sql
USE welvision_db;
SHOW TABLES;
-- Should show 10+ tables including:
-- users, roller_informations, global_roller_limits, od_models, etc.
```

### Application Test
```bash
# Quick application test
python main.py
# Should show login screen without errors
```

## 📁 Required Files

Core files that must exist:
- `main.py` - Application entry point
- `config.py` - Configuration
- `database.py` - Database manager
- `init_database.py` - Database setup script
- Tab modules: `*_tab.py` files
- Helper modules: `password_manager.py`, etc.

## 🚨 Critical Issues Resolution

### Issue: "No module named 'tkinter'"
**Linux Solution:**
```bash
sudo apt-get install python3-tk
```

### Issue: "MySQL service not running"
**Windows:**
```cmd
net start mysql
```
**Linux:**
```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Issue: "Tables don't exist"
**Solution:**
```bash
python init_database.py
```

### Issue: "Global limits not working"
**Check:**
1. `global_roller_limits` table exists
2. Super Admin has set limits in Data tab
3. Validation logic is working

## 🔄 Reset/Reinstall Process

### Complete Reset
```bash
# 1. Drop database
mysql -u root -p -e "DROP DATABASE welvision_db;"

# 2. Recreate database
mysql -u root -p -e "CREATE DATABASE welvision_db;"

# 3. Reinitialize
python init_database.py

# 4. Restart application
python main.py
```

## 📊 System Status Indicators

### ✅ System Ready
- All dependencies installed
- Database connected
- Tables created
- User accounts exist
- Global limits configured

### ⚠️ Needs Attention
- Missing AI models
- No global limits set
- Only default admin user

### ❌ Not Ready
- Database connection failed
- Missing dependencies
- Tables don't exist
- No user accounts

## 🎓 User Training Points

### For Super Admin
1. Set global roller limits first
2. Create user accounts for team
3. Upload and activate AI models
4. Monitor system logs

### For Admin
1. Create rollers within global limits
2. Manage AI model uploads
3. Run inspection sessions
4. Generate reports

### For Operator
1. Select roller type for inspection
2. Start/stop inspection sessions
3. View real-time results
4. Basic troubleshooting

---

**Quick Reference**: For immediate help, run `python system_diagnostics.py` to identify issues automatically. 