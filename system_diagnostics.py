#!/usr/bin/env python3
"""
WelVision System Diagnostics Tool
=================================

This script performs comprehensive system diagnostics to help identify
and troubleshoot issues with the WelVision system.

Usage:
    python system_diagnostics.py [--verbose] [--fix-issues]

Author: WelVision Development Team
Date: 2025-06-13
"""

import sys
import os
import subprocess
import importlib
from datetime import datetime
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SystemDiagnostics:
    def __init__(self, verbose=False, fix_issues=False):
        self.verbose = verbose
        self.fix_issues = fix_issues
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def log(self, message, level="INFO"):
        """Log diagnostic messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "ERROR":
            self.issues.append(message)
            print(f"❌ [{timestamp}] {message}")
        elif level == "WARNING":
            self.warnings.append(message)
            print(f"⚠️  [{timestamp}] {message}")
        elif level == "SUCCESS":
            self.successes.append(message)
            print(f"✅ [{timestamp}] {message}")
        else:
            if self.verbose:
                print(f"ℹ️  [{timestamp}] {message}")
    
    def check_python_version(self):
        """Check Python version compatibility"""
        self.log("Checking Python version...", "INFO")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 7:
            self.log(f"Python {version.major}.{version.minor}.{version.micro} - Compatible", "SUCCESS")
            return True
        else:
            self.log(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+", "ERROR")
            return False
    
    def check_required_packages(self):
        """Check if required Python packages are installed"""
        self.log("Checking required Python packages...", "INFO")
        
        required_packages = {
            'mysql.connector': 'mysql-connector-python',
            'cv2': 'opencv-python',
            'tkinter': 'tkinter (built-in)',
            'ultralytics': 'ultralytics',
            'PIL': 'Pillow',
            'numpy': 'numpy'
        }
        
        missing_packages = []
        
        for package, install_name in required_packages.items():
            try:
                importlib.import_module(package)
                self.log(f"Package {package} - Available", "SUCCESS")
            except ImportError:
                self.log(f"Package {package} - Missing (install: pip install {install_name})", "ERROR")
                missing_packages.append(install_name)
        
        if missing_packages and self.fix_issues:
            self.log("Attempting to install missing packages...", "INFO")
            for package in missing_packages:
                if package != 'tkinter (built-in)':
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                        self.log(f"Successfully installed {package}", "SUCCESS")
                    except subprocess.CalledProcessError:
                        self.log(f"Failed to install {package}", "ERROR")
        
        return len(missing_packages) == 0
    
    def check_database_connection(self):
        """Check database connection"""
        self.log("Checking database connection...", "INFO")
        
        try:
            from config import DB_CONFIG
            self.log(f"Database config found: {DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['DATABASE']}", "INFO")
        except ImportError:
            self.log("config.py not found or invalid", "ERROR")
            return False
        except KeyError as e:
            self.log(f"Missing database configuration key: {e}", "ERROR")
            return False
        
        try:
            from database import DatabaseManager
            db_manager = DatabaseManager()
            
            if db_manager.connect():
                self.log("Database connection - Successful", "SUCCESS")
                db_manager.disconnect()
                return True
            else:
                self.log("Database connection - Failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Database connection error: {e}", "ERROR")
            return False
    
    def run_comprehensive_check(self):
        """Run all diagnostic checks"""
        print("=" * 60)
        print("WelVision System Diagnostics")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run basic checks
        checks = [
            ("Python Version", self.check_python_version),
            ("Required Packages", self.check_required_packages),
            ("Database Connection", self.check_database_connection)
        ]
        
        results = {}
        for check_name, check_func in checks:
            print(f"\n🔍 {check_name}:")
            try:
                result = check_func()
                results[check_name] = result
            except Exception as e:
                self.log(f"Check failed with exception: {e}", "ERROR")
                results[check_name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        total_checks = len(results)
        passed_checks = sum(1 for r in results.values() if r is True)
        failed_checks = sum(1 for r in results.values() if r is False)
        
        print(f"✅ Passed: {passed_checks}/{total_checks}")
        print(f"❌ Failed: {failed_checks}/{total_checks}")
        
        if self.issues:
            print(f"\n🚨 Critical Issues ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue}")
        
        return failed_checks == 0

def main():
    """Main function"""
    diagnostics = SystemDiagnostics(verbose=True, fix_issues=False)
    
    try:
        success = diagnostics.run_comprehensive_check()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostics cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during diagnostics: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 