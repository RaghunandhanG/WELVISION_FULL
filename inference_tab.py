import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from database import db_manager

class InferenceTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_tab()
    
    def setup_tab(self):
        inference_container = tk.Frame(self.parent, bg="#0a2158")
        inference_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top row: Roller Type and Date & Time with proper centering
        top_row_frame = tk.Frame(inference_container, bg="#0a2158")
        top_row_frame.pack(fill=tk.X, padx=5, pady=(5, 10))
        
        # Configure grid to center Date & Time
        top_row_frame.grid_columnconfigure(0, weight=1)  # Left space
        top_row_frame.grid_columnconfigure(1, weight=0)  # Date & Time (fixed)
        top_row_frame.grid_columnconfigure(2, weight=1)  # Right space
        
        # Roller Type (Combobox) - left side
        roller_frame = tk.LabelFrame(top_row_frame, text="Roller type", 
                                   font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        roller_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Date & Time (centered on screen)
        date_time_frame = tk.LabelFrame(top_row_frame, text="Date & Time", 
                                       font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        date_time_frame.grid(row=0, column=1, padx=5, pady=5)
        
        # Model Selection - right side
        model_frame = tk.LabelFrame(top_row_frame, text="AI Models", 
                                   font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        model_frame.grid(row=0, column=2, padx=5, pady=5, sticky="e")
        
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
        
        date_time_label = tk.Label(date_time_frame, text="07/06/2025 12:00AM", 
                                  font=("Arial", 12), fg="white", bg="#0a2158")
        date_time_label.pack(padx=20, pady=8)
        
        self.app.roller_name_var = tk.StringVar()
        self.app.roller_name_combobox = ttk.Combobox(roller_frame, textvariable=self.app.roller_name_var, 
                                                font=("Arial", 12), state="readonly")
        self.app.roller_name_combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True, pady=5)
        
        def set_combobox_values():
            self.app.roller_name_combobox['values'] = ("4TN1248", "32310")
            self.app.roller_name_combobox.set("4TN1248")
            print(f"Combobox values set to: {self.app.roller_name_combobox['values']}")
        
        self.parent.after(100, set_combobox_values)
        
        def check_combobox_values(event=None):
            print(f"Combobox values after rendering: {self.app.roller_name_combobox['values']}")
            print(f"Current selection: {self.app.roller_name_var.get()}")
        
        self.app.roller_name_combobox.bind("<<ComboboxSelected>>", check_combobox_values)
        self.parent.after(500, check_combobox_values)
        
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
        
        self.app.overall_inspected_var = tk.StringVar(value="1000")
        self.app.overall_ok_var = tk.StringVar(value="810")
        self.app.overall_not_ok_var = tk.StringVar(value="190")
        self.app.overall_percentage_var = tk.StringVar(value="81%")
        
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
        
        # Recently rejected OD roller images (left side)
        od_rejected_frame = tk.LabelFrame(rejected_images_container, text="OD Rejected", 
                                        font=("Arial", 9, "bold"), fg="white", bg="#0a2158", bd=1)
        od_rejected_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        
        # Canvas for OD rejected images with placeholder
        self.app.od_rejected_canvas = tk.Canvas(od_rejected_frame, bg="black", highlightthickness=0)
        self.app.od_rejected_canvas.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        
        # Recently rejected BigFace roller images (right side)
        bf_rejected_frame = tk.LabelFrame(rejected_images_container, text="BigFace Rejected", 
                                        font=("Arial", 9, "bold"), fg="white", bg="#0a2158", bd=1)
        bf_rejected_frame.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        
        # Canvas for BigFace rejected images with placeholder
        self.app.bf_rejected_canvas = tk.Canvas(bf_rejected_frame, bg="black", highlightthickness=0)
        self.app.bf_rejected_canvas.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        
        # Add placeholder functionality for both canvases
        self.setup_rejected_images_placeholders()
        
        # BF Statistics (directly below BF camera, matching camera width)
        bf_stats_frame = tk.LabelFrame(main_content, text="Bigface Result:", font=("Arial", 14, "bold"), fg="white", bg="#0a2158", width=480, height=160)
        bf_stats_frame.grid(row=1, column=0, padx=(0, 5), pady=(0, 2), sticky="ew")
        bf_stats_frame.pack_propagate(False)  # Maintain fixed size
        self.app.bf_inspected_var = tk.StringVar(value="1000")
        self.app.bf_defective_var = tk.StringVar(value="100")
        self.app.bf_good_var = tk.StringVar(value="900")
        self.app.bf_proportion_var = tk.StringVar(value="90%")
        self.create_stat_label(bf_stats_frame, "Inspected :", self.app.bf_inspected_var, 0)
        self.create_stat_label(bf_stats_frame, "Ok rollers :", self.app.bf_good_var, 1)
        self.create_stat_label(bf_stats_frame, "Not OK rollers:", self.app.bf_defective_var, 2)
        self.create_stat_label(bf_stats_frame, "Percentage:", self.app.bf_proportion_var, 3)
        
        # OD Statistics (directly below OD camera, matching camera width)
        od_stats_frame = tk.LabelFrame(main_content, text="OD Result:", font=("Arial", 14, "bold"), fg="white", bg="#0a2158", width=480, height=160)
        od_stats_frame.grid(row=1, column=1, padx=(0, 5), pady=(0, 2), sticky="ew")
        od_stats_frame.pack_propagate(False)  # Maintain fixed size
        self.app.od_inspected_var = tk.StringVar(value="900")
        self.app.od_defective_var = tk.StringVar(value="90")
        self.app.od_good_var = tk.StringVar(value="810")
        self.app.od_proportion_var = tk.StringVar(value="90%")
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
        
        # Three buttons with increased spacing and size
        start_button = tk.Button(left_frame, text="Start", font=("Arial", 12, "bold"), fg="white", bg="#28a745", width=8, height=1)
        start_button.pack(side=tk.LEFT, padx=8, pady=5)
        
        stop_button = tk.Button(left_frame, text="Stop", font=("Arial", 12, "bold"), fg="white", bg="#dc3545", width=8, height=1)
        stop_button.pack(side=tk.LEFT, padx=8, pady=5)
        
        reset_button = tk.Button(left_frame, text="Reset", font=("Arial", 12, "bold"), fg="white", bg="#ffc107", width=8, height=1)
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
        
        # Bottom buttons and footer frame
        bottom_frame = tk.Frame(inference_container, bg="#0a2158")
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Buttons (left side)
        buttons_frame = tk.Frame(bottom_frame, bg="#0a2158")
        buttons_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        start_button = tk.Button(buttons_frame, text="Start", font=("Arial", 12), fg="white", bg="#28a745")
        start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        stop_button = tk.Button(buttons_frame, text="Stop", font=("Arial", 12), fg="white", bg="#dc3545")
        stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        reset_button = tk.Button(buttons_frame, text="Reset", font=("Arial", 12), fg="white", bg="#ffc107")
        reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        home_button = tk.Button(buttons_frame, text="Home", font=("Arial", 12), fg="white", bg="#6c757d")
        home_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        settings_button = tk.Button(buttons_frame, text="Settings", font=("Arial", 12), fg="white", bg="#6c757d")
        settings_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        reports_button = tk.Button(buttons_frame, text="Reports", font=("Arial", 12), fg="white", bg="#17a2b8")
        reports_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        data_button = tk.Button(buttons_frame, text="Data", font=("Arial", 12), fg="white", bg="#17a2b8")
        data_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        manual_button = tk.Button(buttons_frame, text="Manual", font=("Arial", 12), fg="white", bg="#6f42c1")
        manual_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        exit_button = tk.Button(buttons_frame, text="Exit", font=("Arial", 12), fg="white", bg="#dc3545")
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
        self.load_model_dropdowns()