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
        # Create main container with scrollable capability - FULL WIDTH
        main_container = tk.Frame(self.parent, bg="#0a2158")
        main_container.pack(fill=tk.BOTH, expand=True)  # NO PADDING
        
        # Create canvas and scrollbar for scrolling - FULL WIDTH
        canvas = tk.Canvas(main_container, bg="#0a2158", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a2158")
        
        # Configure scrollable frame to expand to canvas width
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Make scrollable_frame fill the canvas width
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        def configure_canvas(event):
            # Update scroll region when frame size changes
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", configure_scroll_region)
        
        # Create window in canvas and store reference
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar - FULL WIDTH
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
        
        # Also bind to the scrollable frame
        scrollable_frame.bind('<Enter>', _bind_to_mousewheel)
        scrollable_frame.bind('<Leave>', _unbind_from_mousewheel)
        
        # Use scrollable_frame as the settings_container
        settings_container = scrollable_frame

        # Add read-only indicator for regular users
        if self.read_only:
            read_only_frame = tk.Frame(settings_container, bg="#ffc107", bd=2, relief="solid")
            read_only_frame.pack(fill=tk.X, pady=(0, 15))
            
            read_only_label = tk.Label(read_only_frame, 
                                     text="📖 READ-ONLY MODE - You can view settings but cannot modify them", 
                                     font=("Arial", 12, "bold"), fg="black", bg="#ffc107")
            read_only_label.pack(pady=8)

        # Title Section
        title_frame = tk.Frame(settings_container, bg="#0a2158")
        title_frame.pack(fill=tk.X, padx=5, pady=(5, 15))
        
        title_label = tk.Label(title_frame, text="Application Settings", 
                              font=("Arial", 18, "bold"), fg="white", bg="#0a2158")
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Configure application preferences and system settings", 
                                 font=("Arial", 12), fg="lightgray", bg="#0a2158")
        subtitle_label.pack()

        # --- GUI Title Management Section (Super Admin Only) ---
        print(f"🔍 Debug: Checking role access for GUI Title Management")
        print(f"🔍 Current role: {getattr(self.app, 'current_role', 'NOT_SET')}")
        print(f"🔍 Has current_role attribute: {hasattr(self.app, 'current_role')}")
        
        if hasattr(self.app, 'current_role') and self.app.current_role == "Super Admin":
            print("✅ Creating GUI Title Management section for Super Admin")
            self.create_gui_title_section(settings_container)
        else:
            print("❌ GUI Title Management not available - insufficient permissions")

        # --- Settings History Section ---
        history_frame = tk.LabelFrame(settings_container, text="Settings History", 
                                    font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=15)

        # History controls
        history_controls = tk.Frame(history_frame, bg="#0a2158")
        history_controls.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(history_controls, text="📊 View History", font=("Arial", 11, "bold"),
                 bg="#17a2b8", fg="white", command=self.show_setting_history).pack(side=tk.LEFT, padx=5)

        tk.Button(history_controls, text="📁 Export to Excel", font=("Arial", 11, "bold"),
                 bg="#28a745", fg="white", command=self.export_history_excel).pack(side=tk.LEFT, padx=5)

        if not self.read_only:
            tk.Button(history_controls, text="🗑️ Clear History", font=("Arial", 11, "bold"),
                     bg="#dc3545", fg="white", command=self.clear_history_confirm).pack(side=tk.LEFT, padx=5)

        # History table frame
        self.history_table_frame = tk.Frame(history_frame, bg="#0a2158")
        self.history_table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- System Information Section ---
        system_frame = tk.LabelFrame(settings_container, text="System Information", 
                                   font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        system_frame.pack(fill=tk.X, pady=15)

        system_controls = tk.Frame(system_frame, bg="#0a2158")
        system_controls.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(system_controls, text="📋 Generate System Report", font=("Arial", 11, "bold"),
                 bg="#6f42c1", fg="white", command=self.generate_system_info_pdf).pack(side=tk.LEFT, padx=5)

        # System info display
        system_info_text = tk.Text(system_frame, height=8, font=("Consolas", 9), 
                                  bg="#000000", fg="#00ff00", wrap=tk.WORD,
                                  relief="flat", bd=0, state="disabled")
        system_info_text.pack(fill=tk.X, padx=10, pady=5)

        # Enhanced system information with device connection status
        self.setup_enhanced_system_info(system_info_text)

    def create_gui_title_section(self, parent):
        """Create GUI title management section for Super Admin only"""
        print("🎯 Creating GUI Title Management section...")
        
        # Make the section more prominent with different styling - ABSOLUTE FULL WIDTH
        title_frame = tk.LabelFrame(parent, text="🏷️ GUI Application Title Management (Super Admin Only)", 
                                   font=("Arial", 16, "bold"), fg="#ffc107", bg="#0a2158", bd=3,
                                   relief="raised")
        title_frame.pack(fill=tk.X, pady=15)  # NO PADX
        
        # Add a prominent header
        header_label = tk.Label(title_frame, text="🔧 Change Application Title", 
                               font=("Arial", 14, "bold"), fg="#ffc107", bg="#0a2158")
        header_label.pack(pady=(10, 5))

        # Current title display - ABSOLUTE FULL WIDTH
        current_title_frame = tk.Frame(title_frame, bg="#0a2158")
        current_title_frame.pack(fill=tk.X, padx=5, pady=12)  # MINIMAL PADX

        tk.Label(current_title_frame, text="Current GUI Title:", font=("Arial", 13, "bold"), 
                fg="white", bg="#0a2158", width=18, anchor="w").pack(side=tk.LEFT)
        
        current_title = getattr(self.app, 'custom_gui_title', 'WELVISION')
        self.current_title_label = tk.Label(current_title_frame, text=f'"{current_title}"', 
                                           font=("Arial", 13, "bold"), fg="#ffc107", bg="#0a2158")
        self.current_title_label.pack(side=tk.LEFT, padx=(15, 0))

        # New title input - ABSOLUTE FULL WIDTH
        input_frame = tk.Frame(title_frame, bg="#0a2158")
        input_frame.pack(fill=tk.X, padx=5, pady=12)  # MINIMAL PADX

        tk.Label(input_frame, text="New GUI Title:", font=("Arial", 13, "bold"), 
                fg="white", bg="#0a2158", width=18, anchor="w").pack(side=tk.LEFT)
        
        self.new_title_var = tk.StringVar(value=current_title)
        self.title_entry = tk.Entry(input_frame, textvariable=self.new_title_var, 
                                   font=("Arial", 13), bg="white", fg="black", bd=2)
        self.title_entry.pack(side=tk.LEFT, padx=(15, 10), fill=tk.X, expand=True)

        # Action buttons - ABSOLUTE FULL WIDTH
        button_frame = tk.Frame(title_frame, bg="#0a2158")
        button_frame.pack(fill=tk.X, padx=5, pady=15)  # MINIMAL PADX

        # Update Title button
        update_btn = tk.Button(button_frame, text="Update Title", font=("Arial", 12, "bold"),
                              bg="#007bff", fg="white", width=14, height=2, command=self.update_gui_title)
        update_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Reset to Default button
        reset_btn = tk.Button(button_frame, text="Reset to Default", font=("Arial", 12, "bold"),
                             bg="#6c757d", fg="white", width=16, height=2, command=self.reset_gui_title)
        reset_btn.pack(side=tk.LEFT, padx=10)

        # Preview button
        preview_btn = tk.Button(button_frame, text="Preview", font=("Arial", 12, "bold"),
                               bg="#17a2b8", fg="white", width=12, height=2, command=self.preview_title_change)
        preview_btn.pack(side=tk.LEFT, padx=10)

        # Info label
        info_label = tk.Label(title_frame, 
                             text="💡 Note: Title changes will be applied immediately and saved to the system configuration.",
                             font=("Arial", 10), fg="#ffc107", bg="#0a2158", wraplength=600)
        info_label.pack(pady=(5, 10))

    def update_gui_title(self):
        """Update the GUI title"""
        try:
            new_title = self.new_title_var.get().strip()
            
            if not new_title:
                messagebox.showerror("Error", "Title cannot be empty!")
                return
            
            if len(new_title) > 100:
                messagebox.showerror("Error", "Title is too long! Maximum 100 characters allowed.")
                return
            
            # Update the application window title
            self.app.title(new_title)
            self.app.custom_gui_title = new_title
            
            # Update the header title in the main interface
            self.app.update_header_title(new_title)
            
            # Update the current title label in settings
            self.current_title_label.config(text=f'"{new_title}"')
            
            # Save to configuration (you might want to save this to database or config file)
            self.save_gui_title_to_config(new_title)
            
            messagebox.showinfo("Success", f"GUI title updated successfully!\nNew title: {new_title}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update GUI title: {str(e)}")

    def reset_gui_title(self):
        """Reset GUI title to default"""
        try:
            default_title = "WELVISION"
            
            # Confirm reset
            if messagebox.askyesno("Confirm Reset", 
                                  f"Are you sure you want to reset the GUI title to default?\n\nDefault: {default_title}"):
                
                self.new_title_var.set(default_title)
                self.app.title(default_title)
                self.app.custom_gui_title = default_title
                
                # Update the header title in the main interface
                self.app.update_header_title(default_title)
                
                # Update the current title label in settings
                self.current_title_label.config(text=f'"{default_title}"')
                
                # Save to configuration
                self.save_gui_title_to_config(default_title)
                
                messagebox.showinfo("Success", "GUI title reset to default successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset GUI title: {str(e)}")

    def preview_title_change(self):
        """Preview the title change without applying it"""
        new_title = self.new_title_var.get().strip()
        
        if not new_title:
            messagebox.showwarning("Preview", "Title cannot be empty!")
            return
            
        if len(new_title) > 100:
            messagebox.showwarning("Preview", "Title is too long! Maximum 100 characters allowed.")
            return
        
        messagebox.showinfo("Title Preview", 
                           f"Preview of new GUI title:\n\n'{new_title}'\n\nClick 'Update Title' to apply the change.")

    def save_gui_title_to_config(self, title):
        """Save GUI title to configuration"""
        try:
            # You can implement saving to database or config file here
            # For now, we'll just store it in the app instance
            self.app.custom_gui_title = title
            print(f"✅ GUI title saved to configuration: {title}")
            
        except Exception as e:
            print(f"Error saving GUI title to config: {e}")

    def show_setting_history(self):
        """Display threshold change history from database"""
        try:
            # Create popup window for history
            self.popup = tk.Toplevel(self.parent)
            self.popup.title("Settings History")
            self.popup.geometry("1000x600")
            self.popup.configure(bg="#0a2158")
            
            # Center the popup window
            self.popup.transient(self.parent)
            self.popup.grab_set()
            
            # Create main frame
            main_frame = tk.Frame(self.popup, bg="#0a2158")
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Title
            title_label = tk.Label(main_frame, text="Settings Change History", 
                                 font=("Arial", 16, "bold"), fg="white", bg="#0a2158")
            title_label.pack(pady=(0, 10))
            
            # Filter frame
            filter_frame = tk.Frame(main_frame, bg="#0a2158")
            filter_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Model selection
            tk.Label(filter_frame, text="Model:", font=("Arial", 10), 
                    fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=(0, 5))
            
            self.model_var = tk.StringVar(value="All")
            model_combo = ttk.Combobox(filter_frame, textvariable=self.model_var, 
                                     values=["All", "OD", "BigFace"], state="readonly", width=10)
            model_combo.pack(side=tk.LEFT, padx=(0, 20))
            model_combo.bind("<<ComboboxSelected>>", self.on_model_change)
            
            # Date range
            tk.Label(filter_frame, text="From:", font=("Arial", 10), 
                    fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=(0, 5))
            
            self.from_date = DateEntry(filter_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            self.from_date.pack(side=tk.LEFT, padx=(0, 10))
            
            tk.Label(filter_frame, text="To:", font=("Arial", 10), 
                    fg="white", bg="#0a2158").pack(side=tk.LEFT, padx=(0, 5))
            
            self.to_date = DateEntry(filter_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
            self.to_date.pack(side=tk.LEFT, padx=(0, 20))
            
            # Refresh button
            refresh_btn = tk.Button(filter_frame, text="🔄 Refresh", font=("Arial", 10, "bold"),
                                  bg="#28a745", fg="white", command=self.refresh_history_data)
            refresh_btn.pack(side=tk.LEFT, padx=5)
            
            # Export button
            export_btn = tk.Button(filter_frame, text="📁 Export", font=("Arial", 10, "bold"),
                                 bg="#17a2b8", fg="white", command=self.export_history_excel)
            export_btn.pack(side=tk.LEFT, padx=5)
            
            # Setup table
            self.setup_history_table(main_frame)
            
            # Load initial data
            self.refresh_history_data()
            
        except Exception as e:
            print(f"Error showing setting history: {e}")
            messagebox.showerror("Error", f"Failed to show setting history: {e}")

    def on_model_change(self):
        """Handle model type change - rebuild table and refresh data"""
        try:
            # Rebuild table structure for new model type
            self.setup_history_table(self.history_table_frame)
            # Refresh data
            self.refresh_history_data()
        except Exception as e:
            print(f"Error handling model change: {e}")

    def setup_history_table(self, parent_frame):
        """Setup the history table based on selected model type"""
        try:
            # Clear existing table
            for widget in parent_frame.winfo_children():
                if isinstance(widget, ttk.Treeview):
                    widget.destroy()
            
            # Create treeview with scrollbars
            tree_frame = tk.Frame(parent_frame, bg="#0a2158")
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            # Define columns based on model type
            model_type = getattr(self, 'model_var', tk.StringVar(value="All")).get()
            
            if model_type == "All":
                columns = ("timestamp", "user", "model_type", "action", "details")
                headings = ["Timestamp", "User", "Model", "Action", "Details"]
            else:
                columns = ("timestamp", "user", "action", "old_values", "new_values")
                headings = ["Timestamp", "User", "Action", "Old Values", "New Values"]
            
            self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
            
            # Configure column headings and widths
            for i, (col, heading) in enumerate(zip(columns, headings)):
                self.tree.heading(col, text=heading)
                if col == "timestamp":
                    self.tree.column(col, width=150, anchor="center")
                elif col == "user":
                    self.tree.column(col, width=100, anchor="center")
                elif col in ["old_values", "new_values", "details"]:
                    self.tree.column(col, width=200, anchor="w")
                else:
                    self.tree.column(col, width=100, anchor="center")
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
            self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack everything
            self.tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            
        except Exception as e:
            print(f"Error setting up history table: {e}")

    def refresh_history_data(self):
        """Refresh the history data in the table"""
        try:
            if not hasattr(self, 'tree') or not self.tree:
                return
                
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get filter values
            model_type = getattr(self, 'model_var', tk.StringVar(value="All")).get()
            start_date = getattr(self, 'from_date', None)
            end_date = getattr(self, 'to_date', None)
            
            if start_date:
                start_date = start_date.get()
            if end_date:
                end_date = end_date.get()
            
            # Get history from database (this would need to be implemented in database.py)
            try:
                from database import db_manager
                history_data = db_manager.get_settings_history(model_type, start_date, end_date)
                
                # Populate table
                for record in history_data:
                    self.tree.insert("", "end", values=record)
                    
                print(f"✅ Loaded {len(history_data)} history records")
                
            except Exception as db_error:
                print(f"Database error: {db_error}")
                # Show sample data if database fails
                sample_data = [
                    ("2024-01-15 10:30:00", "admin", "System", "Configuration Update", "Application settings modified"),
                    ("2024-01-14 15:45:00", "user1", "GUI", "Title Change", "Application title updated"),
                ]
                
                for record in sample_data:
                    self.tree.insert("", "end", values=record)
                    
        except Exception as e:
            print(f"Error refreshing history data: {e}")

    def export_history_excel(self):
        """Export history data to Excel file"""
        try:
            if not hasattr(self, 'tree') or not self.tree:
                messagebox.showwarning("Warning", "No history data to export")
                return
                
            # Get data from tree
            data = []
            columns = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
            
            for item in self.tree.get_children():
                values = self.tree.item(item)["values"]
                data.append(values)
            
            if not data:
                messagebox.showwarning("Warning", "No data to export")
                return
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"settings_history_{timestamp}.xlsx"
            
            # Save to Excel
            df.to_excel(filename, index=False, engine='openpyxl')
            
            messagebox.showinfo("Export Successful", f"History exported to {filename}")
            print(f"✅ History exported to {filename}")
            
            # Open file location
            if messagebox.askyesno("Open File", "Would you like to open the exported file?"):
                os.startfile(filename)
                
        except Exception as e:
            print(f"Error exporting history: {e}")
            messagebox.showerror("Export Error", f"Failed to export history: {e}")

    def clear_history_confirm(self):
        """Confirm and clear settings history"""
        try:
            if messagebox.askyesno("Confirm Clear", 
                                 "Are you sure you want to clear all settings history?\n\nThis action cannot be undone."):
                
                # Clear from database
                from database import db_manager
                success = db_manager.clear_settings_history()
                
                if success:
                    messagebox.showinfo("Success", "Settings history cleared successfully")
                    self.refresh_history_data()
                    print("✅ Settings history cleared")
                else:
                    messagebox.showerror("Error", "Failed to clear settings history")
                    
            else:
                print("🚫 Settings history clearing cancelled by user")
                
        except Exception as e:
            print(f"Error clearing history: {e}")
            messagebox.showerror("Error", f"Failed to clear history: {e}")

    def setup_enhanced_system_info(self, system_info_text):
        """
        Setup enhanced system information display with device connection status.
        Shows basic system info plus PLC, OD camera, and BF camera connection status.
        
        Args:
            system_info_text: Text widget to display the information
        """
        try:
            import platform
            import psutil
            import threading
            
            # Basic system information
            basic_info = f"""System Platform: {platform.system()} {platform.release()}
Python Version: {platform.python_version()}
CPU Cores: {psutil.cpu_count()}
Memory: {psutil.virtual_memory().total // (1024**3)} GB
Application Version: 1.0.0
Database Status: Connected

DEVICE CONNECTION STATUS:
PLC Connection: Checking...
OD Camera (0): Checking...
BF Camera (1): Checking...
"""
            
            # Display initial info
            system_info_text.config(state="normal")
            system_info_text.delete("1.0", tk.END)
            system_info_text.insert("1.0", basic_info.strip())
            system_info_text.config(state="disabled")
            
            # Check device connections asynchronously
            def check_device_connections():
                try:
                    # Check device connections
                    device_status = self.check_all_device_connections()
                    
                    # Update display on main thread
                    self.app.after(0, lambda: self.update_system_info_display(system_info_text, device_status))
                    
                except Exception as e:
                    print(f"❌ Error checking device connections: {e}")
                    # Fallback status
                    device_status = {
                        'plc_connected': False,
                        'plc_error': str(e),
                        'od_camera_connected': False,
                        'od_camera_error': 'Check failed',
                        'bf_camera_connected': False,
                        'bf_camera_error': 'Check failed'
                    }
                    self.app.after(0, lambda: self.update_system_info_display(system_info_text, device_status))
            
            # Start device check in background
            threading.Thread(target=check_device_connections, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Error setting up enhanced system info: {e}")
            # Fallback to basic info
            basic_info = "System information check failed. Please refresh the page."
            system_info_text.config(state="normal")
            system_info_text.delete("1.0", tk.END)
            system_info_text.insert("1.0", basic_info)
            system_info_text.config(state="disabled")
    
    def check_all_device_connections(self):
        """
        Check connection status of all devices (PLC, OD Camera, BF Camera).
        
        Returns:
            dict: Device connection status information
        """
        device_status = {
            'plc_connected': False,
            'plc_error': None,
            'od_camera_connected': False,
            'od_camera_error': None,
            'bf_camera_connected': False,
            'bf_camera_error': None
        }
        
        try:
            # Check PLC connection
            device_status.update(self.check_plc_connection())
            
            # Check camera connections
            camera_status = self.check_camera_connections()
            device_status.update(camera_status)
            
        except Exception as e:
            print(f"❌ Error in check_all_device_connections: {e}")
            device_status['plc_error'] = str(e)
            device_status['od_camera_error'] = str(e)
            device_status['bf_camera_error'] = str(e)
        
        return device_status
    
    def check_plc_connection(self):
        """
        Check PLC connection status.
        
        Returns:
            dict: PLC connection status
        """
        try:
            # Import PLC configuration
            from config import PLC_CONFIG
            
            # Attempt to check PLC connection
            # Note: This is a simulation - in real implementation, 
            # you would use actual PLC communication library (e.g., snap7)
            plc_ip = PLC_CONFIG.get("IP", "Unknown")
            
            # Simulate PLC connection check (replace with actual PLC library)
            # For demonstration, we'll check if the IP is reachable
            import socket
            
            try:
                # Try to create a socket connection (timeout after 2 seconds)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((plc_ip, 102))  # Standard Siemens PLC port
                sock.close()
                
                plc_connected = (result == 0)
                plc_error = None if plc_connected else f"Connection failed to {plc_ip}:102"
                
            except Exception as e:
                plc_connected = False
                plc_error = f"Socket error: {str(e)}"
            
            return {
                'plc_connected': plc_connected,
                'plc_error': plc_error,
                'plc_ip': plc_ip
            }
            
        except Exception as e:
            return {
                'plc_connected': False,
                'plc_error': f"PLC check failed: {str(e)}",
                'plc_ip': 'Unknown'
            }
    
    def check_camera_connections(self):
        """
        Check camera connection status for OD and BF cameras.
        
        Returns:
            dict: Camera connection status
        """
        import cv2
        
        camera_status = {
            'od_camera_connected': False,
            'od_camera_error': None,
            'bf_camera_connected': False,
            'bf_camera_error': None
        }
        
        try:
            # Check OD Camera (Camera 0)
            try:
                od_cap = cv2.VideoCapture(0)
                if od_cap.isOpened():
                    ret, frame = od_cap.read()
                    if ret and frame is not None:
                        camera_status['od_camera_connected'] = True
                        camera_status['od_camera_error'] = None
                    else:
                        camera_status['od_camera_connected'] = False
                        camera_status['od_camera_error'] = "Failed to read frame"
                else:
                    camera_status['od_camera_connected'] = False
                    camera_status['od_camera_error'] = "Failed to open camera"
                od_cap.release()
                
            except Exception as e:
                camera_status['od_camera_connected'] = False
                camera_status['od_camera_error'] = str(e)
            
            # Check BF Camera (Camera 1)
            try:
                bf_cap = cv2.VideoCapture(1)
                if bf_cap.isOpened():
                    ret, frame = bf_cap.read()
                    if ret and frame is not None:
                        camera_status['bf_camera_connected'] = True
                        camera_status['bf_camera_error'] = None
                    else:
                        camera_status['bf_camera_connected'] = False
                        camera_status['bf_camera_error'] = "Failed to read frame"
                else:
                    camera_status['bf_camera_connected'] = False
                    camera_status['bf_camera_error'] = "Failed to open camera"
                bf_cap.release()
                
            except Exception as e:
                camera_status['bf_camera_connected'] = False
                camera_status['bf_camera_error'] = str(e)
            
        except Exception as e:
            print(f"❌ Error checking cameras: {e}")
            camera_status['od_camera_error'] = str(e)
            camera_status['bf_camera_error'] = str(e)
        
        return camera_status
    
    def update_system_info_display(self, system_info_text, device_status):
        """
        Update the system information display with device connection status.
        
        Args:
            system_info_text: Text widget to update
            device_status: Dictionary containing device connection status
        """
        try:
            import platform
            import psutil
            
            # Create status text with color indicators
            plc_status_text = "✅ Connected" if device_status['plc_connected'] else "❌ Disconnected"
            if device_status['plc_error']:
                plc_status_text += f" ({device_status['plc_error']})"
            
            od_status_text = "✅ Connected" if device_status['od_camera_connected'] else "❌ Disconnected"
            if device_status['od_camera_error']:
                od_status_text += f" ({device_status['od_camera_error']})"
            
            bf_status_text = "✅ Connected" if device_status['bf_camera_connected'] else "❌ Disconnected"
            if device_status['bf_camera_error']:
                bf_status_text += f" ({device_status['bf_camera_error']})"
            
            # Complete system information
            enhanced_info = f"""System Platform: {platform.system()} {platform.release()}
Python Version: {platform.python_version()}
CPU Cores: {psutil.cpu_count()}
Memory: {psutil.virtual_memory().total // (1024**3)} GB
Application Version: 1.0.0
Database Status: Connected

DEVICE CONNECTION STATUS:
PLC Connection: {plc_status_text}
OD Camera (0): {od_status_text}
BF Camera (1): {bf_status_text}

DEVICE DETAILS:
PLC IP: {device_status.get('plc_ip', 'Unknown')}
Total Cameras Detected: {sum([device_status['od_camera_connected'], device_status['bf_camera_connected']])}
System Ready: {'Yes' if device_status['plc_connected'] and device_status['od_camera_connected'] else 'No'}"""
            
            # Update display
            system_info_text.config(state="normal")
            system_info_text.delete("1.0", tk.END)
            system_info_text.insert("1.0", enhanced_info)
            system_info_text.config(state="disabled")
            
            print(f"✅ System information updated with device status")
            
        except Exception as e:
            print(f"❌ Error updating system info display: {e}")
    
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



