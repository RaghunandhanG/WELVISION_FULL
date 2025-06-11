"""
Configuration file for WelVision Application
Contains all constants, user data, and shared configurations
"""

# MySQL Database Configuration
DB_CONFIG = {
    "HOST": "localhost",
    "PORT": 3306,
    "DATABASE": "welvision_db",
    "USER": "root",
    "PASSWORD": "1469"
}

# Fallback user authentication data (used if MySQL is not available)
FALLBACK_USERS = {
    "EMP001": {"password": "password123", "role": "User"},
    "EMP002": {"password": "admin456", "role": "Admin"},
    "EMP003": {"password": "super789", "role": "Super Admin"}
}

# Application constants
APP_TITLE = "WELVISION"
APP_GEOMETRY = "1366x768"
APP_BG_COLOR = "#0a2158"

# PLC Configuration
PLC_CONFIG = {
    "IP": "172.17.8.17",
    "RACK": 0,
    "SLOT": 1,
    "DB_NUMBER": 86
}

# Model paths
MODEL_PATHS = {
    "BIGFACE": r"C:\Users\raghu\OneDrive\Desktop\Excel Sorting\BF_br.pt",
    "OD": r"C:\Users\raghu\OneDrive\Desktop\Excel Sorting\BF_br.pt"
}

# Frame configuration
FRAME_SHAPE = (960, 1280, 3)

# Default defect thresholds
DEFAULT_OD_DEFECT_THRESHOLDS = {
    "Rust": 50,
    "Dent": 50,
    "Spherical Mark": 50,
    "Damage": 50,
    "Flat Line": 50,
    "Damage on End": 50,
    "Roller": 50
}

DEFAULT_BF_DEFECT_THRESHOLDS = {
    "Damage": 50,
    "Rust": 50,
    "Dent": 50,
    "Roller": 50
}

# CSV file names
CSV_FILES = {
    "BIGFACE": "bigface_inspection_data.csv",
    "OD": "od_inspection_data.csv"
}

# CSV headers
CSV_HEADERS = {
    "BIGFACE": ["Component Type", "BF Inspected", "BF Accepted", "BF Rejected", 
                "H_Plus", "H_Minus", "Black", "White", "Report Date", "Report Time", "Comment"],
    "OD": ["Component Type", "OD Inspected", "OD Accepted", "OD Rejected", 
           "Rust", "Dent", "Spherical Mark", "Damage", "Flat Line", 
           "Damage on End", "Roller", "Report Date", "Report Time", "Comment"]
}
