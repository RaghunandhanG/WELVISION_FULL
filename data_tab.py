"""
Data Tab for WelVision Application
Handles roller data management (CRUD operations)
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox

class DataTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_tab()
    
    def setup_tab(self):
        data_container = tk.Frame(self.parent, bg="#0a2158")
        data_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(data_container, text="Roller Data Management", 
                             font=("Arial", 18, "bold"), fg="white", bg="#0a2158")
        title_label.pack(pady=(0, 20))
        
        # Input section
        input_frame = tk.LabelFrame(data_container, text="Roller Information", 
                                  font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        fields = ["Roller Type", "Diameter (mm)", "Thickness (mm)", "Length (mm)"]
        self.app.data_entries = {}
        for i, field in enumerate(fields):
            frame = tk.Frame(input_frame, bg="#0a2158")
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            label = tk.Label(frame, text=field, font=("Arial", 12), 
                           fg="white", bg="#0a2158", width=15, anchor="w")
            label.pack(side=tk.LEFT, padx=5)
            
            # Create text input box for all fields including Roller Type
            entry = tk.Entry(frame, font=("Arial", 12), width=30)
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.app.data_entries[field] = entry
        
        # CRUD buttons
        button_frame = tk.Frame(data_container, bg="#0a2158")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(button_frame, text="Create", font=("Arial", 12, "bold"), 
                 bg="#28a745", fg="white", width=10, 
                 command=self.app.create_roller).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Read", font=("Arial", 12, "bold"), 
                 bg="#007bff", fg="white", width=10, 
                 command=self.app.read_roller).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Update", font=("Arial", 12, "bold"), 
                 bg="#ffc107", fg="white", width=10, 
                 command=self.app.update_roller).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", font=("Arial", 12, "bold"), 
                 bg="#dc3545", fg="white", width=10, 
                 command=self.app.delete_roller).pack(side=tk.LEFT, padx=5)
        
        # Data display
        tree_frame = tk.LabelFrame(data_container, text="Roller Data", 
                                  font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.app.tree = ttk.Treeview(tree_frame, columns=("ID", "Roller Type", "Diameter", "Thickness", "Length"), 
                                show="headings", height=10)
        self.app.tree.heading("ID", text="ID")
        self.app.tree.heading("Roller Type", text="Roller Type")
        self.app.tree.heading("Diameter", text="Diameter (mm)")
        self.app.tree.heading("Thickness", text="Thickness (mm)")
        self.app.tree.heading("Length", text="Length (mm)")
        self.app.tree.column("ID", width=50)
        self.app.tree.column("Roller Type", width=150)
        self.app.tree.column("Diameter", width=100)
        self.app.tree.column("Thickness", width=100)
        self.app.tree.column("Length", width=100)
        self.app.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.app.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.app.tree.configure(yscrollcommand=scrollbar.set)
        
        self.app.load_roller_data()
