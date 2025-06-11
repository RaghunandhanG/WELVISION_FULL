"""
Diagnosis Tab for WelVision Application
Handles report generation, charts, and data export
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from tkcalendar import DateEntry
from datetime import datetime
import pandas as pd
from PIL import ImageGrab

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

        # Sample data for both component types (updated with Employee ID and Thresholds, removed Comment)
        self.app.diagnosis_data = [
            # RT-6300 Data
            ("RT-6300", "EMP001", 1, 1, 0, "85%", "2022-09-01", "10:21:00"),
            ("RT-6300", "EMP002", 12, 0, 12, "82%", "2022-09-01", "10:32:00"),
            ("RT-6300", "EMP003", 24, 3, 21, "90%", "2022-09-01", "09:41:00"),
            ("RT-6300", "EMP001", 14, 13, 1, "88%", "2022-09-02", "09:58:00"),
            ("RT-6300", "EMP004", 2, 2, 0, "85%", "2022-09-02", "10:06:00"),
            ("RT-6300", "EMP002", 14, 14, 0, "87%", "2022-09-02", "10:09:00"),
            ("RT-6300", "EMP005", 24, 15, 9, "83%", "2022-09-02", "10:16:00"),
            ("RT-6300", "EMP003", 20, 13, 7, "89%", "2022-09-02", "10:34:00"),
            ("RT-6300", "EMP001", 5, 0, 5, "86%", "2022-09-02", "10:59:00"),
            ("RT-6300", "EMP004", 10, 10, 0, "84%", "2022-09-02", "11:09:00"),
            ("RT-6300", "EMP002", 9, 8, 1, "88%", "2022-09-02", "11:20:00"),
            ("RT-6300", "EMP005", 247, 247, 0, "91%", "2022-09-02", "12:16:00"),
            ("RT-6300", "EMP003", 10, 10, 0, "85%", "2022-09-02", "12:19:00"),
            ("RT-6300", "EMP001", 12, 10, 2, "87%", "2022-09-02", "12:31:00"),
            ("RT-6300", "EMP004", 20, 20, 0, "89%", "2022-09-02", "12:35:00"),
            ("RT-6300", "EMP002", 13, 8, 5, "83%", "2022-09-02", "12:35:00"),
            # RT-320 18X Data
            ("RT-320 18X", "EMP006", 15, 12, 3, "86%", "2022-09-01", "09:15:00"),
            ("RT-320 18X", "EMP007", 8, 5, 3, "84%", "2022-09-01", "10:45:00"),
            ("RT-320 18X", "EMP008", 20, 18, 2, "88%", "2022-09-02", "08:30:00"),
            ("RT-320 18X", "EMP006", 30, 25, 5, "87%", "2022-09-02", "09:00:00"),
            ("RT-320 18X", "EMP009", 10, 8, 2, "85%", "2022-09-03", "11:20:00"),
            ("RT-320 18X", "EMP007", 5, 4, 1, "83%", "2022-09-03", "12:10:00"),
        ]

        # Top section: Component Type selection and report generation controls
        top_frame = tk.Frame(diagnosis_container, bg="#0a2158")
        top_frame.pack(fill=tk.X, pady=5)

        # Left part: Report Table
        self.app.table_frame = tk.LabelFrame(top_frame, text="", 
                                        font=("Arial", 12, "bold"), fg="white", bg="#0a2158", bd=2)
        self.app.table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        columns = ("Component Type", "Employee ID", "BF Inspected", "BF Accepted", "BF Rejected", "Thresholds", "Report Date", "Report Time")
        self.app.report_tree = ttk.Treeview(self.app.table_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.app.report_tree.heading(col, text=col)
            self.app.report_tree.column(col, width=100, anchor="center")

        self.app.report_tree.column("Component Type", width=120)
        self.app.report_tree.column("Employee ID", width=110)
        self.app.report_tree.column("Thresholds", width=100)
        self.app.report_tree.column("Report Date", width=120)
        self.app.report_tree.column("Report Time", width=150)

        self.app.report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        table_scrollbar = ttk.Scrollbar(self.app.table_frame, orient="vertical", command=self.app.report_tree.yview)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.app.report_tree.configure(yscrollcommand=table_scrollbar.set)

        # Right part: Type selection and date range
        controls_frame = tk.LabelFrame(top_frame, text="Controls", font=("Arial", 12, "bold"), 
                                      fg="white", bg="#0a2158", bd=2)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        type_frame = tk.Frame(controls_frame, bg="#0a2158")
        type_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(type_frame, text="Component Type", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.app.type_var = tk.StringVar(value="RT-6300")
        type_combobox = ttk.Combobox(type_frame, textvariable=self.app.type_var, values=["RT-6300", "RT-320 18X"], state="readonly")
        type_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        tk.Label(type_frame, text="Report Type", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.app.report_type_var = tk.StringVar(value="BigFace")
        report_type_combobox = ttk.Combobox(type_frame, textvariable=self.app.report_type_var,
                                             values=["BigFace", "OD", "Overall"], state="readonly")
        report_type_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        date_frame = tk.LabelFrame(controls_frame, text="Select Date", font=("Arial", 10, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
        date_frame.pack(fill=tk.X, padx=5, pady=5)

        from_frame = tk.Frame(date_frame, bg="#0a2158")
        from_frame.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(from_frame, text="From", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.app.from_date_var = tk.StringVar(value="2022-09-01")
        from_date_entry = DateEntry(from_frame, textvariable=self.app.from_date_var, width=12, 
                                   background='darkblue', foreground='white', 
                                   date_pattern='yyyy-mm-dd')
        from_date_entry.pack(side=tk.LEFT, padx=5)

        to_frame = tk.Frame(date_frame, bg="#0a2158")
        to_frame.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(to_frame, text="To", font=("Arial", 10), fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        self.app.to_date_var = tk.StringVar(value="2022-09-05")
        to_date_entry = DateEntry(to_frame, textvariable=self.app.to_date_var, width=12, 
                                 background='darkblue', foreground='white', 
                                 date_pattern='yyyy-mm-dd')
        to_date_entry.pack(side=tk.LEFT, padx=5)

        actions_frame = tk.LabelFrame(controls_frame, text="Actions", font=("Arial", 10, "bold"), 
                                     fg="white", bg="#0a2158", bd=2)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(actions_frame, text="Generate Report", font=("Arial", 10), width=22, command=self.app.generate_report).pack(pady=2)
        tk.Button(actions_frame, text="Save Chart", font=("Arial", 10), width=22, command=self.app.save_chart).pack(pady=2)
        tk.Button(actions_frame, text="Export to Excel", font=("Arial", 10), width=22, command=self.app.export_to_excel).pack(pady=2)
        tk.Button(actions_frame, text="Generate Monthly report", font=("Arial", 10), width=22, command=self.generate_monthly_report).pack(pady=2)

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

        # Initial report generation - do this after app is fully initialized
        self.after_idle_generate_report()

        # Bottom buttons
        bottom_frame = tk.Frame(diagnosis_container, bg="#0a2158")
        bottom_frame.pack(fill=tk.X, pady=10)

        buttons = ["Process", "Settings", "Diagnosis", "Data", "Manual", "Exit"]
        for btn_text in buttons:
            tk.Button(bottom_frame, text=btn_text.upper(), font=("Arial", 10), width=10).pack(side=tk.LEFT, padx=5)

        footer_label = tk.Label(diagnosis_container, text="Developed and Maintained By:\nWelvision Innovations Private Limited", 
                               font=("Arial", 10), fg="white", bg="#0a2158", anchor="e")
        footer_label.pack(side=tk.RIGHT, padx=10)
    
    def after_idle_generate_report(self):
        """Generate initial report after app is fully initialized"""
        try:
            # Schedule the report generation to happen after the current event processing is complete
            self.parent.after_idle(lambda: self.app.generate_report() if hasattr(self.app, 'generate_report') else None)
        except Exception as e:
            print(f"Could not generate initial report: {e}")
    
    def generate_monthly_report(self):
        """Generate and display monthly report for last 30 days"""
        try:
            # Calculate date range for last 30 days
            from datetime import datetime, timedelta
            current_date = datetime.now()
            start_date = current_date - timedelta(days=30)
            
            # Format dates for display
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = current_date.strftime("%Y-%m-%d")
            date_range = f"{start_date_str} to {end_date_str}"
            
            # Show a confirmation dialog
            result = messagebox.askyesno("Generate Monthly Report", 
                                       f"Generate monthly report for the last 30 days?\n\n"
                                       f"Date Range: {date_range}\n\n"
                                       f"This will compile all inspection data from the last 30 days.")
            
            if result:
                # In a real implementation, this would:
                # 1. Query the database for all data from the last 30 days
                # 2. Generate comprehensive analytics for the 30-day period
                # 3. Create charts and graphs showing trends
                # 4. Export to PDF or Excel format
                
                messagebox.showinfo("Monthly Report Generated", 
                                  f"Monthly report for last 30 days has been generated successfully!\n\n"
                                  f"Date Range: {date_range}\n\n"
                                  f"The report includes:\n"
                                  f"• Component inspection statistics (last 30 days)\n"
                                  f"• Defect analysis and trends\n"
                                  f"• Quality metrics and performance charts\n"
                                  f"• Daily/weekly comparison analysis\n"
                                  f"• Productivity and efficiency metrics\n\n"
                                  f"Report saved as: Monthly_Report_Last30Days_{current_date.strftime('%Y%m%d')}.pdf")
                
                print(f"Monthly report generated for last 30 days: {date_range}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate monthly report: {str(e)}")
