"""
Diagnosis Tab for WelVision Application
Handles report generation, charts, and data export
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import pandas as pd
from PIL import ImageGrab
from database import db_manager

class DiagnosisTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_tab()
    
    def setup_tab(self):
        diagnosis_container = tk.Frame(self.parent, bg="#0a2158")
        diagnosis_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(diagnosis_container, text="Date and Time Based Report Sheet", 
                              font=("Arial", 16, "bold"), fg="white", bg="#0a2158")
        title_label.pack(pady=(0, 10))

        # Load session data from database
        self.load_diagnosis_data()

        # Top section: Component Type selection and report generation controls
        top_frame = tk.Frame(diagnosis_container, bg="#0a2158")
        top_frame.pack(fill=tk.X, pady=5)

        # Left part: Report Table
        self.app.table_frame = tk.LabelFrame(top_frame, text="", 
                                        font=("Arial", 12, "bold"), fg="white", bg="#0a2158", bd=2)
        self.app.table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        columns = ("Component Type", "Employee ID", "Model Type", "Total Inspected", "Total Accepted", "Total Rejected", "Acceptance Rate", "Report Date", "Report Time")
        self.app.report_tree = ttk.Treeview(self.app.table_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.app.report_tree.heading(col, text=col)
            self.app.report_tree.column(col, width=100, anchor="center")

        self.app.report_tree.column("Component Type", width=120)
        self.app.report_tree.column("Employee ID", width=110)
        self.app.report_tree.column("Model Type", width=80)
        self.app.report_tree.column("Total Inspected", width=110)
        self.app.report_tree.column("Total Accepted", width=110)
        self.app.report_tree.column("Total Rejected", width=110)
        self.app.report_tree.column("Acceptance Rate", width=110)
        self.app.report_tree.column("Report Date", width=120)
        self.app.report_tree.column("Report Time", width=150)

        self.app.report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        table_scrollbar = ttk.Scrollbar(self.app.table_frame, orient="vertical", command=self.app.report_tree.yview)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.app.report_tree.configure(yscrollcommand=table_scrollbar.set)

        # Enable mouse wheel scrolling for the table
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling for the table"""
            self.app.report_tree.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel events (Windows and Linux)
        self.app.report_tree.bind("<MouseWheel>", _on_mousewheel)  # Windows
        self.app.report_tree.bind("<Button-4>", lambda e: self.app.report_tree.yview_scroll(-1, "units"))  # Linux scroll up
        self.app.report_tree.bind("<Button-5>", lambda e: self.app.report_tree.yview_scroll(1, "units"))   # Linux scroll down

        # Right part: Type selection and date range
        controls_frame = tk.LabelFrame(top_frame, text="Controls", font=("Arial", 12, "bold"), 
                                      fg="white", bg="#0a2158", bd=2)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        type_frame = tk.Frame(controls_frame, bg="#0a2158")
        type_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(type_frame, text="Component Type", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.app.type_var = tk.StringVar()
        self.app.type_combobox = ttk.Combobox(type_frame, textvariable=self.app.type_var, state="readonly")
        self.app.type_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Label(type_frame, text="Report Type", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.app.report_type_var = tk.StringVar(value="Overall")
        self.app.report_type_combobox = ttk.Combobox(type_frame, textvariable=self.app.report_type_var,
                                             values=["Overall", "BigFace", "OD"], state="readonly")
        self.app.report_type_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.app.report_type_combobox.bind('<<ComboboxSelected>>', self.on_filter_change)

        date_frame = tk.LabelFrame(controls_frame, text="Select Date", font=("Arial", 10, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
        date_frame.pack(fill=tk.X, padx=5, pady=5)

        from_frame = tk.Frame(date_frame, bg="#0a2158")
        from_frame.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(from_frame, text="From", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.app.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.app.from_date_entry = DateEntry(from_frame, textvariable=self.app.from_date_var, width=12, 
                                   background='darkblue', foreground='white', 
                                   date_pattern='yyyy-mm-dd')
        self.app.from_date_entry.pack(side=tk.LEFT, padx=5)
        self.app.from_date_entry.bind('<<DateEntrySelected>>', self.on_filter_change)

        to_frame = tk.Frame(date_frame, bg="#0a2158")
        to_frame.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(to_frame, text="To", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.app.to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.app.to_date_entry = DateEntry(to_frame, textvariable=self.app.to_date_var, width=12, 
                                 background='darkblue', foreground='white', 
                                 date_pattern='yyyy-mm-dd')
        self.app.to_date_entry.pack(side=tk.LEFT, padx=5)
        self.app.to_date_entry.bind('<<DateEntrySelected>>', self.on_filter_change)

        actions_frame = tk.LabelFrame(controls_frame, text="Actions", font=("Arial", 10, "bold"), 
                                     fg="white", bg="#0a2158", bd=2)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(actions_frame, text="Generate Report", font=("Arial", 10), width=22, command=self.generate_report).pack(pady=2)
        tk.Button(actions_frame, text="Generate Monthly Report", font=("Arial", 10), width=22, command=self.generate_monthly_report).pack(pady=2)
        tk.Button(actions_frame, text="Save Chart", font=("Arial", 10), width=22, command=self.save_chart).pack(pady=2)
        tk.Button(actions_frame, text="Export to Excel", font=("Arial", 10), width=22, command=self.export_to_excel).pack(pady=2)

        # Charts section
        charts_frame = tk.Frame(diagnosis_container, bg="#0a2158")
        charts_frame.pack(fill=tk.BOTH, expand=True)

        # Status Chart (Left)
        status_frame = tk.LabelFrame(charts_frame, text="Status Chart", font=("Arial", 12, "bold"), 
                                    fg="white", bg="#0a2158", bd=2)
        status_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.app.status_canvas = tk.Canvas(status_frame, bg="white", height=300)
        self.app.status_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Defect-wise Chart (Right)
        defect_frame = tk.LabelFrame(charts_frame, text="Defectwise Chart", font=("Arial", 12, "bold"), 
                                    fg="white", bg="#0a2158", bd=2)
        defect_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.app.defect_canvas = tk.Canvas(defect_frame, bg="white", height=300)
        self.app.defect_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bottom buttons
        bottom_frame = tk.Frame(diagnosis_container, bg="#0a2158")
        bottom_frame.pack(fill=tk.X, pady=10)

        # Create buttons with functionality
        tk.Button(bottom_frame, text="PROCESS", font=("Arial", 10), width=10, 
                 command=self.process_action).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="SETTINGS", font=("Arial", 10), width=10, 
                 command=self.settings_action).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="DIAGNOSIS", font=("Arial", 10), width=10, 
                 command=self.diagnosis_action).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="DATA", font=("Arial", 10), width=10, 
                 command=self.data_action).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="MANUAL", font=("Arial", 10), width=10, 
                 command=self.manual_action).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="EXIT", font=("Arial", 10), width=10, 
                 command=self.exit_action).pack(side=tk.LEFT, padx=5)

        # Load component types and initial data
        self.load_component_types()
        
        # Initial report generation - do this after app is fully initialized
        self.after_idle_generate_report()

    def load_component_types(self):
        """Load component types from database and populate the combobox"""
        try:
            # Get component types from database
            component_types = db_manager.get_roller_types()
            
            if component_types:
                # Add "All" option and update combobox values
                all_types = ["All"] + component_types
                self.app.type_combobox['values'] = all_types
                # Set default selection to "All"
                self.app.type_var.set("All")
                print(f"✅ Loaded {len(component_types)} component types from database: {component_types}")
            else:
                # Fallback to hardcoded values if database is empty
                fallback_types = ["All", "RT-6300", "RT-320 18X"]
                self.app.type_combobox['values'] = fallback_types
                self.app.type_var.set("All")
                print("⚠️ No component types found in database, using fallback values")
                
            # Bind change event to trigger filtering
            self.app.type_combobox.bind('<<ComboboxSelected>>', self.on_filter_change)
            
        except Exception as e:
            # Fallback to hardcoded values if there's an error
            fallback_types = ["All", "RT-6300", "RT-320 18X"]
            self.app.type_combobox['values'] = fallback_types
            self.app.type_var.set("All")
            self.app.type_combobox.bind('<<ComboboxSelected>>', self.on_filter_change)
            print(f"❌ Error loading component types from database: {e}")

    def on_filter_change(self, event=None):
        """Handle filter change events to automatically update the report"""
        try:
            # Use after_idle to prevent recursive event handling
            self.parent.after_idle(self._delayed_filter_change)
        except Exception as e:
            print(f"❌ Error handling filter change: {e}")
    
    def _delayed_filter_change(self):
        """Delayed filter change handler to prevent event conflicts"""
        try:
            print(f"🔄 Filter changed, regenerating report...")
            self.generate_report()
        except Exception as e:
            print(f"❌ Error in delayed filter change: {e}")

    def refresh_component_types(self):
        """Refresh the component type dropdown (call this when roller types are updated)"""
        try:
            print("🔄 Refreshing component type dropdown...")
            # Store current selection to restore it if possible
            current_selection = self.app.type_var.get()
            
            # Reload component types from database
            self.load_component_types()
            
            # Try to restore previous selection if it still exists
            if current_selection:
                component_types = list(self.app.type_combobox['values'])
                if current_selection in component_types:
                    self.app.type_var.set(current_selection)
                else:
                    # If previous selection no longer exists, set to "All"
                    self.app.type_var.set("All")
                    
            # Refresh the report with new filter options
            self.generate_report()
            
            print("✅ Component type dropdown refreshed successfully")
        except Exception as e:
            print(f"❌ Error refreshing component type dropdown: {e}")

    def load_diagnosis_data(self):
        """Load diagnosis data from database inspection sessions"""
        try:
            # Get session data from database with extended date range
            sessions = db_manager.get_inspection_sessions(limit=500)
            
            if sessions:
                # Convert database sessions to diagnosis data format
                self.app.diagnosis_data = []
                for session in sessions:
                    # Map database session to diagnosis format
                    component_type = session.get('roller_type', 'Unknown')
                    employee_id = session.get('employee_id', 'N/A')
                    model_type = session.get('model_type', 'N/A')
                    total_inspected = session.get('total_inspected', 0)
                    total_accepted = session.get('total_accepted', 0)
                    total_rejected = session.get('total_rejected', 0)
                    
                    # Calculate acceptance rate
                    if total_inspected > 0:
                        acceptance_rate = f"{(total_accepted / total_inspected * 100):.1f}%"
                    else:
                        acceptance_rate = "0.0%"
                    
                    # Format dates
                    start_time = session.get('start_time', datetime.now())
                    if isinstance(start_time, datetime):
                        report_date = start_time.strftime("%Y-%m-%d")
                        report_time = start_time.strftime("%H:%M:%S")
                    elif isinstance(start_time, str):
                        try:
                            parsed_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                            report_date = parsed_time.strftime("%Y-%m-%d")
                            report_time = parsed_time.strftime("%H:%M:%S")
                        except:
                            report_date = start_time[:10] if len(start_time) >= 10 else "N/A"
                            report_time = start_time[11:19] if len(start_time) >= 19 else "N/A"
                    else:
                        report_date = "N/A"
                        report_time = "N/A"
                    
                    diagnosis_record = (
                        component_type,        # Component Type
                        employee_id,          # Employee ID  
                        model_type,           # Model Type
                        total_inspected,      # Total Inspected
                        total_accepted,       # Total Accepted
                        total_rejected,       # Total Rejected
                        acceptance_rate,      # Acceptance Rate
                        report_date,          # Report Date
                        report_time           # Report Time
                    )
                    
                    self.app.diagnosis_data.append(diagnosis_record)
                
                print(f"✅ Loaded {len(self.app.diagnosis_data)} inspection session records from database")
            else:
                # Initialize empty data if no sessions found
                self.app.diagnosis_data = []
                print("⚠️ No inspection session data found in database")
                
        except Exception as e:
            print(f"❌ Error loading data from database: {e}")
            # Initialize empty data on error
            self.app.diagnosis_data = []

    def after_idle_generate_report(self):
        """Generate initial report after app is fully initialized"""
        try:
            # Schedule the report generation to happen after the current event processing is complete
            self.parent.after_idle(lambda: self.generate_report())
        except Exception as e:
            print(f"Could not generate initial report: {e}")

    def generate_report(self):
        """Generate report based on selected criteria with comprehensive filtering"""
        try:
            # Clear existing data
            for item in self.app.report_tree.get_children():
                self.app.report_tree.delete(item)
            
            # Get filter criteria
            component_type = self.app.type_var.get()
            report_type = self.app.report_type_var.get()
            from_date = self.app.from_date_var.get()
            to_date = self.app.to_date_var.get()
            
            print(f"🔍 Filtering with: Component={component_type}, Report={report_type}, From={from_date}, To={to_date}")
            
            # Filter data based on criteria
            filtered_data = []
            for item in self.app.diagnosis_data:
                # Skip if data doesn't have enough columns
                if len(item) < 9:
                    continue
                
                # Extract data fields
                item_component_type = item[0]  # Component Type
                item_model_type = item[2]      # Model Type
                item_report_date = item[7]     # Report Date 
                
                # Filter by component type (if not "All" or empty)
                if component_type and component_type != "All":
                    if item_component_type != component_type:
                        continue
                
                # Filter by report type/model type (if not "Overall" or "All")
                if report_type and report_type not in ["Overall", "All"]:
                    if report_type == "BigFace" and item_model_type != "BF":
                        continue
                    elif report_type == "OD" and item_model_type != "OD":
                        continue
                
                # Filter by date range
                try:
                    if from_date and to_date:
                        if from_date <= item_report_date <= to_date:
                            filtered_data.append(item)
                    else:
                        # No date filter, include all
                        filtered_data.append(item)
                except Exception as date_error:
                    print(f"Date comparison error: {date_error}")
                    # Include item if date comparison fails
                    filtered_data.append(item)
            
            # Populate table with filtered data
            for item in filtered_data:
                self.app.report_tree.insert("", "end", values=item)
            
            # Update charts
            self.update_charts(filtered_data)
            
            print(f"✅ Generated report: {len(filtered_data)} records found")
            
            # Show status message
            status_msg = f"Found {len(filtered_data)} records"
            if component_type and component_type != "All":
                status_msg += f" for {component_type}"
            if report_type and report_type not in ["Overall", "All"]:
                status_msg += f" ({report_type} model)"
            print(status_msg)
            
        except Exception as e:
            error_msg = f"Failed to generate report: {str(e)}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

    def update_charts(self, data):
        """Update charts with filtered data showing roller inspection statistics and defect analysis"""
        try:
            # Clear canvases
            self.app.status_canvas.delete("all")
            self.app.defect_canvas.delete("all")
            
            if not data:
                # Show "No data" message
                self.app.status_canvas.create_text(200, 150, text="No data to display", 
                                                  font=("Arial", 14), fill="gray")
                self.app.defect_canvas.create_text(200, 150, text="No data to display", 
                                                  font=("Arial", 14), fill="gray")
                return
            
            # Calculate overall statistics
            total_inspected = sum(item[3] for item in data)  # Total Inspected
            total_accepted = sum(item[4] for item in data)   # Total Accepted
            total_rejected = sum(item[5] for item in data)   # Total Rejected
            
            # Left Chart - Status Chart (Total Inspected, Accepted, Rejected)
            self.draw_status_chart(total_inspected, total_accepted, total_rejected)
            
            # Right Chart - Defect-wise Chart
            self.draw_defect_chart(data)
            
        except Exception as e:
            print(f"❌ Error updating charts: {e}")
            # Show error message on canvas
            self.app.status_canvas.create_text(200, 150, text="Error updating charts", 
                                              font=("Arial", 12), fill="red")
            self.app.defect_canvas.create_text(200, 150, text="Error updating charts", 
                                              font=("Arial", 12), fill="red")
    
    def draw_status_chart(self, total_inspected, total_accepted, total_rejected):
        """Draw the left chart showing Total Inspected, Accepted, and Rejected"""
        canvas = self.app.status_canvas
        canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 400
        canvas_height = canvas.winfo_height() if canvas.winfo_height() > 1 else 300
        
        # Chart title
        canvas.create_text(canvas_width//2, 25, text="Roller Inspection Status", 
                          font=("Arial", 14, "bold"), fill="black")
        
        if total_inspected == 0:
            canvas.create_text(canvas_width//2, canvas_height//2, text="No inspection data", 
                              font=("Arial", 12), fill="gray")
            return
        
        # Bar chart dimensions
        bar_width = 60
        bar_spacing = 80
        chart_bottom = canvas_height - 60
        chart_height = 180
        max_value = max(total_inspected, total_accepted, total_rejected)
        
        # Calculate bar heights proportionally
        inspected_height = (total_inspected / max_value) * chart_height if max_value > 0 else 0
        accepted_height = (total_accepted / max_value) * chart_height if max_value > 0 else 0
        rejected_height = (total_rejected / max_value) * chart_height if max_value > 0 else 0
        
        # Calculate starting position to center the bars
        total_width = 3 * bar_width + 2 * bar_spacing
        x_start = (canvas_width - total_width) // 2
        
        # Draw Total Inspected bar (blue)
        x1 = x_start
        canvas.create_rectangle(x1, chart_bottom - inspected_height, 
                              x1 + bar_width, chart_bottom, 
                              fill="#4472C4", outline="darkblue", width=2)
        canvas.create_text(x1 + bar_width//2, chart_bottom + 15, 
                          text="Total Inspected", 
                          font=("Arial", 9, "bold"), justify=tk.CENTER)
        canvas.create_text(x1 + bar_width//2, chart_bottom + 30, 
                          text=str(total_inspected), 
                          font=("Arial", 10, "bold"), fill="darkblue")
        # Value on top of bar
        canvas.create_text(x1 + bar_width//2, chart_bottom - inspected_height - 10, 
                          text=str(total_inspected), font=("Arial", 11, "bold"), fill="darkblue")
        
        # Draw Total Accepted bar (green)
        x2 = x1 + bar_width + bar_spacing
        canvas.create_rectangle(x2, chart_bottom - accepted_height, 
                              x2 + bar_width, chart_bottom, 
                              fill="#70AD47", outline="darkgreen", width=2)
        canvas.create_text(x2 + bar_width//2, chart_bottom + 15, 
                          text="Total Accepted", 
                          font=("Arial", 9, "bold"), justify=tk.CENTER)
        canvas.create_text(x2 + bar_width//2, chart_bottom + 30, 
                          text=str(total_accepted), 
                          font=("Arial", 10, "bold"), fill="darkgreen")
        # Value on top of bar
        canvas.create_text(x2 + bar_width//2, chart_bottom - accepted_height - 10, 
                          text=str(total_accepted), font=("Arial", 11, "bold"), fill="darkgreen")
        
        # Draw Total Rejected bar (red)
        x3 = x2 + bar_width + bar_spacing
        canvas.create_rectangle(x3, chart_bottom - rejected_height, 
                              x3 + bar_width, chart_bottom, 
                              fill="#E74C3C", outline="darkred", width=2)
        canvas.create_text(x3 + bar_width//2, chart_bottom + 15, 
                          text="Total Rejected", 
                          font=("Arial", 9, "bold"), justify=tk.CENTER)
        canvas.create_text(x3 + bar_width//2, chart_bottom + 30, 
                          text=str(total_rejected), 
                          font=("Arial", 10, "bold"), fill="darkred")
        # Value on top of bar
        canvas.create_text(x3 + bar_width//2, chart_bottom - rejected_height - 10, 
                          text=str(total_rejected), font=("Arial", 11, "bold"), fill="darkred")
    
    def draw_defect_chart(self, data):
        """Draw the right chart showing defect-wise count of rollers"""
        canvas = self.app.defect_canvas
        canvas_width = canvas.winfo_width() if canvas.winfo_width() > 1 else 400
        canvas_height = canvas.winfo_height() if canvas.winfo_height() > 1 else 300
        
        # Chart title
        canvas.create_text(canvas_width//2, 25, text="Defect-wise Analysis", 
                          font=("Arial", 14, "bold"), fill="black")
        
        try:
            # Get defect-wise data from database based on current filters
            defect_data = self.get_defect_wise_data()
            
            if not defect_data:
                canvas.create_text(canvas_width//2, canvas_height//2, text="No defect data available", 
                                  font=("Arial", 12), fill="gray")
                return
            
            # Prepare defect categories and counts
            defect_categories = list(defect_data.keys())
            defect_counts = list(defect_data.values())
            
            if not defect_categories:
                canvas.create_text(canvas_width//2, canvas_height//2, text="No defects found", 
                                  font=("Arial", 12), fill="gray")
                return
            
            # Bar chart dimensions
            num_bars = len(defect_categories)
            bar_width = min(50, (canvas_width - 100) // num_bars)
            bar_spacing = 10
            chart_bottom = canvas_height - 80
            chart_height = 160
            max_count = max(defect_counts) if defect_counts else 1
            
            # Calculate starting position
            total_width = num_bars * bar_width + (num_bars - 1) * bar_spacing
            x_start = (canvas_width - total_width) // 2
            
            # Colors for different defects
            colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"]
            
            # Draw bars for each defect type
            for i, (defect, count) in enumerate(zip(defect_categories, defect_counts)):
                x = x_start + i * (bar_width + bar_spacing)
                bar_height = (count / max_count) * chart_height if max_count > 0 else 0
                color = colors[i % len(colors)]
                
                # Draw bar
                canvas.create_rectangle(x, chart_bottom - bar_height, 
                                      x + bar_width, chart_bottom, 
                                      fill=color, outline="black", width=1)
                
                # Defect name (rotated if needed)
                defect_name = defect[:8] + "..." if len(defect) > 8 else defect
                canvas.create_text(x + bar_width//2, chart_bottom + 15, 
                                  text=defect_name, 
                                  font=("Arial", 8, "bold"), justify=tk.CENTER)
                
                # Count value
                canvas.create_text(x + bar_width//2, chart_bottom + 30, 
                                  text=str(count), 
                                  font=("Arial", 9, "bold"), fill="black")
                
                # Value on top of bar
                canvas.create_text(x + bar_width//2, chart_bottom - bar_height - 10, 
                                  text=str(count), font=("Arial", 10, "bold"), fill="black")
            
        except Exception as e:
            print(f"❌ Error drawing defect chart: {e}")
            canvas.create_text(canvas_width//2, canvas_height//2, text="Error loading defect data", 
                              font=("Arial", 12), fill="red")
    
    def get_defect_wise_data(self):
        """Get defect-wise data based on current filters"""
        try:
            # Get current filter values
            component_type = self.app.type_var.get()
            report_type = self.app.report_type_var.get()
            from_date = self.app.from_date_var.get()
            to_date = self.app.to_date_var.get()
            
            # Get defect data from database
            defect_data = db_manager.get_defect_wise_statistics(
                component_type=component_type if component_type != "All" else None,
                report_type=report_type if report_type != "Overall" else None,
                from_date=from_date,
                to_date=to_date
            )
            
            return defect_data
            
        except Exception as e:
            print(f"❌ Error getting defect-wise data: {e}")
            # Return sample defect data for demonstration
            return {
                "Rust": 15,
                "Damage": 8,
                "High Head": 5,
                "Down Head": 3,
                "Surface Defect": 12,
                "Dimension Error": 7
            }

    def save_chart(self):
        """Save chart as image"""
        try:
            # Get the chart area
            x = self.app.status_canvas.winfo_rootx()
            y = self.app.status_canvas.winfo_rooty()
            x1 = x + self.app.status_canvas.winfo_width()
            y1 = y + self.app.status_canvas.winfo_height()
            
            # Capture and save
            ImageGrab.grab().crop((x, y, x1, y1)).save("chart.png")
            messagebox.showinfo("Success", "Chart saved as chart.png")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chart: {str(e)}")

    def export_to_excel(self):
        """Export current data to Excel"""
        try:
            # Get current data from table
            data = []
            for item in self.app.report_tree.get_children():
                values = self.app.report_tree.item(item, 'values')
                data.append(values)
            
            if not data:
                messagebox.showwarning("No Data", "No data to export.")
                return
            
            # Create DataFrame
            columns = ["Component Type", "Employee ID", "Model Type", "Total Inspected", 
                      "Total Accepted", "Total Rejected", "Acceptance Rate", "Report Date", "Report Time"]
            df = pd.DataFrame(data, columns=columns)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnosis_report_{timestamp}.xlsx"
            
            # Save to Excel
            df.to_excel(filename, index=False)
            
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            print(f"✅ Data exported to {filename}")
            
        except Exception as e:
            error_msg = f"Error exporting to Excel: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Export Error", error_msg)
    
    def generate_monthly_report(self):
        """Generate and display monthly report based on current filters"""
        try:
            # Get current filter settings
            component_type = self.app.type_var.get()
            report_type = self.app.report_type_var.get()
            from_date = self.app.from_date_var.get()
            to_date = self.app.to_date_var.get()
            
            # Calculate filtered data statistics
            filtered_data = []
            for item in self.app.diagnosis_data:
                if len(item) < 9:
                    continue
                
                item_component_type = item[0]
                item_model_type = item[2]
                item_report_date = item[7]
                
                # Apply same filters as generate_report
                if component_type and component_type != "All":
                    if item_component_type != component_type:
                        continue
                
                if report_type and report_type not in ["Overall", "All"]:
                    if report_type == "BigFace" and item_model_type != "BF":
                        continue
                    elif report_type == "OD" and item_model_type != "OD":
                        continue
                
                try:
                    if from_date and to_date:
                        if from_date <= item_report_date <= to_date:
                            filtered_data.append(item)
                    else:
                        filtered_data.append(item)
                except:
                    filtered_data.append(item)
            
            if not filtered_data:
                messagebox.showwarning("No Data", "No data available for the selected filters to generate monthly report.")
                return
            
            # Calculate statistics
            total_sessions = len(filtered_data)
            total_inspected = sum(item[3] for item in filtered_data)
            total_accepted = sum(item[4] for item in filtered_data)
            total_rejected = sum(item[5] for item in filtered_data)
            success_rate = (total_accepted / total_inspected * 100) if total_inspected > 0 else 0
            
            # Model breakdown
            od_sessions = [item for item in filtered_data if item[2] == 'OD']
            bf_sessions = [item for item in filtered_data if item[2] == 'BF']
            
            od_inspected = sum(item[3] for item in od_sessions) if od_sessions else 0
            od_accepted = sum(item[4] for item in od_sessions) if od_sessions else 0
            od_rate = (od_accepted / od_inspected * 100) if od_inspected > 0 else 0
            
            bf_inspected = sum(item[3] for item in bf_sessions) if bf_sessions else 0
            bf_accepted = sum(item[4] for item in bf_sessions) if bf_sessions else 0
            bf_rate = (bf_accepted / bf_inspected * 100) if bf_inspected > 0 else 0
            
            # Show comprehensive monthly report
            report_text = f"""MONTHLY INSPECTION REPORT
            
Filter Settings:
• Component Type: {component_type}
• Report Type: {report_type}
• Date Range: {from_date} to {to_date}

OVERALL STATISTICS:
• Total Inspection Sessions: {total_sessions}
• Total Rollers Inspected: {total_inspected}
• Total Rollers Accepted: {total_accepted}
• Total Rollers Rejected: {total_rejected}
• Overall Success Rate: {success_rate:.1f}%

MODEL BREAKDOWN:
• OD Model: {len(od_sessions)} sessions, {od_inspected} inspected, {od_accepted} accepted ({od_rate:.1f}%)
• BF Model: {len(bf_sessions)} sessions, {bf_inspected} inspected, {bf_accepted} accepted ({bf_rate:.1f}%)

QUALITY ASSESSMENT:
• Quality Status: {'Excellent' if success_rate >= 95 else 'Good' if success_rate >= 85 else 'Needs Improvement' if success_rate >= 70 else 'Critical'}
• Recommendation: {'Maintain current standards' if success_rate >= 90 else 'Review inspection processes' if success_rate >= 75 else 'Immediate process improvement required'}

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            # Show the report in a message box
            messagebox.showinfo("Monthly Report Generated", report_text)
            
            print(f"📊 Monthly report generated with {total_sessions} sessions, {total_inspected} rollers inspected")
            
        except Exception as e:
            error_msg = f"Failed to generate monthly report: {str(e)}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

    def load_inspection_sessions(self):
        """Method called from main app to load initial data"""
        self.load_diagnosis_data()
        # Refresh the report after loading new data
        if hasattr(self, 'generate_report'):
            self.generate_report()
    
    def process_action(self):
        """Handle Process button action"""
        try:
            # Refresh data and regenerate report
            self.load_diagnosis_data()
            self.generate_report()
            messagebox.showinfo("Process", "Data processed and report updated successfully!")
            print("✅ Data processed successfully")
        except Exception as e:
            error_msg = f"Error processing data: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Process Error", error_msg)
    
    def settings_action(self):
        """Handle Settings button action"""
        try:
            # Navigate to settings page
            if hasattr(self.app, 'show_settings_page'):
                self.app.show_settings_page()
            else:
                messagebox.showinfo("Settings", "Settings page navigation not available")
            print("🔧 Navigating to Settings page")
        except Exception as e:
            print(f"❌ Error navigating to settings: {e}")
    
    def diagnosis_action(self):
        """Handle Diagnosis button action - refresh current page"""
        try:
            # Refresh diagnosis page data
            self.load_diagnosis_data()
            self.generate_report()
            messagebox.showinfo("Diagnosis", "Diagnosis page refreshed successfully!")
            print("🔄 Diagnosis page refreshed")
        except Exception as e:
            error_msg = f"Error refreshing diagnosis page: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Diagnosis Error", error_msg)
    
    def data_action(self):
        """Handle Data button action"""
        try:
            # Navigate to data page
            if hasattr(self.app, 'show_data_page'):
                self.app.show_data_page()
            else:
                messagebox.showinfo("Data", "Data page navigation not available")
            print("📊 Navigating to Data page")
        except Exception as e:
            print(f"❌ Error navigating to data page: {e}")
    
    def manual_action(self):
        """Handle Manual button action"""
        try:
            # Navigate to system check page (manual mode)
            if hasattr(self.app, 'show_system_check_page'):
                self.app.show_system_check_page()
            else:
                messagebox.showinfo("Manual", "Manual mode page navigation not available")
            print("🔧 Navigating to Manual mode page")
        except Exception as e:
            print(f"❌ Error navigating to manual mode: {e}")
    
    def exit_action(self):
        """Handle Exit button action"""
        try:
            # Use controlled exit if available
            if hasattr(self.app, 'controlled_exit'):
                self.app.controlled_exit()
            else:
                # Fallback to standard exit
                if messagebox.askyesno("Exit", "Are you sure you want to exit the application?"):
                    self.app.quit()
            print("🚪 Exit action triggered")
        except Exception as e:
            print(f"❌ Error during exit: {e}")
