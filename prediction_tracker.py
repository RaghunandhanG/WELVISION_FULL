"""
Enhanced Prediction Tracker - Individual Prediction Storage
Stores every model prediction with detailed defect information and acceptance status
"""

import csv
import os
import datetime
import uuid
from threading import Lock
from database import db_manager

class PredictionTracker:
    def __init__(self):
        # CSV files for individual predictions
        self.od_predictions_csv = "od_predictions.csv"
        self.bf_predictions_csv = "bf_predictions.csv"
        self.csv_lock = Lock()
        
        # OD Predictions CSV Headers
        self.od_prediction_headers = [
            'prediction_id',
            'session_id',
            'timestamp',
            'roller_type',
            'employee_id',
            'status',  # 'ACCEPTED' or 'REJECTED'
            'total_detections',
            # Individual defect counts
            'rust_count',
            'dent_count',
            'spherical_mark_count',
            'damage_count',
            'flat_line_count',
            'damage_on_end_count',
            'roller_count',
            # Confidence scores (average)
            'avg_confidence',
            'max_confidence',
            'min_confidence',
            # Raw prediction data (JSON string)
            'raw_predictions'
        ]
        
        # BF Predictions CSV Headers
        self.bf_prediction_headers = [
            'prediction_id',
            'session_id',
            'timestamp',
            'roller_type',
            'employee_id',
            'status',  # 'ACCEPTED' or 'REJECTED'
            'total_detections',
            # Individual defect counts
            'rust_count',
            'dent_count',
            'damage_count',
            'roller_count',
            # Confidence scores (average)
            'avg_confidence',
            'max_confidence',
            'min_confidence',
            # Raw prediction data (JSON string)
            'raw_predictions'
        ]
        
        self.initialize_csv_files()
    
    def initialize_csv_files(self):
        """Initialize prediction CSV files with headers if they don't exist"""
        # Initialize OD predictions CSV
        if not os.path.exists(self.od_predictions_csv):
            with open(self.od_predictions_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.od_prediction_headers)
            print(f"✅ Created OD predictions CSV: {self.od_predictions_csv}")
        
        # Initialize BF predictions CSV
        if not os.path.exists(self.bf_predictions_csv):
            with open(self.bf_predictions_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.bf_prediction_headers)
            print(f"✅ Created BF predictions CSV: {self.bf_predictions_csv}")
    
    def log_prediction(self, component_type, predictions, session_id, roller_type=None, employee_id=None):
        """
        Log a single prediction with detailed defect information
        
        Args:
            component_type: 'od' or 'bf'
            predictions: List of prediction dictionaries [{'class_name': str, 'confidence': float}]
            session_id: Current session identifier
            roller_type: Type of roller being inspected
            employee_id: ID of the employee performing inspection
            
        Returns:
            dict: Prediction summary with acceptance status and defect counts
        """
        try:
            with self.csv_lock:
                prediction_id = str(uuid.uuid4())
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Analyze predictions
                analysis = self._analyze_predictions(predictions, component_type)
                
                # Determine acceptance status
                status = 'ACCEPTED' if analysis['is_accepted'] else 'REJECTED'
                
                # Prepare CSV row
                if component_type.lower() == 'od':
                    csv_file = self.od_predictions_csv
                    row = [
                        prediction_id,
                        session_id,
                        timestamp,
                        roller_type or 'Unknown',
                        employee_id or 'Unknown',
                        status,
                        analysis['total_detections'],
                        analysis['defect_counts'].get('rust', 0),
                        analysis['defect_counts'].get('dent', 0),
                        analysis['defect_counts'].get('spherical_mark', 0),
                        analysis['defect_counts'].get('damage', 0),
                        analysis['defect_counts'].get('flat_line', 0),
                        analysis['defect_counts'].get('damage_on_end', 0),
                        analysis['defect_counts'].get('roller', 0),
                        analysis['avg_confidence'],
                        analysis['max_confidence'],
                        analysis['min_confidence'],
                        str(predictions)  # Raw predictions as string
                    ]
                else:  # bf
                    csv_file = self.bf_predictions_csv
                    row = [
                        prediction_id,
                        session_id,
                        timestamp,
                        roller_type or 'Unknown',
                        employee_id or 'Unknown',
                        status,
                        analysis['total_detections'],
                        analysis['defect_counts'].get('rust', 0),
                        analysis['defect_counts'].get('dent', 0),
                        analysis['defect_counts'].get('damage', 0),
                        analysis['defect_counts'].get('roller', 0),
                        analysis['avg_confidence'],
                        analysis['max_confidence'],
                        analysis['min_confidence'],
                        str(predictions)  # Raw predictions as string
                    ]
                
                # Write to CSV
                with open(csv_file, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(row)
                
                print(f"📝 Logged {component_type.upper()} prediction: {prediction_id} - {status}")
                
                # Return summary for UI updates
                return {
                    'prediction_id': prediction_id,
                    'status': status,
                    'is_accepted': analysis['is_accepted'],
                    'defect_counts': analysis['defect_counts'],
                    'total_detections': analysis['total_detections'],
                    'confidence_stats': {
                        'avg': analysis['avg_confidence'],
                        'max': analysis['max_confidence'],
                        'min': analysis['min_confidence']
                    }
                }
                
        except Exception as e:
            print(f"❌ Error logging {component_type} prediction: {e}")
            return None
    
    def _analyze_predictions(self, predictions, component_type):
        """
        Analyze predictions to extract defect counts and acceptance status
        
        Args:
            predictions: List of prediction dictionaries
            component_type: 'od' or 'bf'
            
        Returns:
            dict: Analysis results with defect counts and acceptance status
        """
        defect_counts = {}
        confidences = []
        
        # Count each type of defect
        for pred in predictions:
            class_name = pred.get('class_name', '').lower()
            confidence = pred.get('confidence', 0.0)
            confidences.append(confidence)
            
            # Normalize class names and count
            if class_name in ['rust']:
                defect_counts['rust'] = defect_counts.get('rust', 0) + 1
            elif class_name in ['dent']:
                defect_counts['dent'] = defect_counts.get('dent', 0) + 1
            elif class_name in ['spherical_mark', 'spherical mark'] and component_type.lower() == 'od':
                defect_counts['spherical_mark'] = defect_counts.get('spherical_mark', 0) + 1
            elif class_name in ['damage']:
                defect_counts['damage'] = defect_counts.get('damage', 0) + 1
            elif class_name in ['flat_line', 'flat line'] and component_type.lower() == 'od':
                defect_counts['flat_line'] = defect_counts.get('flat_line', 0) + 1
            elif class_name in ['damage_on_end', 'damage on end'] and component_type.lower() == 'od':
                defect_counts['damage_on_end'] = defect_counts.get('damage_on_end', 0) + 1
            elif class_name in ['roller']:
                defect_counts['roller'] = defect_counts.get('roller', 0) + 1
        
        # Calculate confidence statistics
        if confidences:
            avg_confidence = round(sum(confidences) / len(confidences), 3)
            max_confidence = round(max(confidences), 3)
            min_confidence = round(min(confidences), 3)
        else:
            avg_confidence = max_confidence = min_confidence = 0.0
        
        # Determine acceptance: ACCEPTED only if predictions contain ONLY 'roller' class
        non_roller_defects = sum(count for key, count in defect_counts.items() if key != 'roller')
        is_accepted = (non_roller_defects == 0 and defect_counts.get('roller', 0) > 0)
        
        return {
            'defect_counts': defect_counts,
            'total_detections': len(predictions),
            'is_accepted': is_accepted,
            'avg_confidence': avg_confidence,
            'max_confidence': max_confidence,
            'min_confidence': min_confidence
        }
    
    def transfer_predictions_to_database_and_clear_csvs(self):
        """
        Transfer all prediction records from CSV files to database and clear CSV files
        
        Returns:
            tuple: (success: bool, message: str, transferred_counts: dict)
        """
        try:
            # Create database tables if not exist
            self._create_prediction_tables()
            
            # Transfer OD predictions
            od_success, od_message, od_count = self._transfer_predictions_data('od')
            
            # Transfer BF predictions
            bf_success, bf_message, bf_count = self._transfer_predictions_data('bf')
            
            if od_success and bf_success:
                # Clear CSV files (keep headers)
                self._clear_prediction_csv_files()
                
                message = f"Transferred {od_count} OD and {bf_count} BF prediction records to database"
                return True, message, {'od': od_count, 'bf': bf_count}
            else:
                error_msg = f"Transfer errors - OD: {od_message}, BF: {bf_message}"
                return False, error_msg, {'od': 0, 'bf': 0}
                
        except Exception as e:
            error_msg = f"Error transferring predictions to database: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg, {'od': 0, 'bf': 0}
    
    def _create_prediction_tables(self):
        """Create database tables for storing individual predictions"""
        try:
            if not db_manager.connection or not db_manager.connection.is_connected():
                if not db_manager.connect():
                    raise Exception("Failed to connect to database")
            
            cursor = db_manager.connection.cursor()
            
            # Create OD predictions table
            od_table_query = """
            CREATE TABLE IF NOT EXISTS od_predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prediction_id VARCHAR(100) UNIQUE NOT NULL,
                session_id VARCHAR(100) NOT NULL,
                timestamp DATETIME NOT NULL,
                roller_type VARCHAR(50),
                employee_id VARCHAR(20),
                status ENUM('ACCEPTED', 'REJECTED') NOT NULL,
                total_detections INT DEFAULT 0,
                rust_count INT DEFAULT 0,
                dent_count INT DEFAULT 0,
                spherical_mark_count INT DEFAULT 0,
                damage_count INT DEFAULT 0,
                flat_line_count INT DEFAULT 0,
                damage_on_end_count INT DEFAULT 0,
                roller_count INT DEFAULT 0,
                avg_confidence DECIMAL(5,3) DEFAULT 0.000,
                max_confidence DECIMAL(5,3) DEFAULT 0.000,
                min_confidence DECIMAL(5,3) DEFAULT 0.000,
                raw_predictions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_prediction_id (prediction_id),
                INDEX idx_session_id (session_id),
                INDEX idx_timestamp (timestamp),
                INDEX idx_status (status),
                INDEX idx_roller_type (roller_type),
                INDEX idx_employee_id (employee_id)
            )
            """
            
            # Create BF predictions table
            bf_table_query = """
            CREATE TABLE IF NOT EXISTS bf_predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prediction_id VARCHAR(100) UNIQUE NOT NULL,
                session_id VARCHAR(100) NOT NULL,
                timestamp DATETIME NOT NULL,
                roller_type VARCHAR(50),
                employee_id VARCHAR(20),
                status ENUM('ACCEPTED', 'REJECTED') NOT NULL,
                total_detections INT DEFAULT 0,
                rust_count INT DEFAULT 0,
                dent_count INT DEFAULT 0,
                damage_count INT DEFAULT 0,
                roller_count INT DEFAULT 0,
                avg_confidence DECIMAL(5,3) DEFAULT 0.000,
                max_confidence DECIMAL(5,3) DEFAULT 0.000,
                min_confidence DECIMAL(5,3) DEFAULT 0.000,
                raw_predictions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_prediction_id (prediction_id),
                INDEX idx_session_id (session_id),
                INDEX idx_timestamp (timestamp),
                INDEX idx_status (status),
                INDEX idx_roller_type (roller_type),
                INDEX idx_employee_id (employee_id)
            )
            """
            
            cursor.execute(od_table_query)
            cursor.execute(bf_table_query)
            db_manager.connection.commit()
            cursor.close()
            
            print("✅ OD and BF prediction tables created/verified")
            
        except Exception as e:
            print(f"❌ Error creating prediction tables: {e}")
            raise
    
    def _transfer_predictions_data(self, component_type):
        """Transfer prediction data from CSV to database for a specific component type"""
        try:
            csv_file = self.od_predictions_csv if component_type == 'od' else self.bf_predictions_csv
            table_name = f"{component_type}_predictions"
            
            if not os.path.exists(csv_file):
                return True, f"No {component_type.upper()} CSV file found", 0
            
            transferred_count = 0
            
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Skip empty rows or header-only files
                    if not row.get('prediction_id'):
                        continue
                    
                    success = self._insert_prediction_to_database(row, component_type)
                    if success:
                        transferred_count += 1
            
            return True, f"Transferred {transferred_count} {component_type.upper()} predictions", transferred_count
            
        except Exception as e:
            error_msg = f"Error transferring {component_type} predictions: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg, 0
    
    def _insert_prediction_to_database(self, csv_row, component_type):
        """Insert a single prediction record into the database"""
        try:
            cursor = db_manager.connection.cursor()
            table_name = f"{component_type}_predictions"
            
            if component_type == 'od':
                insert_query = f"""
                INSERT INTO {table_name} (
                    prediction_id, session_id, timestamp, roller_type, employee_id,
                    status, total_detections, rust_count, dent_count, spherical_mark_count,
                    damage_count, flat_line_count, damage_on_end_count, roller_count,
                    avg_confidence, max_confidence, min_confidence, raw_predictions
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                values = (
                    csv_row['prediction_id'],
                    csv_row['session_id'],
                    csv_row['timestamp'],
                    csv_row['roller_type'],
                    csv_row['employee_id'],
                    csv_row['status'],
                    int(csv_row['total_detections']),
                    int(csv_row['rust_count']),
                    int(csv_row['dent_count']),
                    int(csv_row['spherical_mark_count']),
                    int(csv_row['damage_count']),
                    int(csv_row['flat_line_count']),
                    int(csv_row['damage_on_end_count']),
                    int(csv_row['roller_count']),
                    float(csv_row['avg_confidence']),
                    float(csv_row['max_confidence']),
                    float(csv_row['min_confidence']),
                    csv_row['raw_predictions']
                )
            else:  # bf
                insert_query = f"""
                INSERT INTO {table_name} (
                    prediction_id, session_id, timestamp, roller_type, employee_id,
                    status, total_detections, rust_count, dent_count, damage_count,
                    roller_count, avg_confidence, max_confidence, min_confidence, raw_predictions
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                values = (
                    csv_row['prediction_id'],
                    csv_row['session_id'],
                    csv_row['timestamp'],
                    csv_row['roller_type'],
                    csv_row['employee_id'],
                    csv_row['status'],
                    int(csv_row['total_detections']),
                    int(csv_row['rust_count']),
                    int(csv_row['dent_count']),
                    int(csv_row['damage_count']),
                    int(csv_row['roller_count']),
                    float(csv_row['avg_confidence']),
                    float(csv_row['max_confidence']),
                    float(csv_row['min_confidence']),
                    csv_row['raw_predictions']
                )
            
            cursor.execute(insert_query, values)
            db_manager.connection.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error inserting {component_type} prediction to database: {e}")
            db_manager.connection.rollback()
            return False
    
    def _clear_prediction_csv_files(self):
        """Clear prediction CSV files but keep headers"""
        try:
            # Clear OD predictions CSV
            with open(self.od_predictions_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.od_prediction_headers)
            
            # Clear BF predictions CSV
            with open(self.bf_predictions_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.bf_prediction_headers)
            
            print("✅ Prediction CSV files cleared (headers preserved)")
            
        except Exception as e:
            print(f"❌ Error clearing prediction CSV files: {e}")
            raise
    
    def get_prediction_stats(self):
        """Get statistics from current prediction CSV files"""
        try:
            od_stats = self._get_prediction_component_stats('od')
            bf_stats = self._get_prediction_component_stats('bf')
            
            total_predictions = od_stats['total_predictions'] + bf_stats['total_predictions']
            
            return {
                'total_predictions': total_predictions,
                'od': od_stats,
                'bf': bf_stats
            }
            
        except Exception as e:
            print(f"❌ Error getting prediction stats: {e}")
            return {'total_predictions': 0, 'od': {}, 'bf': {}}
    
    def _get_prediction_component_stats(self, component_type):
        """Get statistics for a specific component type"""
        try:
            csv_file = self.od_predictions_csv if component_type == 'od' else self.bf_predictions_csv
            
            if not os.path.exists(csv_file):
                return {
                    'total_predictions': 0,
                    'accepted': 0,
                    'rejected': 0,
                    'acceptance_rate': 0.0
                }
            
            total_predictions = 0
            accepted = 0
            rejected = 0
            
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if row.get('prediction_id'):  # Skip empty rows
                        total_predictions += 1
                        if row.get('status') == 'ACCEPTED':
                            accepted += 1
                        else:
                            rejected += 1
            
            acceptance_rate = (accepted / total_predictions * 100) if total_predictions > 0 else 0.0
            
            return {
                'total_predictions': total_predictions,
                'accepted': accepted,
                'rejected': rejected,
                'acceptance_rate': acceptance_rate
            }
            
        except Exception as e:
            print(f"❌ Error getting {component_type} prediction stats: {e}")
            return {
                'total_predictions': 0,
                'accepted': 0,
                'rejected': 0,
                'acceptance_rate': 0.0
            }

# Global prediction tracker instance
prediction_tracker = PredictionTracker() 
