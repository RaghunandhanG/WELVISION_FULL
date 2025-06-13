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
        """Setup the Manual Mode Control interface with scrolling and full width"""
        # Configure parent to use full width
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Create main canvas and scrollbar for scrolling
        canvas = tk.Canvas(self.parent, bg="#0a2158", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0a2158")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Use grid instead of pack for better width control
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure canvas to expand to full width
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas_width)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # Store canvas reference for focus management
        self.canvas = canvas
        
        # Bind enter/leave events for mouse wheel
        canvas.bind("<Enter>", lambda e: canvas.focus_set())
        canvas.bind("<Leave>", lambda e: self.parent.focus_set())
        
        main_container = tk.Frame(scrollable_frame, bg="#0a2158")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_container, text="System Check & Manual Mode Control", 
                              font=("Arial", 20, "bold"), fg="white", bg="#0a2158")
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = tk.Label(main_container, 
                             text="Monitor system status and control component acceptance patterns for OD and Big Face inspection",
                             font=("Arial", 12), fg="lightgray", bg="#0a2158")
        desc_label.pack(pady=(0, 15))
        
        # Add result widgets from inference page (full width)
        self.setup_result_widgets(main_container)
        
        # Manual mode toggle section (centered)
        mode_section = tk.Frame(main_container, bg="#0a2158")
        mode_section.pack(fill=tk.X, pady=(0, 20))
        
        mode_frame = tk.Frame(mode_section, bg="#0a2158")
        mode_frame.pack()
        
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
        
        # Main sections container (enhanced full width utilization)
        sections_container = tk.Frame(main_container, bg="#0a2158")
        sections_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Configure grid for equal distribution with better space utilization
        sections_container.grid_columnconfigure(0, weight=1)
        sections_container.grid_columnconfigure(1, weight=1)
        sections_container.grid_rowconfigure(0, weight=1)
        
        # OD Section (Left - enhanced full width utilization)
        self.setup_od_section(sections_container)
        
        # Big Face Section (Right - enhanced full width utilization)  
        self.setup_bf_section(sections_container)
        
        # Action buttons (enhanced full width utilization)
        self.setup_action_buttons(main_container)
    
    def setup_result_widgets(self, parent):
        """Setup result widgets from inference page with enhanced full width layout"""
        results_container = tk.Frame(parent, bg="#0a2158")
        results_container.pack(fill=tk.X, pady=(0, 25), padx=20)
        
        # Configure grid for equal distribution across full width with better spacing
        results_container.grid_columnconfigure(0, weight=1)
        results_container.grid_columnconfigure(1, weight=1)
        results_container.grid_columnconfigure(2, weight=1)
        results_container.grid_rowconfigure(0, weight=1)
        
        # Overall Result
        overall_frame = tk.LabelFrame(results_container, text="Overall Result", 
                                    font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        overall_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        # Initialize variables if they don't exist in app
        if not hasattr(self.app, 'overall_inspected_var'):
            self.app.overall_inspected_var = tk.StringVar(value="0")
            self.app.overall_ok_var = tk.StringVar(value="0")
            self.app.overall_not_ok_var = tk.StringVar(value="0")
            self.app.overall_percentage_var = tk.StringVar(value="0%")
        
        self.create_result_stat_label(overall_frame, "Inspected:", self.app.overall_inspected_var, 0)
        self.create_result_stat_label(overall_frame, "Ok rollers:", self.app.overall_ok_var, 1)
        self.create_result_stat_label(overall_frame, "Not OK rollers:", self.app.overall_not_ok_var, 2)
        self.create_result_stat_label(overall_frame, "Percentage:", self.app.overall_percentage_var, 3)
        
        # Big Face Result
        bf_frame = tk.LabelFrame(results_container, text="Big Face Result", 
                               font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        bf_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Initialize BF variables if they don't exist
        if not hasattr(self.app, 'bf_inspected_var'):
            self.app.bf_inspected_var = tk.StringVar(value="0")
            self.app.bf_good_var = tk.StringVar(value="0")
            self.app.bf_defective_var = tk.StringVar(value="0")
            self.app.bf_proportion_var = tk.StringVar(value="0%")
        
        self.create_result_stat_label(bf_frame, "Inspected:", self.app.bf_inspected_var, 0)
        self.create_result_stat_label(bf_frame, "Good rollers:", self.app.bf_good_var, 1)
        self.create_result_stat_label(bf_frame, "Defective rollers:", self.app.bf_defective_var, 2)
        self.create_result_stat_label(bf_frame, "Percentage:", self.app.bf_proportion_var, 3)
        
        # OD Result
        od_frame = tk.LabelFrame(results_container, text="OD Result", 
                               font=("Arial", 14, "bold"), fg="white", bg="#0a2158", bd=2)
        od_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=5)
        
        # Initialize OD variables if they don't exist
        if not hasattr(self.app, 'od_inspected_var'):
            self.app.od_inspected_var = tk.StringVar(value="0")
            self.app.od_good_var = tk.StringVar(value="0")
            self.app.od_defective_var = tk.StringVar(value="0")
            self.app.od_proportion_var = tk.StringVar(value="0%")
        
        self.create_result_stat_label(od_frame, "Inspected:", self.app.od_inspected_var, 0)
        self.create_result_stat_label(od_frame, "Good rollers:", self.app.od_good_var, 1)
        self.create_result_stat_label(od_frame, "Defective rollers:", self.app.od_defective_var, 2)
        self.create_result_stat_label(od_frame, "Percentage:", self.app.od_proportion_var, 3)
    
    def create_result_stat_label(self, parent, text, var, row):
        """Create a compact stat label for results"""
        label = tk.Label(parent, text=text, font=("Arial", 10), fg="white", bg="#0a2158", anchor="w")
        label.grid(row=row, column=0, sticky="w", padx=8, pady=2)
        value_label = tk.Label(parent, textvariable=var, font=("Arial", 10, "bold"), fg="white", bg="#0a2158")
        value_label.grid(row=row, column=1, sticky="e", padx=8, pady=2)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
    
    def setup_od_section(self, parent):
        """Setup OD control section"""
        od_frame = tk.LabelFrame(parent, text="OD Control", 
                                font=("Arial", 16, "bold"), fg="white", bg="#0a2158", 
                                bd=3, relief="solid")
        od_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)
        
        # Mode selection checkboxes for OD
        modes_frame = tk.Frame(od_frame, bg="#0a2158")
        modes_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=15)
        
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
        self.od_status_frame.pack(fill=tk.X, pady=15, padx=15, ipady=10)
        
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
                                font=("Arial", 16, "bold"), fg="white", bg="#0a2158", 
                                bd=3, relief="solid")
        bf_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=10)
        
        # Mode selection checkboxes for Big Face
        modes_frame = tk.Frame(bf_frame, bg="#0a2158")
        modes_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=15)
        
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
        self.bf_status_frame.pack(fill=tk.X, pady=15, padx=15, ipady=10)
        
        self.bf_status_label = tk.Label(self.bf_status_frame, text="Big Face Status: INACTIVE", 
                                       font=("Arial", 14, "bold"), fg="white", bg="#17a2b8")
        self.bf_status_label.pack(pady=5)
        
        self.bf_counter_label = tk.Label(self.bf_status_frame, text="Components Processed: 0", 
                                        font=("Arial", 12), fg="white", bg="#17a2b8")
        self.bf_counter_label.pack(pady=2)
        
        # Disable initially
        self.set_bf_controls_state('disabled')
    
    def setup_action_buttons(self, parent):
        """Setup action buttons with enhanced full width layout and better space utilization"""
        button_container = tk.Frame(parent, bg="#0a2158")
        button_container.pack(fill=tk.X, pady=20, padx=20)
        
        button_frame = tk.Frame(button_container, bg="#0a2158")
        button_frame.pack(expand=True)
        
        reset_button = tk.Button(button_frame, text="Reset Counters", 
                                font=("Arial", 12, "bold"), bg="#6c757d", fg="white",
                                width=18, height=2, command=self.reset_counters)
        reset_button.pack(side=tk.LEFT, padx=15)
        
        apply_pattern_button = tk.Button(button_frame, text="Apply Pattern", 
                                         font=("Arial", 12, "bold"), bg="#007bff", fg="white",
                                         width=18, height=2, command=self.apply_pattern)
        apply_pattern_button.pack(side=tk.LEFT, padx=15)
        
        self.emergency_stop_button = tk.Button(button_frame, text="EMERGENCY STOP", 
                                              font=("Arial", 12, "bold"), bg="#dc3545", fg="white",
                                              width=18, height=2, command=self.emergency_stop)
        self.emergency_stop_button.pack(side=tk.LEFT, padx=15)
    
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
        
        # Update mode indicator in inference tab
        self.update_inference_mode_indicator()
    
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
    
    def update_inference_mode_indicator(self):
        """Update the mode indicator in the inference tab"""
        try:
            # Check if inference tab exists and has the update method
            if hasattr(self.app, 'inference_tab') and hasattr(self.app.inference_tab, 'update_mode_indicator'):
                self.app.inference_tab.update_mode_indicator(self.manual_mode_active)
        except Exception as e:
            print(f"❌ Error updating inference mode indicator: {e}") 