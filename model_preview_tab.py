import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
import cv2
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading
import time

class ModelPreviewTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.preview_running = False
        
        # Initialize webcam variables
        self.bf_camera = None
        self.od_camera = None
        self.available_cameras = []
        
        # Camera selection checkboxes
        self.od_camera_enabled = tk.BooleanVar(value=True)  # Default OD enabled
        self.bf_camera_enabled = tk.BooleanVar(value=True)  # Default BF enabled
        self.both_cameras_enabled = tk.BooleanVar(value=False)  # Default both disabled
        
        self.detect_available_cameras()
        self.setup_tab()
    
    def setup_tab(self):
        # Create main container with scrollable capability
        main_container = tk.Frame(self.parent, bg="#0a2158")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(main_container, bg="#0a2158", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        scrollable_frame = tk.Frame(self.canvas, bg="#0a2158")
        
        # Configure scrollable frame to expand to canvas width
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            canvas_width = event.width
            self.canvas.itemconfig(canvas_window, width=canvas_width)
        
        def configure_canvas(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_canvas)
        self.canvas.bind("<Configure>", configure_scroll_region)
        
        # Create window in canvas and store reference
        canvas_window = self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel events when mouse enters/leaves the canvas
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Use scrollable_frame as the preview_container
        preview_container = scrollable_frame
        
        # Title Section
        title_frame = tk.Frame(preview_container, bg="#0a2158")
        title_frame.pack(fill=tk.X, padx=5, pady=(5, 15))
        
        title_label = tk.Label(title_frame, text="Model Preview - Real-time Inference", 
                              font=("Arial", 18, "bold"), fg="white", bg="#0a2158")
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Live model predictions with current threshold settings", 
                                 font=("Arial", 12), fg="lightgray", bg="#0a2158")
        subtitle_label.pack()
        
        # Control Panel
        control_frame = tk.LabelFrame(preview_container, text="Preview Controls", 
                                     font=("Arial", 12, "bold"), fg="white", bg="#0a2158", bd=2)
        control_frame.pack(fill=tk.X, padx=5, pady=(0, 15))
        
        # Camera Selection Section
        camera_selection_frame = tk.Frame(control_frame, bg="#0a2158")
        camera_selection_frame.pack(pady=5, padx=10, fill=tk.X)
        
        tk.Label(camera_selection_frame, text="Camera Selection:", 
                font=("Arial", 11, "bold"), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=(0, 10))
        
        # Checkboxes for camera selection
        self.camera_checkbox_frame = tk.Frame(camera_selection_frame, bg="#0a2158")
        self.camera_checkbox_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.setup_camera_selection_controls()
        
        button_frame = tk.Frame(control_frame, bg="#0a2158")
        button_frame.pack(pady=10)
        
        self.start_preview_btn = tk.Button(button_frame, text="▶ Start Preview", 
                                          font=("Arial", 12, "bold"), bg="#28a745", fg="white",
                                          relief="flat", padx=20, pady=8,
                                          command=self.start_preview)
        self.start_preview_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_preview_btn = tk.Button(button_frame, text="⏹ Stop Preview", 
                                         font=("Arial", 12, "bold"), bg="#dc3545", fg="white",
                                         relief="flat", padx=20, pady=8, state="disabled",
                                         command=self.stop_preview)
        self.stop_preview_btn.pack(side=tk.LEFT, padx=10)
        
        # Main content area: Camera Feeds with Predictions
        main_content = tk.Frame(preview_container, bg="#0a2158")
        main_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)
        
        # BF Feed with Predictions
        bf_container = tk.Frame(main_content, bg="#0a2158")
        bf_container.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="nsew")
        
        # BF Prediction Status
        bf_status_frame = tk.Frame(bf_container, bg="#0a2158", height=40)
        bf_status_frame.pack(fill=tk.X, pady=(0, 3))
        bf_status_frame.pack_propagate(False)
        
        self.bf_prediction_status = tk.Label(bf_status_frame, text="● READY", 
                                            font=("Arial", 14, "bold"), fg="#ffc107", bg="#0a2158",
                                            relief="solid", bd=1, padx=15, pady=5)
        self.bf_prediction_status.pack()
        
        bf_feed_frame = tk.LabelFrame(bf_container, text="BF Feed - Live Predictions", 
                                     font=("Arial", 14, "bold"), fg="white", bg="#0a2158", 
                                     width=400, height=350)
        bf_feed_frame.pack(fill=tk.BOTH, expand=True)
        bf_feed_frame.pack_propagate(False)
        
        self.bf_preview_canvas = tk.Canvas(bf_feed_frame, width=380, height=320, bg="black", highlightthickness=0)
        self.bf_preview_canvas.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
        
        # OD Feed with Predictions
        od_container = tk.Frame(main_content, bg="#0a2158")
        od_container.grid(row=0, column=1, padx=(8, 8), pady=5, sticky="nsew")
        
        # OD Prediction Status
        od_status_frame = tk.Frame(od_container, bg="#0a2158", height=40)
        od_status_frame.pack(fill=tk.X, pady=(0, 3))
        od_status_frame.pack_propagate(False)
        
        self.od_prediction_status = tk.Label(od_status_frame, text="● READY", 
                                            font=("Arial", 14, "bold"), fg="#ffc107", bg="#0a2158",
                                            relief="solid", bd=1, padx=15, pady=5)
        self.od_prediction_status.pack()
        
        od_feed_frame = tk.LabelFrame(od_container, text="OD Feed - Live Predictions", 
                                     font=("Arial", 14, "bold"), fg="white", bg="#0a2158", 
                                     width=400, height=350)
        od_feed_frame.pack(fill=tk.BOTH, expand=True)
        od_feed_frame.pack_propagate(False)
        
        self.od_preview_canvas = tk.Canvas(od_feed_frame, width=380, height=320, bg="black", highlightthickness=0)
        self.od_preview_canvas.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
        
        # Threshold Settings Section
        threshold_frame = tk.LabelFrame(preview_container, text="Threshold Settings", 
                                      font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        threshold_frame.pack(fill=tk.X, padx=5, pady=15)
        
        # Split into two columns for OD and BigFace Defect Thresholds
        top_frame = tk.Frame(threshold_frame, bg="#0a2158")
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Left Column: BigFace Defect Thresholds
        left_column = tk.Frame(top_frame, bg="#0a2158")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        
        bf_defect_frame = tk.LabelFrame(left_column, text="Big Face Defect Thresholds", 
                                      font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        bf_defect_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # BigFace defect types
        bf_defect_types = ["Rust", "Dent", "Damage", "Roller"]
        for idx, defect in enumerate(bf_defect_types):
            current_value = self.app.bf_defect_thresholds.get(defect, 50)
            self.app.create_slider(bf_defect_frame, defect, 0, 100, current_value, row=idx, is_od=False)
        
        # Right Column: OD Defect Thresholds
        right_column = tk.Frame(top_frame, bg="#0a2158")
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 0))
        
        od_defect_frame = tk.LabelFrame(right_column, text="OD Defect Thresholds", 
                                      font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        od_defect_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # OD defect types
        od_defect_types = ["Rust", "Dent", "Spherical Mark", "Damage", "Flat Line", "Damage on End", "Roller"]
        for idx, defect in enumerate(od_defect_types):
            current_value = self.app.od_defect_thresholds.get(defect, 50)
            self.app.create_slider(od_defect_frame, defect, 0, 100, current_value, row=idx, is_od=True)
        
        # Model Confidence Thresholds
        conf_frame = tk.LabelFrame(threshold_frame, text="Model Confidence Thresholds", 
                                 font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        conf_frame.pack(fill=tk.X, pady=10)
        
        # OD Model Confidence
        od_conf_frame = tk.Frame(conf_frame, bg="#0a2158", pady=8)
        od_conf_frame.pack(fill=tk.X, padx=5)
        
        od_conf_label = tk.Label(od_conf_frame, text="OD Model Confidence", font=("Arial", 12), 
                               fg="white", bg="#0a2158", width=22, anchor="w")
        od_conf_label.pack(side=tk.LEFT, padx=(5, 15))
        
        if not hasattr(self.app, 'od_conf_threshold'):
            self.app.od_conf_threshold = 0.25
        self.app.od_conf_slider_value = tk.DoubleVar(value=self.app.od_conf_threshold * 100)
        
        od_conf_slider = ttk.Scale(od_conf_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                 length=400, variable=self.app.od_conf_slider_value)
        od_conf_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.app.od_conf_value_label = tk.Label(od_conf_frame, text=f"{int(self.app.od_conf_threshold * 100)}%", 
                                            font=("Arial", 12, "bold"), fg="#ffc107", bg="#0a2158", width=6)
        self.app.od_conf_value_label.pack(side=tk.LEFT, padx=(15, 5))
        
        def update_od_conf_label(val):
            self.app.od_conf_value_label.config(text=f"{int(float(val))}%")
            self.app.od_conf_threshold = float(val) / 100
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()
        
        od_conf_slider.config(command=update_od_conf_label)
        
        # BigFace Model Confidence
        bf_conf_frame = tk.Frame(conf_frame, bg="#0a2158", pady=8)
        bf_conf_frame.pack(fill=tk.X, padx=5)
        
        bf_conf_label = tk.Label(bf_conf_frame, text="BigFace Model Confidence", font=("Arial", 12), 
                               fg="white", bg="#0a2158", width=22, anchor="w")
        bf_conf_label.pack(side=tk.LEFT, padx=(5, 15))
        
        if not hasattr(self.app, 'bf_conf_threshold'):
            self.app.bf_conf_threshold = 0.25
        self.app.bf_conf_slider_value = tk.DoubleVar(value=self.app.bf_conf_threshold * 100)
        
        bf_conf_slider = ttk.Scale(bf_conf_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                 length=400, variable=self.app.bf_conf_slider_value)
        bf_conf_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.app.bf_conf_value_label = tk.Label(bf_conf_frame, text=f"{int(self.app.bf_conf_threshold * 100)}%", 
                                            font=("Arial", 12, "bold"), fg="#ffc107", bg="#0a2158", width=6)
        self.app.bf_conf_value_label.pack(side=tk.LEFT, padx=(15, 5))
        
        def update_bf_conf_label(val):
            self.app.bf_conf_value_label.config(text=f"{int(float(val))}%")
            self.app.bf_conf_threshold = float(val) / 100
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()
        
        bf_conf_slider.config(command=update_bf_conf_label)
        
        # Save Button
        save_button = tk.Button(threshold_frame, text="Save Settings", font=("Arial", 12, "bold"),
                              bg="#28a745", fg="white", command=self.app.save_all_thresholds)
        save_button.pack(pady=20)
        
        # Initialize
        self.setup_preview_placeholders()
        
        # Load current threshold values
        if hasattr(self.app, 'od_defect_thresholds'):
            for defect, value in self.app.od_defect_thresholds.items():
                if hasattr(self.app, f'od_{defect.lower().replace(" ", "_")}_slider'):
                    slider = getattr(self.app, f'od_{defect.lower().replace(" ", "_")}_slider')
                    slider.set(value)
        
        if hasattr(self.app, 'bf_defect_thresholds'):
            for defect, value in self.app.bf_defect_thresholds.items():
                if hasattr(self.app, f'bf_{defect.lower().replace(" ", "_")}_slider'):
                    slider = getattr(self.app, f'bf_{defect.lower().replace(" ", "_")}_slider')
                    slider.set(value)
    
    def create_compact_stat_label(self, parent, text, var, row):
        label = tk.Label(parent, text=text, font=("Arial", 9), fg="white", bg="#0a2158", anchor="w")
        label.grid(row=row, column=0, sticky="w", padx=5, pady=1)
        value_label = tk.Label(parent, textvariable=var, font=("Arial", 9, "bold"), fg="white", bg="#0a2158")
        value_label.grid(row=row, column=1, sticky="e", padx=5, pady=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
    
    def setup_preview_placeholders(self):
        def update_bf_placeholder():
            self.bf_preview_canvas.delete("bf_placeholder")
            canvas_width = self.bf_preview_canvas.winfo_width()
            canvas_height = self.bf_preview_canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                self.bf_preview_canvas.create_rectangle(10, 10, canvas_width-10, canvas_height-10, 
                                                       outline="gray", width=2, fill="black", tags="bf_placeholder")
                self.bf_preview_canvas.create_text(canvas_width//2, canvas_height//2, 
                                                  text="BF Model Preview\n\nStart Preview to see\nlive predictions", 
                                                  fill="white", font=("Arial", 11), 
                                                  justify=tk.CENTER, tags="bf_placeholder")
        
        def update_od_placeholder():
            self.od_preview_canvas.delete("od_placeholder")
            canvas_width = self.od_preview_canvas.winfo_width()
            canvas_height = self.od_preview_canvas.winfo_height()
            if canvas_width > 1 and canvas_height > 1:
                self.od_preview_canvas.create_rectangle(10, 10, canvas_width-10, canvas_height-10, 
                                                       outline="gray", width=2, fill="black", tags="od_placeholder")
                self.od_preview_canvas.create_text(canvas_width//2, canvas_height//2, 
                                                  text="OD Model Preview\n\nStart Preview to see\nlive predictions", 
                                                  fill="white", font=("Arial", 11), 
                                                  justify=tk.CENTER, tags="od_placeholder")
        
        self.bf_preview_canvas.bind("<Configure>", lambda e: update_bf_placeholder())
        self.od_preview_canvas.bind("<Configure>", lambda e: update_od_placeholder())
        
        self.parent.after(100, update_bf_placeholder)
        self.parent.after(100, update_od_placeholder)
    
    def detect_available_cameras(self):
        """Detect available cameras on the system"""
        self.available_cameras = []
        
        # Test cameras 0 through 4 (most systems won't have more than 5 cameras)
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self.available_cameras.append(i)
                cap.release()
        
        if not self.available_cameras:
            self.available_cameras = [0]  # Default fallback
    
    def setup_camera_selection_controls(self):
        """Setup checkboxes for camera selection"""
        for widget in self.camera_checkbox_frame.winfo_children():
            widget.destroy()
        
        # Individual camera checkboxes with specific camera assignments
        if len(self.available_cameras) >= 1:
            # OD Camera Checkbox (always uses Camera 0)
            self.od_checkbox = tk.Checkbutton(self.camera_checkbox_frame, 
                                            text="OD Camera (0)", 
                                            variable=self.od_camera_enabled,
                                            font=("Arial", 10), fg="white", bg="#0a2158",
                                            selectcolor="#0a2158", activebackground="#0a2158",
                                            activeforeground="white",
                                            command=self.on_camera_selection_change)
            self.od_checkbox.pack(side=tk.LEFT, padx=5)
            
            # BigFace Camera Checkbox (always uses Camera 1 if available)
            bf_available = len(self.available_cameras) >= 2
            bf_text = "BigFace Camera (1)" if bf_available else "BigFace Camera (1) - Not Available"
            bf_color = "white" if bf_available else "gray"
            
            self.bf_checkbox = tk.Checkbutton(self.camera_checkbox_frame, 
                                            text=bf_text, 
                                            variable=self.bf_camera_enabled,
                                            font=("Arial", 10), fg=bf_color, bg="#0a2158",
                                            selectcolor="#0a2158", activebackground="#0a2158",
                                            activeforeground=bf_color,
                                            state="normal" if bf_available else "disabled",
                                            command=self.on_camera_selection_change)
            self.bf_checkbox.pack(side=tk.LEFT, padx=5)
            
            # Both Cameras Checkbox (only if both cameras available)
            if len(self.available_cameras) >= 2:
                self.both_checkbox = tk.Checkbutton(self.camera_checkbox_frame, 
                                                  text="Both Cameras (0 & 1)", 
                                                  variable=self.both_cameras_enabled,
                                                  font=("Arial", 10), fg="white", bg="#0a2158",
                                                  selectcolor="#0a2158", activebackground="#0a2158",
                                                  activeforeground="white",
                                                  command=self.on_camera_selection_change)
                self.both_checkbox.pack(side=tk.LEFT, padx=5)
            else:
                # Show disabled "Both Cameras" option with warning
                disabled_both = tk.Checkbutton(self.camera_checkbox_frame, 
                                              text="Both Cameras - Need 2 Cameras", 
                                              variable=self.both_cameras_enabled,
                                              font=("Arial", 10), fg="gray", bg="#0a2158",
                                              selectcolor="#0a2158", activebackground="#0a2158",
                                              activeforeground="gray",
                                              state="disabled")
                disabled_both.pack(side=tk.LEFT, padx=5)
        
        # Camera status display and refresh button
        status_frame = tk.Frame(self.camera_checkbox_frame, bg="#0a2158")
        status_frame.pack(side=tk.RIGHT, padx=10)
        
        status_text = f"Available: {len(self.available_cameras)} camera(s) detected"
        self.camera_status_label = tk.Label(status_frame, 
                                           text=status_text,
                                           font=("Arial", 9), fg="lightgray", bg="#0a2158")
        self.camera_status_label.pack(side=tk.LEFT)
        
        refresh_btn = tk.Button(status_frame, text="🔄", 
                               font=("Arial", 8), bg="#17a2b8", fg="white",
                               relief="flat", padx=5, pady=1,
                               command=self.refresh_cameras)
        refresh_btn.pack(side=tk.LEFT, padx=(5, 0))
    
    def on_camera_selection_change(self):
        """Handle camera selection checkbox changes with validation"""
        # Check for camera availability and show warnings
        bf_enabled = self.bf_camera_enabled.get()
        
        if bf_enabled and len(self.available_cameras) < 2:
            self.bf_camera_enabled.set(False)  # Disable if camera not available
            print("⚠️ BigFace Camera (1) not available - only 1 camera detected")
    
    def refresh_cameras(self):
        """Refresh the list of available cameras"""
        if self.preview_running:
            print("⚠️ Stop preview before refreshing cameras")
            return
        
        print("🔄 Refreshing camera list...")
        self.detect_available_cameras()
        self.setup_camera_selection_controls()
        print(f"✅ Found {len(self.available_cameras)} camera(s)")
    
    def start_preview(self):
        """Start the model preview with live camera feeds"""
        if self.preview_running:
            return
        
        # Validate camera selection
        if not (self.od_camera_enabled.get() or self.bf_camera_enabled.get() or self.both_cameras_enabled.get()):
            print("❌ Please select at least one camera option!")
            return
        
        try:
            # Initialize cameras based on selection
            if self.both_cameras_enabled.get():
                # Use separate cameras for OD and BF
                if len(self.available_cameras) >= 2:
                    try:
                        self.od_camera = cv2.VideoCapture(0)
                        if not self.od_camera.isOpened():
                            print("❌ Error: Camera 0 (OD) failed to open!")
                            return
                        
                        self.bf_camera = cv2.VideoCapture(1)
                        if not self.bf_camera.isOpened():
                            print("❌ Error: Camera 1 (BF) failed to open!")
                            self.od_camera.release()
                            self.od_camera = None
                            return
                        
                        # Set camera properties for better performance
                        for camera in [self.od_camera, self.bf_camera]:
                            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            camera.set(cv2.CAP_PROP_FPS, 30)
                        
                        print("📷 Using Camera 0 for OD and Camera 1 for BF")
                        
                    except Exception as e:
                        print(f"❌ Error initializing dual cameras: {str(e)}")
                        return
                else:
                    print("❌ Two cameras required for dual camera mode!")
                    return
            
            elif self.od_camera_enabled.get():
                try:
                    self.od_camera = cv2.VideoCapture(0)
                    if not self.od_camera.isOpened():
                        print("❌ Error: Camera 0 (OD) failed to open!")
                        return
                    
                    self.od_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.od_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.od_camera.set(cv2.CAP_PROP_FPS, 30)
                    
                    print("📷 Using Camera 0 for OD feed")
                except:
                    print("❌ Camera 0 not available for OD feed!")
                    return
            
            elif self.bf_camera_enabled.get():
                try:
                    self.bf_camera = cv2.VideoCapture(1 if len(self.available_cameras) > 1 else 0)
                    if not self.bf_camera.isOpened():
                        print("❌ Error: Camera 1 (BF) failed to open!")
                        return
                    
                    self.bf_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.bf_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.bf_camera.set(cv2.CAP_PROP_FPS, 30)
                    
                    print("📷 Using Camera 1 for BF feed")
                except:
                    print("❌ Camera 1 not available for BF feed!")
                    return
            
        except Exception as e:
            print(f"❌ Camera initialization error: {str(e)}")
            return
        
        # Start preview
        self.preview_running = True
        self.start_preview_btn.config(state="disabled")
        self.stop_preview_btn.config(state="normal")
        
        # Start camera threads
        if self.bf_camera:
            threading.Thread(target=self.run_bf_preview, daemon=True).start()
            self.bf_prediction_status.config(text="● RUNNING", fg="#00ff00")
        else:
            self.bf_prediction_status.config(text="● DISABLED", fg="#6c757d")
        
        if self.od_camera:
            threading.Thread(target=self.run_od_preview, daemon=True).start()
            self.od_prediction_status.config(text="● RUNNING", fg="#00ff00")
        else:
            self.od_prediction_status.config(text="● DISABLED", fg="#6c757d")
        
        print("🔄 Model preview started with dedicated camera feeds")
    
    def stop_preview(self):
        """Stop the model preview and release cameras"""
        self.preview_running = False
        
        # Release cameras
        if self.bf_camera:
            self.bf_camera.release()
            self.bf_camera = None
            self.bf_prediction_status.config(text="● READY", fg="#ffc107")
        
        if self.od_camera:
            self.od_camera.release()
            self.od_camera = None
            self.od_prediction_status.config(text="● READY", fg="#ffc107")
        
        # Update UI
        self.start_preview_btn.config(state="normal")
        self.stop_preview_btn.config(state="disabled")
        
        print("⏹️ Model preview stopped - webcam released")
    
    def run_bf_preview(self):
        if self.bf_camera is None:
            return  # BF camera not enabled
            
        while self.preview_running and self.bf_camera and self.bf_camera.isOpened():
            try:
                ret, frame = self.bf_camera.read()
                if not ret:
                    print("❌ BF Camera: Failed to read frame")
                    time.sleep(0.1)
                    continue
                
                # Get threshold from app settings
                threshold = getattr(self.app, 'bf_conf_threshold', 0.25)
                
                # Run YOLO inference if model is available
                if hasattr(self.app, 'model_bf') and self.app.model_bf:
                    try:
                        results = self.app.model_bf(frame, conf=threshold, verbose=False)
                        
                        # Process results
                        annotated_frame = frame.copy()
                        max_confidence = 0
                        
                        for result in results:
                            if result.boxes is not None and len(result.boxes) > 0:
                                for box in result.boxes:
                                    confidence = float(box.conf[0])
                                    max_confidence = max(max_confidence, confidence)
                                    
                                    # Draw bounding boxes
                                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                                    color = (0, 255, 0) if confidence >= threshold else (0, 0, 255)
                                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                                    
                                    # Add confidence text
                                    label = f"BF: {confidence:.2f}"
                                    cv2.putText(annotated_frame, label, (x1, y1-10), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        # Update status indicator
                        if max_confidence > 0:
                            if max_confidence >= threshold:
                                status = "ACCEPTED"
                                status_color = "#00ff00"
                            else:
                                status = "REJECTED"
                                status_color = "#ff0000"
                            
                            self.parent.after(0, lambda s=status, c=status_color: 
                                             self.bf_prediction_status.config(text=f"● {s}", fg=c))
                        
                        # Convert and display the frame
                        processed_frame = self.process_frame_for_display(annotated_frame)
                        self.parent.after(0, lambda img=processed_frame: self.update_bf_canvas(img))
                        
                    except Exception as model_error:
                        # Fallback: show raw camera feed
                        processed_frame = self.process_frame_for_display(frame)
                        self.parent.after(0, lambda img=processed_frame: self.update_bf_canvas(img))
                        print(f"BF Model inference error: {model_error}")
                
                else:
                    # No model available - show raw camera feed
                    processed_frame = self.process_frame_for_display(frame)
                    self.parent.after(0, lambda img=processed_frame: self.update_bf_canvas(img))
                
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"BF Preview error: {e}")
                break
    
    def run_od_preview(self):
        if self.od_camera is None:
            return  # OD camera not enabled
            
        while self.preview_running and self.od_camera and self.od_camera.isOpened():
            try:
                # Small delay to avoid camera conflicts (only needed when sharing cameras)
                if self.bf_camera == self.od_camera:
                    time.sleep(0.02)
                ret, frame = self.od_camera.read()
                if not ret:
                    print("❌ OD Camera: Failed to read frame")
                    time.sleep(0.1)
                    continue
                
                # Get threshold from app settings
                threshold = getattr(self.app, 'od_conf_threshold', 0.25)
                
                # Run YOLO inference if model is available
                if hasattr(self.app, 'model_od') and self.app.model_od:
                    try:
                        results = self.app.model_od(frame, conf=threshold, verbose=False)
                        
                        # Process results
                        annotated_frame = frame.copy()
                        max_confidence = 0
                        
                        for result in results:
                            if result.boxes is not None and len(result.boxes) > 0:
                                for box in result.boxes:
                                    confidence = float(box.conf[0])
                                    max_confidence = max(max_confidence, confidence)
                                    
                                    # Draw bounding boxes
                                    x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                                    color = (0, 255, 0) if confidence >= threshold else (0, 0, 255)
                                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                                    
                                    # Add confidence text
                                    label = f"OD: {confidence:.2f}"
                                    cv2.putText(annotated_frame, label, (x1, y1-10), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                        
                        # Update status indicator
                        if max_confidence > 0:
                            if max_confidence >= threshold:
                                status = "ACCEPTED"
                                status_color = "#00ff00"
                            else:
                                status = "REJECTED"
                                status_color = "#ff0000"
                            
                            self.parent.after(0, lambda s=status, c=status_color: 
                                             self.od_prediction_status.config(text=f"● {s}", fg=c))
                        
                        # Convert and display the frame
                        processed_frame = self.process_frame_for_display(annotated_frame)
                        self.parent.after(0, lambda img=processed_frame: self.update_od_canvas(img))
                        
                    except Exception as model_error:
                        # Fallback: show raw camera feed
                        processed_frame = self.process_frame_for_display(frame)
                        self.parent.after(0, lambda img=processed_frame: self.update_od_canvas(img))
                        print(f"OD Model inference error: {model_error}")
                
                else:
                    # No model available - show raw camera feed
                    processed_frame = self.process_frame_for_display(frame)
                    self.parent.after(0, lambda img=processed_frame: self.update_od_canvas(img))
                
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"OD Preview error: {e}")
                break
    
    def process_frame_for_display(self, frame):
        """Convert OpenCV frame to PIL Image for display in canvas"""
        try:
            # Resize frame to fit canvas
            height, width = frame.shape[:2]
            target_width, target_height = 380, 320
            
            # Calculate scaling to maintain aspect ratio
            scale = min(target_width/width, target_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize frame
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            
            # Create PIL image
            pil_image = Image.fromarray(rgb_frame)
            
            # Create a black background of target size
            final_image = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            
            # Center the resized image on the black background
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            final_image.paste(pil_image, (x_offset, y_offset))
            
            return final_image
            
        except Exception as e:
            print(f"Error processing frame for display: {e}")
            # Return a black image as fallback
            return Image.new('RGB', (380, 320), (0, 0, 0))
    
    def update_bf_canvas(self, pil_image):
        """Update the BigFace canvas with the processed image"""
        try:
            photo = ImageTk.PhotoImage(pil_image)
            self.bf_preview_canvas.delete("all")
            self.bf_preview_canvas.create_image(190, 160, image=photo)
            self.bf_preview_canvas.image = photo
        except Exception as e:
            print(f"Error updating BF canvas: {e}")
    
    def update_od_canvas(self, pil_image):
        """Update the OD canvas with the processed image"""
        try:
            photo = ImageTk.PhotoImage(pil_image)
            self.od_preview_canvas.delete("all")
            self.od_preview_canvas.create_image(190, 160, image=photo)
            self.od_preview_canvas.image = photo
        except Exception as e:
            print(f"Error updating OD canvas: {e}") 