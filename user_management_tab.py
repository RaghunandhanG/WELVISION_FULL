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
        """Setup the User Management tab"""
        # Main container
        main_container = tk.Frame(self.parent, bg="#0a2158")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Check access rights
        if not self.check_access_rights():
            self.show_access_denied(main_container)
            return
        
        # Title section
        self.setup_title_section(main_container)
        
        # Content container with two panels
        content_container = tk.Frame(main_container, bg="#0a2158")
        content_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left Panel - User List
        left_panel = tk.Frame(content_container, bg="#0a2158")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.setup_user_list_panel(left_panel)
        
        # Right Panel - User Details/Form
        right_panel = tk.Frame(content_container, bg="#0a2158")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        self.setup_user_form_panel(right_panel)
        
        # Bottom Panel - Action Buttons
        bottom_panel = tk.Frame(main_container, bg="#0a2158")
        bottom_panel.pack(fill=tk.X, pady=(10, 0))
        
        self.setup_action_buttons(bottom_panel)
        
        # Load users initially
        self.refresh_user_list()
    
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
        
        # Left side buttons
        left_buttons = tk.Frame(button_container, bg="#0a2158")
        left_buttons.pack(side=tk.LEFT)
        
        tk.Button(left_buttons, text="➕ Add New User", font=("Arial", 12, "bold"), 
                 bg="#28a745", fg="white", command=self.add_user, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(left_buttons, text="💾 Update User", font=("Arial", 12, "bold"), 
                 bg="#007bff", fg="white", command=self.update_user, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(left_buttons, text="🔑 Change Password", font=("Arial", 12, "bold"), 
                 bg="#ffc107", fg="black", command=self.change_password_dialog, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        # Center area - Status indicator
        center_frame = tk.Frame(button_container, bg="#0a2158")
        center_frame.pack(side=tk.LEFT, expand=True)
        
        self.status_label = tk.Label(center_frame, text="Ready", font=("Arial", 10), 
                                    fg="#b0c4de", bg="#0a2158")
        self.status_label.pack(pady=10)
        
        # Right side buttons
        right_buttons = tk.Frame(button_container, bg="#0a2158")
        right_buttons.pack(side=tk.RIGHT)
        
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
        """Handle user selection in the tree"""
        selection = self.user_tree.selection()
        if not selection:
            return
        
        item = self.user_tree.item(selection[0])
        values = item['values']
        
        if values:
            # Fill form with selected user data
            self.form_vars['employee_id'].set(values[0])
            self.form_vars['email'].set(values[1])
            self.form_vars['role'].set(values[2])
            self.form_vars['is_active'].set("Active" in values[3])
            
            # Clear password fields when selecting existing user
            self.form_vars['password'].set("")
            self.form_vars['confirm_password'].set("")
    
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
                else:
                    messagebox.showerror("Error", message)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add user: {str(e)}")
    
    def update_user(self):
        """Update selected user"""
        if not self.check_admin_access():
            return
        
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to update")
            return
        
        item = self.user_tree.item(selection[0])
        original_employee_id = item['values'][0]
        
        try:
            if not self.form_vars['employee_id'].get():
                messagebox.showerror("Error", "Employee ID is required")
                return
            
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
            
            if messagebox.askyesno("Confirm Update", 
                                  f"Are you sure you want to update user '{original_employee_id}'?"):
                
                from password_manager import password_manager
                
                success, message = password_manager.update_user(
                    employee_id=original_employee_id,
                    email=self.form_vars['email'].get(),
                    role=self.form_vars['role'].get(),
                    is_active=self.form_vars['is_active'].get()
                )
                
                if success:
                    messagebox.showinfo("Success", message)
                    self.refresh_user_list()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update user: {str(e)}")
    
    def delete_user(self):
        """Delete selected user"""
        if not hasattr(self.app, 'current_role') or self.app.current_role != 'Super Admin':
            messagebox.showerror("Access Denied", "User deletion requires Super Administrator privileges")
            return
        
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return
        
        item = self.user_tree.item(selection[0])
        employee_id = item['values'][0]
        
        if hasattr(self.app, 'current_user') and employee_id == self.app.current_user:
            messagebox.showerror("Error", "You cannot delete your own account")
            return
        
        if messagebox.askyesno("⚠️ CONFIRM DELETION", 
                              f"Are you sure you want to PERMANENTLY DELETE user '{employee_id}'?\n\n"
                              f"⚠️ This action CANNOT be undone!"):
            try:
                from password_manager import password_manager
                success, message = password_manager.delete_user(employee_id)
                
                if success:
                    messagebox.showinfo("Success", message)
                    self.refresh_user_list()
                    self.clear_form()
                else:
                    messagebox.showerror("Error", message)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
    
    def change_password_dialog(self):
        """Open change password dialog"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user to change password")
            return
        
        item = self.user_tree.item(selection[0])
        employee_id = item['values'][0]
        
        is_own_password = hasattr(self.app, 'current_user') and employee_id == self.app.current_user
        is_admin = hasattr(self.app, 'current_role') and self.app.current_role in ['Admin', 'Super Admin']
        
        if not is_own_password and not is_admin:
            messagebox.showerror("Access Denied", "You can only change your own password or need admin privileges")
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
        title_text = f"Change Password for {employee_id}"
        if employee_id == self.app.current_user:
            title_text += " (Your Account)"
        elif is_admin:
            title_text += f" (Admin Override)"
        
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
