import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import pandas as pd  # For Excel export
from tkcalendar import DateEntry  # For calendar date picker
import os
import webbrowser
from datetime import datetime, timedelta

class SettingsTab:
    def __init__(self, parent, app_instance, read_only=False):
        self.parent = parent
        self.app = app_instance
        self.read_only = read_only
        self.setup_tab()
    
    def setup_tab(self):
        settings_container = tk.Frame(self.parent, bg="#0a2158")
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Add read-only indicator for regular users
        if self.read_only:
            read_only_frame = tk.Frame(settings_container, bg="#ffc107", bd=2, relief="solid")
            read_only_frame.pack(fill=tk.X, pady=(0, 15))
            
            read_only_label = tk.Label(read_only_frame, 
                                     text="📖 READ-ONLY MODE - You can view settings but cannot modify them", 
                                     font=("Arial", 12, "bold"), fg="black", bg="#ffc107")
            read_only_label.pack(pady=8)

        # Load current threshold values from database
        self.load_threshold_values()

        # --- Top Section: Split into two columns for OD and BigFace Defect Thresholds ---
        top_frame = tk.Frame(settings_container, bg="#0a2158")
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # Left Column: BigFace Defect Thresholds
        left_column = tk.Frame(top_frame, bg="#0a2158")
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        bf_defect_frame = tk.LabelFrame(left_column, text="Big Face Defect Thresholds", 
                                        font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        bf_defect_frame.pack(fill=tk.X, padx=10, pady=10)

        # BigFace defect types (limited set)
        bf_defect_types = ["Rust", "Dent", "Damage", "Roller"]
        for idx, defect in enumerate(bf_defect_types):
            current_value = self.app.bf_defect_thresholds.get(defect, 50)
            self.app.create_slider(bf_defect_frame, defect, 0, 100, current_value, row=idx, is_od=False, read_only=self.read_only)

        # Right Column: OD Defect Thresholds
        right_column = tk.Frame(top_frame, bg="#0a2158")
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        od_defect_frame = tk.LabelFrame(right_column, text="OD Defect Thresholds", 
                                        font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        od_defect_frame.pack(fill=tk.X, padx=10, pady=10)

        # OD defect types (full set)
        od_defect_types = ["Rust", "Dent", "Spherical Mark", "Damage", "Flat Line", "Damage on End", "Roller"]
        for idx, defect in enumerate(od_defect_types):
            current_value = self.app.od_defect_thresholds.get(defect, 50)
            self.app.create_slider(od_defect_frame, defect, 0, 100, current_value, row=idx, is_od=True, read_only=self.read_only)

        # --- Middle Section: Model Confidence Thresholds ---
        conf_frame = tk.LabelFrame(settings_container, text="Model Confidence Thresholds", 
                                   font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        conf_frame.pack(fill=tk.X, padx=10, pady=10)

        title_label = tk.Label(conf_frame, text="Model Confidence Settings", 
                               font=("Arial", 18, "bold"), fg="white", bg="#0a2158")
        title_label.pack(pady=(10, 20))

        # OD Model Confidence
        od_conf_frame = tk.Frame(conf_frame, bg="#0a2158", pady=10)
        od_conf_frame.pack(fill=tk.X, padx=10)

        od_conf_label = tk.Label(od_conf_frame, text="OD Model Confidence", font=("Arial", 12), 
                                 fg="white", bg="#0a2158", width=20, anchor="w")
        od_conf_label.pack(side=tk.LEFT, padx=10)

        # Initialize with current value from database
        if not hasattr(self.app, 'od_conf_threshold'):
            self.app.od_conf_threshold = 0.25
        self.app.od_conf_slider_value = tk.DoubleVar(value=self.app.od_conf_threshold * 100)

        od_conf_slider = ttk.Scale(od_conf_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                   length=200, variable=self.app.od_conf_slider_value)
        od_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Disable slider if in read-only mode
        if self.read_only:
            od_conf_slider.config(state="disabled")

        self.app.od_conf_value_label = tk.Label(od_conf_frame, text=f"{int(self.app.od_conf_threshold * 100)}%", 
                                            font=("Arial", 12), fg="white", bg="#0a2158", width=5)
        self.app.od_conf_value_label.pack(side=tk.LEFT, padx=10)

        def update_od_conf_label(val):
            self.app.od_conf_value_label.config(text=f"{int(float(val))}%")
            self.app.od_conf_threshold = float(val) / 100
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()

        # Only configure command if not read-only
        if not self.read_only:
            od_conf_slider.config(command=update_od_conf_label)

        # BigFace Model Confidence
        bf_conf_frame = tk.Frame(conf_frame, bg="#0a2158", pady=10)
        bf_conf_frame.pack(fill=tk.X, padx=10)

        bf_conf_label = tk.Label(bf_conf_frame, text="Bigface Model Confidence", font=("Arial", 12), 
                                 fg="white", bg="#0a2158", width=20, anchor="w")
        bf_conf_label.pack(side=tk.LEFT, padx=10)

        # Initialize with current value from database
        if not hasattr(self.app, 'bf_conf_threshold'):
            self.app.bf_conf_threshold = 0.25
        self.app.bf_conf_slider_value = tk.DoubleVar(value=self.app.bf_conf_threshold * 100)

        bf_conf_slider = ttk.Scale(bf_conf_frame, from_=1, to=100, orient=tk.HORIZONTAL, 
                                   length=200, variable=self.app.bf_conf_slider_value)
        bf_conf_slider.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Disable slider if in read-only mode
        if self.read_only:
            bf_conf_slider.config(state="disabled")

        self.app.bf_conf_value_label = tk.Label(bf_conf_frame, text=f"{int(self.app.bf_conf_threshold * 100)}%", 
                                            font=("Arial", 12), fg="white", bg="#0a2158", width=5)
        self.app.bf_conf_value_label.pack(side=tk.LEFT, padx=10)

        def update_bf_conf_label(val):
            self.app.bf_conf_value_label.config(text=f"{int(float(val))}%")
            self.app.bf_conf_threshold = float(val) / 100
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()

        # Only configure command if not read-only
        if not self.read_only:
            bf_conf_slider.config(command=update_bf_conf_label)

        save_button = tk.Button(conf_frame, text="Save Settings", font=("Arial", 12, "bold"),
                                bg="#28a745", fg="white", command=self.save_thresholds)
        
        # Disable save button if in read-only mode
        if self.read_only:
            save_button.config(state="disabled", bg="gray")
        
        save_button.pack(pady=20)

        # --- Bottom Section: Buttons ---
        button_frame = tk.Frame(settings_container, bg="#0a2158")
        button_frame.pack(fill=tk.X, pady=10)

        history_button = tk.Button(button_frame, text="Threshold History", font=("Arial", 12, "bold"),
                                   bg="#007bff", fg="white", command=self.show_setting_history)
        
        # Disable Setting History button if in read-only mode
        if self.read_only:
            history_button.config(state="disabled", bg="gray")
        
        history_button.pack(side=tk.LEFT, padx=5)

        # System Information button remains enabled for all users
        system_info_button = tk.Button(button_frame, text="System Information", font=("Arial", 12, "bold"),
                                      bg="#17a2b8", fg="white", command=self.generate_system_info_pdf)
        system_info_button.pack(side=tk.LEFT, padx=5)

        # Note: User Management is now available as a separate tab for Admin and Super Admin users

    def load_threshold_values(self):
        """Load current threshold values from database"""
        try:
            # Load current threshold values if not already loaded
            if not hasattr(self.app, 'od_defect_thresholds') or not self.app.od_defect_thresholds:
                self.app.load_current_thresholds()
                
            print(f"✅ Threshold values loaded for settings tab")
            print(f"OD Thresholds: {self.app.od_defect_thresholds}")
            print(f"BF Thresholds: {self.app.bf_defect_thresholds}")
            print(f"OD Confidence: {getattr(self.app, 'od_conf_threshold', 0.25)}")
            print(f"BF Confidence: {getattr(self.app, 'bf_conf_threshold', 0.25)}")
            
        except Exception as e:
            print(f"Error loading threshold values: {e}")

    def show_setting_history(self):
        """Display threshold change history from database"""
        # Create a popup window for Setting History
        popup = tk.Toplevel(self.parent)
        popup.title("Threshold Change History")
        popup.configure(bg="#0a2158")
        popup.geometry("1000x600")  # Larger size for more data

        history_frame = tk.LabelFrame(popup, text="Threshold Change History", 
                                      font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Model selection radio buttons
        filter_frame = tk.Frame(history_frame, bg="#0a2158")
        filter_frame.pack(fill=tk.X, pady=5)

        self.model_var = tk.StringVar(value="OD")
        tk.Radiobutton(filter_frame, text="OD Model", variable=self.model_var, value="OD",
                       fg="white", bg="#0a2158", selectcolor="#0a2158",
                       command=self.on_model_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(filter_frame, text="BigFace Model", variable=self.model_var, value="BIGFACE",
                       fg="white", bg="#0a2158", selectcolor="#0a2158",
                       command=self.on_model_change).pack(side=tk.LEFT, padx=10)

        # Date range selection with calendar widgets
        date_frame = tk.Frame(history_frame, bg="#0a2158")
        date_frame.pack(fill=tk.X, pady=5)

        tk.Label(date_frame, text="From Date:", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        from datetime import datetime, timedelta
        default_from = datetime.now() - timedelta(days=30)
        self.from_date_var = tk.StringVar(value=default_from.strftime("%Y-%m-%d"))
        from_date_entry = DateEntry(date_frame, textvariable=self.from_date_var, width=12, 
                                    background='darkblue', foreground='white', 
                                    date_pattern='yyyy-mm-dd')
        from_date_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(date_frame, text="To Date:", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_date_entry = DateEntry(date_frame, textvariable=self.to_date_var, width=12, 
                                  background='darkblue', foreground='white', 
                                  date_pattern='yyyy-mm-dd')
        to_date_entry.pack(side=tk.LEFT, padx=5)

        # Refresh button
        refresh_btn = tk.Button(date_frame, text="Refresh", font=("Arial", 10), 
                               bg="#007bff", fg="white", command=self.refresh_history_data)
        refresh_btn.pack(side=tk.LEFT, padx=10)

        # Table for historical threshold data
        self.table_frame = tk.Frame(history_frame, bg="#0a2158")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Define columns based on model type
        self.setup_history_table(self.table_frame)

        # Buttons for actions
        button_frame = tk.Frame(history_frame, bg="#0a2158")
        button_frame.pack(fill=tk.X, pady=5)

        tk.Button(button_frame, text="Export to Excel", command=self.export_history_excel,
                  bg="#28a745", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear History", command=self.clear_history_confirm,
                  bg="#dc3545", fg="white").pack(side=tk.LEFT, padx=5)

        # Load initial data
        self.popup = popup  # Store reference for refresh
        self.refresh_history_data()

    def on_model_change(self):
        """Handle model type change - rebuild table and refresh data"""
        try:
            # Rebuild table structure for new model type
            self.setup_history_table(self.table_frame)
            # Refresh data
            self.refresh_history_data()
        except Exception as e:
            print(f"Error handling model change: {e}")

    def setup_history_table(self, parent_frame):
        """Setup the history table with appropriate columns"""
        # Clear existing table if any
        for widget in parent_frame.winfo_children():
            widget.destroy()

        model_type = self.model_var.get()
        
        if model_type == "OD":
            columns = ("ID", "Employee", "Rust", "Dent", "Spherical Mark", "Damage", 
                      "Flat Line", "Damage on End", "Roller", "Model Conf", "Timestamp")
        else:  # BIGFACE
            columns = ("ID", "Employee", "Rust", "Dent", "Damage", "Roller", 
                      "Model Conf", "Timestamp")

        self.history_tree = ttk.Treeview(parent_frame, columns=columns, show="headings", height=12)

        # Set column headings and widths
        for i, col in enumerate(columns):
            self.history_tree.heading(col, text=col)
            if col == "ID":
                self.history_tree.column(col, width=50, anchor="center")
            elif col == "Employee":
                self.history_tree.column(col, width=80, anchor="center")
            elif col == "Timestamp":
                self.history_tree.column(col, width=150, anchor="center")
            elif "Conf" in col:
                self.history_tree.column(col, width=80, anchor="center")
            else:
                self.history_tree.column(col, width=70, anchor="center")

        # Add scrollbars
        yscroll = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        xscroll = ttk.Scrollbar(parent_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.history_tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

    def refresh_history_data(self):
        """Refresh history data from database"""
        try:
            # Clear existing data
            if hasattr(self, 'history_tree'):
                for item in self.history_tree.get_children():
                    self.history_tree.delete(item)
            else:
                print("Warning: No history_tree found for refresh")
                return

            # Get filter values
            model_type = self.model_var.get()
            start_date = self.from_date_var.get()
            end_date = self.to_date_var.get()

            # Get history from database
            from database import db_manager
            history_data = db_manager.get_threshold_history(
                model_type=model_type,
                start_date=start_date,
                end_date=end_date,
                employee_id=None,
                limit=200
            )

            print(f"📊 Loading {len(history_data)} records for {model_type} model")

            # Populate table
            for record in history_data:
                if model_type == "OD":
                    values = (
                        record['id'],
                        record['employee_id'],
                        record['rust_threshold'],
                        record['dent_threshold'],
                        record['spherical_mark_threshold'],
                        record['damage_threshold'],
                        record['flat_line_threshold'],
                        record['damage_on_end_threshold'],
                        record['roller_threshold'],
                        f"{record['model_confidence_threshold']:.3f}",
                        record['change_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    )
                else:  # BIGFACE
                    values = (
                        record['id'],
                        record['employee_id'],
                        record['rust_threshold'],
                        record['dent_threshold'],
                        record['damage_threshold'],
                        record['roller_threshold'],
                        f"{record['model_confidence_threshold']:.3f}",
                        record['change_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    )
                
                self.history_tree.insert("", tk.END, values=values)
            
            print(f"✅ Successfully loaded {len(history_data)} threshold history records")

        except Exception as e:
            print(f"Error refreshing history data: {e}")
            messagebox.showerror("Error", f"Failed to load history data: {e}")

    def export_history_excel(self):
        """Export history data to Excel"""
        try:
            # Get current data from tree
            columns = []
            for col in self.history_tree["columns"]:
                columns.append(self.history_tree.heading(col)["text"])
            
            data = []
            for item in self.history_tree.get_children():
                values = self.history_tree.item(item, "values")
                data.append(values)

            if not data:
                messagebox.showwarning("Warning", "No data to export.")
                return

            df = pd.DataFrame(data, columns=columns)
            filename = f"threshold_history_{self.model_var.get()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("Success", f"History exported to '{filename}'.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export to Excel: {str(e)}")

    def clear_history_confirm(self):
        """Confirm and clear history data"""
        # Get current model type for confirmation message
        model_type = self.model_var.get()
        
        # Create a more detailed confirmation dialog
        dialog_title = "⚠️ Clear Threshold History"
        
        if model_type == "OD":
            confirm_message = ("Are you sure you want to clear ALL OD Model threshold history?\n\n"
                             "This will permanently delete:\n"
                             "• All OD threshold change records\n"
                             "• Employee change tracking\n"
                             "• Historical timestamps\n\n"
                             "This action CANNOT be undone!")
        else:  # BIGFACE
            confirm_message = ("Are you sure you want to clear ALL BigFace Model threshold history?\n\n"
                             "This will permanently delete:\n"
                             "• All BigFace threshold change records\n"
                             "• Employee change tracking\n"  
                             "• Historical timestamps\n\n"
                             "This action CANNOT be undone!")
        
        # Show confirmation dialog
        if messagebox.askyesno(dialog_title, confirm_message, icon='warning'):
            try:
                # Show progress message
                progress_msg = f"Clearing {model_type} threshold history..."
                print(progress_msg)
                
                # Clear history from database
                from database import db_manager
                success, message, records_deleted = db_manager.clear_threshold_history(
                    model_type=model_type, 
                    confirm_deletion=True
                )
                
                if success:
                    # Show success message with count
                    success_msg = f"✅ Successfully cleared {records_deleted} {model_type} threshold history records."
                    messagebox.showinfo("History Cleared", success_msg)
                    print(f"✅ {success_msg}")
                    
                    # Refresh the history display to show empty table
                    self.refresh_history_data()
                    
                else:
                    # Show error message
                    error_msg = f"❌ Failed to clear threshold history: {message}"
                    messagebox.showerror("Clear Failed", error_msg)
                    print(error_msg)
                    
            except Exception as e:
                error_msg = f"❌ Error clearing threshold history: {e}"
                print(error_msg)
                messagebox.showerror("Error", f"An unexpected error occurred while clearing history:\n{e}")
        else:
            print("🚫 Threshold history clearing cancelled by user")

    def save_thresholds(self):
        """Save threshold settings to database with tracking"""
        try:
            # Update confidence thresholds
            self.app.od_conf_threshold = float(self.app.od_conf_slider_value.get()) / 100
            self.app.bf_conf_threshold = float(self.app.bf_conf_slider_value.get()) / 100
            
            # Update shared data if available
            if hasattr(self.app, 'shared_data'):
                self.app.shared_data['od_conf_threshold'] = self.app.od_conf_threshold
                self.app.shared_data['bf_conf_threshold'] = self.app.bf_conf_threshold
            
            # Update model confidence if inspection is running
            if hasattr(self.app, 'inspection_running') and self.app.inspection_running:
                self.app.update_model_confidence()
            
            # Save all thresholds to database
            success, message = self.app.save_all_thresholds()
            
            if success:
                messagebox.showinfo("Settings Saved", "All threshold settings have been saved successfully to the database.")
                print(f"✅ Thresholds saved - OD Confidence: {self.app.od_conf_threshold}, BF Confidence: {self.app.bf_conf_threshold}")
                
                # Auto-refresh threshold history if the window is open
                if hasattr(self, 'popup') and self.popup and self.popup.winfo_exists():
                    print("🔄 Auto-refreshing threshold history...")
                    self.refresh_history_data()
                    
            else:
                messagebox.showerror("Save Error", f"Failed to save thresholds: {message}")
                print(f"❌ Failed to save thresholds: {message}")
                
        except Exception as e:
            print(f"Error saving thresholds: {e}")
            messagebox.showerror("Error", f"An error occurred while saving thresholds: {e}")

    def generate_system_info_pdf(self):
        try:
            # Specify the path to the existing PDF file
            pdf_path = "system_info.pdf"  # Adjust this to the actual path of your PDF
            if not os.path.exists(pdf_path):
                messagebox.showerror("Error", f"PDF file '{pdf_path}' not found. Please ensure the file exists.")
                return
            
            # Open the PDF using the default system viewer
            webbrowser.open(f"file://{os.path.abspath(pdf_path)}")
            messagebox.showinfo("Success", "System information PDF opened.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open system info PDF: {str(e)}")



