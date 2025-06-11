# WelVision MySQL Authentication Setup Guide

## Prerequisites
- MySQL Server installed and running on your PC
- Python with pip package manager

## Step 1: Install MySQL Connector
```bash
pip install mysql-connector-python
```

## Step 2: Configure MySQL Database

### Option A: Using MySQL Command Line
1. Open MySQL Command Line Client
2. Enter your root password
3. Run the setup script:
```sql
source setup_database.sql
```

### Option B: Using MySQL Workbench
1. Open MySQL Workbench
2. Connect to your local MySQL server
3. Open the `setup_database.sql` file
4. Execute the entire script

## Step 3: Update Database Configuration
Edit the `config.py` file and update the DB_CONFIG section:

```python
DB_CONFIG = {
    "HOST": "localhost",
    "PORT": 3306,
    "DATABASE": "welvision_db",
    "USER": "your_mysql_username",     # Change this
    "PASSWORD": "your_mysql_password"   # Change this
}
```

## Step 4: Test the Connection
Run the application:
```bash
python main.py
```

## Default Login Credentials

| Employee ID | Password    | Role        |
|-------------|-------------|-------------|
| EMP001      | password123 | User        |
| EMP002      | admin456    | Admin       |
| EMP003      | super789    | Super Admin |

## Features
- ✅ Secure password hashing (SHA-256)
- ✅ Role-based access control
- ✅ Last login tracking
- ✅ Account activation/deactivation
- ✅ Fallback authentication if MySQL is unavailable
- ✅ User management capabilities

## Database Tables Created
1. **users** - User authentication and profiles
2. **component_types** - Component type definitions
3. **employees** - Employee information
4. **inspection_sessions** - Inspection session tracking
5. **system_logs** - System activity logging

## Troubleshooting

### Connection Issues
- Verify MySQL server is running
- Check username/password in config.py
- Ensure database 'welvision_db' exists
- Check firewall settings

### Fallback Mode
If MySQL is unavailable, the application will use fallback authentication with the same credentials.

## Security Notes
- Passwords are hashed using SHA-256
- Never store plain text passwords
- Regularly update MySQL and Python packages
- Use strong passwords for MySQL root account 