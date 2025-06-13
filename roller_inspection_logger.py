"""
Roller Inspection CSV Logger - Separate OD and BigFace Tracking
Tracks roller acceptance/rejection with detailed defect counts for each component
"""

import csv
import os
import datetime
from threading import Lock
from database import db_manager

class RollerInspectionLogger:
    def __init__(self):
        self.od_csv_file = "od_inspection_sessions.csv"
        self.bf_csv_file = "bf_inspection_sessions.csv"
        self.csv_lock = Lock()
        
        # OD CSV Headers
        self.od_csv_headers = [
            'session_id',
            'start_of_session',
            'end_of_session',
            'total_inspected',
            'total_accepted',
            'total_rejected',
            # OD Defect columns
            'rust_detections',
            'dent_detections',
            'spherical_mark_detections',
            'damage_detections',
            'flat_line_detections',
            'damage_on_end_detections',
            'roller_detections'
        ]
        
        # BigFace CSV Headers
        self.bf_csv_headers = [
            'session_id',
            'start_of_session',
            'end_of_session', 
            'total_inspected',
            'total_accepted',
            'total_rejected',
            # BF Defect columns
            'rust_detections',
            'dent_detections',
            'damage_detections',
            'roller_detections'
        ]
        
        self.initialize_csv_files()
    
    def initialize_csv_files(self):
        """Initialize both CSV files with headers if they don't exist"""
        # Initialize OD CSV
        if not os.path.exists(self.od_csv_file):
            with open(self.od_csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.od_csv_headers)
            print(f"✅ Created OD CSV log file: {self.od_csv_file}")
        
        # Initialize BF CSV
        if not os.path.exists(self.bf_csv_file):
            with open(self.bf_csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.bf_csv_headers)
            print(f"✅ Created BF CSV log file: {self.bf_csv_file}")
    
    def start_new_session(self, session_id):
        """
        Start a new inspection session for both OD and BF
        
        Args:
            session_id: Unique session identifier
        """
        try:
            with self.csv_lock:
                start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Initialize OD session
                od_row = [
                    session_id,
                    start_time,
                    '',  # end_of_session - will be filled when session ends
                    0,   # total_inspected
                    0,   # total_accepted
                    0,   # total_rejected
                    0,   # rust_detections
                    0,   # dent_detections
                    0,   # spherical_mark_detections
                    0,   # damage_detections
                    0,   # flat_line_detections
                    0,   # damage_on_end_detections
                    0    # roller_detections
                ]
                
                # Initialize BF session
                bf_row = [
                    session_id,
                    start_time,
                    '',  # end_of_session
                    0,   # total_inspected
                    0,   # total_accepted
                    0,   # total_rejected
                    0,   # rust_detections
                    0,   # dent_detections
                    0,   # damage_detections
                    0    # roller_detections
                ]
                
                # Write initial session rows
                with open(self.od_csv_file, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(od_row)
                
                with open(self.bf_csv_file, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(bf_row)
                
                print(f"📝 Started new inspection session: {session_id}")
                
        except Exception as e:
            print(f"❌ Error starting new session: {e}")
    
    def update_component_session(self, session_id, component_type, predictions):
        """
        Update session data for a specific component (OD or BF)
        
        Args:
            session_id: Session identifier
            component_type: 'od' or 'bf'
            predictions: List of prediction dictionaries
        """
        try:
            with self.csv_lock:
                csv_file = self.od_csv_file if component_type.lower() == 'od' else self.bf_csv_file
                
                # Read current session data
                session_data = self._read_current_session(csv_file, session_id)
                if not session_data:
                    return
                
                # Count defects in predictions
                defect_counts = self._count_defects(predictions, component_type)
                
                # Determine if component is accepted (only roller detections)
                is_accepted = self._is_component_accepted(defect_counts, component_type)
                
                # Update session totals
                session_data['total_inspected'] = str(int(session_data['total_inspected']) + 1)
                if is_accepted:
                    session_data['total_accepted'] = str(int(session_data['total_accepted']) + 1)
                else:
                    session_data['total_rejected'] = str(int(session_data['total_rejected']) + 1)
                
                # Update defect counts
                if component_type.lower() == 'od':
                    session_data['rust_detections'] = str(int(session_data['rust_detections']) + defect_counts.get('rust', 0))
                    session_data['dent_detections'] = str(int(session_data['dent_detections']) + defect_counts.get('dent', 0))
                    session_data['spherical_mark_detections'] = str(int(session_data['spherical_mark_detections']) + defect_counts.get('spherical_mark', 0))
                    session_data['damage_detections'] = str(int(session_data['damage_detections']) + defect_counts.get('damage', 0))
                    session_data['flat_line_detections'] = str(int(session_data['flat_line_detections']) + defect_counts.get('flat_line', 0))
                    session_data['damage_on_end_detections'] = str(int(session_data['damage_on_end_detections']) + defect_counts.get('damage_on_end', 0))
                    session_data['roller_detections'] = str(int(session_data['roller_detections']) + defect_counts.get('roller', 0))
                else:  # bf
                    session_data['rust_detections'] = str(int(session_data['rust_detections']) + defect_counts.get('rust', 0))
                    session_data['dent_detections'] = str(int(session_data['dent_detections']) + defect_counts.get('dent', 0))
                    session_data['damage_detections'] = str(int(session_data['damage_detections']) + defect_counts.get('damage', 0))
                    session_data['roller_detections'] = str(int(session_data['roller_detections']) + defect_counts.get('roller', 0))
                
                # Write updated session data back to CSV
                self._update_session_in_csv(csv_file, session_id, session_data)
                
                print(f"📊 Updated {component_type.upper()} session: {session_id} - {'ACCEPTED' if is_accepted else 'REJECTED'}")
                
        except Exception as e:
            print(f"❌ Error updating {component_type} session: {e}")
    
    def end_session(self, session_id):
        """
        End the current session by updating end_of_session timestamp
        
        Args:
            session_id: Session identifier
        """
        try:
            with self.csv_lock:
                end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Update both OD and BF sessions
                for csv_file in [self.od_csv_file, self.bf_csv_file]:
                    session_data = self._read_current_session(csv_file, session_id)
                    if session_data:
                        session_data['end_of_session'] = end_time
                        self._update_session_in_csv(csv_file, session_id, session_data)
                
                print(f"🏁 Ended inspection session: {session_id} at {end_time}")
                
        except Exception as e:
            print(f"❌ Error ending session: {e}")
    
    def _read_current_session(self, csv_file, session_id):
        """Read current session data from CSV file"""
        try:
            if not os.path.exists(csv_file):
                return None
                
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['session_id'] == session_id:
                        return row
            return None
            
        except Exception as e:
            print(f"❌ Error reading session from {csv_file}: {e}")
            return None
    
    def _update_session_in_csv(self, csv_file, session_id, updated_data):
        """Update specific session row in CSV file"""
        try:
            # Read all data
            all_rows = []
            headers = self.od_csv_headers if 'od_' in csv_file else self.bf_csv_headers
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['session_id'] == session_id:
                        all_rows.append(updated_data)
                    else:
                        all_rows.append(row)
            
            # Write all data back
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_rows)
                
        except Exception as e:
            print(f"❌ Error updating session in {csv_file}: {e}")
    
    def _count_defects(self, predictions, component_type):
        """Count defect types from model predictions"""
        if component_type.lower() == 'bf':
            defect_types = ['rust', 'dent', 'damage', 'roller']
        else:  # od
            defect_types = ['rust', 'dent', 'spherical_mark', 'damage', 'flat_line', 'damage_on_end', 'roller']
        
        counts = {defect: 0 for defect in defect_types}
        
        for pred in predictions:
            class_name = pred.get('class_name', '').lower().replace(' ', '_')
            if class_name in counts:
                counts[class_name] += 1
        
        return counts
    
    def _is_component_accepted(self, defect_counts, component_type):
        """Determine if component is accepted (only roller detections)"""
        total_defects = sum(count for defect, count in defect_counts.items() if defect != 'roller')
        return total_defects == 0
    
    def transfer_to_database_and_clear_csvs(self, session_id=None):
        """
        Transfer all CSV entries to database and clear CSV files
        
        Args:
            session_id: Optional session ID for tracking
            
        Returns:
            tuple: (success: bool, message: str, transferred_counts: dict)
        """
        try:
            # Create database tables if not exist
            self._create_database_tables()
            
            # Transfer OD data
            od_success, od_message, od_count = self._transfer_component_data('od', session_id)
            
            # Transfer BF data  
            bf_success, bf_message, bf_count = self._transfer_component_data('bf', session_id)
            
            if od_success and bf_success:
                # Clear CSV files (keep headers)
                self._clear_csv_files()
                
                message = f"Transferred {od_count} OD and {bf_count} BF session records to database"
                return True, message, {'od': od_count, 'bf': bf_count}
            else:
                error_msg = f"Transfer errors - OD: {od_message}, BF: {bf_message}"
                return False, error_msg, {'od': 0, 'bf': 0}
                
        except Exception as e:
            error_msg = f"Error transferring CSV to database: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg, {'od': 0, 'bf': 0}
    
    def _transfer_component_data(self, component_type, session_id):
        """Transfer data for specific component to database"""
        try:
            csv_file = self.od_csv_file if component_type == 'od' else self.bf_csv_file
            table_name = f"{component_type}_inspection_sessions"
            
            if not os.path.exists(csv_file):
                return True, f"No {component_type.upper()} CSV file to transfer", 0
            
            # Read CSV data
            csv_data = []
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                csv_data = list(reader)
            
            if not csv_data:
                return True, f"{component_type.upper()} CSV file is empty", 0
            
            # Insert data to database
            transferred_count = 0
            failed_count = 0
            
            for row in csv_data:
                success = self._insert_component_session_to_database(row, component_type, session_id)
                if success:
                    transferred_count += 1
                else:
                    failed_count += 1
            
            message = f"Transferred {transferred_count} {component_type.upper()} records"
            if failed_count > 0:
                message += f", {failed_count} failed"
            
            return True, message, transferred_count
            
        except Exception as e:
            return False, f"Error transferring {component_type} data: {e}", 0
    
    def _create_database_tables(self):
        """Create separate database tables for OD and BF inspection sessions"""
        try:
            if not db_manager.connection or not db_manager.connection.is_connected():
                if not db_manager.connect():
                    raise Exception("Failed to connect to database")
            
            cursor = db_manager.connection.cursor()
            
            # Create OD inspection sessions table
            od_table_query = """
            CREATE TABLE IF NOT EXISTS od_inspection_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                start_of_session DATETIME NOT NULL,
                end_of_session DATETIME,
                total_inspected INT DEFAULT 0,
                total_accepted INT DEFAULT 0,
                total_rejected INT DEFAULT 0,
                rust_detections INT DEFAULT 0,
                dent_detections INT DEFAULT 0,
                spherical_mark_detections INT DEFAULT 0,
                damage_detections INT DEFAULT 0,
                flat_line_detections INT DEFAULT 0,
                damage_on_end_detections INT DEFAULT 0,
                roller_detections INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_session_id (session_id),
                INDEX idx_start_time (start_of_session)
            )
            """
            
            # Create BF inspection sessions table
            bf_table_query = """
            CREATE TABLE IF NOT EXISTS bf_inspection_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                start_of_session DATETIME NOT NULL,
                end_of_session DATETIME,
                total_inspected INT DEFAULT 0,
                total_accepted INT DEFAULT 0,
                total_rejected INT DEFAULT 0,
                rust_detections INT DEFAULT 0,
                dent_detections INT DEFAULT 0,
                damage_detections INT DEFAULT 0,
                roller_detections INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_session_id (session_id),
                INDEX idx_start_time (start_of_session)
            )
            """
            
            cursor.execute(od_table_query)
            cursor.execute(bf_table_query)
            db_manager.connection.commit()
            cursor.close()
            
            print("✅ OD and BF inspection session tables created/verified")
            
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            raise
    
    def _insert_component_session_to_database(self, csv_row, component_type, session_id=None):
        """Insert a single component session row into the database"""
        try:
            cursor = db_manager.connection.cursor()
            table_name = f"{component_type}_inspection_sessions"
            
            if component_type == 'od':
                insert_query = f"""
                INSERT INTO {table_name} (
                    session_id, start_of_session, end_of_session, total_inspected, 
                    total_accepted, total_rejected, rust_detections, dent_detections,
                    spherical_mark_detections, damage_detections, flat_line_detections,
                    damage_on_end_detections, roller_detections
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                values = (
                    csv_row['session_id'],
                    csv_row['start_of_session'],
                    csv_row['end_of_session'] if csv_row['end_of_session'] else None,
                    int(csv_row['total_inspected']),
                    int(csv_row['total_accepted']),
                    int(csv_row['total_rejected']),
                    int(csv_row['rust_detections']),
                    int(csv_row['dent_detections']),
                    int(csv_row['spherical_mark_detections']),
                    int(csv_row['damage_detections']),
                    int(csv_row['flat_line_detections']),
                    int(csv_row['damage_on_end_detections']),
                    int(csv_row['roller_detections'])
                )
            else:  # bf
                insert_query = f"""
                INSERT INTO {table_name} (
                    session_id, start_of_session, end_of_session, total_inspected,
                    total_accepted, total_rejected, rust_detections, dent_detections,
                    damage_detections, roller_detections
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                
                values = (
                    csv_row['session_id'],
                    csv_row['start_of_session'],
                    csv_row['end_of_session'] if csv_row['end_of_session'] else None,
                    int(csv_row['total_inspected']),
                    int(csv_row['total_accepted']),
                    int(csv_row['total_rejected']),
                    int(csv_row['rust_detections']),
                    int(csv_row['dent_detections']),
                    int(csv_row['damage_detections']),
                    int(csv_row['roller_detections'])
                )
            
            cursor.execute(insert_query, values)
            db_manager.connection.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error inserting {component_type} session to database: {e}")
            db_manager.connection.rollback()
            return False
    
    def _clear_csv_files(self):
        """Clear both CSV files but keep headers"""
        try:
            # Clear OD CSV
            with open(self.od_csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.od_csv_headers)
            
            # Clear BF CSV
            with open(self.bf_csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.bf_csv_headers)
                
            print("🧹 Cleared both OD and BF CSV files")
            
        except Exception as e:
            print(f"❌ Error clearing CSV files: {e}")
    
    def get_session_stats(self):
        """
        Get current statistics from both CSV files
        
        Returns:
            dict: Combined statistics
        """
        try:
            od_stats = self._get_component_stats('od')
            bf_stats = self._get_component_stats('bf')
            
            return {
                'od': od_stats,
                'bf': bf_stats,
                'total_sessions': max(od_stats.get('sessions', 0), bf_stats.get('sessions', 0))
            }
            
        except Exception as e:
            print(f"❌ Error getting session stats: {e}")
            return {'od': {'sessions': 0}, 'bf': {'sessions': 0}, 'total_sessions': 0}
    
    def _get_component_stats(self, component_type):
        """Get statistics for specific component"""
        try:
            csv_file = self.od_csv_file if component_type == 'od' else self.bf_csv_file
            
            if not os.path.exists(csv_file):
                return {'sessions': 0, 'total_inspected': 0, 'total_accepted': 0, 'total_rejected': 0}
            
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
            
            sessions = len(data)
            total_inspected = sum(int(row['total_inspected']) for row in data)
            total_accepted = sum(int(row['total_accepted']) for row in data)
            total_rejected = sum(int(row['total_rejected']) for row in data)
            
            return {
                'sessions': sessions,
                'total_inspected': total_inspected,
                'total_accepted': total_accepted,
                'total_rejected': total_rejected,
                'acceptance_rate': (total_accepted / total_inspected * 100) if total_inspected > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting {component_type} stats: {e}")
            return {'sessions': 0, 'total_inspected': 0, 'total_accepted': 0, 'total_rejected': 0}

# Global logger instance
roller_logger = RollerInspectionLogger() 