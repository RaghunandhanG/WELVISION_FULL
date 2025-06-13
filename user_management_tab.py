"""
User Management Tab for WelVision Application
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox

class UserManagementTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.setup_tab()
    
    def setup_tab(self):
        """Setup the User Management tab with scrollable content"""
        # Create main canvas and scrollbar for scrollable content
        self.main_canvas = tk.Canvas(self.parent, bg="#0a2158")
        self.main_scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg="#0a2158")
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # Pack canvas and scrollbar
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.main_canvas.unbind_all("<MouseWheel>")
        
        self.main_canvas.bind('<Enter>', _bind_to_mousewheel)
        self.main_canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Add keyboard navigation support
        def _on_key_press(event):
            if event.keysym == 'Up':
                self.main_canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                self.main_canvas.yview_scroll(1, "units")
            elif event.keysym == 'Page_Up':
                self.main_canvas.yview_scroll(-10, "units")
            elif event.keysym == 'Page_Down':
                self.main_canvas.yview_scroll(10, "units")
            elif event.keysym == 'Home':
                self.main_canvas.yview_moveto(0)
            elif event.keysym == 'End':
                self.main_canvas.yview_moveto(1)
        
        # Make canvas focusable for keyboard events
        self.main_canvas.focus_set()
        self.main_canvas.bind('<Key>', _on_key_press)
        
        # Configure canvas window width to match canvas width
        def configure_canvas_window(event):
            canvas_width = event.width
            self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.main_canvas.bind('<Configure>', configure_canvas_window)
        
        # Main container inside scrollable frame
        main_container = tk.Frame(self.scrollable_frame, bg="#0a2158")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Check access rights
        if not self.check_access_rights():
            self.show_access_denied(main_container)
            return
        
        # Title section
        self.setup_title_section(main_container)
        
        # Content container with notebook for tabs
        content_container = tk.Frame(main_container, bg="#0a2158")
        content_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(content_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # User Management Tab
        user_tab = tk.Frame(self.notebook, bg="#0a2158")
        self.notebook.add(user_tab, text="👥 User Accounts")
        
        # Roller Management Tab
        roller_tab = tk.Frame(self.notebook, bg="#0a2158")
        self.notebook.add(roller_tab, text="🔧 Roller Information")
        
        # Setup User Management Tab
        self.setup_user_management_tab(user_tab)
        
        # Setup Roller Management Tab
        self.setup_roller_management_tab(roller_tab)
        
        # Load data initially (with delay to ensure widgets are created)
        self.parent.after(100, self.refresh_user_list)
        self.parent.after(200, self.refresh_roller_list)
    
    def check_access_rights(self):
        """Check if current user has access to user management"""
        if not hasattr(self.app, 'current_role'):
            return False
        return self.app.current_role in ['Admin', 'Super Admin']
    
    def show_access_denied(self, parent):
        """Show access denied message"""
        access_frame = tk.Frame(parent, bg="#0a2158")
        access_frame.pack(fill=tk.BOTH, expand=True)
        
        # Center the access denied message
        center_frame = tk.Frame(access_frame, bg="#0a2158")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Access denied icon and message
        tk.Label(center_frame, text="🚫", font=("Arial", 48), 
                fg="#dc3545", bg="#0a2158").pack(pady=(0, 20))
        
        tk.Label(center_frame, text="Access Denied", font=("Arial", 24, "bold"), 
                fg="#dc3545", bg="#0a2158").pack(pady=(0, 10))
        
        tk.Label(center_frame, text="User Management requires Administrator privileges", 
                font=("Arial", 14), fg="white", bg="#0a2158").pack(pady=(0, 20))
        
        tk.Label(center_frame, text="Please contact your system administrator", 
                font=("Arial", 12), fg="#b0c4de", bg="#0a2158").pack()
    
    def setup_user_management_tab(self, parent):
        """Setup the User Management tab content"""
        # Content container with two panels
        content_container = tk.Frame(parent, bg="#0a2158")
        content_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel - User List
        left_panel = tk.Frame(content_container, bg="#0a2158")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.setup_user_list_panel(left_panel)
        
        # Right Panel - User Details/Form
        right_panel = tk.Frame(content_container, bg="#0a2158")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.setup_user_form_panel(right_panel)
        
        # Bottom Panel - User Action Buttons
        bottom_panel = tk.Frame(parent, bg="#0a2158")
        bottom_panel.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.setup_action_buttons(bottom_panel)
    
    def setup_roller_management_tab(self, parent):
        """Setup the Roller Management tab content"""
        # Content container with two panels
        content_container = tk.Frame(parent, bg="#0a2158")
        content_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel - Roller List
        left_panel = tk.Frame(content_container, bg="#0a2158")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.setup_roller_list_panel(left_panel)
        
        # Right Panel - Roller Details/Form
        right_panel = tk.Frame(content_container, bg="#0a2158")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.setup_roller_form_panel(right_panel)
        
        # Bottom Panel - Roller Action Buttons
        bottom_panel = tk.Frame(parent, bg="#0a2158")
        bottom_panel.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.setup_roller_action_buttons(bottom_panel)
    
    def setup_title_section(self, parent):
        """Setup the title section"""
        title_frame = tk.Frame(parent, bg="#0a2158")
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="👥 User Management System", 
                              font=("Arial", 20, "bold"), fg="white", bg="#0a2158")
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Manage user accounts, roles, and passwords", 
                                 font=("Arial", 12), fg="#b0c4de", bg="#0a2158")
        subtitle_label.pack(pady=(5, 0))
        
        # Add scroll help text
        scroll_help = tk.Label(title_frame, text="💡 Use mouse wheel, arrow keys, or Page Up/Down to scroll", 
                              font=("Arial", 10), fg="#ffc107", bg="#0a2158")
        scroll_help.pack(pady=(5, 0))
    
    def setup_user_list_panel(self, parent):
        """Setup the user list panel"""
        # User List Frame
        list_frame = tk.LabelFrame(parent, text="📋 Current Users", font=("Arial", 14, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = tk.Frame(list_frame, bg="#0a2158")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍 Search:", font=("Arial", 10), 
                fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 10), width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_users)
        
        refresh_btn = tk.Button(search_frame, text="🔄", font=("Arial", 10), 
                               command=self.refresh_user_list, bg="#28a745", fg="white")
        refresh_btn.pack(side=tk.LEFT)
        
        # Treeview for user list
        tree_frame = tk.Frame(list_frame, bg="#0a2158")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("Employee ID", "Email", "Role", "Status", "Created", "Last Login")
        self.user_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns with better headers
        self.user_tree.heading("Employee ID", text="👤 Employee ID", anchor="w")
        self.user_tree.heading("Email", text="📧 Email Address", anchor="w")
        self.user_tree.heading("Role", text="🎭 Role", anchor="w")
        self.user_tree.heading("Status", text="🟢 Status", anchor="w")
        self.user_tree.heading("Created", text="📅 Created", anchor="w")
        self.user_tree.heading("Last Login", text="🕐 Last Login", anchor="w")
        
        # Set column widths for better scaling
        self.user_tree.column("Employee ID", width=120, minwidth=100)
        self.user_tree.column("Email", width=250, minwidth=200)
        self.user_tree.column("Role", width=120, minwidth=100)
        self.user_tree.column("Status", width=100, minwidth=80)
        self.user_tree.column("Created", width=120, minwidth=100)
        self.user_tree.column("Last Login", width=120, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.user_tree.xview)
        self.user_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Enable mouse wheel scrolling for the user tree
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling for the user tree"""
            self.user_tree.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel events (Windows and Linux)
        self.user_tree.bind("<MouseWheel>", _on_mousewheel)  # Windows
        self.user_tree.bind("<Button-4>", lambda e: self.user_tree.yview_scroll(-1, "units"))  # Linux scroll up
        self.user_tree.bind("<Button-5>", lambda e: self.user_tree.yview_scroll(1, "units"))   # Linux scroll down
        
        # Make the tree widget focusable so it can receive mouse wheel events
        self.user_tree.focus_set()
        
        # Bind selection event
        self.user_tree.bind('<<TreeviewSelect>>', self.on_user_select)
    
    def setup_user_form_panel(self, parent):
        """Setup the user form panel"""
        form_frame = tk.LabelFrame(parent, text="👤 User Details", font=("Arial", 14, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
        form_frame.pack(fill=tk.Y, expand=False)
        
        # Create regular frame for form (no scrolling)
        form_scrollable = tk.Frame(form_frame, bg="#0a2158")
        form_scrollable.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Form fields
        self.form_vars = {}
        
        # Employee ID
        tk.Label(form_scrollable, text="👤 Employee ID:", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(15, 3))
        self.form_vars['employee_id'] = tk.StringVar()
        tk.Entry(form_scrollable, textvariable=self.form_vars['employee_id'], 
                font=("Arial", 11), width=30).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Email
        tk.Label(form_scrollable, text="📧 Email Address:", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.form_vars['email'] = tk.StringVar()
        tk.Entry(form_scrollable, textvariable=self.form_vars['email'], 
                font=("Arial", 11), width=30).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Role
        tk.Label(form_scrollable, text="🎭 Role:", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.form_vars['role'] = tk.StringVar()
        role_combo = ttk.Combobox(form_scrollable, textvariable=self.form_vars['role'], 
                                 font=("Arial", 11), width=28, state="readonly")
        role_combo['values'] = ('User', 'Admin', 'Super Admin')
        role_combo.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Password section
        password_section = tk.LabelFrame(form_scrollable, text="🔑 Password", font=("Arial", 11, "bold"), 
                                        fg="white", bg="#0a2158")
        password_section.pack(fill=tk.X, padx=15, pady=15)
        
        # New password
        tk.Label(password_section, text="🆕 New Password:", font=("Arial", 10), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=10, pady=(10, 3))
        self.form_vars['password'] = tk.StringVar()
        tk.Entry(password_section, textvariable=self.form_vars['password'], 
                font=("Arial", 10), width=30, show="*").pack(anchor="w", padx=10, pady=(0, 10))
        
        # Confirm password
        tk.Label(password_section, text="✅ Confirm Password:", font=("Arial", 10), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=10, pady=(0, 3))
        self.form_vars['confirm_password'] = tk.StringVar()
        tk.Entry(password_section, textvariable=self.form_vars['confirm_password'], 
                font=("Arial", 10), width=30, show="*").pack(anchor="w", padx=10, pady=(0, 10))
        
        # Status section
        status_section = tk.LabelFrame(form_scrollable, text="🟢 Account Status", font=("Arial", 11, "bold"), 
                                      fg="white", bg="#0a2158")
        status_section.pack(fill=tk.X, padx=15, pady=15)
        
        self.form_vars['is_active'] = tk.BooleanVar(value=True)
        status_frame = tk.Frame(status_section, bg="#0a2158")
        status_frame.pack(anchor="w", padx=10, pady=10)
        
        tk.Radiobutton(status_frame, text="🟢 Active", variable=self.form_vars['is_active'], 
                      value=True, fg="white", bg="#0a2158", selectcolor="#0a2158", 
                      font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 20))
        tk.Radiobutton(status_frame, text="🔴 Inactive", variable=self.form_vars['is_active'], 
                      value=False, fg="white", bg="#0a2158", selectcolor="#0a2158", 
                      font=("Arial", 10)).pack(side=tk.LEFT)
        
        # Add some bottom padding
        tk.Label(form_scrollable, text="", bg="#0a2158").pack(pady=20)
    
    def setup_action_buttons(self, parent):
        """Setup action buttons"""
        # Create a container with better spacing
        button_container = tk.Frame(parent, bg="#0a2158")
        button_container.pack(fill=tk.X, padx=20, pady=10)
        
        # Left side buttons - User Operations
        left_buttons = tk.Frame(button_container, bg="#0a2158")
        left_buttons.pack(side=tk.LEFT)
        
        tk.Button(left_buttons, text="➕ Add New User", font=("Arial", 12, "bold"), 
                 bg="#28a745", fg="white", command=self.add_user, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(left_buttons, text="📖 Read User", font=("Arial", 12, "bold"), 
                 bg="#17a2b8", fg="white", command=self.read_user, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(left_buttons, text="💾 Update User", font=("Arial", 12, "bold"), 
                 bg="#007bff", fg="white", command=self.update_user, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(left_buttons, text="🔑 Change Password", font=("Arial", 12, "bold"), 
                 bg="#ffc107", fg="black", command=self.change_password_dialog, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        # Center area - Status indicator
        center_frame = tk.Frame(button_container, bg="#0a2158")
        center_frame.pack(side=tk.LEFT, expand=True)
        
        self.status_label = tk.Label(center_frame, text="Ready", font=("Arial", 10), 
                                    fg="#b0c4de", bg="#0a2158")
        self.status_label.pack(pady=10)
        
        # Right side buttons
        right_buttons = tk.Frame(button_container, bg="#0a2158")
        right_buttons.pack(side=tk.RIGHT)
        
        tk.Button(right_buttons, text="🚫 Deactivate User", font=("Arial", 12, "bold"), 
                 bg="#fd7e14", fg="white", command=self.deactivate_user, width=18).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(right_buttons, text="🗑️ Delete User", font=("Arial", 12, "bold"), 
                 bg="#dc3545", fg="white", command=self.delete_user, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(right_buttons, text="🔄 Clear Form", font=("Arial", 12, "bold"), 
                 bg="#6c757d", fg="white", command=self.clear_form, width=15).pack(side=tk.LEFT)
    
    def refresh_user_list(self):
        """Refresh the user list from database"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(text="🔄 Refreshing...", fg="yellow")
            
            from password_manager import password_manager
            
            # Clear existing items
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            
            # Get users from database
            users = password_manager.get_all_users()
            
            if not users:
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="⚠️ No users found", fg="orange")
                return
            
            for user in users:
                employee_id, email, role, created_at, last_login, is_active = user
                
                status = "🟢 Active" if is_active else "🔴 Inactive"
                created_str = str(created_at).split()[0] if created_at else "N/A"
                last_login_str = str(last_login).split()[0] if last_login else "Never"
                
                values = (employee_id, email, role, status, created_str, last_login_str)
                self.user_tree.insert("", tk.END, values=values)
            
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"✅ {len(users)} users loaded", fg="#28a745")
                self.parent.after(3000, lambda: self.status_label.config(text="Ready", fg="#b0c4de"))
                
        except Exception as e:
            error_msg = f"Failed to refresh user list: {str(e)}"
            if hasattr(self, 'status_label'):
                self.status_label.config(text="❌ Failed to load users", fg="red")
            messagebox.showerror("Error", error_msg)
    
    def filter_users(self, event=None):
        """Filter users based on search term"""
        search_term = self.search_var.get().lower()
        
        # If search is empty, refresh full list
        if not search_term:
            self.refresh_user_list()
            return
        
        # Clear current items
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        try:
            from password_manager import password_manager
            users = password_manager.get_all_users()
            
            for user in users:
                employee_id, email, role, created_at, last_login, is_active = user
                
                # Check if search term matches any field
                if (search_term in employee_id.lower() or 
                    search_term in email.lower() or 
                    search_term in role.lower()):
                    
                    status = "🟢 Active" if is_active else "🔴 Inactive"
                    created_str = str(created_at).split()[0] if created_at else "N/A"
                    last_login_str = str(last_login).split()[0] if last_login else "Never"
                    
                    self.user_tree.insert("", tk.END, values=(
                        employee_id, email, role, status, created_str, last_login_str
                    ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter users: {str(e)}")
    
    def on_user_select(self, event):
        """Handle user selection in the tree - just highlight, don't auto-load"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        # Update status to show which user is selected
        item = self.user_tree.item(selection[0])
        values = item['values']
        
        if values and hasattr(self, 'status_label'):
            self.status_label.config(text=f"📋 Selected: {values[0]} ({values[1]})", fg="#17a2b8")
    
    def read_user(self):
        """Read/Load selected user data into the form"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user from the table to read their information")
            return
        
        try:
            item = self.user_tree.item(selection[0])
            values = item['values']
            
            if values:
                # Fill form with selected user data
                self.form_vars['employee_id'].set(values[0])
                self.form_vars['email'].set(values[1])
                self.form_vars['role'].set(values[2])
                self.form_vars['is_active'].set("Active" in values[3])
                
                # Clear password fields when reading existing user
                self.form_vars['password'].set("")
                self.form_vars['confirm_password'].set("")
                
                # Update status
                if hasattr(self, 'status_label'):
                    self.status_label.config(text=f"📖 Loaded: {values[0]} data into form", fg="#28a745")
                    self.parent.after(3000, lambda: self.status_label.config(text="Ready", fg="#b0c4de"))
                
                messagebox.showinfo("User Loaded", 
                                  f"User information for '{values[0]}' has been loaded into the form.\n\n"
                                  f"Employee ID: {values[0]}\n"
                                  f"Email: {values[1]}\n"
                                  f"Role: {values[2]}\n"
                                  f"Status: {values[3]}\n\n"
                                  f"You can now make changes and click 'Update User' to save them.")
            else:
                messagebox.showerror("Error", "Unable to read user data from selection")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read user data: {str(e)}")
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.form_vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(True)
            else:
                var.set("")
    
    def check_admin_access(self):
        """Check if current user has admin access"""
        if not hasattr(self.app, 'current_role'):
            messagebox.showerror("Access Denied", "User role not identified")
            return False
        
        if self.app.current_role not in ['Admin', 'Super Admin']:
            messagebox.showerror("Access Denied", "This operation requires Administrator privileges")
            return False
        
        return True
    
    def add_user(self):
        """Add a new user"""
        if not self.check_admin_access():
            return
        
        try:
            if not self.validate_form(require_password=True):
                return
            
            # Check Super Admin constraint before showing confirmation
            role = self.form_vars['role'].get()
            if role == 'Super Admin':
                from password_manager import password_manager
                super_admin_count = password_manager.get_super_admin_count()
                if super_admin_count > 0:
                    super_admin_info = password_manager.get_super_admin_info()
                    if super_admin_info:
                        messagebox.showerror("Super Admin Constraint", 
                                           f"⚠️ Only one Super Admin is allowed in the system.\n\n"
                                           f"Current Super Admin: {super_admin_info[0]} ({super_admin_info[1]})\n"
                                           f"Created: {super_admin_info[2]}\n\n"
                                           f"Please select a different role (User or Admin).")
                    else:
                        messagebox.showerror("Super Admin Constraint", 
                                           "⚠️ Only one Super Admin is allowed in the system.\n"
                                           "Please select a different role (User or Admin).")
                    return
            
            if messagebox.askyesno("Confirm Add User", 
                                  f"Add new user '{self.form_vars['employee_id'].get()}' "
                                  f"with role '{self.form_vars['role'].get()}'?"):
                
                from password_manager import password_manager
                
                success, message = password_manager.create_user(
                    employee_id=self.form_vars['employee_id'].get(),
                    email=self.form_vars['email'].get(),
                    password=self.form_vars['password'].get(),
                    role=self.form_vars['role'].get()
                )
                
                if success:
                    messagebox.showinfo("Success", message)
                    self.refresh_user_list()
                    self.clear_form()
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text="✅ User added successfully", fg="#28a745")
                        self.parent.after(3000, lambda: self.status_label.config(text="Ready", fg="#b0c4de"))
                else:
                    messagebox.showerror("Error", message)
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text="❌ Failed to add user", fg="red")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add user: {str(e)}")
            if hasattr(self, 'status_label'):
                self.status_label.config(text="❌ Error adding user", fg="red")
    
    def update_user(self):
        """Update user with form data"""
        if not self.check_admin_access():
            return
        
        # Check if form has data
        if not self.form_vars['employee_id'].get():
            messagebox.showwarning("Warning", 
                                 "No user data in form. Please:\n"
                                 "1. Select a user from the table\n"
                                 "2. Click 'Read User' to load their data\n"
                                 "3. Make your changes\n"
                                 "4. Click 'Update User' to save")
            return
        
        # Find the original user in the table to get the original employee_id
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", 
                                 "Please select the user from the table that you want to update")
            return
        
        item = self.user_tree.item(selection[0])
        original_employee_id = item['values'][0]
        
        try:
            # Validate form data
            if not self.form_vars['email'].get():
                messagebox.showerror("Error", "Email is required")
                return
            
            if not self.form_vars['role'].get():
                messagebox.showerror("Error", "Role is required")
                return
            
            email = self.form_vars['email'].get()
            if '@' not in email or '.' not in email:
                messagebox.showerror("Error", "Please enter a valid email address")
                return
            
            # Show confirmation with changes
            current_employee_id = self.form_vars['employee_id'].get()
            current_email = self.form_vars['email'].get()
            current_role = self.form_vars['role'].get()
            current_status = "Active" if self.form_vars['is_active'].get() else "Inactive"
            
            confirm_msg = (f"Update user '{original_employee_id}' with the following changes?\n\n"
                          f"Employee ID: {current_employee_id}\n"
                          f"Email: {current_email}\n"
                          f"Role: {current_role}\n"
                          f"Status: {current_status}")
            
            if messagebox.askyesno("Confirm Update", confirm_msg):
                
                from password_manager import password_manager
                
                success, message = password_manager.update_user(
                    employee_id=original_employee_id,
                    email=current_email,
                    role=current_role,
                    is_active=self.form_vars['is_active'].get()
                )
                
                if success:
                    messagebox.showinfo("Success", f"✅ {message}")
                    self.refresh_user_list()
                    self.clear_form()
                    
                    # Update status
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text=f"✅ Updated: {original_employee_id}", fg="#28a745")
                        self.parent.after(3000, lambda: self.status_label.config(text="Ready", fg="#b0c4de"))
                else:
                    messagebox.showerror("Error", f"❌ {message}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update user: {str(e)}")
    
    def delete_user(self):
        """Delete selected user with enhanced error handling"""
        if not hasattr(self.app, 'current_role') or self.app.current_role != 'Super Admin':
            messagebox.showerror("Access Denied", "User deletion requires Super Administrator privileges")
            return
        
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        item = self.user_tree.item(selection[0])
        employee_id = item['values'][0]
        user_role = item['values'][2]
        
        if hasattr(self.app, 'current_user') and employee_id == self.app.current_user:
            messagebox.showerror("Error", "You cannot delete your own account")
            return
        
        # Enhanced warning dialog
        warning_msg = (f"⚠️ PERMANENT DELETION WARNING ⚠️\n\n"
                      f"User: {employee_id} ({user_role})\n"
                      f"Email: {item['values'][1]}\n\n"
                      f"This will PERMANENTLY DELETE the user account.\n"
                      f"If the user has associated data (sessions, settings),\n"
                      f"the deletion may fail due to database constraints.\n\n"
                      f"💡 Consider using 'Deactivate User' instead for safer removal.\n\n"
                      f"Are you sure you want to proceed with PERMANENT DELETION?")
        
        if messagebox.askyesno("⚠️ CONFIRM PERMANENT DELETION", warning_msg):
            try:
                from password_manager import password_manager
                success, message = password_manager.delete_user(employee_id)
                
                if success:
                    messagebox.showinfo("✅ Success", f"User {employee_id} has been permanently deleted.\n\n{message}")
                    self.refresh_user_list()
                    self.clear_form()
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text=f"✅ Deleted user {employee_id}", fg="#28a745")
                else:
                    # Show detailed error with suggestion
                    error_msg = f"❌ Deletion Failed\n\n{message}\n\n💡 Suggestion: Use 'Deactivate User' instead to safely disable the account while preserving data integrity."
                    messagebox.showerror("Deletion Failed", error_msg)
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text="❌ Deletion failed", fg="red")
                
            except Exception as e:
                error_msg = f"❌ System Error\n\nFailed to delete user: {str(e)}\n\n💡 Try using 'Deactivate User' instead."
                messagebox.showerror("System Error", error_msg)
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="❌ System error", fg="red")
    
    def deactivate_user(self):
        """Deactivate selected user (safer alternative to deletion)"""
        if not hasattr(self.app, 'current_role') or self.app.current_role not in ['Admin', 'Super Admin']:
            messagebox.showerror("Access Denied", "User deactivation requires Administrator privileges")
            return
        
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to deactivate")
            return
        
        item = self.user_tree.item(selection[0])
        employee_id = item['values'][0]
        user_role = item['values'][2]
        current_status = item['values'][3]
        
        if hasattr(self.app, 'current_user') and employee_id == self.app.current_user:
            messagebox.showerror("Error", "You cannot deactivate your own account")
            return
        
        if "Inactive" in current_status:
            messagebox.showinfo("Already Inactive", f"User {employee_id} is already deactivated.")
            return
        
        # Confirmation dialog
        confirm_msg = (f"🚫 Deactivate User Account\n\n"
                      f"User: {employee_id} ({user_role})\n"
                      f"Email: {item['values'][1]}\n\n"
                      f"This will deactivate the user account, preventing login\n"
                      f"while preserving all associated data and history.\n\n"
                      f"✅ The account can be reactivated later if needed.\n\n"
                      f"Proceed with deactivation?")
        
        if messagebox.askyesno("🚫 Confirm Deactivation", confirm_msg):
            try:
                from password_manager import password_manager
                success, message = password_manager.deactivate_user(employee_id)
                
                if success:
                    messagebox.showinfo("✅ Success", f"User {employee_id} has been deactivated.\n\n{message}")
                    self.refresh_user_list()
                    self.clear_form()
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text=f"✅ Deactivated user {employee_id}", fg="#fd7e14")
                else:
                    messagebox.showerror("Error", f"Failed to deactivate user:\n\n{message}")
                    if hasattr(self, 'status_label'):
                        self.status_label.config(text="❌ Deactivation failed", fg="red")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to deactivate user: {str(e)}")
                if hasattr(self, 'status_label'):
                    self.status_label.config(text="❌ System error", fg="red")
    
    def change_password_dialog(self):
        """Open change password dialog with role hierarchy enforcement"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to change password")
            return
        
        item = self.user_tree.item(selection[0])
        employee_id = item['values'][0]
        target_role = item['values'][2]  # Role is in column 2
        
        is_own_password = hasattr(self.app, 'current_user') and employee_id == self.app.current_user
        current_role = getattr(self.app, 'current_role', None)
        
        # Enforce role hierarchy for password changes
        if not is_own_password:
            if not current_role or current_role not in ['Admin', 'Super Admin']:
                messagebox.showerror("Access Denied", "You can only change your own password or need admin privileges")
                return
            
            # Admin can only change User passwords
            if current_role == 'Admin' and target_role != 'User':
                messagebox.showerror("Access Denied", f"Admin can only change User passwords, not {target_role} passwords")
                return
            
            # Super Admin can change Admin and User passwords, but not other Super Admin
            if current_role == 'Super Admin' and target_role == 'Super Admin' and employee_id != self.app.current_user:
                messagebox.showerror("Access Denied", "Cannot change another Super Admin's password")
                return
        
        # Create password change dialog
        dialog = tk.Toplevel(self.app)
        dialog.title(f"🔑 Change Password - {employee_id}")
        dialog.configure(bg="#0a2158")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.app)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Dialog content
        title_text = f"Change Password for {employee_id} ({target_role})"
        if employee_id == self.app.current_user:
            title_text += " (Your Account)"
        elif current_role in ['Admin', 'Super Admin']:
            title_text += f" ({current_role} Override)"
        
        tk.Label(dialog, text=title_text, 
                font=("Arial", 14, "bold"), fg="white", bg="#0a2158").pack(pady=20)
        
        # Old password (for current user only)
        if employee_id == self.app.current_user:
            tk.Label(dialog, text="🔑 Current Password:", font=("Arial", 10), 
                    fg="white", bg="#0a2158").pack(anchor="w", padx=50, pady=(10, 2))
            old_password_var = tk.StringVar()
            tk.Entry(dialog, textvariable=old_password_var, font=("Arial", 10), 
                    width=30, show="*").pack(padx=50, pady=(0, 10))
        else:
            old_password_var = None
        
        # New password
        tk.Label(dialog, text="🆕 New Password:", font=("Arial", 10), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=50, pady=(10, 2))
        new_password_var = tk.StringVar()
        tk.Entry(dialog, textvariable=new_password_var, font=("Arial", 10), 
                width=30, show="*").pack(padx=50, pady=(0, 10))
        
        # Confirm password
        tk.Label(dialog, text="✅ Confirm Password:", font=("Arial", 10), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=50, pady=(0, 2))
        confirm_password_var = tk.StringVar()
        tk.Entry(dialog, textvariable=confirm_password_var, font=("Arial", 10), 
                width=30, show="*").pack(padx=50, pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(dialog, bg="#0a2158")
        button_frame.pack(pady=10)
        
        def change_password():
            try:
                new_pass = new_password_var.get()
                confirm_pass = confirm_password_var.get()
                
                if not new_pass:
                    messagebox.showerror("Error", "Please enter a new password")
                    return
                
                if new_pass != confirm_pass:
                    messagebox.showerror("Error", "Passwords do not match")
                    return
                
                if len(new_pass) < 6:
                    messagebox.showerror("Error", "Password must be at least 6 characters long")
                    return
                
                from password_manager import password_manager
                
                if old_password_var:
                    old_pass = old_password_var.get()
                    if not old_pass:
                        messagebox.showerror("Error", "Please enter your current password")
                        return
                    
                    success, message = password_manager.change_password(
                        employee_id, old_pass, new_pass
                    )
                else:
                    if hasattr(self.app, 'current_user'):
                        success, message = password_manager.admin_change_password(
                            self.app.current_user, employee_id, new_pass
                        )
                    else:
                        messagebox.showerror("Error", "Current user not identified")
                        return
                
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", message)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change password: {str(e)}")
        
        tk.Button(button_frame, text="✅ Change Password", font=("Arial", 10, "bold"), 
                 bg="#28a745", fg="white", command=change_password).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="❌ Cancel", font=("Arial", 10, "bold"), 
                 bg="#dc3545", fg="white", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def validate_form(self, require_password=True):
        """Validate form fields"""
        if not self.form_vars['employee_id'].get():
            messagebox.showerror("Error", "Employee ID is required")
            return False
        
        if not self.form_vars['email'].get():
            messagebox.showerror("Error", "Email is required")
            return False
        
        if not self.form_vars['role'].get():
            messagebox.showerror("Error", "Role is required")
            return False
        
        email = self.form_vars['email'].get()
        if '@' not in email or '.' not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return False
        
        if require_password:
            password = self.form_vars['password'].get()
            confirm_password = self.form_vars['confirm_password'].get()
            
            if not password:
                messagebox.showerror("Error", "Password is required")
                return False
            
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return False
            
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return False
        
        return True 
    
    # ==================== ROLLER MANAGEMENT METHODS ====================
    
    def setup_roller_list_panel(self, parent):
        """Setup the roller list panel"""
        # Roller List Frame
        list_frame = tk.LabelFrame(parent, text="🔧 Roller Information", font=("Arial", 14, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = tk.Frame(list_frame, bg="#0a2158")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍 Search:", font=("Arial", 10), 
                fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=(0, 5))
        
        self.roller_search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.roller_search_var, font=("Arial", 10), width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_rollers)
        
        refresh_btn = tk.Button(search_frame, text="🔄", font=("Arial", 10), 
                               command=self.refresh_roller_list, bg="#28a745", fg="white")
        refresh_btn.pack(side=tk.LEFT)
        
        # Treeview for roller list
        tree_frame = tk.Frame(list_frame, bg="#0a2158")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns = ("ID", "Name", "Type", "Diameter", "Thickness", "Length", "Status")
        self.roller_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns with better headers
        self.roller_tree.heading("ID", text="🆔 ID", anchor="w")
        self.roller_tree.heading("Name", text="📛 Name", anchor="w")
        self.roller_tree.heading("Type", text="🔧 Type", anchor="w")
        self.roller_tree.heading("Diameter", text="📏 Diameter", anchor="w")
        self.roller_tree.heading("Thickness", text="📐 Thickness", anchor="w")
        self.roller_tree.heading("Length", text="📏 Length", anchor="w")
        self.roller_tree.heading("Status", text="🟢 Status", anchor="w")
        
        # Set column widths
        self.roller_tree.column("ID", width=60, minwidth=50)
        self.roller_tree.column("Name", width=200, minwidth=150)
        self.roller_tree.column("Type", width=150, minwidth=100)
        self.roller_tree.column("Diameter", width=100, minwidth=80)
        self.roller_tree.column("Thickness", width=100, minwidth=80)
        self.roller_tree.column("Length", width=100, minwidth=80)
        self.roller_tree.column("Status", width=100, minwidth=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.roller_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.roller_tree.xview)
        self.roller_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.roller_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Enable mouse wheel scrolling
        def _on_roller_mousewheel(event):
            self.roller_tree.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.roller_tree.bind("<MouseWheel>", _on_roller_mousewheel)
        self.roller_tree.bind("<Button-4>", lambda e: self.roller_tree.yview_scroll(-1, "units"))
        self.roller_tree.bind("<Button-5>", lambda e: self.roller_tree.yview_scroll(1, "units"))
        self.roller_tree.focus_set()
        
        # Bind selection event
        self.roller_tree.bind('<<TreeviewSelect>>', self.on_roller_select)
    
    def setup_roller_form_panel(self, parent):
        """Setup the roller form panel"""
        form_frame = tk.LabelFrame(parent, text="🔧 Roller Details", font=("Arial", 14, "bold"), 
                                  fg="white", bg="#0a2158", bd=2)
        form_frame.pack(fill=tk.Y, expand=False)
        
        # Create form
        form_scrollable = tk.Frame(form_frame, bg="#0a2158")
        form_scrollable.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Form fields
        self.roller_form_vars = {}
        
        # Roller ID (read-only)
        tk.Label(form_scrollable, text="🆔 Roller ID:", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(15, 3))
        self.roller_form_vars['id'] = tk.StringVar()
        id_entry = tk.Entry(form_scrollable, textvariable=self.roller_form_vars['id'], 
                           font=("Arial", 11), width=30, state="readonly")
        id_entry.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Name
        tk.Label(form_scrollable, text="📛 Name:", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.roller_form_vars['name'] = tk.StringVar()
        tk.Entry(form_scrollable, textvariable=self.roller_form_vars['name'], 
                font=("Arial", 11), width=30).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Type
        tk.Label(form_scrollable, text="🔧 Type:", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.roller_form_vars['roller_type'] = tk.StringVar()
        tk.Entry(form_scrollable, textvariable=self.roller_form_vars['roller_type'], 
                font=("Arial", 11), width=30).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Diameter
        tk.Label(form_scrollable, text="📏 Diameter (mm):", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.roller_form_vars['diameter'] = tk.StringVar()
        tk.Entry(form_scrollable, textvariable=self.roller_form_vars['diameter'], 
                font=("Arial", 11), width=30).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Thickness
        tk.Label(form_scrollable, text="📐 Thickness (mm):", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.roller_form_vars['thickness'] = tk.StringVar()
        tk.Entry(form_scrollable, textvariable=self.roller_form_vars['thickness'], 
                font=("Arial", 11), width=30).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Length
        tk.Label(form_scrollable, text="📏 Length (mm):", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.roller_form_vars['length'] = tk.StringVar()
        tk.Entry(form_scrollable, textvariable=self.roller_form_vars['length'], 
                font=("Arial", 11), width=30).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Description
        tk.Label(form_scrollable, text="📝 Description:", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.roller_form_vars['description'] = tk.StringVar()
        tk.Entry(form_scrollable, textvariable=self.roller_form_vars['description'], 
                font=("Arial", 11), width=30).pack(anchor="w", padx=15, pady=(0, 15))
        
        # Status
        tk.Label(form_scrollable, text="🟢 Status:", font=("Arial", 11, "bold"), 
                fg="white", bg="#0a2158").pack(anchor="w", padx=15, pady=(0, 3))
        self.roller_form_vars['status'] = tk.StringVar()
        status_combo = ttk.Combobox(form_scrollable, textvariable=self.roller_form_vars['status'], 
                                   font=("Arial", 11), width=28, state="readonly")
        status_combo['values'] = ('Active', 'Inactive', 'Maintenance')
        status_combo.pack(anchor="w", padx=15, pady=(0, 15))
        
        # Add bottom padding
        tk.Label(form_scrollable, text="", bg="#0a2158").pack(pady=20)
    
    def setup_roller_action_buttons(self, parent):
        """Setup roller action buttons"""
        button_container = tk.Frame(parent, bg="#0a2158")
        button_container.pack(fill=tk.X, padx=20, pady=10)
        
        # Left side buttons
        left_buttons = tk.Frame(button_container, bg="#0a2158")
        left_buttons.pack(side=tk.LEFT)
        
        tk.Button(left_buttons, text="📖 Read Roller", font=("Arial", 12, "bold"), 
                 bg="#17a2b8", fg="white", command=self.read_roller, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(left_buttons, text="💾 Update Roller", font=("Arial", 12, "bold"), 
                 bg="#007bff", fg="white", command=self.update_roller, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        # Center area - Status indicator
        center_frame = tk.Frame(button_container, bg="#0a2158")
        center_frame.pack(side=tk.LEFT, expand=True)
        
        self.roller_status_label = tk.Label(center_frame, text="Ready", font=("Arial", 10), 
                                           fg="#b0c4de", bg="#0a2158")
        self.roller_status_label.pack(pady=10)
        
        # Right side buttons
        right_buttons = tk.Frame(button_container, bg="#0a2158")
        right_buttons.pack(side=tk.RIGHT)
        
        tk.Button(right_buttons, text="🔄 Clear Form", font=("Arial", 12, "bold"), 
                 bg="#6c757d", fg="white", command=self.clear_roller_form, width=15).pack(side=tk.LEFT)
    
    def refresh_roller_list(self):
        """Refresh the roller list from database"""
        try:
            # Check if roller tree exists before trying to refresh
            if not hasattr(self, 'roller_tree'):
                print("Roller tree not initialized yet, skipping refresh")
                return
                
            if hasattr(self, 'roller_status_label'):
                self.roller_status_label.config(text="🔄 Refreshing...", fg="yellow")
            
            from database import db_manager
            
            # Clear existing items
            for item in self.roller_tree.get_children():
                self.roller_tree.delete(item)
            
            # Get rollers from database
            rollers = db_manager.get_all_rollers()
            
            if not rollers:
                if hasattr(self, 'roller_status_label'):
                    self.roller_status_label.config(text="⚠️ No rollers found", fg="orange")
                return
            
            for roller in rollers:
                roller_id = roller.get('id', '')
                name = roller.get('name', '')
                roller_type = roller.get('roller_type', '')
                diameter = f"{roller.get('diameter', 0):.3f}"
                thickness = f"{roller.get('thickness', 0):.3f}"
                length = f"{roller.get('length', 0):.3f}"
                status = roller.get('status', 'Active')
                
                values = (roller_id, name, roller_type, diameter, thickness, length, status)
                self.roller_tree.insert("", tk.END, values=values)
            
            if hasattr(self, 'roller_status_label'):
                self.roller_status_label.config(text=f"✅ {len(rollers)} rollers loaded", fg="#28a745")
                self.parent.after(3000, lambda: self.roller_status_label.config(text="Ready", fg="#b0c4de"))
                
        except Exception as e:
            error_msg = f"Failed to refresh roller list: {str(e)}"
            if hasattr(self, 'roller_status_label'):
                self.roller_status_label.config(text="❌ Failed to load rollers", fg="red")
            print(f"Error: {error_msg}")
    
    def filter_rollers(self, event=None):
        """Filter rollers based on search term"""
        if not hasattr(self, 'roller_tree'):
            return
            
        search_term = self.roller_search_var.get().lower()
        
        # If search is empty, refresh full list
        if not search_term:
            self.refresh_roller_list()
            return
        
        # Clear current items
        for item in self.roller_tree.get_children():
            self.roller_tree.delete(item)
        
        try:
            from database import db_manager
            rollers = db_manager.get_all_rollers()
            
            for roller in rollers:
                name = roller.get('name', '').lower()
                roller_type = roller.get('roller_type', '').lower()
                description = roller.get('description', '').lower()
                
                # Check if search term matches any field
                if (search_term in name or 
                    search_term in roller_type or 
                    search_term in description):
                    
                    roller_id = roller.get('id', '')
                    name_display = roller.get('name', '')
                    roller_type_display = roller.get('roller_type', '')
                    diameter = f"{roller.get('diameter', 0):.3f}"
                    thickness = f"{roller.get('thickness', 0):.3f}"
                    length = f"{roller.get('length', 0):.3f}"
                    status = roller.get('status', 'Active')
                    
                    self.roller_tree.insert("", tk.END, values=(
                        roller_id, name_display, roller_type_display, diameter, thickness, length, status
                    ))
                    
        except Exception as e:
            print(f"Error filtering rollers: {str(e)}")
    
    def on_roller_select(self, event):
        """Handle roller selection in the tree"""
        if not hasattr(self, 'roller_tree'):
            return
            
        selection = self.roller_tree.selection()
        if not selection:
            return
        
        # Update status to show which roller is selected
        item = self.roller_tree.item(selection[0])
        values = item['values']
        
        if values and hasattr(self, 'roller_status_label'):
            self.roller_status_label.config(text=f"📋 Selected: {values[1]} (ID: {values[0]})", fg="#17a2b8")
    
    def read_roller(self):
        """Read/Load selected roller data into the form"""
        if not hasattr(self, 'roller_tree'):
            messagebox.showwarning("Warning", "Roller management not initialized")
            return
            
        selection = self.roller_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a roller from the table to read its information")
            return
        
        try:
            item = self.roller_tree.item(selection[0])
            values = item['values']
            
            if values:
                # Get full roller data from database
                roller_id = values[0]
                from database import db_manager
                
                # Get roller by ID
                cursor = db_manager.connection.cursor()
                cursor.execute("SELECT * FROM roller_informations WHERE id = %s", (roller_id,))
                roller_data = cursor.fetchone()
                cursor.close()
                
                if roller_data:
                    # Map database fields to form variables
                    self.roller_form_vars['id'].set(str(roller_data[0]))  # id
                    self.roller_form_vars['name'].set(roller_data[1] or '')  # name
                    self.roller_form_vars['diameter'].set(str(roller_data[2] or 0))  # diameter
                    self.roller_form_vars['thickness'].set(str(roller_data[3] or 0))  # thickness
                    self.roller_form_vars['length'].set(str(roller_data[4] or 0))  # length
                    self.roller_form_vars['roller_type'].set(roller_data[5] or '')  # roller_type
                    self.roller_form_vars['description'].set(roller_data[6] or '')  # description
                    self.roller_form_vars['status'].set(roller_data[7] or 'Active')  # status
                    
                    # Update status
                    if hasattr(self, 'roller_status_label'):
                        self.roller_status_label.config(text=f"📖 Loaded: {roller_data[1]} data into form", fg="#28a745")
                        self.parent.after(3000, lambda: self.roller_status_label.config(text="Ready", fg="#b0c4de"))
                    
                    messagebox.showinfo("Roller Loaded", 
                                      f"Roller information for '{roller_data[1]}' has been loaded into the form.\n\n"
                                      f"ID: {roller_data[0]}\n"
                                      f"Name: {roller_data[1]}\n"
                                      f"Type: {roller_data[5]}\n"
                                      f"Dimensions: {roller_data[2]}×{roller_data[3]}×{roller_data[4]} mm\n"
                                      f"Status: {roller_data[7]}\n\n"
                                      f"You can now make changes and click 'Update Roller' to save them.")
                else:
                    messagebox.showerror("Error", "Roller data not found in database")
            else:
                messagebox.showerror("Error", "Unable to read roller data from selection")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read roller data: {str(e)}")
    
    def update_roller(self):
        """Update roller with form data"""
        if not self.check_admin_access():
            return
        
        # Check if form has data
        if not self.roller_form_vars['id'].get():
            messagebox.showwarning("Warning", 
                                 "No roller data in form. Please:\n"
                                 "1. Select a roller from the table\n"
                                 "2. Click 'Read Roller' to load its data\n"
                                 "3. Make your changes\n"
                                 "4. Click 'Update Roller' to save")
            return
        
        try:
            # Validate form data
            if not self.roller_form_vars['name'].get():
                messagebox.showerror("Error", "Roller name is required")
                return
            
            # Validate numeric fields
            try:
                diameter = float(self.roller_form_vars['diameter'].get())
                thickness = float(self.roller_form_vars['thickness'].get())
                length = float(self.roller_form_vars['length'].get())
            except ValueError:
                messagebox.showerror("Error", "Diameter, thickness, and length must be valid numbers")
                return
            
            if diameter <= 0 or thickness <= 0 or length <= 0:
                messagebox.showerror("Error", "Diameter, thickness, and length must be positive numbers")
                return
            
            # Get form data
            roller_id = self.roller_form_vars['id'].get()
            name = self.roller_form_vars['name'].get()
            roller_type = self.roller_form_vars['roller_type'].get()
            description = self.roller_form_vars['description'].get()
            status = self.roller_form_vars['status'].get()
            
            # Show confirmation
            confirm_msg = (f"Update roller ID {roller_id} with the following changes?\n\n"
                          f"Name: {name}\n"
                          f"Type: {roller_type}\n"
                          f"Diameter: {diameter} mm\n"
                          f"Thickness: {thickness} mm\n"
                          f"Length: {length} mm\n"
                          f"Description: {description}\n"
                          f"Status: {status}")
            
            if messagebox.askyesno("Confirm Update", confirm_msg):
                from database import db_manager
                
                # Update in database
                cursor = db_manager.connection.cursor()
                update_query = """
                UPDATE roller_informations 
                SET name = %s, diameter = %s, thickness = %s, length = %s, 
                    roller_type = %s, description = %s, status = %s, updated_at = NOW()
                WHERE id = %s
                """
                cursor.execute(update_query, (name, diameter, thickness, length, 
                                            roller_type, description, status, roller_id))
                db_manager.connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"✅ Roller '{name}' updated successfully!")
                self.refresh_roller_list()
                self.clear_roller_form()
                
                # Update status
                if hasattr(self, 'roller_status_label'):
                    self.roller_status_label.config(text=f"✅ Updated: {name}", fg="#28a745")
                    self.parent.after(3000, lambda: self.roller_status_label.config(text="Ready", fg="#b0c4de"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update roller: {str(e)}")
    
    def clear_roller_form(self):
        """Clear all roller form fields"""
        if hasattr(self, 'roller_form_vars'):
            for var in self.roller_form_vars.values():
                var.set("")

