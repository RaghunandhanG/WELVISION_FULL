"""
Model Management Tab for WelVision Application
Handles uploading, listing, and managing AI models for inference
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from datetime import datetime
import threading
from database import db_manager

# UI Constants
APP_BG_COLOR = "#0a2158"
BUTTON_COLOR = "#007bff"
SUCCESS_COLOR = "#28a745"
DANGER_COLOR = "#dc3545"
WARNING_COLOR = "#ffc107"

class ModelManagementTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.models_dir = "models"  # Directory to store model files
        
        # Ensure models directory exists
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
        
        self.setup_tab()
    
    def setup_tab(self):
        """Setup the Model Management tab interface"""
        # Configure the parent frame
        self.parent.configure(bg=APP_BG_COLOR)
        
        # Main container with padding
        main_frame = tk.Frame(self.parent, bg=APP_BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="AI Model Management", 
                              font=("Arial", 18, "bold"), fg="white", bg=APP_BG_COLOR)
        title_label.pack(pady=(0, 20))
        
        # Create two main sections: Upload and Model List
        self.create_upload_section(main_frame)
        self.create_model_list_section(main_frame)
        
        # Load existing models
        self.refresh_model_list()
    
    def create_upload_section(self, parent):
        """Create the model upload section"""
        # Upload section frame
        upload_frame = tk.LabelFrame(parent, text="Upload New Model", 
                                   font=("Arial", 14, "bold"), fg="white", 
                                   bg=APP_BG_COLOR, bd=2)
        upload_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Model details form
        self.create_model_form(upload_frame)
        
        # Upload button
        upload_btn = tk.Button(upload_frame, text="Browse & Upload Model", 
                              font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg="white",
                              command=self.browse_and_upload)
        upload_btn.pack(pady=10)
    

    
    def create_model_form(self, parent):
        """Create form for model details"""
        form_frame = tk.Frame(parent, bg=APP_BG_COLOR)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Model Name
        tk.Label(form_frame, text="Model Name:", font=("Arial", 10), 
                fg="white", bg=APP_BG_COLOR).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.model_name_var = tk.StringVar()
        self.model_name_entry = tk.Entry(form_frame, textvariable=self.model_name_var, 
                                        font=("Arial", 10), width=30)
        self.model_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Model Type
        tk.Label(form_frame, text="Model Type:", font=("Arial", 10), 
                fg="white", bg=APP_BG_COLOR).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.model_type_var = tk.StringVar(value="OD")
        self.model_type_combo = ttk.Combobox(form_frame, textvariable=self.model_type_var,
                                           values=["OD", "BIGFACE"], state="readonly",
                                           font=("Arial", 10), width=15)
        self.model_type_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Configure grid weights
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=2)
    
    def create_model_list_section(self, parent):
        """Create the model list and management section"""
        # Model list frame
        list_frame = tk.LabelFrame(parent, text="📋 Installed Models", 
                                 font=("Arial", 14, "bold"), fg="white", 
                                 bg=APP_BG_COLOR, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filter and action buttons
        self.create_filter_buttons(list_frame)
        
        # Model table
        self.create_model_table(list_frame)
        
        # Action buttons
        self.create_action_buttons(list_frame)
    
    def create_filter_buttons(self, parent):
        """Create filter buttons for model types"""
        filter_frame = tk.Frame(parent, bg=APP_BG_COLOR)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filter by Type:", font=("Arial", 10), 
                fg="white", bg=APP_BG_COLOR).pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="ALL")
        filter_options = ["ALL", "OD", "BIGFACE"]
        
        for option in filter_options:
            tk.Radiobutton(filter_frame, text=option, variable=self.filter_var, value=option,
                          fg="white", bg=APP_BG_COLOR, selectcolor=APP_BG_COLOR,
                          font=("Arial", 9), command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        tk.Button(filter_frame, text="Refresh", font=("Arial", 9), 
                 bg=BUTTON_COLOR, fg="white", command=self.refresh_model_list).pack(side=tk.RIGHT, padx=5)
    
    def create_model_table(self, parent):
        """Create table to display models"""
        table_frame = tk.Frame(parent, bg=APP_BG_COLOR)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Define columns
        columns = ("ID", "Name", "Type", "Model Path", "Upload Date", "Uploaded By", "Active")
        
        self.model_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Configure column headings and widths
        column_widths = {
            "ID": 50, "Name": 150, "Type": 80, "Model Path": 300,
            "Upload Date": 120, "Uploaded By": 100, "Active": 60
        }
        
        for col in columns:
            self.model_tree.heading(col, text=col)
            self.model_tree.column(col, width=column_widths[col], anchor="center")
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.model_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.model_tree.xview)
        self.model_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.model_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Enable mouse wheel scrolling for the model tree
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling for the model tree"""
            self.model_tree.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel events (Windows and Linux)
        self.model_tree.bind("<MouseWheel>", _on_mousewheel)  # Windows
        self.model_tree.bind("<Button-4>", lambda e: self.model_tree.yview_scroll(-1, "units"))  # Linux scroll up
        self.model_tree.bind("<Button-5>", lambda e: self.model_tree.yview_scroll(1, "units"))   # Linux scroll down
        
        # Make the tree widget focusable so it can receive mouse wheel events
        self.model_tree.focus_set()
        
        # Bind double-click event
        self.model_tree.bind("<Double-1>", self.on_model_double_click)
    
    def create_action_buttons(self, parent):
        """Create action buttons for model management"""
        action_frame = tk.Frame(parent, bg=APP_BG_COLOR)
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Left side buttons
        left_frame = tk.Frame(action_frame, bg=APP_BG_COLOR)
        left_frame.pack(side=tk.LEFT)
        
        tk.Button(left_frame, text="Set as Active", font=("Arial", 12, "bold"),
                 bg=SUCCESS_COLOR, fg="white", command=self.set_active_model, 
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(left_frame, text="View Details", font=("Arial", 12, "bold"),
                 bg=BUTTON_COLOR, fg="white", command=self.view_model_details, 
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # Right side buttons
        right_frame = tk.Frame(action_frame, bg=APP_BG_COLOR)
        right_frame.pack(side=tk.RIGHT)
        
        tk.Button(right_frame, text="Delete Model", font=("Arial", 12, "bold"),
                 bg=DANGER_COLOR, fg="white", command=self.delete_selected_model, 
                 width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(action_frame, textvariable=self.status_var, 
                                   font=("Arial", 9), fg="white", bg=APP_BG_COLOR)
        self.status_label.pack(expand=True)
    
    def browse_and_upload(self):
        """Browse for model file and upload"""
        file_types = [
            ("PyTorch Models", "*.pt *.pth"),
            ("ONNX Models", "*.onnx"),
            ("TensorFlow Models", "*.h5 *.pb"),
            ("TensorFlow Lite", "*.tflite"),
            ("All Model Files", "*.pt *.pth *.onnx *.h5 *.pb *.tflite"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=file_types
        )
        
        if file_path:
            # Auto-fill model name
            file_name = os.path.basename(file_path)
            if not self.model_name_var.get():
                model_name = os.path.splitext(file_name)[0]
                self.model_name_var.set(model_name)
            
            self.upload_model_file(file_path)
    
    def upload_model_file(self, source_path):
        """Upload model file to system"""
        try:
            # Validate form
            model_name = self.model_name_var.get().strip()
            model_type = self.model_type_var.get()
            
            if not model_name:
                messagebox.showerror("Error", "Please enter a model name")
                return
            
            # Get current user ID
            employee_id = getattr(self.app, 'current_user', 'SYSTEM')
            
            # Show progress
            self.update_status("Uploading model...")
            
            # Create destination path
            file_name = os.path.basename(source_path)
            dest_dir = os.path.join(self.models_dir, model_type.lower())
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            
            dest_path = os.path.join(dest_dir, f"{model_name}_{file_name}")
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Save to database based on model type
            if model_type == "OD":
                success, message = db_manager.upload_od_model(
                    model_name=model_name,
                    model_path=dest_path,
                    uploaded_by=employee_id,
                    set_active=False
                )
            elif model_type == "BIGFACE":
                success, message = db_manager.upload_bigface_model(
                    model_name=model_name,
                    model_path=dest_path,
                    uploaded_by=employee_id,
                    set_active=False
                )
            else:
                success, message = False, "Invalid model type"
            
            if success:
                messagebox.showinfo("Success", f"Model uploaded successfully!\n{message}")
                self.clear_form()
                self.refresh_model_list()
                self.update_status("Model uploaded successfully")
                
                # Refresh model dropdowns in inference tab if it exists
                if hasattr(self.app, 'inference_tab'):
                    self.app.inference_tab.refresh_model_dropdowns()
            else:
                # Remove copied file on database error
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                messagebox.showerror("Error", f"Failed to save model: {message}")
                self.update_status("Upload failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Upload failed: {e}")
            self.update_status("Upload failed")
    
    def refresh_model_list(self):
        """Refresh the model list from database"""
        try:
            self.update_status("Loading models...")
            
            # Clear existing items
            for item in self.model_tree.get_children():
                self.model_tree.delete(item)
            
            # Get filter
            filter_type = self.filter_var.get()
            
            # Get models from database based on filter
            all_models = []
            
            if filter_type == "ALL" or filter_type == "OD":
                od_models = db_manager.get_od_models()
                for model in od_models:
                    model['model_type'] = 'OD'
                all_models.extend(od_models)
            
            if filter_type == "ALL" or filter_type == "BIGFACE":
                bf_models = db_manager.get_bigface_models()
                for model in bf_models:
                    model['model_type'] = 'BIGFACE'
                all_models.extend(bf_models)
            
            # Populate table
            for model in all_models:
                upload_date = model['upload_date'].strftime("%Y-%m-%d %H:%M") if model['upload_date'] else "N/A"
                
                values = (
                    model['id'],
                    model['model_name'],
                    model['model_type'],
                    model['model_path'],
                    upload_date,
                    model['uploaded_by'] or "N/A",
                    "✅" if model['is_active'] else "❌"
                )
                
                item = self.model_tree.insert("", tk.END, values=values)
                
                # Highlight active models
                if model['is_active']:
                    self.model_tree.set(item, "Active", "✅ ACTIVE")
            
            self.update_status(f"Loaded {len(all_models)} models")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load models: {e}")
            self.update_status("Failed to load models")
    
    def apply_filter(self):
        """Apply model type filter"""
        self.refresh_model_list()
    
    def get_selected_model_id(self):
        """Get the ID of the selected model"""
        selection = self.model_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a model from the list.")
            return None
        
        item = self.model_tree.item(selection[0])
        return item['values'][0]  # ID is first column
    
    def set_active_model(self):
        """Set the selected model as active"""
        model_id = self.get_selected_model_id()
        if not model_id:
            return
        
        try:
            # Get model details
            selection = self.model_tree.selection()[0]
            values = self.model_tree.item(selection)['values']
            model_name = values[1]
            model_type = values[2]
            
            # Confirm activation
            if messagebox.askyesno("Confirm Activation", 
                                 f"Set '{model_name}' as the active {model_type} model?\n\n"
                                 f"This will deactivate any other {model_type} models."):
                
                # Call appropriate method based on model type
                if model_type == "OD":
                    success, message = db_manager.set_active_od_model(model_id, "ADMIN")
                elif model_type == "BIGFACE":
                    success, message = db_manager.set_active_bigface_model(model_id, "ADMIN")
                else:
                    success, message = False, "Invalid model type"
                
                if success:
                    messagebox.showinfo("Success", f"Model '{model_name}' is now active!")
                    self.refresh_model_list()
                    self.update_status(f"Model '{model_name}' activated")
                    
                    # Refresh model dropdowns in inference tab if it exists
                    if hasattr(self.app, 'inference_tab'):
                        self.app.inference_tab.refresh_model_dropdowns()
                else:
                    messagebox.showerror("Error", f"Failed to activate model: {message}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Activation failed: {e}")
    
    def delete_selected_model(self):
        """Delete the selected model"""
        model_id = self.get_selected_model_id()
        if not model_id:
            return
        
        try:
            # Get model details
            selection = self.model_tree.selection()[0]
            values = self.model_tree.item(selection)['values']
            model_name = values[1]
            model_type = values[2]
            model_path = values[3]
            is_active = "✅" in str(values[6])
            
            # Warn if active model
            warning_msg = f"Delete model '{model_name}' ({model_type})?\n\nPath: {model_path}\n\n"
            if is_active:
                warning_msg += "⚠️ WARNING: This is the currently active model!\nDeleting it may affect inference operations.\n\n"
            warning_msg += "This action cannot be undone!"
            
            if messagebox.askyesno("Confirm Deletion", warning_msg, icon='warning'):
                # Call appropriate method based on model type
                if model_type == "OD":
                    success, message = db_manager.delete_od_model(model_id, "ADMIN")
                elif model_type == "BIGFACE":
                    success, message = db_manager.delete_bigface_model(model_id, "ADMIN")
                else:
                    success, message = False, "Invalid model type"
                
                if success:
                    # Also try to delete the file
                    try:
                        if os.path.exists(model_path):
                            os.remove(model_path)
                            print(f"🗑️ Deleted model file: {model_path}")
                    except Exception as file_err:
                        print(f"⚠️ Warning: Could not delete model file: {file_err}")
                    
                    messagebox.showinfo("Success", f"Model '{model_name}' deleted successfully!")
                    self.refresh_model_list()
                    self.update_status(f"Model '{model_name}' deleted")
                    
                    # Refresh model dropdowns in inference tab if it exists
                    if hasattr(self.app, 'inference_tab'):
                        self.app.inference_tab.refresh_model_dropdowns()
                else:
                    messagebox.showerror("Error", f"Failed to delete model: {message}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Deletion failed: {e}")
    
    def view_model_details(self):
        """View detailed information about the selected model"""
        model_id = self.get_selected_model_id()
        if not model_id:
            return
        
        try:
            # Get model details from the current selection
            selection = self.model_tree.selection()[0]
            values = self.model_tree.item(selection)['values']
            model_name = values[1]
            model_type = values[2]
            model_path = values[3]
            upload_date = values[4]
            uploaded_by = values[5]
            is_active = values[6]
            
            # Create details window
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Model Details - {model_name}")
            details_window.configure(bg=APP_BG_COLOR)
            details_window.geometry("600x400")
            
            # Model details
            details_text = tk.Text(details_window, font=("Consolas", 10), bg="white", 
                                 fg="black", wrap=tk.WORD, state=tk.DISABLED)
            details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Format model information
            info = f"""
Model Information
{'=' * 50}

ID: {model_id}
Name: {model_name}
Type: {model_type}

File Details
{'=' * 50}
File Path: {model_path}
File Exists: {'✅ Yes' if os.path.exists(model_path) else '❌ No'}

Upload Information
{'=' * 50}
Upload Date: {upload_date}
Uploaded By: {uploaded_by}

Status
{'=' * 50}
Active: {is_active}
            """
            
            details_text.config(state=tk.NORMAL)
            details_text.insert(tk.END, info.strip())
            details_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model details: {e}")
    
    def on_model_double_click(self, event):
        """Handle double-click on model"""
        self.view_model_details()
    
    def clear_form(self):
        """Clear the upload form"""
        self.model_name_var.set("")
        self.model_type_var.set("OD")
    
    def get_file_size_mb(self, file_path):
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except:
            return 0
    
    def update_status(self, message):
        """Update status message"""
        self.status_var.set(message)
        print(f"Model Management: {message}")
        # Auto-clear status after 5 seconds
        self.parent.after(5000, lambda: self.status_var.set("Ready")) 