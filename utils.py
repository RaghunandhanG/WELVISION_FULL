"""
Utility functions for WelVision Application
Contains CSV initialization and other shared utilities
"""

import csv
import os
from config import CSV_FILES, CSV_HEADERS

def initialize_bigface_csv():
    """
    Initializes the CSV file for BigFace inspection data if it doesn't exist.
    """
    filename = CSV_FILES["BIGFACE"]
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS["BIGFACE"])

def initialize_od_csv():
    """
    Initializes the CSV file for OD inspection data if it doesn't exist.
    """
    filename = CSV_FILES["OD"]
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS["OD"])

def initialize_all_csv():
    """Initialize all CSV files"""
    initialize_bigface_csv()
    initialize_od_csv()
