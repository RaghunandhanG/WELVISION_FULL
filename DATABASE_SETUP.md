# WelVision Database Setup Guide

This guide will help you set up the WelVision database on a new machine.

## Prerequisites

### 1. MySQL Server Installation

**Windows:**
- Download MySQL Community Server from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/)
- Install MySQL Server with default settings
- Remember the root password you set during installation

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install mysql-server
sudo systemctl start mysqld
sudo mysql_secure_installation
```

### 2. Python Dependencies

Make sure you have the required Python packages installed:
```bash
pip install mysql-connector-python
pip install hashlib
pip install secrets
```

## Database Setup Steps

### Step 1: Create Database

1. **Connect to MySQL as root:**
   ```bash
   mysql -u root -p
   ```

2. **Create the WelVision database:**
   ```sql
   CREATE DATABASE welvision_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Create a dedicated user (recommended):**
   ```sql
   CREATE USER 'welvision_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON welvision_db.* TO 'welvision_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

### Step 2: Configure Database Connection

1. **Update `config.py` with your database credentials:**
   ```python
   DB_CONFIG = {
       'HOST': 'localhost',
       'PORT': 3306,
       'DATABASE': 'welvision_db',
       'USER': 'welvision_user',
       'PASSWORD': 'your_secure_password'
   }
   ```

### Step 3: Initialize Database Tables

1. **Run the database initialization script:**
   ```bash
   python init_database.py
   ```

2. **Follow the prompts:**
   - The script will test the database connection
   - Create all required tables
   - Optionally create a default Super Admin user

## Database Tables Created

The initialization script creates the following tables:

### Core System Tables
- **users** - User authentication and management
- **system_logs** - System audit trail

### Roller Management Tables
- **roller_informations** - Roller specifications and data
- **roller_specifications** - Per-roller-type specifications (legacy)
- **global_roller_limits** - Global validation limits for all rollers

### Threshold Management Tables
- **od_threshold_history** - OD model threshold change history
- **bigface_threshold_history** - BigFace model threshold change history
- **current_thresholds** - Current active threshold settings

### Model Management Tables
- **od_models** - OD AI model storage and management
- **bigface_models** - BigFace AI model storage and management

### Inspection Session Tables
- **od_inspection_sessions** - OD inspection session data
- **bf_inspection_sessions** - BigFace inspection session data

### Prediction Tracking Tables
- **od_predictions** - Individual OD prediction records
- **bf_predictions** - Individual BigFace prediction records

## Default Super Admin Account

If you choose to create a default Super Admin during initialization:

- **Employee ID:** ADMIN001
- **Email:** admin@welvision.com
- **Password:** WelVision2025!

**⚠️ IMPORTANT:** Change this password immediately after first login!

## Verification

After running the initialization script, you can verify the setup:

1. **Check if tables were created:**
   ```sql
   USE welvision_db;
   SHOW TABLES;
   ```

2. **Verify table structure (example):**
   ```sql
   DESCRIBE users;
   DESCRIBE roller_informations;
   DESCRIBE global_roller_limits;
   ```

3. **Test the application:**
   ```bash
   python main.py
   ```

## Troubleshooting

### Common Issues

1. **Connection Failed:**
   - Check if MySQL server is running
   - Verify credentials in `config.py`
   - Ensure database exists
   - Check firewall settings

2. **Permission Denied:**
   - Verify user has proper privileges
   - Check if user can connect from the host

3. **Import Errors:**
   - Ensure all Python dependencies are installed
   - Run script from the WelVision directory

4. **Table Creation Failed:**
   - Check MySQL error logs
   - Verify sufficient disk space
   - Ensure proper MySQL configuration

### MySQL Service Commands

**Windows:**
```cmd
net start mysql
net stop mysql
```

**Linux:**
```bash
sudo systemctl start mysql
sudo systemctl stop mysql
sudo systemctl status mysql
```

## Backup and Restore

### Create Backup
```bash
mysqldump -u welvision_user -p welvision_db > welvision_backup.sql
```

### Restore from Backup
```bash
mysql -u welvision_user -p welvision_db < welvision_backup.sql
```

## Security Recommendations

1. **Use strong passwords** for database users
2. **Limit database user privileges** to only what's needed
3. **Enable SSL connections** for production environments
4. **Regular backups** of the database
5. **Monitor system logs** for suspicious activity
6. **Keep MySQL server updated** with security patches

## Support

If you encounter issues during setup:

1. Check the error messages in the initialization script output
2. Review MySQL error logs
3. Verify all prerequisites are met
4. Contact the WelVision development team

---

**Last Updated:** 2025-06-13  
**Version:** 1.0  
**Author:** WelVision Development Team 