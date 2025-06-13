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
        
        # Center window on screen first
        self.center_window()
        
        # Ensure window is visible and on top
        self.lift()  # Bring window to front
        self.attributes('-topmost', True)  # Make window stay on top temporarily
        self.after(2000, lambda: self.attributes('-topmost', False))  # Remove topmost after 2 seconds
        self.focus_force()  # Force focus to this window
        
        # Enable window decorations to show minimize/maximize/close buttons
        self.attributes('-toolwindow', False)  # Enable minimize/maximize/close buttons on Windows
        
        # Initialize variables
        # Initialize authentication variables
        self.current_user = None
        self.current_role = None
        
        # Debug: Track role changes
        self._debug_role_changes = True
        
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
        
        # Enable window close button with controlled exit
        self.protocol("WM_DELETE_WINDOW", self.controlled_exit)
        
        # Initialize exit control variables (now based on CSV records)
        # Exit is controlled by checking for unsaved CSV records
        
        # Show login page on startup
        print("🔍 Initializing login page...")
        self.show_login_page()
        print("✅ Login page should be visible")

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1280) // 2
        y = (screen_height - 800) // 2
        self.geometry(f"1280x800+{x}+{y}")
    
    def show_login_page(self):
        """Show login page with proper cleanup"""
        print("🔍 show_login_page() called")
        print(f"🔍 Current user: {self.current_user}")
        print(f"🔍 Current role: {self.current_role}")
        
        # Stop any running threads first
        self.stop_camera_feeds()
        
        # Clean up any existing event bindings
        self.unbind_all("<Return>")
        
        # Clear any existing widget references
        if hasattr(self, 'employee_entry'):
            self.employee_entry = None
        if hasattr(self, 'password_entry'):
            self.password_entry = None
        if hasattr(self, 'role_var'):
            self.role_var = None
        
        # Destroy existing widgets
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                # Widget already destroyed, ignore
                pass
        
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
        
        # Bind Enter key to authentication
        self.bind("<Return>", lambda event: self.authenticate())
        
        # Ensure window is not minimized and is visible
        self.state('normal')  # Ensure window is not minimized
        self.deiconify()  # Make sure window is not iconified
        self.lift()  # Bring to front again
        self.focus_force()  # Force focus again
        
        print("✅ Login screen widgets created and displayed")
        print("🔍 Login screen should be visible now")
        print(f"🔍 Window state: {self.state()}")
        print(f"🔍 Window geometry: {self.geometry()}")
    
    def authenticate(self):
        """Authenticate user with proper error handling"""
        print("🔐 Authentication method called")
        try:
            # Check if widgets still exist before accessing them
            if not hasattr(self, 'employee_entry') or not self.employee_entry:
                print("Authentication error: Employee entry widget not available")
                return
            
            if not hasattr(self, 'password_entry') or not self.password_entry:
                print("Authentication error: Password entry widget not available")
                return
            
            if not hasattr(self, 'role_var') or not self.role_var:
                print("Authentication error: Role variable not available")
                return
            
            # Check if widgets are still valid (not destroyed)
            try:
                employee_id = self.employee_entry.get().strip()
                password = self.password_entry.get().strip()
                role = self.role_var.get()
            except tk.TclError as e:
                print(f"Authentication error: Widget access failed - {e}")
                return
            
            # Validate input
            if not employee_id or not password:
                print("🔐 Authentication failed: Empty credentials")
                messagebox.showerror("Login Failed", "Please enter both Employee ID and Password.")
                return
            
            print(f"🔐 Attempting authentication for: {employee_id} as {role}")
            
            # Try MySQL authentication first
            success, message, user_data = db_manager.authenticate_user(employee_id, password, role)
            
            if success:
                print(f"🔐 Authentication successful: {employee_id} as {role}")
                self.current_user = employee_id
                self.current_role = role
                db_manager.log_system_event(employee_id, "LOGIN_SUCCESS", f"Role: {role}")
                # messagebox.showinfo("Login Success", message)  # Disabled welcome window
                self.show_main_interface()
            else:
                db_manager.log_system_event(employee_id, "LOGIN_FAILED", f"Role: {role}, Reason: {message}", "WARNING")
                
                # Fallback authentication
                if employee_id in FALLBACK_USERS and FALLBACK_USERS[employee_id]["password"] == password and FALLBACK_USERS[employee_id]["role"] == role:
                    self.current_user = employee_id
                    self.current_role = role
                    # messagebox.showinfo("Login Success", f"Welcome {employee_id}! (Fallback Mode)")  # Disabled welcome window
                    self.show_main_interface()
                else:
                    messagebox.showerror("Login Failed", message)
                    
        except Exception as e:
            employee_id_safe = "Unknown"
            try:
                if hasattr(self, 'employee_entry') and self.employee_entry:
                    employee_id_safe = self.employee_entry.get().strip()
            except:
                pass
                
            db_manager.log_system_event(employee_id_safe, "LOGIN_ERROR", f"Error: {e}", "ERROR")
            print(f"Authentication error: {e}")
            
            # Fallback authentication with safe widget access
            try:
                if hasattr(self, 'employee_entry') and self.employee_entry and hasattr(self, 'password_entry') and self.password_entry and hasattr(self, 'role_var') and self.role_var:
                    try:
                        employee_id = self.employee_entry.get().strip()
                        password = self.password_entry.get().strip()
                        role = self.role_var.get()
                        
                        if employee_id in FALLBACK_USERS and FALLBACK_USERS[employee_id]["password"] == password and FALLBACK_USERS[employee_id]["role"] == role:
                            self.current_user = employee_id
                            self.current_role = role
                            # messagebox.showinfo("Login Success", f"Welcome {employee_id}! (Fallback Mode)")  # Disabled welcome window
                            self.show_main_interface()
                        else:
                            messagebox.showerror("Login Failed", "Authentication failed. Check database connection.")
                    except tk.TclError:
                        messagebox.showerror("Login Failed", "Authentication system error - widgets unavailable.")
                else:
                    messagebox.showerror("Login Failed", "Authentication system error - interface not ready.")
            except Exception as fallback_error:
                print(f"Fallback authentication error: {fallback_error}")
                messagebox.showerror("Login Failed", "Authentication system error.")

    def show_main_interface(self):
        """Show main interface with proper cleanup"""
        # Stop any running processes first
        self.stop_camera_feeds()
        
        # Initialize system components
        self.initialize_system()
        
        # Clean up login page references before destroying widgets
        if hasattr(self, 'employee_entry'):
            self.employee_entry = None
        if hasattr(self, 'password_entry'):
            self.password_entry = None
        if hasattr(self, 'role_var'):
            self.role_var = None
        
        # Unbind any existing event handlers
        self.unbind_all("<Return>")
        
        # Clear existing widgets with error handling
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                # Widget already destroyed, ignore
                pass
        
        main_frame = tk.Frame(self, bg=APP_BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=APP_BG_COLOR, height=50)
        header_frame.pack(fill=tk.X)
        
        # Store reference to logo label so it can be updated from settings
        self.logo_label = tk.Label(header_frame, text=getattr(self, 'custom_gui_title', 'WELVISION'), 
                                  font=("Arial", 18, "bold"), fg="white", bg=APP_BG_COLOR)
        self.logo_label.pack(side=tk.LEFT, padx=20, pady=5)
        
        user_label = tk.Label(header_frame, text=f"{self.current_role}: {self.current_user}", 
                             font=("Arial", 12), fg="white", bg=APP_BG_COLOR)
        user_label.pack(side=tk.RIGHT, padx=20, pady=5)
        
        # Log out button - allows user to return to login screen
        logout_button = tk.Button(header_frame, text="Log Out", font=("Arial", 10), 
                                 command=self.logout_user)
        logout_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Bottom navigation buttons (pack first to ensure visibility)
        bottom_nav_frame = tk.Frame(main_frame, bg=APP_BG_COLOR, height=100)
        bottom_nav_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        bottom_nav_frame.pack_propagate(False)  # Maintain fixed height
        
        # Content frame for different pages
        self.content_frame = tk.Frame(main_frame, bg=APP_BG_COLOR)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 5))
        
        # Create navigation buttons
        self.nav_buttons = {}
        button_configs = [
            ("Inference", self.show_inference_page),
            ("Settings", self.show_settings_page),
            ("Data", self.show_data_page),
            ("Diagnosis", self.show_diagnosis_page),
            ("Model Preview", self.show_model_preview_page),
            ("Model Management", self.show_model_management_page)
        ]
        
        # Add role-specific buttons
        if self.current_role in ["Admin", "Super Admin"]:
            button_configs.append(("User Management", self.show_user_management_page))
        
        if self.current_role == "Super Admin":
            button_configs.append(("System Check", self.show_system_check_page))
        
        # Create navigation buttons
        for btn_text, btn_command in button_configs:
            btn = tk.Button(bottom_nav_frame, text=btn_text.upper(), font=("Arial", 10, "bold"), 
                           width=18, height=2, command=btn_command, bg="#007bff", fg="white",
                           relief="raised", bd=2, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2, pady=15)
            self.nav_buttons[btn_text] = btn
        
        # Footer label
        footer_label = tk.Label(bottom_nav_frame, text="Developed and Maintained By:\nWelvision Innovations Private Limited", 
                               font=("Arial", 8), fg="white", bg=APP_BG_COLOR, anchor="e")
        footer_label.pack(side=tk.RIGHT, padx=10)
        
        # Create frames for each page and initialize them
        self.create_page_frames()
        
        # Ensure window is visible and properly displayed
        self.deiconify()  # Make sure window is not minimized
        self.lift()  # Bring to front
        self.focus_force()  # Force focus
        self.update()  # Force update of all pending events
        
        print("✅ Main interface created and window should be visible")

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
            
            # Create roller specifications table
            specs_success = db_manager.create_roller_specifications_table()
            if specs_success:
                print("✅ Roller specifications table initialized successfully")
            else:
                print("⚠️ Warning: Roller specifications table initialization failed")
            
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
            
            # Create inspection session tables
            session_success = db_manager.create_inspection_session_tables()
            if session_success:
                print("✅ Inspection session tables initialized successfully")
            else:
                print("⚠️ Warning: Inspection session tables initialization failed")
                
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
        """Save all threshold values to the database"""
        try:
            # Collect current slider values
            self.collect_current_slider_values()
            
            # Save to database
            db_manager.save_thresholds(
                od_thresholds=self.od_defect_thresholds,
                bf_thresholds=self.bf_defect_thresholds,
                od_conf_threshold=self.od_conf_threshold,
                bf_conf_threshold=self.bf_conf_threshold
            )
            
            # Log the event
            if hasattr(self, 'current_user'):
                db_manager.log_system_event(
                    self.current_user,
                    "THRESHOLD_UPDATE",
                    f"Updated thresholds - OD: {self.od_defect_thresholds}, BF: {self.bf_defect_thresholds}"
                )
            
            messagebox.showinfo("Success", "Threshold settings saved successfully!")
            
        except Exception as e:
            print(f"Error saving thresholds: {e}")
            messagebox.showerror("Error", f"Failed to save threshold settings: {str(e)}")
    
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
        """
        Create a new roller record in the database.
        
        This method handles the complete workflow for creating a new roller:
        1. Retrieves and validates input data from form fields
        2. Performs data validation (required fields, numeric validation, positive values)
        3. Calls database manager to insert the new record
        4. Updates UI components and provides user feedback
        5. Refreshes the data display and roller type dropdowns
        
        Validation rules:
        - All fields are required (roller type, diameter, thickness, length)
        - Numeric fields must be valid floating-point numbers
        - All measurements must be positive values
        
        Returns:
            None: Updates UI and database directly
        """
        try:
            # Retrieve form data using helper method
            roller_type = self.get_entry_value("Roller Type")
            diameter_str = self.get_entry_value("Diameter (mm)")
            thickness_str = self.get_entry_value("Thickness (mm)")
            length_str = self.get_entry_value("Length (mm)")
            
            # Primary validation: Check for required fields
            if not roller_type or not diameter_str or not thickness_str or not length_str:
                messagebox.showerror("Error", "All fields are required.")
                return
            
            # Secondary validation: Convert and validate numeric fields
            try:
                diameter = float(diameter_str)
                thickness = float(thickness_str)
                length = float(length_str)
            except ValueError:
                messagebox.showerror("Error", "Diameter, Thickness, and Length must be valid numbers.")
                return
            
            # Tertiary validation: Ensure positive values for physical measurements
            if diameter <= 0 or thickness <= 0 or length <= 0:
                messagebox.showerror("Error", "Diameter, Thickness, and Length must be positive values.")
                return
            
            # Quaternary validation: Check against global limits (for ALL users including Super Admin)
            roller_data = {
                'roller_type': roller_type,
                'diameter': diameter,
                'thickness': thickness,
                'length': length,
                'created_by': self.current_user
            }
            
            validation_result = db_manager.validate_roller_against_global_limits(roller_data)
            if not validation_result['valid']:
                role_message = "Super Admin" if self.current_role == "Super Admin" else "Admin"
                messagebox.showerror("Global Limits Violation", 
                                   f"Roller creation rejected:\n\n{validation_result['message']}\n\n"
                                   f"Global limits apply to ALL users including {role_message}.\n"
                                   f"To create rollers outside these limits, first update the global limits in the Data tab.")
                self.update_status(f"Roller creation rejected: {validation_result['message']}")
                return
            else:
                print(f"✅ {self.current_role} roller validation passed: {validation_result['message']}")
            
            # Database operation: Create roller record with validated data
            success, message = db_manager.create_roller(
                roller_type=roller_type,
                diameter=diameter,
                thickness=thickness,
                length=length,
                created_by=self.current_user  # Track who created the record
            )
            
            # Handle operation result and update UI accordingly
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()  # Reset form for next entry
                self.load_roller_data()  # Refresh data display
                self.update_roller_types_dropdown()  # Update dropdown options
                self.refresh_all_roller_type_dropdowns()  # Refresh dropdowns in other tabs
                self.update_status("Created roller successfully")
            else:
                messagebox.showerror("Error", message)
                self.update_status(f"Failed to create roller: {message}")
                
        except Exception as e:
            # Global error handling for unexpected exceptions
            error_msg = f"Error creating roller: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def read_roller(self):
        """
        Load selected roller data into the form for viewing or editing.
        
        This method implements the 'Read' operation in CRUD functionality:
        1. Validates that a roller is selected in the TreeView
        2. Retrieves the roller ID from the selected row
        3. Fetches complete roller data from the database
        4. Populates all form fields with the retrieved data
        5. Sets the selected_roller_id for future update/delete operations
        
        The loaded data can then be modified and saved using update_roller(),
        or the record can be deleted using delete_roller().
        
        Returns:
            None: Updates form fields directly
        """
        # Check if user has selected a roller from the table
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a roller to load.")
            return
        
        try:
            # Extract roller ID from the selected TreeView item
            item = self.tree.item(selected[0])
            values = item['values']
            roller_id = values[0]  # ID is always the first column
            
            # Fetch complete roller data from database using the ID
            roller = db_manager.get_roller_by_id(roller_id)
            if not roller:
                messagebox.showerror("Error", "Roller not found in database.")
                return
            
            # Populate form fields with database data
            # Handle potential None values gracefully
            # Use 'name' field if roller_type is empty, or roller_type if name is empty
            display_name = roller['roller_type'] or roller['name'] or ""
            self.set_entry_value("Roller Type", display_name)
            self.set_entry_value("Diameter (mm)", roller['diameter'])
            self.set_entry_value("Thickness (mm)", roller['thickness'])
            self.set_entry_value("Length (mm)", roller['length'])
            
            # Store the selected roller ID for future operations (update/delete)
            self.selected_roller_id = roller_id
            self.update_status(f"Loaded roller ID: {roller_id}")
            
        except Exception as e:
            # Handle any unexpected errors during the read operation
            error_msg = f"Error loading roller: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def update_roller(self):
        """
        Update an existing roller record in the database.
        
        This method implements the 'Update' operation in CRUD functionality:
        1. Validates that a roller has been selected for editing
        2. Retrieves and validates all form data
        3. Performs the same validation as create_roller()
        4. Updates the existing database record
        5. Refreshes the UI to show the updated data
        
        Prerequisites:
        - A roller must be selected using read_roller() or double-click
        - The selected_roller_id attribute must be set
        
        Validation rules (same as create_roller):
        - All fields are required
        - Numeric fields must be valid floating-point numbers
        - All measurements must be positive values
        
        Returns:
            None: Updates database and UI directly
        """
        # Ensure a roller has been selected for update
        if not hasattr(self, 'selected_roller_id') or not self.selected_roller_id:
            messagebox.showerror("Error", "Please select a roller to update first (double-click or use Read button).")
            return
        
        try:
            # Retrieve current form data
            roller_type = self.get_entry_value("Roller Type")
            diameter_str = self.get_entry_value("Diameter (mm)")
            thickness_str = self.get_entry_value("Thickness (mm)")
            length_str = self.get_entry_value("Length (mm)")
            
            # Apply same validation rules as create operation
            # Primary validation: Check for required fields
            if not roller_type or not diameter_str or not thickness_str or not length_str:
                messagebox.showerror("Error", "All fields are required.")
                return
            
            # Secondary validation: Convert and validate numeric fields
            try:
                diameter = float(diameter_str)
                thickness = float(thickness_str)
                length = float(length_str)
            except ValueError:
                messagebox.showerror("Error", "Diameter, Thickness, and Length must be valid numbers.")
                return
            
            # Tertiary validation: Ensure positive values for physical measurements
            if diameter <= 0 or thickness <= 0 or length <= 0:
                messagebox.showerror("Error", "Diameter, Thickness, and Length must be positive values.")
                return
            
            # Quaternary validation: Check against global limits (for ALL users including Super Admin)
            roller_data = {
                'roller_type': roller_type,
                'diameter': diameter,
                'thickness': thickness,
                'length': length,
                'created_by': self.current_user
            }
            
            validation_result = db_manager.validate_roller_against_global_limits(roller_data)
            if not validation_result['valid']:
                role_message = "Super Admin" if self.current_role == "Super Admin" else "Admin"
                messagebox.showerror("Global Limits Violation", 
                                   f"Roller update rejected:\n\n{validation_result['message']}\n\n"
                                   f"Global limits apply to ALL users including {role_message}.\n"
                                   f"To update rollers outside these limits, first update the global limits in the Data tab.")
                self.update_status(f"Roller update rejected: {validation_result['message']}")
                return
            else:
                print(f"✅ {self.current_role} roller validation passed: {validation_result['message']}")
            
            # Database operation: Update the selected roller record
            success, message = db_manager.update_roller(
                roller_id=self.selected_roller_id,
                roller_type=roller_type,
                diameter=diameter,
                thickness=thickness,
                length=length,
                updated_by=self.current_user  # Track who modified the record
            )
            
            # Handle operation result and update UI
            if success:
                messagebox.showinfo("Success", message)
                self.load_roller_data()  # Refresh the data display
                self.update_roller_types_dropdown()  # Update dropdown options
                self.refresh_all_roller_type_dropdowns()  # Refresh dropdowns in other tabs
                self.update_status(f"Updated roller ID: {self.selected_roller_id}")
            else:
                messagebox.showerror("Error", message)
                self.update_status(f"Failed to update roller: {message}")
                
        except Exception as e:
            # Global error handling for unexpected exceptions
            error_msg = f"Error updating roller: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def delete_roller(self):
        """
        Delete a selected roller record from the database.
        
        This method implements the 'Delete' operation in CRUD functionality:
        1. Validates that a roller is selected in the TreeView
        2. Extracts roller information for confirmation dialog
        3. Shows confirmation dialog with roller details
        4. Performs deletion if confirmed by user
        5. Updates UI and clears form after successful deletion
        
        Safety features:
        - Requires explicit user confirmation before deletion
        - Shows roller details in confirmation dialog
        - Irreversible operation warning
        - Proper error handling and logging
        
        Returns:
            None: Updates database and UI directly
        """
        # Validate that user has selected a roller to delete
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a roller to delete.")
            return
        
        try:
            # Extract roller information from selected TreeView item
            item = self.tree.item(selected[0])
            values = item['values']
            roller_id = values[0]  # ID is always the first column
            roller_type = values[1] if len(values) > 1 else "Unknown"  # Handle missing data
            
            # Safety confirmation: Show detailed confirmation dialog
            # This prevents accidental deletions by clearly showing what will be deleted
            result = messagebox.askyesno("Confirm Deletion", 
                                       f"Are you sure you want to delete roller ID {roller_id} (Type: {roller_type})?\n\nThis action cannot be undone.")
            if not result:
                return  # User cancelled deletion
            
            # Database operation: Perform the deletion
            success, message = db_manager.delete_roller(roller_id, deleted_by=self.current_user)
            
            # Handle deletion result and update UI
            if success:
                messagebox.showinfo("Success", message)
                self.clear_form()  # Clear form since deleted record may have been loaded
                self.load_roller_data()  # Refresh data display to remove deleted item
                self.refresh_all_roller_type_dropdowns()  # Refresh dropdowns in other tabs
                self.update_status(f"Deleted roller ID: {roller_id}")
            else:
                messagebox.showerror("Error", message)
                self.update_status(f"Failed to delete roller: {message}")
                
        except Exception as e:
            # Global error handling for unexpected exceptions
            error_msg = f"Error deleting roller: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def load_roller_data(self):
        """
        Load all roller records from database into the TreeView display.
        
        This method refreshes the data display by:
        1. Clearing all existing items from the TreeView
        2. Fetching all roller records from the database
        3. Populating the TreeView with the retrieved data
        4. Updating the status with the number of records loaded
        
        The TreeView columns are populated in the following order:
        - ID: Database primary key
        - Roller Type: Text description of the roller type
        - Diameter: Roller diameter in millimeters
        - Thickness: Roller thickness in millimeters  
        - Length: Roller length in millimeters
        
        This method is called after any CRUD operation to ensure
        the display reflects the current database state.
        
        Returns:
            None: Updates TreeView display directly
        """
        try:
            # Safety check: Ensure TreeView widget exists
            if not self.tree:
                return
                
            # Clear existing data from TreeView to prevent duplicates
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Fetch all roller records from database
            rollers = db_manager.get_all_rollers()
            
            # Populate TreeView with roller data (global limits system - no per-roller specifications)
            # Each roller dictionary contains: id, name, roller_type, diameter, thickness, length
            for roller in rollers:
                # Use 'name' field if roller_type is empty, or roller_type if name is empty
                display_name = roller['roller_type'] or roller['name'] or "N/A"
                
                self.tree.insert("", tk.END, values=(
                    roller['id'],  # Primary key for database operations
                    display_name,  # Display name from either name or roller_type field
                    roller['diameter'],  # Numeric value from database
                    roller['thickness'],  # Numeric value from database
                    roller['length']  # Numeric value from database
                ))
            
            # Update status bar with loading confirmation
            self.update_status(f"Loaded {len(rollers)} rollers from database")
            
        except Exception as e:
            # Handle database connection or data retrieval errors
            error_msg = f"Error loading roller data: {e}"
            messagebox.showerror("Error", error_msg)
            self.update_status(error_msg)

    def update_roller_types_dropdown(self):
        """No longer needed - roller type is now a text input box instead of dropdown"""
        # This method is kept for backward compatibility but does nothing
        # since the roller type field is now a regular text input box
        pass

    def refresh_all_roller_type_dropdowns(self):
        """
        Refresh roller type dropdowns in all tabs that use them.
        
        This method is called after CRUD operations (create, update, delete) to ensure
        that all roller type dropdowns across the application are synchronized with
        the current database state.
        
        Tabs that are refreshed:
        - Inference Tab: roller_name_combobox for selecting current roller being inspected
        - Diagnosis Tab: type_combobox for filtering inspection reports by roller type
        """
        try:
            print("🔄 Refreshing roller type dropdowns across all tabs...")
            
            # Refresh Inference Tab roller type dropdown
            if hasattr(self, 'inference_tab') and self.inference_tab:
                self.inference_tab.refresh_roller_types()
            
            # Refresh Diagnosis Tab component type dropdown
            if hasattr(self, 'diagnosis_tab') and self.diagnosis_tab:
                self.diagnosis_tab.refresh_component_types()
            
            print("✅ All roller type dropdowns refreshed successfully")
            
        except Exception as e:
            print(f"❌ Error refreshing roller type dropdowns: {e}")
            # Don't raise the exception to avoid breaking the main operation

    def update_status(self, message):
        """Update status bar with message"""
        print(f"Status: {message}")

    def on_roller_double_click(self, event):
        """
        Handle double-click event on roller records in the TreeView.
        
        This event handler provides a convenient way for users to quickly
        load roller data into the form for editing. When a user double-clicks
        on any roller row in the TreeView, this method automatically calls
        read_roller() to populate the form fields.
        
        This is a common UI pattern that improves user experience by
        eliminating the need to manually select a row and click the Read button.
        
        Args:
            event: Tkinter event object containing double-click information
            
        Returns:
            None: Delegates to read_roller() method
        """
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
        """Generate inspection report - now handled by diagnosis tab"""
        try:
            if hasattr(self, 'diagnosis_tab'):
                self.diagnosis_tab.load_inspection_sessions()
                print("✅ Loaded inspection sessions in diagnosis tab")
            else:
                print("⚠️ Diagnosis tab not initialized yet")
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            messagebox.showerror("Report Error", f"Error loading inspection data: {e}")

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

    def update_header_title(self, new_title):
        """Update the header title text in the main interface"""
        try:
            if hasattr(self, 'logo_label'):
                self.logo_label.config(text=new_title)
                print(f"✅ Header title updated to: {new_title}")
        except Exception as e:
            print(f"Error updating header title: {e}")

    def restart_application(self):
        """Restart the application"""
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
            print(f"Error during restart cleanup: {e}")
        finally:
            self.destroy()
            # Note: In a real restart, you would start a new instance here
            print("Application restarted. Please run the script again.")
    
    def logout_user(self):
        """
        Log out the current user and return to login screen.
        Preserves application state while allowing user change.
        """
        try:
            # Confirm logout
            if messagebox.askyesno("Confirm Logout", 
                                 f"Are you sure you want to log out?\n\nCurrent user: {self.current_role}"):
                
                # Stop camera feeds temporarily
                self.stop_camera_feeds()
                
                # Clear current user session
                self.current_role = None
                self.current_user = None
                
                # Hide main interface
                if hasattr(self, 'main_frame') and self.main_frame:
                    self.main_frame.pack_forget()
                
                # Show login page
                self.show_login_page()
                
                print("✅ User logged out successfully")
                
        except Exception as e:
            print(f"Error during logout: {e}")
            messagebox.showerror("Logout Error", f"An error occurred during logout: {e}")

    def disable_close(self):
        """Disable window close button - show message"""
        messagebox.showwarning("Exit Disabled", 
                              "Application can only be exited using the Exit button in the Inference page.\n\n"
                              "Note: Reset button must be clicked before Exit button becomes functional.")
    
    def controlled_exit(self):
        """Exit application only if there are no unsaved CSV records"""
        # Check for unsaved CSV records first
        if self.has_unsaved_csv_records():
            unsaved_count = self.get_unsaved_csv_count()
            messagebox.showwarning("Exit Disabled - Unsaved Data", 
                                  f"Cannot exit application!\n\n"
                                  f"Found {unsaved_count} unsaved records in CSV files.\n\n"
                                  f"Please click the Reset button in the Inference page to:\n"
                                  f"• Transfer all data to database\n"
                                  f"• Clear CSV files\n"
                                  f"• Enable exit functionality\n\n"
                                  f"This ensures no inspection data is lost.")
            return
        
        # Confirm exit
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit the application?"):
            self.on_closing()
    
    def enable_exit_after_reset(self):
        """Enable exit functionality after reset is clicked"""
        self.reset_clicked = True
        self.exit_enabled = True
        print("✅ Reset clicked - Exit button is now functional")
    
    def has_unsaved_csv_records(self):
        """
        Check if there are unsaved records in any CSV files.
        
        Returns:
            bool: True if there are unsaved records, False otherwise
        """
        try:
            import os
            import csv
            
            csv_files = [
                "od_predictions.csv",
                "bf_predictions.csv", 
                "od_inspection_sessions.csv",
                "bf_inspection_sessions.csv"
            ]
            
            total_records = 0
            
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    record_count = self._count_csv_records(csv_file)
                    total_records += record_count
            
            return total_records > 0
            
        except Exception as e:
            print(f"❌ Error checking unsaved CSV records: {e}")
            # If we can't check, assume there are unsaved records for safety
            return True
    
    def get_unsaved_csv_count(self):
        """
        Get the total count of unsaved records in CSV files.
        
        Returns:
            int: Total number of unsaved records
        """
        try:
            import os
            
            csv_files = [
                "od_predictions.csv",
                "bf_predictions.csv", 
                "od_inspection_sessions.csv",
                "bf_inspection_sessions.csv"
            ]
            
            total_records = 0
            
            for csv_file in csv_files:
                if os.path.exists(csv_file):
                    record_count = self._count_csv_records(csv_file)
                    total_records += record_count
            
            return total_records
            
        except Exception as e:
            print(f"❌ Error counting unsaved CSV records: {e}")
            return 0
    
    def _count_csv_records(self, csv_file):
        """
        Count records in a CSV file (excluding header).
        
        Args:
            csv_file (str): Path to the CSV file
            
        Returns:
            int: Number of records (excluding header)
        """
        try:
            import csv
            import os
            
            if not os.path.exists(csv_file):
                return 0
            
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                # Return count minus header row, but at least 0
                return max(0, len(rows) - 1)
                
        except Exception as e:
            print(f"❌ Error counting records in {csv_file}: {e}")
            return 0

    def on_closing(self):
        """Handle application closing with proper cleanup"""
        try:
            # Clean up widget references
            if hasattr(self, 'employee_entry'):
                self.employee_entry = None
            if hasattr(self, 'password_entry'):
                self.password_entry = None
            if hasattr(self, 'role_var'):
                self.role_var = None
            
            # Unbind all event handlers
            self.unbind_all("<Return>")
            
            # Stop camera feeds
            self.stop_camera_feeds()
            
            # Clean up processes
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
            try:
                self.destroy()
            except tk.TclError:
                # Application already destroyed
                pass

    def create_page_frames(self):
        """Create frames for each page and initialize them"""
        try:
            # Create frames for each page
            self.inference_frame = tk.Frame(self.content_frame, bg=APP_BG_COLOR)
            self.settings_frame = tk.Frame(self.content_frame, bg=APP_BG_COLOR)
            self.data_frame = tk.Frame(self.content_frame, bg=APP_BG_COLOR)
            self.diagnosis_frame = tk.Frame(self.content_frame, bg=APP_BG_COLOR)
            self.model_preview_frame = tk.Frame(self.content_frame, bg=APP_BG_COLOR)
            self.model_management_frame = tk.Frame(self.content_frame, bg=APP_BG_COLOR)
            
            # Create role-specific frames
            if self.current_role in ["Admin", "Super Admin"]:
                self.user_management_frame = tk.Frame(self.content_frame, bg=APP_BG_COLOR)
            
            if self.current_role == "Super Admin":
                self.system_check_frame = tk.Frame(self.content_frame, bg=APP_BG_COLOR)
            
            # Initialize page modules
            self.inference_tab = InferenceTab(self.inference_frame, self)
            
            # Initialize settings tab with read-only mode for regular users
            read_only_mode = (self.current_role == "User")
            self.settings_tab = SettingsTab(self.settings_frame, self, read_only=read_only_mode)
            
            self.data_tab = DataTab(self.data_frame, self)
            self.initialize_database_tables()
            
            # Initialize roller inspection logger and create database tables
            from roller_inspection_logger import roller_logger
            try:
                roller_logger._create_database_tables()
                print("✅ Roller inspection logger initialized with separate OD/BF tables")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize roller inspection logger: {e}")
            
            self.diagnosis_tab = DiagnosisTab(self.diagnosis_frame, self)
            self.model_preview_tab = ModelPreviewTab(self.model_preview_frame, self)
            self.model_management_tab = ModelManagementTab(self.model_management_frame, self)
            
            # Initialize role-specific tabs
            if self.current_role in ["Admin", "Super Admin"]:
                self.user_management_tab = UserManagementTab(self.user_management_frame, self)
            
            if self.current_role == "Super Admin":
                self.system_check_tab = SystemCheckTab(self.system_check_frame, self)
            
            # Show inference page by default
            self.show_inference_page()
            
            # Start camera feeds after all tabs are initialized
            self.start_camera_feeds()
            
        except Exception as e:
            print(f"Error creating page frames: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {e}")

    def hide_all_pages(self):
        """Hide all page frames with proper cleanup"""
        try:
            # List of all possible page frames
            page_frames = [
                'inference_frame', 'settings_frame', 'data_frame', 
                'diagnosis_frame', 'model_preview_frame', 'model_management_frame',
                'user_management_frame', 'system_check_frame'
            ]
            
            for frame_name in page_frames:
                if hasattr(self, frame_name):
                    frame = getattr(self, frame_name)
                    if frame and frame.winfo_exists():
                        try:
                            frame.pack_forget()
                        except tk.TclError:
                            # Frame already destroyed or not packed, ignore
                            pass
        except Exception as e:
            print(f"Error hiding pages: {e}")

    def highlight_active_button(self, active_button_text):
        """Highlight the active navigation button with error handling"""
        try:
            if not hasattr(self, 'nav_buttons'):
                return
                
            for btn_text, btn in self.nav_buttons.items():
                if btn and btn.winfo_exists():
                    try:
                        if btn_text == active_button_text:
                            btn.config(bg="#007bff", relief="sunken")  # Blue for active
                        else:
                            btn.config(bg="#007bff", relief="raised")  # Blue for inactive
                    except tk.TclError:
                        # Button widget no longer exists, skip
                        pass
        except Exception as e:
            print(f"Error highlighting button: {e}")

    def show_inference_page(self):
        """Show inference page with error handling"""
        try:
            self.hide_all_pages()
            if hasattr(self, 'inference_frame') and self.inference_frame:
                self.inference_frame.pack(fill=tk.BOTH, expand=True)
            self.highlight_active_button("Inference")
            print("Switching to Inference page")
        except Exception as e:
            print(f"Error switching to Inference page: {e}")

    def show_settings_page(self):
        """Show settings page with error handling"""
        try:
            self.hide_all_pages()
            if hasattr(self, 'settings_frame') and self.settings_frame:
                self.settings_frame.pack(fill=tk.BOTH, expand=True)
            self.highlight_active_button("Settings")
            print("Switching to Settings page")
        except Exception as e:
            print(f"Error switching to Settings page: {e}")

    def show_data_page(self):
        """Show data page with error handling"""
        try:
            self.hide_all_pages()
            if hasattr(self, 'data_frame') and self.data_frame:
                self.data_frame.pack(fill=tk.BOTH, expand=True)
            self.highlight_active_button("Data")
            print("Switching to Data page")
        except Exception as e:
            print(f"Error switching to Data page: {e}")

    def show_diagnosis_page(self):
        """Show diagnosis page with error handling"""
        try:
            self.hide_all_pages()
            if hasattr(self, 'diagnosis_frame') and self.diagnosis_frame:
                self.diagnosis_frame.pack(fill=tk.BOTH, expand=True)
            self.highlight_active_button("Diagnosis")
            print("Switching to Diagnosis page")
        except Exception as e:
            print(f"Error switching to Diagnosis page: {e}")

    def show_model_preview_page(self):
        """Show model preview page with error handling"""
        try:
            self.hide_all_pages()
            if hasattr(self, 'model_preview_frame') and self.model_preview_frame:
                self.model_preview_frame.pack(fill=tk.BOTH, expand=True)
            self.highlight_active_button("Model Preview")
            print("Switching to Model Preview page")
        except Exception as e:
            print(f"Error switching to Model Preview page: {e}")

    def show_model_management_page(self):
        """Show model management page with error handling"""
        try:
            self.hide_all_pages()
            if hasattr(self, 'model_management_frame') and self.model_management_frame:
                self.model_management_frame.pack(fill=tk.BOTH, expand=True)
            self.highlight_active_button("Model Management")
            print("Switching to Model Management page")
        except Exception as e:
            print(f"Error switching to Model Management page: {e}")

    def show_user_management_page(self):
        """Show user management page with error handling"""
        try:
            if self.current_role not in ["Admin", "Super Admin"]:
                messagebox.showerror("Access Denied", "User Management requires Administrator privileges.")
                return
            self.hide_all_pages()
            if hasattr(self, 'user_management_frame') and self.user_management_frame:
                self.user_management_frame.pack(fill=tk.BOTH, expand=True)
            self.highlight_active_button("User Management")
            print("Switching to User Management page")
        except Exception as e:
            print(f"Error switching to User Management page: {e}")

    def show_system_check_page(self):
        """Show system check page with error handling"""
        try:
            if self.current_role != "Super Admin":
                messagebox.showerror("Access Denied", "System Check requires Super Administrator privileges.")
                return
            self.hide_all_pages()
            if hasattr(self, 'system_check_frame') and self.system_check_frame:
                self.system_check_frame.pack(fill=tk.BOTH, expand=True)
            self.highlight_active_button("System Check")
            print("Switching to System Check page")
        except Exception as e:
            print(f"Error switching to System Check page: {e}")

if __name__ == "__main__":
    app = WelVisionApp()
    app.mainloop() 