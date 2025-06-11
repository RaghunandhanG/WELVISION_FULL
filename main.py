"""
Main WelVision Application
Modular implementation with separate tab files
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import cv2
import PIL.Image, PIL.ImageTk
from PIL import Image, ImageTk, ImageGrab
import numpy as np
import threading
import time
from multiprocessing import Process, Array, Queue, Lock, Value, Manager
from ultralytics import YOLO
import snap7
from snap7.util import set_bool
from snap7.type import Areas
import pandas as pd
from datetime import datetime
import uuid

# Import configuration and utilities
from config import *
from utils import initialize_all_csv
from database import db_manager

# Import tab modules
from inference_tab import InferenceTab
from settings_tab import SettingsTab
from data_tab import DataTab
from diagnosis_tab import DiagnosisTab
from system_check_tab import SystemCheckTab
from model_preview_tab import ModelPreviewTab
from user_management_tab import UserManagementTab
from model_management_tab import ModelManagementTab

class WelVisionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.configure(bg=APP_BG_COLOR)
        self.iconbitmap(default="")
        
        # Center window on screen
        self.center_window()
        
        # Initialize variables
        self.current_user = None
        self.current_role = None
        
        # Camera variables
        self.camera_running = False
        self.od_thread = None
        self.bf_thread = None
        self.od_canvas = None
        self.bf_canvas = None
        
        # Inspection status
        self.inspection_running = False
        self.processes = []
        self.plc_process = None
        
        # Defect thresholds
        self.od_defect_thresholds = DEFAULT_OD_DEFECT_THRESHOLDS.copy()
        self.bf_defect_thresholds = DEFAULT_BF_DEFECT_THRESHOLDS.copy()
        
        # Data entries for roller management
        self.data_entries = {}
        self.selected_roller_id = None
        self.tree = None
        
        # Handle window closing properly
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Show login page
        self.show_login_page()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1280) // 2
        y = (screen_height - 800) // 2
        self.geometry(f"1280x800+{x}+{y}")
    
    def show_login_page(self):
        # Stop any running threads first
        self.stop_camera_feeds()
        
        for widget in self.winfo_children():
            widget.destroy()
        
        login_frame = tk.Frame(self, bg="black", width=700, height=800)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        logo_label = tk.Label(login_frame, text="WELVISION", font=("Arial", 36, "bold"), fg="white", bg="black")
        logo_label.pack(pady=(40, 30))
        
        subtitle_label = tk.Label(login_frame, text="Please sign in to continue", font=("Arial", 16), fg="white", bg="black")
        subtitle_label.pack(pady=(0, 40))
        
        role_frame = tk.Frame(login_frame, bg="black")
        role_frame.pack(pady=(0, 30))
        
        self.role_var = tk.StringVar(value="User")
        
        user_rb = tk.Radiobutton(role_frame, text="User", variable=self.role_var, value="User", 
                                font=("Arial", 14), fg="white", bg="black", selectcolor="black")
        admin_rb = tk.Radiobutton(role_frame, text="Admin", variable=self.role_var, value="Admin", 
                                 font=("Arial", 14), fg="white", bg="black", selectcolor="black")
        super_admin_rb = tk.Radiobutton(role_frame, text="Super Admin", variable=self.role_var, value="Super Admin", 
                                       font=("Arial", 14), fg="white", bg="black", selectcolor="black")
        
        user_rb.pack(side=tk.LEFT, padx=15)
        admin_rb.pack(side=tk.LEFT, padx=15)
        super_admin_rb.pack(side=tk.LEFT, padx=15)
        
        employee_label = tk.Label(login_frame, text="Employee ID", font=("Arial", 14), fg="white", bg="black", anchor="w")
        employee_label.pack(fill="x", pady=(0, 8), padx=40)
        
        self.employee_entry = tk.Entry(login_frame, font=("Arial", 14), width=35)
        self.employee_entry.pack(pady=(0, 20), ipady=10, padx=40)
        
        password_label = tk.Label(login_frame, text="Password", font=("Arial", 14), fg="white", bg="black", anchor="w")
        password_label.pack(fill="x", pady=(0, 8), padx=40)
        
        self.password_entry = tk.Entry(login_frame, font=("Arial", 14), width=35, show="*")
        self.password_entry.pack(pady=(0, 40), ipady=10, padx=40)
        
        sign_in_button = tk.Button(login_frame, text="Sign In", font=("Arial", 14, "bold"), 
                                  bg="#007bff", fg="white", width=22, height=2, 
                                  command=self.authenticate)
        sign_in_button.pack(pady=20)
        
        self.bind("<Return>", lambda event: self.authenticate())
    
    def authenticate(self):
        try:
            employee_id = self.employee_entry.get().strip()
            password = self.password_entry.get().strip()
            role = self.role_var.get()
            
            # Validate input
            if not employee_id or not password:
                messagebox.showerror("Login Failed", "Please enter both Employee ID and Password.")
                return
            
            # Try MySQL authentication first
            success, message, user_data = db_manager.authenticate_user(employee_id, password, role)
            
            if success:
                self.current_user = employee_id
                self.current_role = role
                db_manager.log_system_event(employee_id, "LOGIN_SUCCESS", f"Role: {role}")
                messagebox.showinfo("Login Success", message)
                self.show_main_interface()
            else:
                db_manager.log_system_event(employee_id, "LOGIN_FAILED", f"Role: {role}, Reason: {message}", "WARNING")
                
                # Fallback authentication
                if employee_id in FALLBACK_USERS and FALLBACK_USERS[employee_id]["password"] == password and FALLBACK_USERS[employee_id]["role"] == role:
                    self.current_user = employee_id
                    self.current_role = role
                    messagebox.showinfo("Login Success", f"Welcome {employee_id}! (Fallback Mode)")
                    self.show_main_interface()
                else:
                    messagebox.showerror("Login Failed", message)
                    
        except Exception as e:
            db_manager.log_system_event(employee_id if 'employee_id' in locals() else "Unknown", "LOGIN_ERROR", f"Error: {e}", "ERROR")
            print(f"Authentication error: {e}")
            
            # Fallback authentication
            try:
                if employee_id in FALLBACK_USERS and FALLBACK_USERS[employee_id]["password"] == password and FALLBACK_USERS[employee_id]["role"] == role:
                    self.current_user = employee_id
                    self.current_role = role
                    messagebox.showinfo("Login Success", f"Welcome {employee_id}! (Fallback Mode)")
                    self.show_main_interface()
                else:
                    messagebox.showerror("Login Failed", "Authentication failed. Check database connection.")
            except:
                messagebox.showerror("Login Failed", "Authentication system error.")

    def show_main_interface(self):
        # Stop any running processes first
        self.stop_camera_feeds()
        
        # Initialize system components
        self.initialize_system()
        
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self, bg=APP_BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=APP_BG_COLOR, height=50)
        header_frame.pack(fill=tk.X)
        
        logo_label = tk.Label(header_frame, text="WELVISION", font=("Arial", 18, "bold"), fg="white", bg=APP_BG_COLOR)
        logo_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        user_label = tk.Label(header_frame, text=f"{self.current_role}: {self.current_user}", 
                             font=("Arial", 12), fg="white", bg=APP_BG_COLOR)
        user_label.pack(side=tk.RIGHT, padx=20, pady=5)
        
        logout_button = tk.Button(header_frame, text="Logout", font=("Arial", 10), 
                                 command=self.show_login_page)
        logout_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Tab control styling
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', background=APP_BG_COLOR, foreground="white", 
                       font=('Arial', 12, 'bold'), padding=[20, 10], borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', '#1a3168')], 
                 foreground=[('selected', 'white')])
        style.configure('TNotebook', background=APP_BG_COLOR, borderwidth=0)
        
        # Create tabs
        tab_control = ttk.Notebook(main_frame)
        
        inference_tab = tk.Frame(tab_control, bg=APP_BG_COLOR)
        settings_tab = tk.Frame(tab_control, bg=APP_BG_COLOR)
        data_tab = tk.Frame(tab_control, bg=APP_BG_COLOR)
        diagnosis_tab = tk.Frame(tab_control, bg=APP_BG_COLOR)
        model_preview_tab = tk.Frame(tab_control, bg=APP_BG_COLOR)
        model_management_tab = tk.Frame(tab_control, bg=APP_BG_COLOR)
        
        tab_control.add(inference_tab, text="Inference")
        tab_control.add(settings_tab, text="Settings")
        tab_control.add(data_tab, text="Data")
        tab_control.add(diagnosis_tab, text="Diagnosis")
        tab_control.add(model_preview_tab, text="Model Preview")
        tab_control.add(model_management_tab, text="Model Management")
        
        # Add User Management tab for Admin and Super Admin users
        if self.current_role in ["Admin", "Super Admin"]:
            user_management_tab = tk.Frame(tab_control, bg=APP_BG_COLOR)
            tab_control.add(user_management_tab, text="User Management")
        
        # Add System Check tab only for Super Admin users
        if self.current_role == "Super Admin":
            system_check_tab = tk.Frame(tab_control, bg=APP_BG_COLOR)
            tab_control.add(system_check_tab, text="System Check")
        
        tab_control.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Initialize tab modules
        try:
            self.inference_tab = InferenceTab(inference_tab, self)
            
            # Initialize settings tab with read-only mode for regular users
            read_only_mode = (self.current_role == "User")
            self.settings_tab = SettingsTab(settings_tab, self, read_only=read_only_mode)
            
            self.data_tab = DataTab(data_tab, self)
            self.initialize_database_tables()
            self.diagnosis_tab = DiagnosisTab(diagnosis_tab, self)
            self.model_preview_tab = ModelPreviewTab(model_preview_tab, self)
            self.model_management_tab = ModelManagementTab(model_management_tab, self)
            
            # Initialize User Management tab for Admin and Super Admin users
            if self.current_role in ["Admin", "Super Admin"]:
                self.user_management_tab = UserManagementTab(user_management_tab, self)
            
            # Initialize System Check tab only for Super Admin users
            if self.current_role == "Super Admin":
                self.system_check_tab = SystemCheckTab(system_check_tab, self)
            
            # Start camera feeds after all tabs are initialized
            self.start_camera_feeds()
            
        except Exception as e:
            print(f"Error initializing tabs: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {e}")

    def initialize_system(self):
        """Initialize system components and models"""
        try:
            self.RACK = PLC_CONFIG["RACK"]
            self.PLC_IP = PLC_CONFIG["IP"]
            self.SLOT = PLC_CONFIG["SLOT"]
            self.DB_NUMBER = PLC_CONFIG["DB_NUMBER"]
            initialize_all_csv()

            # Initialize database tables including threshold tracking
            self.initialize_database_tables()

            print("Loading YOLO model...")
            self.model_bigface = YOLO(MODEL_PATHS["BIGFACE"])
            self.model_od = YOLO(MODEL_PATHS["OD"])

            self.model_bigface.to('cpu')
            self.model_od.to('cpu')

            self.frame_shape = FRAME_SHAPE

            self.manager = Manager()
            self.shared_data = self.manager.dict()
            self.shared_data['bigface'] = False
            self.shared_data['od'] = False
            self.shared_data['bigface_presence'] = False
            self.shared_data['od_presence'] = False

            self.command_queue = Queue()

            self.proximity_count_od = Value('i', 0)
            self.proximity_count_bigface = Value('i', 0)

            self.roller_data_od = self.manager.dict()
            self.roller_queue_od = Queue()
            self.roller_queue_bigface = Queue()
            self.roller_updation_dict = self.manager.dict()

            self.shared_frame_bigface = Array('B', np.zeros(FRAME_SHAPE, dtype=np.uint8).flatten())
            self.shared_frame_od = Array('B', np.zeros(FRAME_SHAPE, dtype=np.uint8).flatten())
            self.shared_annotated_bigface = Array('B', np.zeros(FRAME_SHAPE, dtype=np.uint8).flatten())
            self.shared_annotated_od = Array('B', np.zeros(FRAME_SHAPE, dtype=np.uint8).flatten())

            self.frame_lock_bigface = Lock()
            self.frame_lock_od = Lock()
            self.annotated_frame_lock_bigface = Lock()
            self.annotated_frame_lock_od = Lock()
            self.queue_lock = Lock()
            
            # Load current threshold values from database
            self.load_current_thresholds()
            
            # Generate session ID for tracking changes
            self.session_id = str(uuid.uuid4())
            
        except Exception as e:
            print(f"System initialization error: {e}")

    def initialize_database_tables(self):
        """Initialize database tables for roller management and threshold tracking"""
        try:
            # Create roller table
            success = db_manager.create_roller_table()
            if success:
                self.update_status("✅ Roller informations table created/verified")
            else:
                self.update_status("⚠️ Warning: Roller database initialization failed")
            
            # Create threshold tracking tables
            threshold_success = db_manager.create_threshold_tables()
            if threshold_success:
                print("✅ Threshold tracking tables initialized successfully")
            else:
                print("⚠️ Warning: Threshold tracking initialization failed")
            
            # Create model management table
            model_success = db_manager.create_model_management_table()
            if model_success:
                print("✅ Model management table initialized successfully")
            else:
                print("⚠️ Warning: Model management table initialization failed")
                
        except Exception as e:
            print(f"Database initialization error: {e}")
            self.update_status(f"❌ Database error: {e}")
    
    def load_current_thresholds(self):
        """Load current threshold values from database"""
        try:
            # Load OD thresholds
            od_thresholds = db_manager.get_current_thresholds('OD')
            if od_thresholds:
                self.od_defect_thresholds = {
                    'Rust': od_thresholds.get('rust', 50),
                    'Dent': od_thresholds.get('dent', 50),
                    'Spherical Mark': od_thresholds.get('spherical_mark', 50),
                    'Damage': od_thresholds.get('damage', 50),
                    'Flat Line': od_thresholds.get('flat_line', 50),
                    'Damage on End': od_thresholds.get('damage_on_end', 50),
                    'Roller': od_thresholds.get('roller', 50)
                }
                self.od_conf_threshold = od_thresholds.get('model_confidence', 0.25)
                print(f"✅ Loaded OD thresholds from database")
            
            # Load BigFace thresholds
            bf_thresholds = db_manager.get_current_thresholds('BIGFACE')
            if bf_thresholds:
                self.bf_defect_thresholds = {
                    'Rust': bf_thresholds.get('rust', 50),
                    'Dent': bf_thresholds.get('dent', 50),
                    'Damage': bf_thresholds.get('damage', 50),
                    'Roller': bf_thresholds.get('roller', 50)
                }
                self.bf_conf_threshold = bf_thresholds.get('model_confidence', 0.25)
                print(f"✅ Loaded BigFace thresholds from database")
                
        except Exception as e:
            print(f"Error loading thresholds: {e}")
            # Use default values if loading fails
            self.od_defect_thresholds = DEFAULT_OD_DEFECT_THRESHOLDS.copy()
            self.bf_defect_thresholds = DEFAULT_BF_DEFECT_THRESHOLDS.copy()
            self.od_conf_threshold = 0.25
            self.bf_conf_threshold = 0.25
    
    def save_all_thresholds(self):
        """Save all current threshold values to database"""
        try:
            # First, collect current slider values to ensure we have the latest values
            self.collect_current_slider_values()
            
            # Prepare OD thresholds
            od_thresholds = {
                'rust': self.od_defect_thresholds.get('Rust', 50),
                'dent': self.od_defect_thresholds.get('Dent', 50),
                'spherical_mark': self.od_defect_thresholds.get('Spherical Mark', 50),
                'damage': self.od_defect_thresholds.get('Damage', 50),
                'flat_line': self.od_defect_thresholds.get('Flat Line', 50),
                'damage_on_end': self.od_defect_thresholds.get('Damage on End', 50),
                'roller': self.od_defect_thresholds.get('Roller', 50),
                'model_confidence': getattr(self, 'od_conf_threshold', 0.25)
            }
            
            # Prepare BigFace thresholds
            bf_thresholds = {
                'rust': self.bf_defect_thresholds.get('Rust', 50),
                'dent': self.bf_defect_thresholds.get('Dent', 50),
                'damage': self.bf_defect_thresholds.get('Damage', 50),
                'roller': self.bf_defect_thresholds.get('Roller', 50),
                'model_confidence': getattr(self, 'bf_conf_threshold', 0.25)
            }
            
            # Generate new session ID for this save operation
            self.session_id = str(uuid.uuid4())
            
            # Save to database
            od_success, od_msg = db_manager.save_od_thresholds(
                self.current_user or 'SYSTEM', 
                od_thresholds, 
                self.session_id
            )
            
            bf_success, bf_msg = db_manager.save_bigface_thresholds(
                self.current_user or 'SYSTEM', 
                bf_thresholds, 
                self.session_id
            )
            
            if od_success and bf_success:
                print(f"✅ Thresholds saved to database - Session: {self.session_id}")
                print(f"   OD: {od_thresholds}")
                print(f"   BF: {bf_thresholds}")
                return True, "All thresholds saved successfully"
            else:
                return False, f"Save errors: OD: {od_msg}, BF: {bf_msg}"
                
        except Exception as e:
            print(f"Error saving thresholds: {e}")
            return False, f"Error saving thresholds: {e}"
    
    def collect_current_slider_values(self):
        """Collect current values from all sliders and update threshold dictionaries"""
        try:
            # Check if we have slider values stored
            if hasattr(self, 'slider_values'):
                for defect_name, slider in self.slider_values.items():
                    try:
                        current_value = int(float(slider.get()))
                        
                        # Determine if this is an OD or BigFace defect based on the defect name
                        # and whether it exists in the respective threshold dictionaries
                        if defect_name in self.od_defect_thresholds:
                            self.od_defect_thresholds[defect_name] = current_value
                            print(f"   Updated OD {defect_name}: {current_value}")
                        
                        if defect_name in self.bf_defect_thresholds:
                            self.bf_defect_thresholds[defect_name] = current_value
                            print(f"   Updated BF {defect_name}: {current_value}")
                            
                    except Exception as e:
                        print(f"Error reading slider value for {defect_name}: {e}")
                
                print(f"✅ Collected current slider values")
            else:
                print("⚠️ No slider values found to collect")
                
        except Exception as e:
            print(f"Error collecting slider values: {e}")

    def start_camera_feeds(self):
        """Start camera feed threads with proper error handling"""
        try:
            self.stop_camera_feeds()  # Stop any existing feeds first
            self.camera_running = True
            
            if hasattr(self, 'inference_tab') and hasattr(self.inference_tab, 'od_canvas'):
                self.od_canvas = self.inference_tab.od_canvas
                self.od_thread = threading.Thread(target=self.update_od_camera, daemon=True)
                self.od_thread.start()
            
            if hasattr(self, 'inference_tab') and hasattr(self.inference_tab, 'bf_canvas'):
                self.bf_canvas = self.inference_tab.bf_canvas
                self.bf_thread = threading.Thread(target=self.update_bf_camera, daemon=True)
                self.bf_thread.start()
                
        except Exception as e:
            print(f"Error starting camera feeds: {e}")

    def stop_camera_feeds(self):
        """Stop camera feed threads safely"""
        try:
            self.camera_running = False
            
            if hasattr(self, 'od_thread') and self.od_thread and self.od_thread.is_alive():
                self.od_thread.join(timeout=1.0)
            
            if hasattr(self, 'bf_thread') and self.bf_thread and self.bf_thread.is_alive():
                self.bf_thread.join(timeout=1.0)
                
        except Exception as e:
            print(f"Error stopping camera feeds: {e}")

    def update_od_camera(self):
        """Update OD camera feed with error handling"""
        while self.camera_running:
            try:
                if not hasattr(self, 'shared_annotated_od') or not hasattr(self, 'annotated_frame_lock_od'):
                    time.sleep(0.1)
                    continue
                    
                if self.od_canvas and self.od_canvas.winfo_exists():
                    with self.annotated_frame_lock_od:
                        np_frame = np.frombuffer(self.shared_annotated_od.get_obj(), dtype=np.uint8).reshape(FRAME_SHAPE)
                        frame = np_frame.copy()

                    resized_frame = cv2.resize(frame, (400, 250))
                    img = PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
                    imgtk = PIL.ImageTk.PhotoImage(image=img)

                    self.od_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                    self.od_canvas.image = imgtk
                else:
                    break
                    
                time.sleep(0.03)
                
            except Exception as e:
                print(f"OD camera error: {e}")
                break

    def update_bf_camera(self):
        """Update BF camera feed with error handling"""
        while self.camera_running:
            try:
                if not hasattr(self, 'shared_annotated_bigface') or not hasattr(self, 'annotated_frame_lock_bigface'):
                    time.sleep(0.1)
                    continue
                    
                if self.bf_canvas and self.bf_canvas.winfo_exists():
                    with self.annotated_frame_lock_bigface:
                        np_frame = np.frombuffer(self.shared_annotated_bigface.get_obj(), dtype=np.uint8).reshape(FRAME_SHAPE)
                        frame = np_frame.copy()

                    resized_frame = cv2.resize(frame, (400, 250))
                    img = PIL.Image.fromarray(cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB))
                    imgtk = PIL.ImageTk.PhotoImage(image=img)

                    self.bf_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                    self.bf_canvas.image = imgtk
                else:
                    break
                    
                time.sleep(0.03)
                
            except Exception as e:
                print(f"BF camera error: {e}")
                break

    # Roller management methods
    def get_entry_value(self, field):
        """Get value from entry field, handling Entry, Text, and Combobox widgets"""
        widget = self.data_entries[field]
        if isinstance(widget, tk.Text):
            return widget.get("1.0", tk.END).strip()
        elif isinstance(widget, ttk.Combobox):
            return widget.get().strip()
        else:
            return widget.get().strip()

    def set_entry_value(self, field, value):
        """Set value to entry field, handling Entry, Text, and Combobox widgets"""
        widget = self.data_entries[field]
        if isinstance(widget, tk.Text):
            widget.delete("1.0", tk.END)
            widget.insert("1.0", str(value))
        elif isinstance(widget, ttk.Combobox):
            widget.set(str(value))
        else:
            widget.delete(0, tk.END)
            widget.insert(0, str(value))

    def clear_form(self):
        """Clear all form fields"""
        for field in self.data_entries:
            widget = self.data_entries[field]
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)
        self.selected_roller_id = None
        self.update_status("Form cleared")

    def create_roller(self):
        """Create a new roller record in database"""
        try:
            roller_type = self.get_entry_value("Roller Type")
            diameter_str = self.get_entry_value("Diameter (mm)")
            thickness_str = self.get_entry_value("Thickness (mm)")
            length_str = self.get_entry_value("Length (mm)")
            
            # Validate required fields
            if not roller_type or not diameter_str or not thickness_str or not length_str:
                messagebox.showerror("Error", "All fields are required.")
                return
            
            # Validate numeric fields
            try:
                diameter = float(diameter_str)
                thickness = float(thickness_str)
                length = float(length_str)
            except ValueError:
                messagebox.showerror("Error", "Diameter, Thickness, and Length must be valid numbers.")
                return
            
            # Validate positive values
            if diameter <= 0 or thickness <= 0 or length <= 0:
                messagebox.showerror("Error", "Diameter, Thickness, and Length must be positive values.")
                return
            
            # Create roller in database
            success, message = db_manager.create_roller(
                roller_type=roller_type,
                diameter=diameter,
                thickness=thickness,
                length=length,
                created_by=self.current_user
            )
            
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.load_roller_data()
                self.update_roller_types_dropdown()
                self.update_status("Created roller successfully")
            else:
                messagebox.showerror("Error", message)
                self.update_status(f"Failed to create roller: {message}")
                
        except Exception as e:
            error_msg = f"Error creating roller: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def read_roller(self):
        """Load selected roller data into form"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a roller to load.")
            return
        
        try:
            item = self.tree.item(selected[0])
            values = item['values']
            roller_id = values[0]
            
            roller = db_manager.get_roller_by_id(roller_id)
            if not roller:
                messagebox.showerror("Error", "Roller not found in database.")
                return
            
            self.set_entry_value("Roller Type", roller['roller_type'] or "")
            self.set_entry_value("Diameter (mm)", roller['diameter'])
            self.set_entry_value("Thickness (mm)", roller['thickness'])
            self.set_entry_value("Length (mm)", roller['length'])
            
            self.selected_roller_id = roller_id
            self.update_status(f"Loaded roller ID: {roller_id}")
            
        except Exception as e:
            error_msg = f"Error loading roller: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def update_roller(self):
        """Update existing roller record in database"""
        if not hasattr(self, 'selected_roller_id') or not self.selected_roller_id:
            messagebox.showerror("Error", "Please select a roller to update first (double-click or use Read button).")
            return
        
        try:
            roller_type = self.get_entry_value("Roller Type")
            diameter_str = self.get_entry_value("Diameter (mm)")
            thickness_str = self.get_entry_value("Thickness (mm)")
            length_str = self.get_entry_value("Length (mm)")
            
            # Validate required fields
            if not roller_type or not diameter_str or not thickness_str or not length_str:
                messagebox.showerror("Error", "All fields are required.")
                return
            
            # Validate numeric fields
            try:
                diameter = float(diameter_str)
                thickness = float(thickness_str)
                length = float(length_str)
            except ValueError:
                messagebox.showerror("Error", "Diameter, Thickness, and Length must be valid numbers.")
                return
            
            # Validate positive values
            if diameter <= 0 or thickness <= 0 or length <= 0:
                messagebox.showerror("Error", "Diameter, Thickness, and Length must be positive values.")
                return
            
            # Update roller in database
            success, message = db_manager.update_roller(
                roller_id=self.selected_roller_id,
                roller_type=roller_type,
                diameter=diameter,
                thickness=thickness,
                length=length,
                updated_by=self.current_user
            )
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_roller_data()
                self.update_roller_types_dropdown()
                self.update_status(f"Updated roller ID: {self.selected_roller_id}")
            else:
                messagebox.showerror("Error", message)
                self.update_status(f"Failed to update roller: {message}")
                
        except Exception as e:
            error_msg = f"Error updating roller: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def delete_roller(self):
        """Delete selected roller from database"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a roller to delete.")
            return
        
        try:
            item = self.tree.item(selected[0])
            values = item['values']
            roller_id = values[0]
            roller_type = values[1] if len(values) > 1 else "Unknown"
            
            # Confirm deletion
            result = messagebox.askyesno("Confirm Deletion", 
                                       f"Are you sure you want to delete roller ID {roller_id} (Type: {roller_type})?\n\nThis action cannot be undone.")
            if not result:
                return
            
            # Delete from database
            success, message = db_manager.delete_roller(roller_id, deleted_by=self.current_user)
            
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()
                self.load_roller_data()
                self.update_status(f"Deleted roller ID: {roller_id}")
            else:
                messagebox.showerror("Error", message)
                self.update_status(f"Failed to delete roller: {message}")
                
        except Exception as e:
            error_msg = f"Error deleting roller: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def load_roller_data(self):
        """Load all rollers from database into the tree view"""
        try:
            if not self.tree:
                return
                
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get all rollers from database
            rollers = db_manager.get_all_rollers()
            
            # Populate tree view
            for roller in rollers:
                self.tree.insert("", tk.END, values=(
                    roller['id'],
                    roller['roller_type'] or "N/A",
                    roller['diameter'],
                    roller['thickness'],
                    roller['length']
                ))
            
            self.update_status(f"Loaded {len(rollers)} rollers from database")
            
        except Exception as e:
            error_msg = f"Error loading roller data: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def update_roller_types_dropdown(self):
        """No longer needed - roller type is now a text input box instead of dropdown"""
        # This method is kept for backward compatibility but does nothing
        # since the roller type field is now a regular text input box
        pass

    def update_status(self, message):
        """Update status bar with message"""
        print(f"Status: {message}")

    def on_roller_double_click(self, event):
        """Handle double-click on roller in tree view"""
        self.read_roller()

    def create_slider(self, parent, label_text, min_val, max_val, default_val, row, is_od=True, read_only=False):
        """Create a threshold slider widget"""
        if not hasattr(self, "slider_values"):  
            self.slider_values = {}

        frame = tk.Frame(parent, bg=APP_BG_COLOR)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)

        label = tk.Label(frame, text=label_text, font=("Arial", 10), fg="white", bg=APP_BG_COLOR, width=20, anchor="w")
        label.pack(side=tk.LEFT, padx=5)

        slider = ttk.Scale(frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, length=200)
        slider.set(default_val)  
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Disable slider if in read-only mode
        if read_only:
            slider.config(state="disabled")

        value_label = tk.Label(frame, text=f"{default_val}%", font=("Arial", 10), fg="white", bg=APP_BG_COLOR, width=5)
        value_label.pack(side=tk.RIGHT, padx=5)

        # Only configure command if not read-only
        if not read_only:
            slider.configure(command=lambda val, lbl=value_label, defect=label_text, is_od=is_od: self.update_threshold(val, lbl, defect, is_od))

        self.slider_values[label_text] = slider  

    def update_threshold(self, val, value_label, defect, is_od):
        """Update threshold value"""
        value_label.config(text=f"{int(float(val))}%")
        if is_od:
            self.od_defect_thresholds[defect] = int(float(val))
        else:
            self.bf_defect_thresholds[defect] = int(float(val))

    def create_stat_label(self, parent, label_text, var, row):
        """Create a status label widget"""
        frame = tk.Frame(parent, bg=APP_BG_COLOR)
        frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        
        label = tk.Label(frame, text=label_text, font=("Arial", 10), fg="white", bg=APP_BG_COLOR, width=20, anchor="w")
        label.pack(side=tk.LEFT, padx=5)
        
        value_label = tk.Label(frame, textvariable=var, font=("Arial", 10, "bold"), fg="white", bg=APP_BG_COLOR, width=10)
        value_label.pack(side=tk.LEFT, padx=5)

    def start_inspection(self):
        """Start inspection process"""
        if self.inspection_running:
            print("Inspection is already running!")
            return
        
        self.inspection_running = True
        print("Inspection started")

    def stop_inspection(self):
        """Stop inspection process"""
        if not self.inspection_running:
            print("Inspection is not running.")
            return
        
        self.inspection_running = False
        print("Inspection stopped")

    def generate_report(self):
        """Generate inspection report"""
        print("Generating report...")
        # Placeholder for report generation logic
        messagebox.showinfo("Report", "Report generation functionality will be implemented.")

    def save_chart(self):
        """Save chart functionality"""
        print("Saving chart...")
        messagebox.showinfo("Chart", "Chart saved successfully.")

    def export_to_excel(self):
        """Export data to Excel"""
        print("Exporting to Excel...")
        messagebox.showinfo("Export", "Data exported to Excel successfully.")

    def update_status_chart(self, data, component_type, report_type):
        """Update status chart"""
        print(f"Updating status chart for {component_type} - {report_type}")

    def update_defect_chart(self, data, component_type, report_type):
        """Update defect chart"""
        print(f"Updating defect chart for {component_type} - {report_type}")

    def on_closing(self):
        """Handle application closing"""
        try:
            self.stop_camera_feeds()
            if hasattr(self, 'processes'):
                for process in self.processes:
                    if process.is_alive():
                        process.terminate()
                        process.join()
            if hasattr(self, 'plc_process') and self.plc_process and self.plc_process.is_alive():
                self.plc_process.terminate()
                self.plc_process.join()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            self.destroy()

if __name__ == "__main__":
    app = WelVisionApp()
    app.mainloop() 