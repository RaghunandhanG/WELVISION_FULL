"""
Data Tab for WelVision Application
Handles roller data management (CRUD operations)

This module provides a complete interface for managing roller information in the WelVision system.
It includes functionality for creating, reading, updating, and deleting (CRUD) roller records,
with validation, error handling, and database integration.

Key Features:
- Interactive form for roller data entry
- TreeView display for roller data visualization
- CRUD operation buttons with validation
- Mouse wheel scrolling support
- Double-click event handling for quick record loading
- Automatic database synchronization
- Super Admin roller specifications management
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox

class DataTab:
    """
    Data Tab class for managing roller information in the WelVision application.
    
    This class creates and manages the UI components for roller data management,
    including input forms, data display tables, and CRUD operation buttons.
    
    Attributes:
        parent: The parent tkinter widget (typically a tab container)
        app: Reference to the main WelVision application instance
    """
    
    def __init__(self, parent, app_instance):
        """
        Initialize the Data Tab with parent widget and app instance.
        
        Args:
            parent: Parent tkinter widget where this tab will be placed
            app_instance: Reference to the main WelVision application
        """
        self.parent = parent
        self.app = app_instance
        self.setup_tab()
    
    def setup_tab(self):
        """
        Set up the complete UI layout for the data management tab.
        
        This method creates all the UI components including:
        - Scrollable main container
        - Super Admin roller specifications (if applicable)
        - Input form section for roller data entry
        - CRUD operation buttons
        - TreeView table for data display
        - Scrollbars and event bindings
        """
        # Create main container with scrollable capability
        main_container = tk.Frame(self.parent, bg="#0a2158")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_container, bg="#0a2158", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a2158")
        
        # Configure scrollable frame to expand to canvas width
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Create window in canvas and store reference
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel events
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        scrollable_frame.bind('<Enter>', _bind_to_mousewheel)
        scrollable_frame.bind('<Leave>', _unbind_from_mousewheel)
        
        # Use scrollable_frame as the data_container
        data_container = scrollable_frame
        
        # Title section
        title_label = tk.Label(data_container, text="Roller Data Management", 
                             font=("Arial", 18, "bold"), fg="white", bg="#0a2158")
        title_label.pack(pady=(20, 20))
        
        # Role-specific sections
        if hasattr(self.app, 'current_role'):
            if self.app.current_role == "Super Admin":
                # Super Admin Global Limits Section
                self.create_global_limits_section(data_container)
            elif self.app.current_role == "Admin":
                # Admin Validation Information Section
                self.create_admin_global_limits_info_section(data_container)
        
        # Input section for roller data entry
        input_frame = tk.LabelFrame(data_container, text="Roller Information", 
                                  font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Define input fields for roller data
        fields = ["Roller Type", "Diameter (mm)", "Thickness (mm)", "Length (mm)"]
        self.app.data_entries = {}
        
        # Create input fields dynamically
        for i, field in enumerate(fields):
            # Individual frame for each field to maintain proper layout
            frame = tk.Frame(input_frame, bg="#0a2158")
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Field label with consistent styling
            label = tk.Label(frame, text=field, font=("Arial", 12), 
                           fg="white", bg="#0a2158", width=15, anchor="w")
            label.pack(side=tk.LEFT, padx=5)
            
            # Input entry widget - text input for all fields including Roller Type
            entry = tk.Entry(frame, font=("Arial", 12), width=30)
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.app.data_entries[field] = entry
        
        # CRUD operation buttons section
        button_frame = tk.Frame(data_container, bg="#0a2158")
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create CRUD buttons with color-coded styling
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
        
        # Data display section with TreeView
        tree_frame = tk.LabelFrame(data_container, text="Roller Data", 
                                  font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # TreeView widget for displaying roller data in tabular format (global limits system)
        self.app.tree = ttk.Treeview(tree_frame, columns=("ID", "Roller Type", "Diameter", "Thickness", "Length"), 
                                show="headings", height=10)
        
        # Configure column headings
        self.app.tree.heading("ID", text="ID")
        self.app.tree.heading("Roller Type", text="Roller Type")
        self.app.tree.heading("Diameter", text="Diameter (mm)")
        self.app.tree.heading("Thickness", text="Thickness (mm)")
        self.app.tree.heading("Length", text="Length (mm)")
        
        # Configure column widths for optimal display
        self.app.tree.column("ID", width=50)
        self.app.tree.column("Roller Type", width=200)
        self.app.tree.column("Diameter", width=120)
        self.app.tree.column("Thickness", width=120)
        self.app.tree.column("Length", width=120)
        
        # Pack TreeView with proper expansion settings
        self.app.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Vertical scrollbar for TreeView
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.app.tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.app.tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Mouse wheel scrolling support for TreeView
        def _on_tree_mousewheel(event):
            """Handle mouse wheel scrolling for the data tree."""
            self.app.tree.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Multi-platform mouse wheel event bindings for TreeView
        self.app.tree.bind("<MouseWheel>", _on_tree_mousewheel)  # Windows
        self.app.tree.bind("<Button-4>", lambda e: self.app.tree.yview_scroll(-1, "units"))  # Linux scroll up
        self.app.tree.bind("<Button-5>", lambda e: self.app.tree.yview_scroll(1, "units"))   # Linux scroll down
        
        # Add double-click event binding for quick record loading
        self.app.tree.bind("<Double-1>", self.app.on_roller_double_click)
        
        # Make the tree widget focusable so it can receive mouse wheel events
        self.app.tree.focus_set()
        
        # Load initial data from database
        self.app.load_roller_data()

    def create_global_limits_section(self, parent):
        """
        Create the global limits management section for Super Admin.
        
        This section allows Super Admin to set global min/max limits for diameter, 
        thickness, and length that apply to ALL roller types.
        
        Args:
            parent: Parent widget where this section will be placed
        """
        # Main global limits frame
        limits_frame = tk.LabelFrame(parent, text="🌐 Global Roller Limits (Super Admin Only)", 
                                   font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        limits_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Instructions label
        instructions_label = tk.Label(limits_frame, 
                                    text="Set global minimum and maximum limits for ALL roller types to ensure quality standards",
                                    font=("Arial", 11, "bold"), fg="#ffc107", bg="#0a2158")
        instructions_label.pack(pady=5)
        
        # Current limits display
        current_limits_frame = tk.Frame(limits_frame, bg="#0a2158")
        current_limits_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(current_limits_frame, text="Current Global Limits:", font=("Arial", 12, "bold"), 
                fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        
        self.current_limits_label = tk.Label(current_limits_frame, text="Loading...", 
                                           font=("Arial", 10), fg="lightgray", bg="#0a2158")
        self.current_limits_label.pack(side=tk.LEFT, padx=10)
        
        # Refresh button
        tk.Button(current_limits_frame, text="🔄 Refresh", font=("Arial", 10, "bold"),
                 bg="#17a2b8", fg="white", command=self.load_current_global_limits).pack(side=tk.RIGHT, padx=5)
        
        # Global limits input frame
        limits_input_frame = tk.Frame(limits_frame, bg="#0a2158")
        limits_input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create input fields for global limits
        min_fields = [
            ("Global Min Diameter (mm):", "min_diameter"),
            ("Global Min Thickness (mm):", "min_thickness"),
            ("Global Min Length (mm):", "min_length")
        ]
        
        max_fields = [
            ("Global Max Diameter (mm):", "max_diameter"),
            ("Global Max Thickness (mm):", "max_thickness"),
            ("Global Max Length (mm):", "max_length")
        ]
        
        self.global_limits_entries = {}
        
        # Create two rows - Min values on top, Max values on bottom
        min_row_frame = tk.Frame(limits_input_frame, bg="#0a2158")
        min_row_frame.pack(fill=tk.X, pady=2)
        
        max_row_frame = tk.Frame(limits_input_frame, bg="#0a2158")
        max_row_frame.pack(fill=tk.X, pady=2)
        
        # Create Min value fields (top row)
        for label_text, field_key in min_fields:
            col_frame = tk.Frame(min_row_frame, bg="#0a2158")
            col_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # Label
            tk.Label(col_frame, text=label_text, font=("Arial", 10, "bold"), 
                    fg="#28a745", bg="#0a2158").pack(anchor="w")
            
            # Entry
            entry = tk.Entry(col_frame, font=("Arial", 10), width=12)
            entry.pack(fill=tk.X, pady=2)
            self.global_limits_entries[field_key] = entry
        
        # Create Max value fields (bottom row)
        for label_text, field_key in max_fields:
            col_frame = tk.Frame(max_row_frame, bg="#0a2158")
            col_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # Label
            tk.Label(col_frame, text=label_text, font=("Arial", 10, "bold"), 
                    fg="#dc3545", bg="#0a2158").pack(anchor="w")
            
            # Entry
            entry = tk.Entry(col_frame, font=("Arial", 10), width=12)
            entry.pack(fill=tk.X, pady=2)
            self.global_limits_entries[field_key] = entry
        
        # Warning message
        warning_label = tk.Label(limits_frame, 
                               text="⚠️ These limits will apply to ALL roller types. Admin users cannot create rollers outside these ranges.",
                               font=("Arial", 10, "bold"), fg="#ff6b6b", bg="#0a2158", wraplength=600)
        warning_label.pack(pady=5)
        
        # Action buttons frame
        action_frame = tk.Frame(limits_frame, bg="#0a2158")
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(action_frame, text="💾 Save Global Limits", font=("Arial", 11, "bold"),
                 bg="#28a745", fg="white", command=self.save_global_limits).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="📋 Load Current", font=("Arial", 11, "bold"),
                 bg="#007bff", fg="white", command=self.load_current_global_limits).pack(side=tk.LEFT, padx=5)
        
        tk.Button(action_frame, text="🗑️ Clear Fields", font=("Arial", 11, "bold"),
                 bg="#6c757d", fg="white", command=self.clear_global_limits).pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        self.load_current_global_limits()



    def load_current_global_limits(self):
        """Load current global limits from database and display them."""
        try:
            from database import db_manager
            limits = db_manager.get_global_limits()
            
            if limits:
                # Update current limits display
                limits_text = (f"D: {limits['min_diameter']}-{limits['max_diameter']}mm, "
                             f"T: {limits['min_thickness']}-{limits['max_thickness']}mm, "
                             f"L: {limits['min_length']}-{limits['max_length']}mm")
                self.current_limits_label.config(text=limits_text, fg="#28a745")
                
                # Fill input fields with current values
                if hasattr(self, 'global_limits_entries'):
                    self.global_limits_entries['min_diameter'].delete(0, tk.END)
                    self.global_limits_entries['min_diameter'].insert(0, str(limits['min_diameter']))
                    
                    self.global_limits_entries['max_diameter'].delete(0, tk.END)
                    self.global_limits_entries['max_diameter'].insert(0, str(limits['max_diameter']))
                    
                    self.global_limits_entries['min_thickness'].delete(0, tk.END)
                    self.global_limits_entries['min_thickness'].insert(0, str(limits['min_thickness']))
                    
                    self.global_limits_entries['max_thickness'].delete(0, tk.END)
                    self.global_limits_entries['max_thickness'].insert(0, str(limits['max_thickness']))
                    
                    self.global_limits_entries['min_length'].delete(0, tk.END)
                    self.global_limits_entries['min_length'].insert(0, str(limits['min_length']))
                    
                    self.global_limits_entries['max_length'].delete(0, tk.END)
                    self.global_limits_entries['max_length'].insert(0, str(limits['max_length']))
                
                print(f"✅ Loaded global limits: {limits_text}")
            else:
                # No limits set
                self.current_limits_label.config(text="No global limits set", fg="#ffc107")
                print("⚠️ No global limits found in database")
                
        except Exception as e:
            print(f"Error loading global limits: {e}")
            self.current_limits_label.config(text="Error loading limits", fg="#dc3545")

    def save_global_limits(self):
        """Save global limits to database."""
        try:
            # Get values from entries
            min_diameter = self.global_limits_entries['min_diameter'].get().strip()
            max_diameter = self.global_limits_entries['max_diameter'].get().strip()
            min_thickness = self.global_limits_entries['min_thickness'].get().strip()
            max_thickness = self.global_limits_entries['max_thickness'].get().strip()
            min_length = self.global_limits_entries['min_length'].get().strip()
            max_length = self.global_limits_entries['max_length'].get().strip()
            
            # Validate inputs
            if not all([min_diameter, max_diameter, min_thickness, max_thickness, min_length, max_length]):
                messagebox.showwarning("Warning", "Please fill in all global limit fields")
                return
            
            try:
                min_diameter = float(min_diameter)
                max_diameter = float(max_diameter)
                min_thickness = float(min_thickness)
                max_thickness = float(max_thickness)
                min_length = float(min_length)
                max_length = float(max_length)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values")
                return
            
            if any(val <= 0 for val in [min_diameter, max_diameter, min_thickness, max_thickness, min_length, max_length]):
                messagebox.showerror("Error", "All values must be greater than 0")
                return
            
            # Validate min <= max for each dimension
            if min_diameter > max_diameter:
                messagebox.showerror("Error", "Minimum diameter cannot be greater than maximum diameter")
                return
            if min_thickness > max_thickness:
                messagebox.showerror("Error", "Minimum thickness cannot be greater than maximum thickness")
                return
            if min_length > max_length:
                messagebox.showerror("Error", "Minimum length cannot be greater than maximum length")
                return
            
            # Confirm with user
            confirm_message = (f"Set Global Limits for ALL Roller Types?\n\n"
                             f"Diameter: {min_diameter} - {max_diameter} mm\n"
                             f"Thickness: {min_thickness} - {max_thickness} mm\n"
                             f"Length: {min_length} - {max_length} mm\n\n"
                             f"This will affect all Admin users when creating rollers.")
            
            if not messagebox.askyesno("Confirm Global Limits", confirm_message):
                return
            
            # Prepare global limits data
            limits_data = {
                'min_diameter': min_diameter,
                'max_diameter': max_diameter,
                'min_thickness': min_thickness,
                'max_thickness': max_thickness,
                'min_length': min_length,
                'max_length': max_length,
                'updated_by': getattr(self.app, 'current_user', 'SYSTEM')
            }
            
            # Save to database
            from database import db_manager
            success = db_manager.save_global_limits(limits_data)
            
            if success:
                messagebox.showinfo("Success", "Global limits saved successfully!")
                self.load_current_global_limits()  # Refresh display
                print(f"✅ Global limits saved by {limits_data['updated_by']}")
            else:
                messagebox.showerror("Error", "Failed to save global limits")
                
        except Exception as e:
            print(f"Error saving global limits: {e}")
            messagebox.showerror("Error", f"Failed to save global limits: {e}")

    def clear_global_limits(self):
        """Clear all global limits input fields."""
        if hasattr(self, 'global_limits_entries'):
            for entry in self.global_limits_entries.values():
                entry.delete(0, tk.END)

    def create_admin_global_limits_info_section(self, parent):
        """
        Create the global limits information section for Admin users.
        
        This section shows admins the current global limits that apply 
        when creating new roller types.
        
        Args:
            parent: Parent widget where this section will be placed
        """
        # Main info frame
        info_frame = tk.LabelFrame(parent, text="🌐 Global Roller Limits (All Users)", 
                                  font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Instructions label
        instructions_label = tk.Label(info_frame, 
                                    text="Global limits apply to ALL users (including Super Admin). Only Super Admin can modify these limits.",
                                    font=("Arial", 11, "bold"), fg="#ffc107", bg="#0a2158")
        instructions_label.pack(pady=5)
        
        # Current global limits display
        current_limits_frame = tk.Frame(info_frame, bg="#0a2158")
        current_limits_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(current_limits_frame, text="Current Global Limits:", font=("Arial", 12, "bold"), 
                fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=5)
        
        self.admin_current_limits_label = tk.Label(current_limits_frame, text="Loading...", 
                                                 font=("Arial", 10), fg="lightgray", bg="#0a2158")
        self.admin_current_limits_label.pack(side=tk.LEFT, padx=10)
        
        # Refresh button
        tk.Button(current_limits_frame, text="🔄 Refresh", font=("Arial", 10, "bold"),
                 bg="#17a2b8", fg="white", command=self.load_admin_global_limits).pack(side=tk.RIGHT, padx=5)
        
        # Global limits display frame
        self.admin_limits_display_frame = tk.Frame(info_frame, bg="#0a2158")
        self.admin_limits_display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Load and display initial data
        self.load_admin_global_limits()

    def load_admin_global_limits(self):
        """Load and display global limits for admin users."""
        try:
            from database import db_manager
            limits = db_manager.get_global_limits()
            
            # Clear existing display
            for widget in self.admin_limits_display_frame.winfo_children():
                widget.destroy()
            
            if limits:
                # Update current limits display
                limits_text = (f"D: {limits['min_diameter']}-{limits['max_diameter']}mm, "
                             f"T: {limits['min_thickness']}-{limits['max_thickness']}mm, "
                             f"L: {limits['min_length']}-{limits['max_length']}mm")
                self.admin_current_limits_label.config(text=limits_text, fg="#28a745")
                
                # Create detailed limits display
                title_label = tk.Label(self.admin_limits_display_frame, 
                                     text="Global Limits for ALL Roller Types",
                                     font=("Arial", 12, "bold"), fg="white", bg="#0a2158")
                title_label.pack(pady=(0, 10))
                
                # Create grid for limits
                limits_grid = tk.Frame(self.admin_limits_display_frame, bg="#0a2158")
                limits_grid.pack(fill=tk.X)
                
                # Headers
                tk.Label(limits_grid, text="Dimension", font=("Arial", 11, "bold"), 
                        fg="white", bg="#0a2158", width=12).grid(row=0, column=0, padx=5, pady=2)
                tk.Label(limits_grid, text="Minimum", font=("Arial", 11, "bold"), 
                        fg="white", bg="#0a2158", width=12).grid(row=0, column=1, padx=5, pady=2)
                tk.Label(limits_grid, text="Maximum", font=("Arial", 11, "bold"), 
                        fg="white", bg="#0a2158", width=12).grid(row=0, column=2, padx=5, pady=2)
                tk.Label(limits_grid, text="Valid Range", font=("Arial", 11, "bold"), 
                        fg="white", bg="#0a2158", width=20).grid(row=0, column=3, padx=5, pady=2)
                
                # Diameter row
                tk.Label(limits_grid, text="Diameter (mm)", font=("Arial", 10), 
                        fg="lightgray", bg="#0a2158").grid(row=1, column=0, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['min_diameter']}", font=("Arial", 10), 
                        fg="#28a745", bg="#0a2158").grid(row=1, column=1, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['max_diameter']}", font=("Arial", 10), 
                        fg="#dc3545", bg="#0a2158").grid(row=1, column=2, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['min_diameter']} - {limits['max_diameter']} mm", 
                        font=("Arial", 10, "bold"), fg="#ffc107", bg="#0a2158").grid(row=1, column=3, padx=5, pady=2)
                
                # Thickness row
                tk.Label(limits_grid, text="Thickness (mm)", font=("Arial", 10), 
                        fg="lightgray", bg="#0a2158").grid(row=2, column=0, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['min_thickness']}", font=("Arial", 10), 
                        fg="#28a745", bg="#0a2158").grid(row=2, column=1, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['max_thickness']}", font=("Arial", 10), 
                        fg="#dc3545", bg="#0a2158").grid(row=2, column=2, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['min_thickness']} - {limits['max_thickness']} mm", 
                        font=("Arial", 10, "bold"), fg="#ffc107", bg="#0a2158").grid(row=2, column=3, padx=5, pady=2)
                
                # Length row
                tk.Label(limits_grid, text="Length (mm)", font=("Arial", 10), 
                        fg="lightgray", bg="#0a2158").grid(row=3, column=0, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['min_length']}", font=("Arial", 10), 
                        fg="#28a745", bg="#0a2158").grid(row=3, column=1, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['max_length']}", font=("Arial", 10), 
                        fg="#dc3545", bg="#0a2158").grid(row=3, column=2, padx=5, pady=2)
                tk.Label(limits_grid, text=f"{limits['min_length']} - {limits['max_length']} mm", 
                        font=("Arial", 10, "bold"), fg="#ffc107", bg="#0a2158").grid(row=3, column=3, padx=5, pady=2)
                
                # Warning message
                warning_label = tk.Label(self.admin_limits_display_frame, 
                                       text="⚠️ ALL users (including Super Admin) must create rollers within these global ranges or they will be rejected",
                                       font=("Arial", 10, "bold"), fg="#ff6b6b", bg="#0a2158", wraplength=600)
                warning_label.pack(pady=(15, 5))
                
                # Last updated info
                if limits.get('updated_at') and limits.get('updated_by'):
                    updated_info = tk.Label(self.admin_limits_display_frame, 
                                          text=f"Last updated: {limits['updated_at']} by {limits['updated_by']}",
                                          font=("Arial", 9), fg="#b0c4de", bg="#0a2158")
                    updated_info.pack(pady=2)
                
                print(f"✅ Displayed global limits for admin: {limits_text}")
            else:
                # No global limits found
                self.admin_current_limits_label.config(text="No global limits set", fg="#ffc107")
                no_limits_label = tk.Label(self.admin_limits_display_frame, 
                                        text="No global limits have been set by Super Admin\n\n"
                                             "✅ You can create rollers without global restrictions\n"
                                             "Contact Super Admin to set global limits if needed",
                                        font=("Arial", 11), fg="#28a745", bg="#0a2158", justify=tk.CENTER)
                no_limits_label.pack(pady=20)
                print("⚠️ No global limits found for admin display")
                
        except Exception as e:
            print(f"Error loading admin global limits: {e}")
            self.admin_current_limits_label.config(text="Error loading limits", fg="#dc3545")
            error_label = tk.Label(self.admin_limits_display_frame, 
                                 text=f"Error loading global limits: {e}",
                                 font=("Arial", 11), fg="#dc3545", bg="#0a2158")
            error_label.pack(pady=20)

    def load_admin_roller_types(self):
        """Load available roller types for admin validation info."""
        try:
            # Get roller types from database
            from database import db_manager
            roller_types = db_manager.get_all_roller_types()
            
            if roller_types:
                self.admin_roller_type_combo['values'] = roller_types
                print(f"✅ Loaded {len(roller_types)} roller types for admin validation info")
            else:
                self.admin_roller_type_combo['values'] = []
                print("⚠️ No roller types found for admin validation info")
                
        except Exception as e:
            print(f"Error loading roller types for admin: {e}")
            # Fallback with sample data
            self.admin_roller_type_combo['values'] = ["RT-6300", "RT63", "RT630", "32310", "4TN1248"]

    def on_admin_roller_type_selected(self, event=None):
        """Handle admin roller type selection and display specifications."""
        selected_type = self.admin_roller_type_var.get()
        if selected_type:
            self.display_admin_specifications(selected_type)

    def display_admin_specifications(self, roller_type):
        """Display specifications for the selected roller type to admin."""
        try:
            # Clear existing display
            for widget in self.admin_specs_display_frame.winfo_children():
                widget.destroy()
            
            # Get specifications from database
            from database import db_manager
            specs = db_manager.get_roller_specifications(roller_type)
            
            if specs:
                # Create specifications display
                title_label = tk.Label(self.admin_specs_display_frame, 
                                     text=f"Specifications for '{roller_type}'",
                                     font=("Arial", 12, "bold"), fg="white", bg="#0a2158")
                title_label.pack(pady=(0, 10))
                
                # Create grid for specifications
                specs_grid = tk.Frame(self.admin_specs_display_frame, bg="#0a2158")
                specs_grid.pack(fill=tk.X)
                
                # Headers
                tk.Label(specs_grid, text="Dimension", font=("Arial", 11, "bold"), 
                        fg="white", bg="#0a2158", width=12).grid(row=0, column=0, padx=5, pady=2)
                tk.Label(specs_grid, text="Minimum", font=("Arial", 11, "bold"), 
                        fg="white", bg="#0a2158", width=12).grid(row=0, column=1, padx=5, pady=2)
                tk.Label(specs_grid, text="Maximum", font=("Arial", 11, "bold"), 
                        fg="white", bg="#0a2158", width=12).grid(row=0, column=2, padx=5, pady=2)
                tk.Label(specs_grid, text="Valid Range", font=("Arial", 11, "bold"), 
                        fg="white", bg="#0a2158", width=20).grid(row=0, column=3, padx=5, pady=2)
                
                # Diameter row
                tk.Label(specs_grid, text="Diameter (mm)", font=("Arial", 10), 
                        fg="lightgray", bg="#0a2158").grid(row=1, column=0, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['min_diameter']}", font=("Arial", 10), 
                        fg="#28a745", bg="#0a2158").grid(row=1, column=1, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['max_diameter']}", font=("Arial", 10), 
                        fg="#dc3545", bg="#0a2158").grid(row=1, column=2, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['min_diameter']} - {specs['max_diameter']} mm", 
                        font=("Arial", 10, "bold"), fg="#ffc107", bg="#0a2158").grid(row=1, column=3, padx=5, pady=2)
                
                # Thickness row
                tk.Label(specs_grid, text="Thickness (mm)", font=("Arial", 10), 
                        fg="lightgray", bg="#0a2158").grid(row=2, column=0, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['min_thickness']}", font=("Arial", 10), 
                        fg="#28a745", bg="#0a2158").grid(row=2, column=1, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['max_thickness']}", font=("Arial", 10), 
                        fg="#dc3545", bg="#0a2158").grid(row=2, column=2, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['min_thickness']} - {specs['max_thickness']} mm", 
                        font=("Arial", 10, "bold"), fg="#ffc107", bg="#0a2158").grid(row=2, column=3, padx=5, pady=2)
                
                # Length row
                tk.Label(specs_grid, text="Length (mm)", font=("Arial", 10), 
                        fg="lightgray", bg="#0a2158").grid(row=3, column=0, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['min_length']}", font=("Arial", 10), 
                        fg="#28a745", bg="#0a2158").grid(row=3, column=1, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['max_length']}", font=("Arial", 10), 
                        fg="#dc3545", bg="#0a2158").grid(row=3, column=2, padx=5, pady=2)
                tk.Label(specs_grid, text=f"{specs['min_length']} - {specs['max_length']} mm", 
                        font=("Arial", 10, "bold"), fg="#ffc107", bg="#0a2158").grid(row=3, column=3, padx=5, pady=2)
                
                # Warning message
                warning_label = tk.Label(self.admin_specs_display_frame, 
                                       text="⚠️ Your roller entries must fall within these ranges or they will be rejected",
                                       font=("Arial", 10, "bold"), fg="#ff6b6b", bg="#0a2158", wraplength=600)
                warning_label.pack(pady=(15, 5))
                
                print(f"✅ Displayed specifications for {roller_type} to admin")
            else:
                # No specifications found
                no_specs_label = tk.Label(self.admin_specs_display_frame, 
                                        text=f"No specifications found for '{roller_type}'\n\n"
                                             "✅ You can create rollers of this type without restrictions",
                                        font=("Arial", 11), fg="#28a745", bg="#0a2158", justify=tk.CENTER)
                no_specs_label.pack(pady=20)
                print(f"⚠️ No specifications found for {roller_type}")
                
        except Exception as e:
            print(f"Error displaying admin specifications: {e}")
            error_label = tk.Label(self.admin_specs_display_frame, 
                                 text=f"Error loading specifications: {e}",
                                 font=("Arial", 11), fg="#dc3545", bg="#0a2158")
            error_label.pack(pady=20)
