import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from database import db_manager
from roller_inspection_logger import roller_logger
from prediction_tracker import prediction_tracker
import tkinter.messagebox as messagebox
import uuid

class InferenceTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        
        # Initialize session tracking
        self.current_session_id = str(uuid.uuid4())
        self.session_started = False
        
        self.setup_tab()
        
        # Load current session data on initialization
        self.load_current_session_data()
    
    def setup_tab(self):
        inference_container = tk.Frame(self.parent, bg="#0a2158")
        inference_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top row: Roller Type and Date & Time with proper centering
        top_row_frame = tk.Frame(inference_container, bg="#0a2158")
        top_row_frame.pack(fill=tk.X, padx=5, pady=(5, 10))
        
        # Configure grid to accommodate all elements
        top_row_frame.grid_columnconfigure(0, weight=1)  # Roller Type
        top_row_frame.grid_columnconfigure(1, weight=0)  # Date & Time (fixed)
        top_row_frame.grid_columnconfigure(2, weight=0)  # System Status (fixed)
        top_row_frame.grid_columnconfigure(3, weight=0)  # Mode Indicator (fixed)
        top_row_frame.grid_columnconfigure(4, weight=1)  # AI Models
        
        # Roller Type (Combobox) - left side
        roller_frame = tk.LabelFrame(top_row_frame, text="Roller type", 
                                   font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        roller_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Date & Time (centered on screen)
        date_time_frame = tk.LabelFrame(top_row_frame, text="Date & Time", 
                                       font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        date_time_frame.grid(row=0, column=1, padx=5, pady=5)
        
        # System Status Indicator
        system_status_frame = tk.LabelFrame(top_row_frame, text="System Status", 
                                          font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        system_status_frame.grid(row=0, column=2, padx=5, pady=5)
        
        # Create system status indicator label
        self.app.system_status_var = tk.StringVar(value="NOT PROCESSING")
        self.app.system_status_label = tk.Label(system_status_frame, textvariable=self.app.system_status_var,
                                               font=("Arial", 12, "bold"), fg="#ffaa00", bg="#0a2158")
        self.app.system_status_label.pack(padx=15, pady=8)
        
        # Mode Indicator (between System Status and AI Models)
        mode_indicator_frame = tk.LabelFrame(top_row_frame, text="System Mode", 
                                           font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        mode_indicator_frame.grid(row=0, column=3, padx=5, pady=5)
        
        # Create mode indicator label
        self.app.mode_indicator_var = tk.StringVar(value="AUTOMATIC")
        self.app.mode_indicator_label = tk.Label(mode_indicator_frame, textvariable=self.app.mode_indicator_var,
                                                font=("Arial", 12, "bold"), fg="#00ff00", bg="#0a2158")
        self.app.mode_indicator_label.pack(padx=15, pady=8)
        
        # Model Selection - right side
        model_frame = tk.LabelFrame(top_row_frame, text="AI Models", 
                                   font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        model_frame.grid(row=0, column=4, padx=5, pady=5, sticky="e")
        
        # Create model selection dropdowns
        model_sub_frame = tk.Frame(model_frame, bg="#0a2158")
        model_sub_frame.pack(padx=10, pady=5)
        
        # OD Model Selection
        tk.Label(model_sub_frame, text="OD Model:", font=("Arial", 10), 
                fg="white", bg="#0a2158").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.app.od_model_var = tk.StringVar()
        self.app.od_model_combo = ttk.Combobox(model_sub_frame, textvariable=self.app.od_model_var,
                                              font=("Arial", 10), state="readonly", width=20)
        self.app.od_model_combo.grid(row=0, column=1, padx=5, pady=2)
        
        # BigFace Model Selection
        tk.Label(model_sub_frame, text="BigFace Model:", font=("Arial", 10), 
                fg="white", bg="#0a2158").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.app.bf_model_var = tk.StringVar()
        self.app.bf_model_combo = ttk.Combobox(model_sub_frame, textvariable=self.app.bf_model_var,
                                              font=("Arial", 10), state="readonly", width=20)
        self.app.bf_model_combo.grid(row=1, column=1, padx=5, pady=2)
        
        # Load models into dropdowns
        self.load_model_dropdowns()
        
        # Create real-time date/time display
        self.app.datetime_var = tk.StringVar()
        self.app.datetime_label = tk.Label(date_time_frame, textvariable=self.app.datetime_var,
                                          font=("Arial", 12), fg="white", bg="#0a2158")
        self.app.datetime_label.pack(padx=20, pady=8)
        
        # Initialize and start the clock
        self.update_datetime()
        self.start_datetime_clock()
        
        self.app.roller_name_var = tk.StringVar()
        self.app.roller_name_combobox = ttk.Combobox(roller_frame, textvariable=self.app.roller_name_var, 
                                                font=("Arial", 12), state="readonly")
        self.app.roller_name_combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True, pady=5)
        
        # Load roller types from database and bind selection event
        self.load_roller_types()
        self.app.roller_name_combobox.bind("<<ComboboxSelected>>", self.on_roller_type_changed)
        
        # Initialize with first roller type if available
        self.parent.after(100, self.initialize_roller_info)
        
        # Initialize mode indicator
        self.parent.after(200, self.initialize_mode_indicator)
        
        # Initialize system status indicator
        self.parent.after(300, self.initialize_system_status)
        
        # Current Roller Status
        status_frame = tk.Frame(inference_container, bg="#0a2158")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        current_status_entry = tk.Entry(status_frame, font=("Arial", 12), fg="black", bg="white", state="readonly")
        current_status_entry.pack(fill=tk.X, padx=5, pady=5)
        current_status_entry.delete(0, tk.END)
        current_status_entry.insert(0, "Current roller status: BF: NOT_OK -> Rust = 1, Dam = 0, High_head = 0, Down_Head = 0")
        
        # Main content area: Camera Feeds, Statistics, and Roller Info
        main_content = tk.Frame(inference_container, bg="#0a2158")
        main_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_rowconfigure(1, weight=0)
        main_content.grid_rowconfigure(2, weight=0)  # Buttons row - no expansion
        main_content.grid_columnconfigure(0, weight=0)  # No expansion for camera columns
        main_content.grid_columnconfigure(1, weight=0)  # No expansion for camera columns
        main_content.grid_columnconfigure(2, weight=1)  # Right column gets all extra space
        
        # Camera Feeds with Status Indicators
        # BF Feed with Status Indicator
        bf_container = tk.Frame(main_content, bg="#0a2158")
        bf_container.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        # BF Status Indicator
        bf_status_frame = tk.Frame(bf_container, bg="#0a2158", height=40)
        bf_status_frame.pack(fill=tk.X, pady=(0, 3))
        bf_status_frame.pack_propagate(False)
        
        self.app.bf_status_indicator = tk.Label(bf_status_frame, text="● ACCEPTED", 
                                               font=("Arial", 14, "bold"), fg="#00ff00", bg="#0a2158",
                                               relief="solid", bd=1, padx=15, pady=5)
        self.app.bf_status_indicator.pack()
        
        bf_feed_frame = tk.LabelFrame(bf_container, text="BF Feed", font=("Arial", 14, "bold"), fg="white", bg="#0a2158", width=480, height=400)
        bf_feed_frame.pack()
        bf_feed_frame.pack_propagate(False)  # Prevent frame from resizing based on content
        self.app.bf_canvas = tk.Canvas(bf_feed_frame, width=460, height=370, bg="black", highlightthickness=0)
        self.app.bf_canvas.pack(padx=1, pady=1)  # Minimal padding for tight border
        
        # OD Feed with Status Indicator
        od_container = tk.Frame(main_content, bg="#0a2158")
        od_container.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")
        
        # OD Status Indicator
        od_status_frame = tk.Frame(od_container, bg="#0a2158", height=40)
        od_status_frame.pack(fill=tk.X, pady=(0, 3))
        od_status_frame.pack_propagate(False)
        
        self.app.od_status_indicator = tk.Label(od_status_frame, text="● ACCEPTED", 
                                               font=("Arial", 14, "bold"), fg="#00ff00", bg="#0a2158",
                                               relief="solid", bd=1, padx=15, pady=5)
        self.app.od_status_indicator.pack()
        
        od_feed_frame = tk.LabelFrame(od_container, text="OD Feed", font=("Arial", 14, "bold"), fg="white", bg="#0a2158", width=480, height=400)
        od_feed_frame.pack()
        od_feed_frame.pack_propagate(False)  # Prevent frame from resizing based on content
        self.app.od_canvas = tk.Canvas(od_feed_frame, width=460, height=370, bg="black", highlightthickness=0)
        self.app.od_canvas.pack(padx=1, pady=1)  # Minimal padding for tight border
        
        # Right Column: Overall Result, Roller Info, Recently rejected images (span all rows, more constrained width)
        right_column = tk.Frame(main_content, bg="#0a2158", width=220)
        right_column.grid(row=0, column=2, rowspan=3, padx=5, pady=5, sticky="nsew")
        right_column.pack_propagate(False)  # Maintain constrained width
        
        # Overall Result (narrower width)
        overall_result_frame = tk.LabelFrame(right_column, text="Over all Result:", 
                                           font=("Arial", 11, "bold"), fg="white", bg="#0a2158", bd=1, height=200)
        overall_result_frame.pack(fill=tk.X, padx=8, pady=(2, 2))
        overall_result_frame.pack_propagate(False)  # Maintain fixed height
        
        self.app.overall_inspected_var = tk.StringVar(value="0")
        self.app.overall_ok_var = tk.StringVar(value="0")
        self.app.overall_not_ok_var = tk.StringVar(value="0")
        self.app.overall_percentage_var = tk.StringVar(value="0%")
        
        self.create_compact_stat_label(overall_result_frame, "Inspected :", self.app.overall_inspected_var, 0)
        self.create_compact_stat_label(overall_result_frame, "Ok rollers :", self.app.overall_ok_var, 1)
        self.create_compact_stat_label(overall_result_frame, "Not OK rollers:", self.app.overall_not_ok_var, 2)
        self.create_compact_stat_label(overall_result_frame, "Percentage:", self.app.overall_percentage_var, 3)
        
        # Roller Info (narrower width)
        roller_info_frame = tk.LabelFrame(right_column, text="Roller Info:", 
                                        font=("Arial", 11, "bold"), fg="white", bg="#0a2158", bd=1, height=180)
        roller_info_frame.pack(fill=tk.X, padx=8, pady=(2, 2))
        roller_info_frame.pack_propagate(False)  # Maintain fixed height
        
        self.app.outer_diameter_var = tk.StringVar(value="25 mm")
        self.app.dimple_diameter_var = tk.StringVar(value="20 mm")
        self.app.roller_length_var = tk.StringVar(value="40.25 mm")
        
        self.create_compact_stat_label(roller_info_frame, "Outer Diameter :", self.app.outer_diameter_var, 0)
        self.create_compact_stat_label(roller_info_frame, "Dimple Diameter:", self.app.dimple_diameter_var, 1)
        self.create_compact_stat_label(roller_info_frame, "Roller Length :", self.app.roller_length_var, 2)
        
        # Container frame for both rejected images frames (horizontal layout)
        rejected_images_container = tk.Frame(right_column, bg="#0a2158")
        rejected_images_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(2, 2))
        
        # Configure grid weights for equal width distribution
        rejected_images_container.grid_columnconfigure(0, weight=1)
        rejected_images_container.grid_columnconfigure(1, weight=1)
        rejected_images_container.grid_rowconfigure(0, weight=1)
        
        # Recently rejected OD roller images (right side)
        od_rejected_frame = tk.LabelFrame(rejected_images_container, text="OD Rejected", 
                                        font=("Arial", 9, "bold"), fg="white", bg="#0a2158", bd=1)
        od_rejected_frame.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        
        # Recently rejected BigFace roller images (left side)
        bf_rejected_frame = tk.LabelFrame(rejected_images_container, text="BigFace Rejected", 
                                        font=("Arial", 9, "bold"), fg="white", bg="#0a2158", bd=1)
        bf_rejected_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        
        # Canvas for OD rejected images with placeholder
        self.app.od_rejected_canvas = tk.Canvas(od_rejected_frame, bg="black", highlightthickness=0)
        self.app.od_rejected_canvas.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        
        # Canvas for BigFace rejected images with placeholder
        self.app.bf_rejected_canvas = tk.Canvas(bf_rejected_frame, bg="black", highlightthickness=0)
        self.app.bf_rejected_canvas.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        
        # Add placeholder functionality for both canvases
        self.setup_rejected_images_placeholders()
        
        # BF Statistics (directly below BF camera, matching camera width)
        bf_stats_frame = tk.LabelFrame(main_content, text="Bigface Result:", font=("Arial", 14, "bold"), fg="white", bg="#0a2158", width=480, height=160)
        bf_stats_frame.grid(row=1, column=0, padx=(0, 5), pady=(0, 2), sticky="ew")
        bf_stats_frame.pack_propagate(False)  # Maintain fixed size
        self.app.bf_inspected_var = tk.StringVar(value="0")
        self.app.bf_defective_var = tk.StringVar(value="0")
        self.app.bf_good_var = tk.StringVar(value="0")
        self.app.bf_proportion_var = tk.StringVar(value="0%")
        self.create_stat_label(bf_stats_frame, "Inspected :", self.app.bf_inspected_var, 0)
        self.create_stat_label(bf_stats_frame, "Ok rollers :", self.app.bf_good_var, 1)
        self.create_stat_label(bf_stats_frame, "Not OK rollers:", self.app.bf_defective_var, 2)
        self.create_stat_label(bf_stats_frame, "Percentage:", self.app.bf_proportion_var, 3)
        
        # OD Statistics (directly below OD camera, matching camera width)
        od_stats_frame = tk.LabelFrame(main_content, text="OD Result:", font=("Arial", 14, "bold"), fg="white", bg="#0a2158", width=480, height=160)
        od_stats_frame.grid(row=1, column=1, padx=(0, 5), pady=(0, 2), sticky="ew")
        od_stats_frame.pack_propagate(False)  # Maintain fixed size
        self.app.od_inspected_var = tk.StringVar(value="0")
        self.app.od_defective_var = tk.StringVar(value="0")
        self.app.od_good_var = tk.StringVar(value="0")
        self.app.od_proportion_var = tk.StringVar(value="0%")
        self.create_stat_label(od_stats_frame, "Inspected :", self.app.od_inspected_var, 0)
        self.create_stat_label(od_stats_frame, "Ok rollers :", self.app.od_good_var, 1)
        self.create_stat_label(od_stats_frame, "Not OK rollers:", self.app.od_defective_var, 2)
        self.create_stat_label(od_stats_frame, "Percentage:", self.app.od_proportion_var, 3)
        
        # Buttons below result widgets (new row)
        buttons_below_results_frame = tk.Frame(main_content, bg="#0a2158")
        buttons_below_results_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=(15, 5), sticky="ew")
        
        # Create left-aligned frame for buttons
        left_frame = tk.Frame(buttons_below_results_frame, bg="#0a2158")
        left_frame.pack(side=tk.LEFT)
        
        # Three buttons with increased spacing and size - now with confirmation popups
        start_button = tk.Button(left_frame, text="Start", font=("Arial", 12, "bold"), fg="white", bg="#28a745", width=8, height=1, command=self.start_inspection_with_confirmation)
        start_button.pack(side=tk.LEFT, padx=8, pady=5)
        
        stop_button = tk.Button(left_frame, text="Stop", font=("Arial", 12, "bold"), fg="white", bg="#dc3545", width=8, height=1, command=self.stop_inspection_with_confirmation)
        stop_button.pack(side=tk.LEFT, padx=8, pady=5)
        
        reset_button = tk.Button(left_frame, text="Reset", font=("Arial", 12, "bold"), fg="white", bg="#ffc107", width=8, height=1, command=self.reset_with_confirmation)
        reset_button.pack(side=tk.LEFT, padx=8, pady=5)
        
        # Allow all images checkbox - only visible to Super Admin users
        if self.app.current_role == "Super Admin":
            self.app.allow_all_images_var = tk.BooleanVar()
            allow_all_checkbox = tk.Checkbutton(left_frame, text="Allow all images", 
                                              variable=self.app.allow_all_images_var,
                                              font=("Arial", 12, "bold"), fg="white", bg="#0a2158", 
                                              selectcolor="#0a2158", activebackground="#0a2158", 
                                              activeforeground="white",
                                              command=self.on_allow_all_images_changed)
            allow_all_checkbox.pack(side=tk.LEFT, padx=8, pady=5)
            
            # Test inspection button for Super Admin
            test_button = tk.Button(left_frame, text="Test Inspection", font=("Arial", 10, "bold"), 
                                   fg="white", bg="#6f42c1", width=15, height=1, 
                                   command=self.simulate_roller_inspection)
            test_button.pack(side=tk.LEFT, padx=8, pady=5)
            
            # Exit button for Super Admin (near test inspection)
            exit_button_top = tk.Button(left_frame, text="Exit", font=("Arial", 10, "bold"), 
                                       fg="white", bg="#ff4444", width=8, height=1, 
                                       command=self.app.controlled_exit)
            exit_button_top.pack(side=tk.LEFT, padx=8, pady=5)
        
        # Bottom buttons and footer frame
        bottom_frame = tk.Frame(inference_container, bg="#0a2158")
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons (left side) - Essential buttons only for better visibility
        buttons_frame = tk.Frame(bottom_frame, bg="#0a2158")
        buttons_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        start_button = tk.Button(buttons_frame, text="Start", font=("Arial", 12, "bold"), fg="white", bg="#28a745", width=10, command=self.start_inspection_with_confirmation)
        start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        stop_button = tk.Button(buttons_frame, text="Stop", font=("Arial", 12, "bold"), fg="white", bg="#dc3545", width=10, command=self.stop_inspection_with_confirmation)
        stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        reset_button = tk.Button(buttons_frame, text="Reset", font=("Arial", 12, "bold"), fg="white", bg="#ffc107", width=10, command=self.reset_with_confirmation)
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        manual_button = tk.Button(buttons_frame, text="Manual", font=("Arial", 12, "bold"), fg="white", bg="#6f42c1", width=10, command=lambda: self.app.show_system_check_page())
        manual_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        exit_button = tk.Button(buttons_frame, text="Exit", font=("Arial", 12, "bold"), fg="white", bg="#ff4444", width=10, command=self.app.controlled_exit)
        exit_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Welvision Innovations (right side of bottom frame)
        welvision_frame = tk.LabelFrame(bottom_frame, text="", bg="#0a2158", bd=2, relief="solid")
        welvision_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        welvision_label = tk.Label(welvision_frame, text="Welvision\nInnovations", 
                                 font=("Arial", 14, "bold"), fg="white", bg="#0a2158", justify=tk.CENTER)
        welvision_label.pack(padx=20, pady=10)
    
    def create_stat_label(self, parent, text, var, row):
        label = tk.Label(parent, text=text, font=("Arial", 14), fg="white", bg="#0a2158", anchor="w")
        label.grid(row=row, column=0, sticky="w", padx=8, pady=4)
        value_label = tk.Label(parent, textvariable=var, font=("Arial", 14, "bold"), fg="white", bg="#0a2158")
        value_label.grid(row=row, column=1, sticky="e", padx=8, pady=4)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
    
    def create_compact_stat_label(self, parent, text, var, row):
        label = tk.Label(parent, text=text, font=("Arial", 11), fg="white", bg="#0a2158", anchor="w")
        label.grid(row=row, column=0, sticky="w", padx=6, pady=2)
        value_label = tk.Label(parent, textvariable=var, font=("Arial", 11, "bold"), fg="white", bg="#0a2158")
        value_label.grid(row=row, column=1, sticky="e", padx=6, pady=2)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
    
    def create_extra_compact_stat_label(self, parent, text, var, row):
        label = tk.Label(parent, text=text, font=("Arial", 9), fg="white", bg="#0a2158", anchor="w")
        label.grid(row=row, column=0, sticky="w", padx=4, pady=1)
        value_label = tk.Label(parent, textvariable=var, font=("Arial", 9, "bold"), fg="white", bg="#0a2158")
        value_label.grid(row=row, column=1, sticky="e", padx=4, pady=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
    
    def create_ultra_compact_stat_label(self, parent, text, var, row):
        label = tk.Label(parent, text=text, font=("Arial", 8), fg="white", bg="#0a2158", anchor="w")
        label.grid(row=row, column=0, sticky="w", padx=2, pady=0)
        value_label = tk.Label(parent, textvariable=var, font=("Arial", 8, "bold"), fg="white", bg="#0a2158")
        value_label.grid(row=row, column=1, sticky="e", padx=2, pady=0)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
    
    def on_allow_all_images_changed(self):
        """Callback function when Allow all images checkbox state changes"""
        # Only available for Super Admin users
        if hasattr(self.app, 'allow_all_images_var') and self.app.current_role == "Super Admin":
            if self.app.allow_all_images_var.get():
                print("Allow all images: ENABLED")
                # Add functionality here for when the checkbox is checked
            else:
                print("Allow all images: DISABLED")
                # Add functionality here for when the checkbox is unchecked
    
    def setup_rejected_images_placeholders(self):
        """Setup placeholder text and images for both OD and BigFace rejected image canvases"""
        
        def update_od_placeholder():
            self.app.od_rejected_canvas.delete("od_placeholder")
            canvas_width = self.app.od_rejected_canvas.winfo_width()
            canvas_height = self.app.od_rejected_canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:  # Only draw if canvas has size
                # Create border rectangle
                self.app.od_rejected_canvas.create_rectangle(5, 5, canvas_width-5, canvas_height-5, 
                                                           outline="gray", width=1, fill="black", tags="od_placeholder")
                # Create centered text
                self.app.od_rejected_canvas.create_text(canvas_width//2, canvas_height//2, 
                                                       text="OD\nRejected\nImages", 
                                                       fill="white", font=("Arial", 9), 
                                                       justify=tk.CENTER, tags="od_placeholder")
        
        def update_bf_placeholder():
            self.app.bf_rejected_canvas.delete("bf_placeholder")
            canvas_width = self.app.bf_rejected_canvas.winfo_width()
            canvas_height = self.app.bf_rejected_canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:  # Only draw if canvas has size
                # Create border rectangle
                self.app.bf_rejected_canvas.create_rectangle(5, 5, canvas_width-5, canvas_height-5, 
                                                           outline="gray", width=1, fill="black", tags="bf_placeholder")
                # Create centered text
                self.app.bf_rejected_canvas.create_text(canvas_width//2, canvas_height//2, 
                                                       text="BigFace\nRejected\nImages", 
                                                       fill="white", font=("Arial", 9), 
                                                       justify=tk.CENTER, tags="bf_placeholder")
        
        # Update placeholders when canvases are configured
        self.app.od_rejected_canvas.bind("<Configure>", lambda e: update_od_placeholder())
        self.app.bf_rejected_canvas.bind("<Configure>", lambda e: update_bf_placeholder())
        
        # Initial draw for both placeholders
        self.parent.after(100, update_od_placeholder)
        self.parent.after(100, update_bf_placeholder)
    
    def update_bf_status(self, accepted=True, custom_text=None):
        """Update BF status indicator
        Args:
            accepted (bool): True for accepted (green), False for rejected (red)
            custom_text (str, optional): Custom text to display instead of default
        """
        if hasattr(self.app, 'bf_status_indicator'):
            if custom_text:
                text = custom_text
            else:
                text = "● ACCEPTED" if accepted else "● REJECTED"
            
            color = "#00ff00" if accepted else "#ff0000"  # Green or Red
            self.app.bf_status_indicator.config(text=text, fg=color)
    
    def update_od_status(self, accepted=True, custom_text=None):
        """Update OD status indicator
        Args:
            accepted (bool): True for accepted (green), False for rejected (red)  
            custom_text (str, optional): Custom text to display instead of default
        """
        if hasattr(self.app, 'od_status_indicator'):
            if custom_text:
                text = custom_text
            else:
                text = "● ACCEPTED" if accepted else "● REJECTED"
            
            color = "#00ff00" if accepted else "#ff0000"  # Green or Red
            self.app.od_status_indicator.config(text=text, fg=color)
    
    def update_both_status(self, bf_accepted=True, od_accepted=True, bf_text=None, od_text=None):
        """Update both BF and OD status indicators simultaneously
        Args:
            bf_accepted (bool): BF acceptance status
            od_accepted (bool): OD acceptance status
            bf_text (str, optional): Custom text for BF indicator
            od_text (str, optional): Custom text for OD indicator
        """
        self.update_bf_status(bf_accepted, bf_text)
        self.update_od_status(od_accepted, od_text)
    
    def load_model_dropdowns(self):
        """Load available models into the dropdown menus"""
        try:
            # Load OD models
            od_models = db_manager.get_od_models()
            od_model_names = [model['model_name'] for model in od_models]
            self.app.od_model_combo['values'] = od_model_names
            
            # Set active OD model as selected
            active_od = db_manager.get_active_od_model()
            if active_od:
                self.app.od_model_var.set(active_od['model_name'])
            elif od_model_names:
                self.app.od_model_var.set(od_model_names[0])
            
            # Load BigFace models
            bf_models = db_manager.get_bigface_models()
            bf_model_names = [model['model_name'] for model in bf_models]
            self.app.bf_model_combo['values'] = bf_model_names
            
            # Set active BigFace model as selected
            active_bf = db_manager.get_active_bigface_model()
            if active_bf:
                self.app.bf_model_var.set(active_bf['model_name'])
            elif bf_model_names:
                self.app.bf_model_var.set(bf_model_names[0])
            
            # Bind selection change events
            self.app.od_model_combo.bind('<<ComboboxSelected>>', self.on_od_model_changed)
            self.app.bf_model_combo.bind('<<ComboboxSelected>>', self.on_bf_model_changed)
            
            print(f"📊 Loaded {len(od_model_names)} OD models and {len(bf_model_names)} BigFace models")
            
        except Exception as e:
            print(f"❌ Error loading models into dropdowns: {e}")
    
    def on_od_model_changed(self, event=None):
        """Handle OD model selection change"""
        try:
            selected_model = self.app.od_model_var.get()
            print(f"🔧 OD model changed to: {selected_model}")
            
            # Find the model and get its path
            od_models = db_manager.get_od_models()
            for model in od_models:
                if model['model_name'] == selected_model:
                    # Here you would load the actual model for inference
                    print(f"📁 OD model path: {model['model_path']}")
                    # Store the model info for inference
                    self.app.current_od_model = model
                    break
            
        except Exception as e:
            print(f"❌ Error changing OD model: {e}")
    
    def on_bf_model_changed(self, event=None):
        """Handle BigFace model selection change"""
        try:
            selected_model = self.app.bf_model_var.get()
            print(f"🔧 BigFace model changed to: {selected_model}")
            
            # Find the model and get its path
            bf_models = db_manager.get_bigface_models()
            for model in bf_models:
                if model['model_name'] == selected_model:
                    # Here you would load the actual model for inference
                    print(f"📁 BigFace model path: {model['model_path']}")
                    # Store the model info for inference
                    self.app.current_bf_model = model
                    break
            
        except Exception as e:
            print(f"❌ Error changing BigFace model: {e}")
    
    def refresh_model_dropdowns(self):
        """Refresh the model dropdowns (call this when models are updated)"""
        try:
            print("🔄 Refreshing model dropdowns...")
            self.load_model_dropdowns()
        except Exception as e:
            print(f"❌ Error refreshing model dropdowns: {e}")
            
    def refresh_roller_types(self):
        """Refresh the roller type dropdown (call this when roller types are updated)"""
        try:
            print("🔄 Refreshing roller type dropdown...")
            # Store current selection to restore it if possible
            current_selection = self.app.roller_name_var.get()
            
            # Reload roller types from database
            self.load_roller_types()
            
            # Try to restore previous selection if it still exists
            if current_selection:
                roller_types = list(self.app.roller_name_combobox['values'])
                if current_selection in roller_types:
                    self.app.roller_name_var.set(current_selection)
                else:
                    # If previous selection no longer exists, set to first available
                    if roller_types:
                        self.app.roller_name_var.set(roller_types[0])
                        self.initialize_roller_info()
                        
            print("✅ Roller type dropdown refreshed successfully")
        except Exception as e:
            print(f"❌ Error refreshing roller type dropdown: {e}")
    
    def log_component_inspection(self, component_type, predictions):
        """
        Log component inspection result to appropriate CSV and update displays
        
        Args:
            component_type: 'od' or 'bf'
            predictions: list of detection dictionaries [{'class_name': str, 'confidence': float}]
        """
        try:
            # Start session if not started
            if not self.session_started:
                roller_logger.start_new_session(self.current_session_id)
                self.session_started = True
                print(f"📝 Started new inspection session: {self.current_session_id}")
            
            # Get current roller type and employee info
            current_roller = self.app.roller_name_var.get() if hasattr(self.app, 'roller_name_var') else None
            current_employee = getattr(self.app, 'current_user_id', 'Unknown')
            
            # Log individual prediction with detailed tracking
            prediction_result = prediction_tracker.log_prediction(
                component_type=component_type,
                predictions=predictions,
                session_id=self.current_session_id,
                roller_type=current_roller,
                employee_id=current_employee
            )
            
            # Update component session data (existing functionality)
            roller_logger.update_component_session(self.current_session_id, component_type, predictions)
            
            # Update status indicators based on prediction result
            if prediction_result:
                status_text = f"● {prediction_result['status']}"
                if not prediction_result['is_accepted'] and prediction_result['defect_counts']:
                    # Add defect information to status
                    defects = []
                    for defect, count in prediction_result['defect_counts'].items():
                        if count > 0 and defect != 'roller':
                            defects.append(f"{defect.title()}: {count}")
                    if defects:
                        status_text += f" ({', '.join(defects)})"
                
                # Update appropriate status indicator
                if component_type.lower() == 'bf':
                    self.update_bf_status(accepted=prediction_result['is_accepted'], custom_text=status_text)
                else:
                    self.update_od_status(accepted=prediction_result['is_accepted'], custom_text=status_text)
            
            # Update the display with current session data
            self.update_result_displays()
            
            print(f"📝 Logged {component_type.upper()} prediction: {prediction_result['status'] if prediction_result else 'ERROR'}")
            
        except Exception as e:
            print(f"❌ Error logging {component_type} inspection: {e}")
    
    def simulate_roller_inspection(self):
        """
        Simulate a roller inspection for testing purposes
        This method shows how to integrate the logging system with real model predictions
        """
        try:
            # Example BF predictions (replace with actual model output)
            sample_bf_predictions = [
                {'class_name': 'roller', 'confidence': 0.85},
                {'class_name': 'rust', 'confidence': 0.72}  # This will cause rejection
            ]
            
            # Example OD predictions (replace with actual model output)
            sample_od_predictions = [
                {'class_name': 'roller', 'confidence': 0.91}  # Only roller, will be accepted
            ]
            
            # Log component inspections separately
            self.log_component_inspection('bf', sample_bf_predictions)
            self.log_component_inspection('od', sample_od_predictions)
            
            # Update status indicators based on the logged results
            # BF will be rejected due to rust detection
            # OD will be accepted (only roller detected)
            self.update_bf_status(accepted=False, custom_text="● REJECTED (Rust)")
            self.update_od_status(accepted=True, custom_text="● ACCEPTED")
            
            # Update result displays with current session data
            self.update_result_displays()
            
        except Exception as e:
            print(f"❌ Error in simulate_roller_inspection: {e}")
    
    def reset_inspection_data(self):
        """
        Reset inspection data - transfer CSVs to database and clear CSV files
        """
        try:
            # End current session
            if self.session_started:
                roller_logger.end_session(self.current_session_id)
            
            # Get current session statistics before transfer
            session_stats = roller_logger.get_session_stats()
            prediction_stats = prediction_tracker.get_prediction_stats()
            
            if session_stats['total_sessions'] == 0 and prediction_stats['total_predictions'] == 0:
                messagebox.showinfo("Reset", "No inspection data to transfer.\nCSV files are already empty.")
                return
            
            # Confirm with user - include both session and prediction data
            od_stats = session_stats.get('od', {})
            bf_stats = session_stats.get('bf', {})
            od_pred_stats = prediction_stats.get('od', {})
            bf_pred_stats = prediction_stats.get('bf', {})
            
            confirm_msg = (
                f"Transfer inspection data to database?\n\n"
                f"📊 SESSION DATA:\n"
                f"OD Sessions: {od_stats.get('sessions', 0)} | Inspected: {od_stats.get('total_inspected', 0)} | Rate: {od_stats.get('acceptance_rate', 0):.1f}%\n"
                f"BF Sessions: {bf_stats.get('sessions', 0)} | Inspected: {bf_stats.get('total_inspected', 0)} | Rate: {bf_stats.get('acceptance_rate', 0):.1f}%\n\n"
                f"🔍 INDIVIDUAL PREDICTIONS:\n"
                f"OD Predictions: {od_pred_stats.get('total_predictions', 0)} | Accepted: {od_pred_stats.get('accepted', 0)} | Rejected: {od_pred_stats.get('rejected', 0)}\n"
                f"BF Predictions: {bf_pred_stats.get('total_predictions', 0)} | Accepted: {bf_pred_stats.get('accepted', 0)} | Rejected: {bf_pred_stats.get('rejected', 0)}\n\n"
                f"This will transfer all data to database and clear CSV files."
            )
            
            if not messagebox.askyesno("Confirm Reset", confirm_msg):
                return
            
            # Transfer session data to database and clear CSVs
            session_success, session_message, session_counts = roller_logger.transfer_to_database_and_clear_csvs(
                session_id=self.current_session_id
            )
            
            # Transfer prediction data to database and clear CSVs
            pred_success, pred_message, pred_counts = prediction_tracker.transfer_predictions_to_database_and_clear_csvs()
            
            if session_success and pred_success:
                # Reset session tracking
                self.current_session_id = str(uuid.uuid4())
                self.session_started = False
                
                # Reset status indicators
                self.update_bf_status(accepted=True, custom_text="● READY")
                self.update_od_status(accepted=True, custom_text="● READY")
                
                # Reset statistics displays
                self.reset_statistics_displays()
                
                # Success message
                success_msg = (
                    f"✅ Reset Completed Successfully!\n\n"
                    f"📊 SESSION DATA TRANSFERRED:\n"
                    f"  • OD Sessions: {session_counts.get('od', 0)}\n"
                    f"  • BF Sessions: {session_counts.get('bf', 0)}\n\n"
                    f"🔍 PREDICTION DATA TRANSFERRED:\n"
                    f"  • OD Predictions: {pred_counts.get('od', 0)}\n"
                    f"  • BF Predictions: {pred_counts.get('bf', 0)}\n\n"
                    f"🔄 All CSV files cleared\n"
                    f"🆕 New session ready for next inspection\n"
                    f"📈 Statistics reset"
                )
                messagebox.showinfo("Reset Successful", success_msg)
                
            else:
                error_details = []
                if not session_success:
                    error_details.append(f"Session transfer failed: {session_message}")
                if not pred_success:
                    error_details.append(f"Prediction transfer failed: {pred_message}")
                
                messagebox.showerror("Reset Failed", f"Failed to transfer data to database:\n\n" + "\n".join(error_details))
                
        except Exception as e:
            error_msg = f"Error during reset operation: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Reset Error", error_msg)
    
    def reset_with_exit_enable(self):
        """Reset inspection data and enable exit functionality"""
        # First perform the normal reset
        self.reset_inspection_data()
        
        # Update system status to show not processing (since reset stops inspection)
        self.update_system_status(False)
        
        # Check if CSV files are now clear
        if hasattr(self.app, 'has_unsaved_csv_records') and not self.app.has_unsaved_csv_records():
            # Show confirmation message that exit is now enabled
            messagebox.showinfo("Reset Complete", 
                              "Inspection data has been reset and transferred to database.\n\n"
                              "✅ CSV files cleared\n"
                              "✅ Exit functionality is now enabled\n"
                              "✅ Application can be safely closed")
        else:
            # Show warning if CSV files still have data
            messagebox.showwarning("Reset Warning", 
                                 "Reset completed, but some CSV files may still contain data.\n\n"
                                 "Please check the CSV files or try reset again if needed.")
        
        print("📊 System status updated: Backend processing RESET (not processing)")
    
    def update_result_displays(self):
        """Update all result sections with current session data"""
        try:
            # Get current session statistics
            session_stats = roller_logger.get_session_stats()
            
            if not session_stats:
                return
            
            od_stats = session_stats.get('od', {})
            bf_stats = session_stats.get('bf', {})
            
            # Update BF statistics
            if hasattr(self.app, 'bf_inspected_var'):
                bf_inspected = bf_stats.get('total_inspected', 0)
                bf_accepted = bf_stats.get('total_accepted', 0)
                bf_rejected = bf_stats.get('total_rejected', 0)
                bf_percentage = (bf_accepted / bf_inspected * 100) if bf_inspected > 0 else 0
                
                self.app.bf_inspected_var.set(str(bf_inspected))
                self.app.bf_good_var.set(str(bf_accepted))
                self.app.bf_defective_var.set(str(bf_rejected))
                self.app.bf_proportion_var.set(f"{bf_percentage:.1f}%")
            
            # Update OD statistics  
            if hasattr(self.app, 'od_inspected_var'):
                od_inspected = od_stats.get('total_inspected', 0)
                od_accepted = od_stats.get('total_accepted', 0)
                od_rejected = od_stats.get('total_rejected', 0)
                od_percentage = (od_accepted / od_inspected * 100) if od_inspected > 0 else 0
                
                self.app.od_inspected_var.set(str(od_inspected))
                self.app.od_good_var.set(str(od_accepted))
                self.app.od_defective_var.set(str(od_rejected))
                self.app.od_proportion_var.set(f"{od_percentage:.1f}%")
            
            # Update overall statistics (combined BF + OD)
            if hasattr(self.app, 'overall_inspected_var'):
                total_inspected = bf_inspected + od_inspected
                total_accepted = bf_accepted + od_accepted
                total_rejected = bf_rejected + od_rejected
                overall_percentage = (total_accepted / total_inspected * 100) if total_inspected > 0 else 0
                
                self.app.overall_inspected_var.set(str(total_inspected))
                self.app.overall_ok_var.set(str(total_accepted))
                self.app.overall_not_ok_var.set(str(total_rejected))
                self.app.overall_percentage_var.set(f"{overall_percentage:.1f}%")
            
            print(f"📊 Updated displays - BF: {bf_inspected}/{bf_accepted}/{bf_rejected}, OD: {od_inspected}/{od_accepted}/{od_rejected}")
            
        except Exception as e:
            print(f"❌ Error updating result displays: {e}")
    
    def reset_statistics_displays(self):
        """Reset all statistics displays to initial values"""
        try:
            # Reset overall statistics
            if hasattr(self.app, 'overall_inspected_var'):
                self.app.overall_inspected_var.set("0")
                self.app.overall_ok_var.set("0")
                self.app.overall_not_ok_var.set("0")
                self.app.overall_percentage_var.set("0%")
            
            # Reset BF statistics
            if hasattr(self.app, 'bf_inspected_var'):
                self.app.bf_inspected_var.set("0")
                self.app.bf_good_var.set("0")
                self.app.bf_defective_var.set("0")
                self.app.bf_proportion_var.set("0%")
            
            # Reset OD statistics
            if hasattr(self.app, 'od_inspected_var'):
                self.app.od_inspected_var.set("0")
                self.app.od_good_var.set("0")
                self.app.od_defective_var.set("0")
                self.app.od_proportion_var.set("0%")
                
            print("📊 Statistics displays reset to initial values")
            
        except Exception as e:
            print(f"❌ Error resetting statistics displays: {e}")
    
    def get_inspection_session_stats(self):
        """
        Get current session inspection statistics
        
        Returns:
            dict: Session statistics
        """
        try:
            session_stats = roller_logger.get_session_stats()
            return {
                'session_id': self.current_session_id,
                'session_started': self.session_started,
                'od_stats': session_stats['od'],
                'bf_stats': session_stats['bf'],
                'total_sessions': session_stats['total_sessions']
            }
        except Exception as e:
            print(f"❌ Error getting session stats: {e}")
            return {
                'session_id': self.current_session_id,
                'session_started': False,
                'od_stats': {'sessions': 0, 'total_inspected': 0, 'total_accepted': 0, 'total_rejected': 0},
                'bf_stats': {'sessions': 0, 'total_inspected': 0, 'total_accepted': 0, 'total_rejected': 0},
                'total_sessions': 0
            }
    
    def load_current_session_data(self):
        """Load and display current session data on initialization"""
        try:
            # Check if there's any existing session data to load
            session_stats = roller_logger.get_session_stats()
            
            if session_stats and session_stats.get('total_sessions', 0) > 0:
                # Update displays with existing session data
                self.update_result_displays()
                print("📊 Loaded existing session data")
            else:
                # Ensure displays start at zero
                self.reset_statistics_displays()
                print("📊 No existing session data, displays initialized to zero")
                
        except Exception as e:
            print(f"❌ Error loading current session data: {e}")
            # Fallback to reset displays
            self.reset_statistics_displays()

    def load_roller_types(self):
        """Load roller types from database and bind selection event"""
        try:
            roller_types = db_manager.get_roller_types()
            self.app.roller_name_combobox['values'] = roller_types
            print(f"📊 Loaded {len(roller_types)} roller types")
        except Exception as e:
            print(f"❌ Error loading roller types: {e}")

    def on_roller_type_changed(self, event=None):
        """Callback function when roller type changes"""
        try:
            selected_type = self.app.roller_name_var.get()
            print(f"🔧 Roller type changed to: {selected_type}")
            
            # Update roller info based on selected type
            self.initialize_roller_info()
        except Exception as e:
            print(f"❌ Error changing roller type: {e}")

    def initialize_roller_info(self):
        """Initialize roller info based on selected roller type"""
        try:
            selected_type = self.app.roller_name_var.get()
            if not selected_type:
                # If no type selected, try to set the first available type
                roller_types = db_manager.get_roller_types()
                if roller_types:
                    selected_type = roller_types[0]
                    self.app.roller_name_var.set(selected_type)
                else:
                    print("❌ No roller types available")
                    return
            
            print(f"🔧 Initializing roller info for: {selected_type}")
            
            # Fetch roller info from database
            roller_info = db_manager.get_roller_by_type(selected_type)
            
            if roller_info:
                # Map database fields to UI display variables
                diameter = roller_info.get('diameter', 0)
                thickness = roller_info.get('thickness', 0)
                length = roller_info.get('length', 0)
                
                # Update UI variables with formatted values
                self.app.outer_diameter_var.set(f"{diameter} mm" if diameter else "N/A")
                self.app.dimple_diameter_var.set(f"{thickness} mm" if thickness else "N/A")  # Using thickness as dimple diameter
                self.app.roller_length_var.set(f"{length} mm" if length else "N/A")
                
                print(f"📊 Roller info updated - Diameter: {diameter}mm, Thickness: {thickness}mm, Length: {length}mm")
            else:
                print(f"❌ No roller info found for type: {selected_type}")
                # Set default values if no data found
                self.app.outer_diameter_var.set("N/A")
                self.app.dimple_diameter_var.set("N/A")
                self.app.roller_length_var.set("N/A")
                
        except Exception as e:
            print(f"❌ Error initializing roller info: {e}")
            # Set default values on error
            self.app.outer_diameter_var.set("N/A")
            self.app.dimple_diameter_var.set("N/A")
            self.app.roller_length_var.set("N/A")
    
    def update_mode_indicator(self, is_manual=False):
        """Update the system mode indicator
        Args:
            is_manual (bool): True for manual mode, False for automatic mode
        """
        if hasattr(self.app, 'mode_indicator_var') and hasattr(self.app, 'mode_indicator_label'):
            if is_manual:
                self.app.mode_indicator_var.set("MANUAL")
                self.app.mode_indicator_label.config(fg="#ff0000")  # Red for manual
            else:
                self.app.mode_indicator_var.set("AUTOMATIC")
                self.app.mode_indicator_label.config(fg="#00ff00")  # Green for automatic
    
    def get_manual_mode_status(self):
        """Get the current manual mode status from system check tab"""
        try:
            # Check if system check tab exists and has manual mode status
            if hasattr(self.app, 'system_check_tab') and hasattr(self.app.system_check_tab, 'manual_mode_active'):
                return self.app.system_check_tab.manual_mode_active
            return False
        except:
            return False
    
    def initialize_mode_indicator(self):
        """Initialize the mode indicator based on current system state"""
        try:
            # Check current manual mode status and update indicator
            is_manual = self.get_manual_mode_status()
            self.update_mode_indicator(is_manual)
        except Exception as e:
            print(f"❌ Error initializing mode indicator: {e}")
            # Default to automatic mode
            self.update_mode_indicator(False)
    
    def update_system_status(self, is_processing=False):
        """Update the system status indicator based on backend processing state
        Args:
            is_processing (bool): True if backend is processing, False if not processing
        """
        if hasattr(self.app, 'system_status_var') and hasattr(self.app, 'system_status_label'):
            if is_processing:
                self.app.system_status_var.set("PROCESSING")
                self.app.system_status_label.config(fg="#00ff00")  # Green for processing
            else:
                self.app.system_status_var.set("NOT PROCESSING")
                self.app.system_status_label.config(fg="#ffaa00")  # Orange for not processing
    
    def get_backend_processing_status(self):
        """Get the current backend processing status
        Returns:
            bool: True if backend is processing, False if not processing
        """
        try:
            # Check if inspection is currently running
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                return True
            
            # Check if any backend processes are alive and running
            if hasattr(self.app, 'processes') and self.app.processes:
                for process in self.app.processes:
                    if hasattr(process, 'is_alive') and process.is_alive():
                        return True
            
            # Check if PLC process is running
            if hasattr(self.app, 'plc_process') and self.app.plc_process:
                if hasattr(self.app.plc_process, 'is_alive') and self.app.plc_process.is_alive():
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error getting backend processing status: {e}")
            return False
    
    def initialize_system_status(self):
        """Initialize the system status indicator based on current backend processing state"""
        try:
            # Check current backend processing status and update indicator
            is_processing = self.get_backend_processing_status()
            self.update_system_status(is_processing)
            
            # Start periodic status updates every 2 seconds
            self.schedule_status_update()
            
        except Exception as e:
            print(f"❌ Error initializing system status: {e}")
            # Default to not processing status
            self.update_system_status(False)
    
    def schedule_status_update(self):
        """Schedule periodic system status updates to monitor backend processes"""
        try:
            # Check current backend processing status
            is_processing = self.get_backend_processing_status()
            self.update_system_status(is_processing)
            
            # Schedule next update in 2 seconds
            if hasattr(self.parent, 'after'):
                self.parent.after(2000, self.schedule_status_update)
            
        except Exception as e:
            print(f"⚠️ Error during scheduled status update: {e}")
            # Continue scheduling updates even if there's an error
            if hasattr(self.parent, 'after'):
                self.parent.after(2000, self.schedule_status_update)
    
    def start_inspection_with_confirmation(self):
        """
        Start inspection with user confirmation popup.
        Displays a confirmation dialog before starting the inspection process.
        """
        try:
            # Check if inspection is already running
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                messagebox.showwarning("Already Running", 
                                     "Inspection is already running!\n\n"
                                     "Please stop the current inspection before starting a new one.")
                return
            
            # Show confirmation popup
            if messagebox.askyesno("Confirm Start Inspection", 
                                 "Are you sure you want to start the inspection?\n\n"
                                 "This will:\n"
                                 "• Activate camera feeds\n"
                                 "• Begin component analysis\n"
                                 "• Start data logging\n"
                                 "• Initialize session tracking"):
                
                # Call the original start inspection method
                self.start_inspection_process()
                print("✅ Inspection started after user confirmation")
                
            else:
                print("🚫 Inspection start cancelled by user")
                
        except Exception as e:
            print(f"❌ Error starting inspection: {e}")
            messagebox.showerror("Start Error", f"Failed to start inspection: {e}")
    
    def stop_inspection_with_confirmation(self):
        """
        Stop inspection with user confirmation popup.
        Displays a confirmation dialog before stopping the inspection process.
        """
        try:
            # Check if inspection is running
            if not hasattr(self.app, 'inspection_running') or not self.app.inspection_running:
                messagebox.showwarning("Not Running", 
                                     "Inspection is not currently running!\n\n"
                                     "There is no active inspection to stop.")
                return
            
            # Show confirmation popup
            if messagebox.askyesno("Confirm Stop Inspection", 
                                 "Are you sure you want to stop the inspection?\n\n"
                                 "This will:\n"
                                 "• Stop camera feeds\n"
                                 "• Halt component analysis\n"
                                 "• Preserve current session data\n"
                                 "• End current session"):
                
                # Call the original stop inspection method
                self.stop_inspection_process()
                print("✅ Inspection stopped after user confirmation")
                
            else:
                print("🚫 Inspection stop cancelled by user")
                
        except Exception as e:
            print(f"❌ Error stopping inspection: {e}")
            messagebox.showerror("Stop Error", f"Failed to stop inspection: {e}")
    
    def reset_with_confirmation(self):
        """
        Reset inspection data with user confirmation popup.
        Enhanced version of reset_with_exit_enable that includes confirmation dialog.
        """
        try:
            # Check if inspection is running and offer to stop it
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                if messagebox.askyesno("Stop Required", 
                                     "Inspection is currently running.\n\n"
                                     "Do you want to stop it and then reset data?\n\n"
                                     "This will stop the inspection and then proceed with data reset."):
                    self.stop_inspection_process()
                else:
                    print("🚫 Reset cancelled - inspection still running")
                    return
            
            # Get current statistics for confirmation dialog
            try:
                session_stats = self.get_inspection_session_stats()
                od_stats = session_stats.get('od_stats', {})
                bf_stats = session_stats.get('bf_stats', {})
                
                # Create detailed confirmation message
                confirm_msg = (
                    f"Are you sure you want to reset all inspection data?\n\n"
                    f"📊 CURRENT SESSION DATA:\n"
                    f"• OD Inspected: {od_stats.get('total_inspected', 0)} | "
                    f"Accepted: {od_stats.get('total_accepted', 0)} | "
                    f"Rejected: {od_stats.get('total_rejected', 0)}\n"
                    f"• BF Inspected: {bf_stats.get('total_inspected', 0)} | "
                    f"Accepted: {bf_stats.get('total_accepted', 0)} | "
                    f"Rejected: {bf_stats.get('total_rejected', 0)}\n\n"
                    f"🔄 THIS WILL:\n"
                    f"• Transfer all data to database\n"
                    f"• Clear current statistics\n"
                    f"• Reset counters to zero\n"
                    f"• Enable exit functionality\n"
                    f"• Generate new session ID\n\n"
                    f"⚠️ This action cannot be undone!"
                )
                
            except Exception as e:
                # Fallback confirmation message if stats can't be retrieved
                confirm_msg = (
                    f"Are you sure you want to reset all inspection data?\n\n"
                    f"🔄 THIS WILL:\n"
                    f"• Transfer all data to database\n"
                    f"• Clear current statistics\n"
                    f"• Reset counters to zero\n"
                    f"• Enable exit functionality\n"
                    f"• Generate new session ID\n\n"
                    f"⚠️ This action cannot be undone!"
                )
                print(f"⚠️ Could not retrieve session stats for confirmation: {e}")
            
            # Show confirmation popup
            if messagebox.askyesno("Confirm Reset Data", confirm_msg):
                
                # Call the original reset method
                self.reset_with_exit_enable()
                print("✅ Data reset completed after user confirmation")
                
            else:
                print("🚫 Data reset cancelled by user")
                
        except Exception as e:
            print(f"❌ Error during reset confirmation: {e}")
            messagebox.showerror("Reset Error", f"Failed to reset data: {e}")
    
    def start_inspection_process(self):
        """
        Start the actual inspection process.
        This method contains the logic for starting inspection.
        """
        try:
            # Set inspection running flag
            if hasattr(self.app, 'inspection_running'):
                self.app.inspection_running = True
            
            # Start camera feeds if not already started
            if hasattr(self.app, 'start_camera_feeds'):
                self.app.start_camera_feeds()
            
            # Update system status to show processing
            self.update_system_status(True)
            
            # Start session if not already started
            if not self.session_started:
                from roller_inspection_logger import roller_logger
                roller_logger.start_new_session(self.current_session_id)
                self.session_started = True
                print(f"📝 Started new inspection session: {self.current_session_id}")
            
            print("🔄 Inspection process started successfully")
            print("📊 System status updated: Backend processing ACTIVE")
            
        except Exception as e:
            print(f"❌ Error in start_inspection_process: {e}")
            # Reset running flag on error
            if hasattr(self.app, 'inspection_running'):
                self.app.inspection_running = False
            raise
    
    def stop_inspection_process(self):
        """
        Stop the actual inspection process.
        This method contains the logic for stopping inspection.
        """
        try:
            # Set inspection stopped flag
            if hasattr(self.app, 'inspection_running'):
                self.app.inspection_running = False
            
            # Stop camera feeds
            if hasattr(self.app, 'stop_camera_feeds'):
                self.app.stop_camera_feeds()
            
            # Update system status to show not processing
            self.update_system_status(False)
            
            # End current session
            if self.session_started:
                from roller_inspection_logger import roller_logger
                roller_logger.end_session(self.current_session_id)
                self.session_started = False
                print(f"📝 Ended inspection session: {self.current_session_id}")
            
            print("⏹️ Inspection process stopped successfully")
            print("📊 System status updated: Backend processing INACTIVE")
            
        except Exception as e:
            print(f"❌ Error in stop_inspection_process: {e}")
            raise
    
    def update_datetime(self):
        """
        Update the date and time display with current date and time.
        Formats the display as: MM/DD/YYYY HH:MM:SS AM/PM
        """
        try:
            from datetime import datetime
            
            # Get current date and time
            now = datetime.now()
            
            # Format: MM/DD/YYYY HH:MM:SS AM/PM
            formatted_datetime = now.strftime("%m/%d/%Y %I:%M:%S %p")
            
            # Update the display
            if hasattr(self.app, 'datetime_var'):
                self.app.datetime_var.set(formatted_datetime)
            
        except Exception as e:
            print(f"❌ Error updating datetime: {e}")
            # Fallback to static display
            if hasattr(self.app, 'datetime_var'):
                self.app.datetime_var.set("Time Error")
    
    def start_datetime_clock(self):
        """
        Start the real-time clock that updates every second.
        This method schedules itself to run continuously.
        """
        try:
            # Update the datetime display
            self.update_datetime()
            
            # Schedule next update in 1000ms (1 second)
            if hasattr(self.parent, 'after'):
                self.parent.after(1000, self.start_datetime_clock)
            
        except Exception as e:
            print(f"⚠️ Error in datetime clock: {e}")
            # Continue scheduling updates even if there's an error
            if hasattr(self.parent, 'after'):
                self.parent.after(1000, self.start_datetime_clock)