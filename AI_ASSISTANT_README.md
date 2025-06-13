# AI Assistant Guide for WelVision Support

## 🤖 For AI Assistants: How to Help Users with WelVision

This README provides AI assistants with everything needed to effectively help users set up, troubleshoot, and use the WelVision roller inspection system.

## 📋 Quick Reference Files

When helping users, reference these files in order of priority:

1. **`QUICK_SETUP_GUIDE.md`** - 5-step setup process
2. **`system_diagnostics.py`** - Automated troubleshooting tool
3. **`TROUBLESHOOTING_KB.json`** - Comprehensive issue database
4. **`AI_ASSISTANT_GUIDE.md`** - Detailed technical information
5. **`DATABASE_SETUP.md`** - Complete database setup guide

## 🚀 Standard Help Workflow

### Step 1: Identify User's Situation
Ask these questions to understand their current state:

```
1. "Is this a fresh installation or existing system?"
2. "What error message are you seeing (if any)?"
3. "What step were you trying to complete?"
4. "What operating system are you using?"
5. "Do you have MySQL installed?"
```

### Step 2: Run Diagnostics
Always start with automated diagnostics:

```bash
# Primary diagnostic command
python system_diagnostics.py

# Quick database test
python -c "from database import DatabaseManager; print('✅ OK' if DatabaseManager().connect() else '❌ FAIL')"
```

### Step 3: Apply Appropriate Solution
Based on diagnostics, use the troubleshooting guides to provide specific solutions.

## 🔧 Common User Scenarios

### Scenario 1: Complete Beginner
**User says**: "I need to set up WelVision from scratch"

**Your response**:
1. Direct them to `QUICK_SETUP_GUIDE.md`
2. Walk through the 5-step process
3. Emphasize running `python system_diagnostics.py` after each step
4. Provide the default login credentials

### Scenario 2: Installation Issues
**User says**: "I'm getting import errors" or "Python/MySQL issues"

**Your response**:
1. Run `python system_diagnostics.py` to identify specific issues
2. Reference `TROUBLESHOOTING_KB.json` for the exact error pattern
3. Provide specific pip install commands or system fixes
4. Verify fix with diagnostic commands

### Scenario 3: Database Problems
**User says**: "Can't connect to database" or "Tables missing"

**Your response**:
1. Check if MySQL service is running
2. Verify `config.py` has correct credentials
3. Run `python init_database.py` if tables are missing
4. Test connection with diagnostic commands

### Scenario 4: Application Won't Start
**User says**: "Application starts but no window" or "Crashes immediately"

**Your response**:
1. Test tkinter: `python -c "import tkinter; tkinter.Tk().mainloop()"`
2. Check for import errors in console output
3. Verify all required files exist
4. Test basic imports one by one

### Scenario 5: Login Issues
**User says**: "Can't log in" or "Invalid credentials"

**Your response**:
1. Provide default credentials: ADMIN001 / WelVision2025!
2. Alternative: EMP003 / password
3. Check if users table exists and has data
4. Verify user roles are correct

## 🎯 Key System Concepts to Explain

### Global Roller Limits System
- **What it is**: Universal min/max values for roller dimensions
- **Who sets it**: Super Admin only
- **Who follows it**: ALL users (including Super Admin)
- **Where to set**: Data tab → Global Limits section
- **Why important**: Prevents invalid roller creation

### User Roles and Access
- **Super Admin**: Full access, can set global limits, manage users
- **Admin**: Can create rollers (within limits), manage models, run inspections
- **Operator**: Inspection interface only

### Database Structure
- **Core tables**: users, roller_informations, global_roller_limits
- **AI tables**: od_models, bigface_models, prediction tables
- **Session tables**: inspection session tracking
- **Audit tables**: system_logs, threshold_history

## 🔍 Diagnostic Commands Reference

### Quick Health Check
```bash
# System overview
python system_diagnostics.py

# Python version
python --version

# Package check
python -c "import mysql.connector, cv2, tkinter; print('All packages OK')"

# Database connection
python -c "from database import DatabaseManager; print('DB OK' if DatabaseManager().connect() else 'DB FAIL')"
```

### Database Verification
```sql
-- Check database exists
SHOW DATABASES;

-- Check tables exist
USE welvision_db;
SHOW TABLES;

-- Check user accounts
SELECT employee_id, role FROM users;

-- Check global limits
SELECT * FROM global_roller_limits;
```

### Application Testing
```bash
# Test main imports
python -c "from main import WelVisionApp; print('Main module OK')"

# Test configuration
python -c "from config import DB_CONFIG; print(f'Database: {DB_CONFIG[\"DATABASE\"]}')"

# Test GUI
python -c "import tkinter; root = tkinter.Tk(); root.title('Test'); root.mainloop()"
```

## 🚨 Emergency Procedures

### Complete System Reset
When everything is broken:

```bash
# 1. Stop application
# 2. Backup data if possible
# 3. Reset database
mysql -u root -p -e "DROP DATABASE IF EXISTS welvision_db;"
mysql -u root -p -e "CREATE DATABASE welvision_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. Reinitialize
python init_database.py

# 5. Test
python main.py
```

### Database Recovery
When database is corrupted:

```sql
-- Check table status
CHECK TABLE table_name;

-- Repair if needed
REPAIR TABLE table_name;

-- If repair fails, reinitialize
```

## 💡 Pro Tips for AI Assistants

### Always Start With Diagnostics
- Never guess the problem
- Run `python system_diagnostics.py` first
- Use diagnostic output to guide solutions

### Be Specific with Commands
- Provide exact commands to run
- Include expected output
- Explain what each command does

### Verify Solutions
- After providing a fix, ask user to test
- Use diagnostic commands to verify
- Don't assume the fix worked

### Know the File Structure
- Understand which files are critical
- Know what each module does
- Reference specific files when helping

### Understand the Workflow
- Setup → Configuration → Database → Testing
- Each step depends on the previous
- Don't skip steps

## 📚 Knowledge Base Usage

### Error Pattern Matching
Use `TROUBLESHOOTING_KB.json` to match error messages:

```json
"import_errors": {
  "pattern": "ImportError|ModuleNotFoundError",
  "action": "Install missing package with pip"
}
```

### Solution Templates
Provide structured solutions:

1. **Identify the problem**
2. **Explain why it happens**
3. **Provide specific fix**
4. **Verify the solution**
5. **Prevent future occurrence**

## 🎓 User Education Points

### For New Users
- Emphasize the importance of following setup steps in order
- Explain that database setup is critical
- Show them how to use diagnostic tools

### For Troubleshooting
- Teach them to read error messages
- Show them diagnostic commands
- Explain how to prevent common issues

### For Advanced Users
- Database backup procedures
- Performance optimization
- System monitoring

## 📞 When to Escalate

Escalate to human support when:
- Hardware compatibility issues
- Network/firewall configuration
- Custom deployment scenarios
- Data corruption requiring manual intervention
- Performance issues requiring system analysis

## 🔄 Continuous Improvement

### Update Knowledge Base
- Track new issues and solutions
- Update troubleshooting guides
- Improve diagnostic tools

### User Feedback
- Ask users about their experience
- Identify common pain points
- Suggest documentation improvements

---

**Remember**: Your goal is to get users up and running quickly while teaching them to be self-sufficient. Always provide clear, actionable guidance and verify that solutions work. 