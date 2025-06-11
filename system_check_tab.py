import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
from datetime import datetime

class SystemCheckTab:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        
        # Manual mode states for OD and Big Face
        self.od_mode = {
            'all_accept': tk.BooleanVar(value=False),
            'all_reject': tk.BooleanVar(value=False),
            'alternate': tk.BooleanVar(value=False)
        }
        
        self.bf_mode = {
            'all_accept': tk.BooleanVar(value=False),
            'all_reject': tk.BooleanVar(value=False),
            'alternate': tk.BooleanVar(value=False)
        }
        
        # Counter for alternate mode
        self.od_alternate_counter = 0
        self.bf_alternate_counter = 0
        
        # Manual mode status
        self.manual_mode_active = False
        
        self.setup_tab()
    
    def setup_tab(self):
        """Setup the Manual Mode Control interface"""
        main_container = tk.Frame(self.parent, bg="#0a2158")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_container, text="Manual Mode Control", 
                              font=("Arial", 24, "bold"), fg="white", bg="#0a2158")
        title_label.pack(pady=(0, 30))
        
        # Description
        desc_label = tk.Label(main_container, 
                             text="Control component acceptance patterns for OD and Big Face inspection",
                             font=("Arial", 14), fg="lightgray", bg="#0a2158")
        desc_label.pack(pady=(0, 20))
        
        # Manual mode toggle (simplified)
        mode_frame = tk.Frame(main_container, bg="#0a2158")
        mode_frame.pack(pady=(0, 20))
        
        self.manual_mode_var = tk.BooleanVar(value=False)
        self.manual_mode_checkbox = tk.Checkbutton(mode_frame, text="Enable Manual Mode", 
                                                  variable=self.manual_mode_var,
                                                  font=("Arial", 14, "bold"), fg="white", bg="#0a2158",
                                                  selectcolor="#0a2158", activebackground="#0a2158",
                                                  activeforeground="white", command=self.toggle_manual_mode)
        self.manual_mode_checkbox.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(mode_frame, text="AUTOMATIC MODE", 
                                    font=("Arial", 14, "bold"), fg="red", bg="#0a2158")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Main sections container
        sections_container = tk.Frame(main_container, bg="#0a2158")
        sections_container.pack(fill=tk.BOTH, expand=True)
        
        # OD Section (Left)
        self.setup_od_section(sections_container)
        
        # Big Face Section (Right)  
        self.setup_bf_section(sections_container)
        
        # Action buttons
        self.setup_action_buttons(main_container)
    
    def setup_od_section(self, parent):
        """Setup OD control section"""
        od_frame = tk.LabelFrame(parent, text="OD Control", 
                                font=("Arial", 18, "bold"), fg="white", bg="#0a2158", 
                                bd=3, relief="solid")
        od_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        # Mode selection checkboxes for OD
        modes_frame = tk.Frame(od_frame, bg="#0a2158")
        modes_frame.pack(pady=20, padx=20)
        
        # ALL ACCEPT
        accept_frame = tk.Frame(modes_frame, bg="#28a745", bd=1, relief="solid")
        accept_frame.pack(fill=tk.X, pady=2, ipady=4)
        
        self.od_accept_cb = tk.Checkbutton(accept_frame, text="ALL ACCEPT", 
                                          variable=self.od_mode['all_accept'],
                                          font=("Arial", 9, "bold"), fg="white", bg="#28a745",
                                          selectcolor="#28a745", activebackground="#28a745",
                                          activeforeground="white", 
                                          command=lambda: self.on_od_mode_change('all_accept'))
        self.od_accept_cb.pack(pady=2)
        
        # ALL REJECT
        reject_frame = tk.Frame(modes_frame, bg="#dc3545", bd=1, relief="solid")
        reject_frame.pack(fill=tk.X, pady=2, ipady=4)
        
        self.od_reject_cb = tk.Checkbutton(reject_frame, text="ALL REJECT", 
                                          variable=self.od_mode['all_reject'],
                                          font=("Arial", 9, "bold"), fg="white", bg="#dc3545",
                                          selectcolor="#dc3545", activebackground="#dc3545",
                                          activeforeground="white",
                                          command=lambda: self.on_od_mode_change('all_reject'))
        self.od_reject_cb.pack(pady=2)
        
        # ALTERNATE
        alternate_frame = tk.Frame(modes_frame, bg="#ffc107", bd=1, relief="solid")
        alternate_frame.pack(fill=tk.X, pady=2, ipady=4)
        
        self.od_alternate_cb = tk.Checkbutton(alternate_frame, text="ALTERNATE\nACCEPT & REJECT", 
                                             variable=self.od_mode['alternate'],
                                             font=("Arial", 9, "bold"), fg="black", bg="#ffc107",
                                             selectcolor="#ffc107", activebackground="#ffc107",
                                             activeforeground="black",
                                             command=lambda: self.on_od_mode_change('alternate'))
        self.od_alternate_cb.pack(pady=2)
        
        # Status display
        self.od_status_frame = tk.Frame(od_frame, bg="#17a2b8", bd=2, relief="solid")
        self.od_status_frame.pack(fill=tk.X, pady=20, padx=20, ipady=10)
        
        self.od_status_label = tk.Label(self.od_status_frame, text="OD Status: INACTIVE", 
                                       font=("Arial", 14, "bold"), fg="white", bg="#17a2b8")
        self.od_status_label.pack(pady=5)
        
        self.od_counter_label = tk.Label(self.od_status_frame, text="Components Processed: 0", 
                                        font=("Arial", 12), fg="white", bg="#17a2b8")
        self.od_counter_label.pack(pady=2)
        
        # Disable initially
        self.set_od_controls_state('disabled')
    
    def setup_bf_section(self, parent):
        """Setup Big Face control section"""
        bf_frame = tk.LabelFrame(parent, text="Big Face Control", 
                                font=("Arial", 18, "bold"), fg="white", bg="#0a2158", 
                                bd=3, relief="solid")
        bf_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        
        # Mode selection checkboxes for Big Face
        modes_frame = tk.Frame(bf_frame, bg="#0a2158")
        modes_frame.pack(pady=20, padx=20)
        
        # ALL ACCEPT
        accept_frame = tk.Frame(modes_frame, bg="#28a745", bd=1, relief="solid")
        accept_frame.pack(fill=tk.X, pady=2, ipady=4)
        
        self.bf_accept_cb = tk.Checkbutton(accept_frame, text="ALL ACCEPT", 
                                          variable=self.bf_mode['all_accept'],
                                          font=("Arial", 9, "bold"), fg="white", bg="#28a745",
                                          selectcolor="#28a745", activebackground="#28a745",
                                          activeforeground="white",
                                          command=lambda: self.on_bf_mode_change('all_accept'))
        self.bf_accept_cb.pack(pady=2)
        
        # ALL REJECT
        reject_frame = tk.Frame(modes_frame, bg="#dc3545", bd=1, relief="solid")
        reject_frame.pack(fill=tk.X, pady=2, ipady=4)
        
        self.bf_reject_cb = tk.Checkbutton(reject_frame, text="ALL REJECT", 
                                          variable=self.bf_mode['all_reject'],
                                          font=("Arial", 9, "bold"), fg="white", bg="#dc3545",
                                          selectcolor="#dc3545", activebackground="#dc3545",
                                          activeforeground="white",
                                          command=lambda: self.on_bf_mode_change('all_reject'))
        self.bf_reject_cb.pack(pady=2)
        
        # ALTERNATE
        alternate_frame = tk.Frame(modes_frame, bg="#ffc107", bd=1, relief="solid")
        alternate_frame.pack(fill=tk.X, pady=2, ipady=4)
        
        self.bf_alternate_cb = tk.Checkbutton(alternate_frame, text="ALTERNATE\nACCEPT & REJECT", 
                                             variable=self.bf_mode['alternate'],
                                             font=("Arial", 9, "bold"), fg="black", bg="#ffc107",
                                             selectcolor="#ffc107", activebackground="#ffc107",
                                             activeforeground="black",
                                             command=lambda: self.on_bf_mode_change('alternate'))
        self.bf_alternate_cb.pack(pady=2)
        
        # Status display
        self.bf_status_frame = tk.Frame(bf_frame, bg="#17a2b8", bd=2, relief="solid")
        self.bf_status_frame.pack(fill=tk.X, pady=20, padx=20, ipady=10)
        
        self.bf_status_label = tk.Label(self.bf_status_frame, text="Big Face Status: INACTIVE", 
                                       font=("Arial", 14, "bold"), fg="white", bg="#17a2b8")
        self.bf_status_label.pack(pady=5)
        
        self.bf_counter_label = tk.Label(self.bf_status_frame, text="Components Processed: 0", 
                                        font=("Arial", 12), fg="white", bg="#17a2b8")
        self.bf_counter_label.pack(pady=2)
        
        # Disable initially
        self.set_bf_controls_state('disabled')
    
    def setup_action_buttons(self, parent):
        """Setup action buttons"""
        button_frame = tk.Frame(parent, bg="#0a2158")
        button_frame.pack(fill=tk.X, pady=10)
        
        reset_button = tk.Button(button_frame, text="Reset Counters", 
                                font=("Arial", 10, "bold"), bg="#6c757d", fg="white",
                                width=12, height=1, command=self.reset_counters)
        reset_button.pack(side=tk.LEFT, padx=5)
        
        apply_pattern_button = tk.Button(button_frame, text="Apply Pattern", 
                                         font=("Arial", 10, "bold"), bg="#007bff", fg="white",
                                         width=20, height=1, command=self.apply_pattern)
        apply_pattern_button.pack(side=tk.LEFT, padx=5)
        
        self.emergency_stop_button = tk.Button(button_frame, text="EMERGENCY STOP", 
                                              font=("Arial", 10, "bold"), bg="#dc3545", fg="white",
                                              width=15, height=1, command=self.emergency_stop)
        self.emergency_stop_button.pack(side=tk.RIGHT, padx=5)
    
    def toggle_manual_mode(self):
        """Toggle manual mode on/off"""
        self.manual_mode_active = self.manual_mode_var.get()
        
        if self.manual_mode_active:
            self.status_label.config(text="MANUAL MODE ACTIVE", fg="green")
            self.set_od_controls_state('normal')
            self.set_bf_controls_state('normal')
            messagebox.showinfo("Manual Mode", "Manual mode activated. Machine will follow selected patterns.")
        else:
            self.status_label.config(text="AUTOMATIC MODE", fg="red")
            self.set_od_controls_state('disabled')
            self.set_bf_controls_state('disabled')
            self.clear_all_modes()
            messagebox.showinfo("Automatic Mode", "Returned to automatic mode.")
    
    def on_od_mode_change(self, selected_mode):
        """Handle OD mode selection (only one can be active)"""
        if not self.manual_mode_active:
            return
        
        # Clear other modes
        for mode in self.od_mode:
            if mode != selected_mode:
                self.od_mode[mode].set(False)
        
        # Update status
        if self.od_mode[selected_mode].get():
            if selected_mode == 'all_accept':
                self.od_status_label.config(text="OD Status: ALL ACCEPT", fg="white", bg="#28a745")
                self.od_status_frame.config(bg="#28a745")
            elif selected_mode == 'all_reject':
                self.od_status_label.config(text="OD Status: ALL REJECT", fg="white", bg="#dc3545")
                self.od_status_frame.config(bg="#dc3545")
            elif selected_mode == 'alternate':
                self.od_status_label.config(text="OD Status: ALTERNATING", fg="black", bg="#ffc107")
                self.od_status_frame.config(bg="#ffc107")
        else:
            self.od_status_label.config(text="OD Status: INACTIVE", fg="white", bg="#17a2b8")
            self.od_status_frame.config(bg="#17a2b8")
    
    def on_bf_mode_change(self, selected_mode):
        """Handle Big Face mode selection (only one can be active)"""
        if not self.manual_mode_active:
            return
        
        # Clear other modes
        for mode in self.bf_mode:
            if mode != selected_mode:
                self.bf_mode[mode].set(False)
        
        # Update status
        if self.bf_mode[selected_mode].get():
            if selected_mode == 'all_accept':
                self.bf_status_label.config(text="Big Face Status: ALL ACCEPT", fg="white", bg="#28a745")
                self.bf_status_frame.config(bg="#28a745")
            elif selected_mode == 'all_reject':
                self.bf_status_label.config(text="Big Face Status: ALL REJECT", fg="white", bg="#dc3545")
                self.bf_status_frame.config(bg="#dc3545")
            elif selected_mode == 'alternate':
                self.bf_status_label.config(text="Big Face Status: ALTERNATING", fg="black", bg="#ffc107")
                self.bf_status_frame.config(bg="#ffc107")
        else:
            self.bf_status_label.config(text="Big Face Status: INACTIVE", fg="white", bg="#17a2b8")
            self.bf_status_frame.config(bg="#17a2b8")
    
    def set_od_controls_state(self, state):
        """Enable/disable OD controls"""
        self.od_accept_cb.config(state=state)
        self.od_reject_cb.config(state=state)
        self.od_alternate_cb.config(state=state)
    
    def set_bf_controls_state(self, state):
        """Enable/disable Big Face controls"""
        self.bf_accept_cb.config(state=state)
        self.bf_reject_cb.config(state=state)
        self.bf_alternate_cb.config(state=state)
    
    def clear_all_modes(self):
        """Clear all mode selections"""
        for mode in self.od_mode.values():
            mode.set(False)
        for mode in self.bf_mode.values():
            mode.set(False)
        
        self.od_status_label.config(text="OD Status: INACTIVE", fg="white", bg="#17a2b8")
        self.od_status_frame.config(bg="#17a2b8")
        self.bf_status_label.config(text="Big Face Status: INACTIVE", fg="white", bg="#17a2b8")
        self.bf_status_frame.config(bg="#17a2b8")
    
    def get_component_decision(self, component_type):
        """Get accept/reject decision for a component based on selected mode"""
        if not self.manual_mode_active:
            return None  # Automatic mode
        
        if component_type.lower() == 'od':
            if self.od_mode['all_accept'].get():
                return 'ACCEPT'
            elif self.od_mode['all_reject'].get():
                return 'REJECT'
            elif self.od_mode['alternate'].get():
                decision = 'ACCEPT' if self.od_alternate_counter % 2 == 0 else 'REJECT'
                self.od_alternate_counter += 1
                self.update_od_counter()
                return decision
        
        elif component_type.lower() == 'bf' or component_type.lower() == 'bigface':
            if self.bf_mode['all_accept'].get():
                return 'ACCEPT'
            elif self.bf_mode['all_reject'].get():
                return 'REJECT'
            elif self.bf_mode['alternate'].get():
                decision = 'ACCEPT' if self.bf_alternate_counter % 2 == 0 else 'REJECT'
                self.bf_alternate_counter += 1
                self.update_bf_counter()
                return decision
        
        return None  # No mode selected
    
    def update_od_counter(self):
        """Update OD component counter"""
        self.od_counter_label.config(text=f"Components Processed: {self.od_alternate_counter}")
    
    def update_bf_counter(self):
        """Update Big Face component counter"""
        self.bf_counter_label.config(text=f"Components Processed: {self.bf_alternate_counter}")
    
    def reset_counters(self):
        """Reset all counters"""
        self.od_alternate_counter = 0
        self.bf_alternate_counter = 0
        self.update_od_counter()
        self.update_bf_counter()
        messagebox.showinfo("Reset", "All counters have been reset.")
    
    def apply_pattern(self):
        """Apply the selected pattern to process components"""
        if not self.manual_mode_active:
            messagebox.showwarning("Manual Mode Required", "Please enable manual mode first.")
            return
        
        # Apply pattern for OD component
        od_decision = self.get_component_decision('od')
        bf_decision = self.get_component_decision('bf')
        
        message = f"Pattern Applied Successfully:\n"
        message += f"OD Decision: {od_decision if od_decision else 'No mode selected'}\n"
        message += f"Big Face Decision: {bf_decision if bf_decision else 'No mode selected'}"
        
        messagebox.showinfo("Pattern Applied", message)
    
    def emergency_stop(self):
        """Emergency stop function"""
        self.manual_mode_var.set(False)
        self.toggle_manual_mode()
        self.clear_all_modes()
        messagebox.showwarning("EMERGENCY STOP", "Manual mode deactivated. All patterns cleared.") 