import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .base_tab import BaseTab


class JSONLToDBTab(BaseTab):
    def __init__(self, parent, app):
        # Initialize variables
        self.jsonl_path_var = tk.StringVar()
        self.jsonl_sent_path_var = tk.StringVar()
        self.db_name_var = tk.StringVar()
        self.db_output_dir_var = tk.StringVar()
        self.db_output_dir_var.set(os.path.join(os.getcwd(), "output"))
        self.jsonl_model_id_var = tk.StringVar()
        self.jsonl_model_id_var.set("ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BHa7AxGJ")
        
        # Output file variables
        self.sql_file_var = tk.StringVar()
        self.error_file_var = tk.StringVar()
        self.error_batch_var = tk.StringVar()
        
        # Result counters
        self.sql_count_var = tk.StringVar()
        self.sql_count_var.set("0")
        self.error_count_var = tk.StringVar()
        self.error_count_var.set("0")
        
        self.jsonl_to_db_progress = None
        
        super().__init__(parent, app)
    
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self.frame, text="Convert JSONL Results to Database", 
                               style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # JSONL results selection
        jsonl_label = ttk.Label(self.frame, text="JSONL Results File:")
        jsonl_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        jsonl_entry = ttk.Entry(self.frame, textvariable=self.jsonl_path_var, width=50)
        jsonl_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        jsonl_button = ttk.Button(self.frame, text="Browse...", command=self.browse_jsonl_file)
        jsonl_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # JSONL sent file selection
        sent_label = ttk.Label(self.frame, text="JSONL Sent File:")
        sent_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        sent_entry = ttk.Entry(self.frame, textvariable=self.jsonl_sent_path_var, width=50)
        sent_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        sent_button = ttk.Button(self.frame, text="Browse...", command=self.browse_jsonl_sent_file)
        sent_button.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Database name
        db_label = ttk.Label(self.frame, text="Database Name:")
        db_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        db_name_entry = ttk.Entry(self.frame, textvariable=self.db_name_var, width=50)
        db_name_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Output directory
        jsonl_output_label = ttk.Label(self.frame, text="Output Directory:")
        jsonl_output_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        jsonl_output_entry = ttk.Entry(self.frame, textvariable=self.db_output_dir_var, width=50)
        jsonl_output_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        jsonl_output_button = ttk.Button(self.frame, text="Browse...", 
                                        command=self.browse_jsonl_output_dir)
        jsonl_output_button.grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Model ID field
        model_label = ttk.Label(self.frame, text="Model ID (for error batch):")
        model_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        model_entry = ttk.Entry(self.frame, textvariable=self.jsonl_model_id_var, width=50)
        model_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Output files frame
        output_files_frame = ttk.LabelFrame(self.frame, text="Output Files")
        output_files_frame.grid(row=6, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # SQL file output
        sql_file_label = ttk.Label(output_files_frame, text="SQL Insert File:")
        sql_file_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        sql_file_path = ttk.Entry(output_files_frame, textvariable=self.sql_file_var, 
                                 width=60, state='readonly')
        sql_file_path.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Error file output
        error_file_label = ttk.Label(output_files_frame, text="Error File:")
        error_file_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        error_file_path = ttk.Entry(output_files_frame, textvariable=self.error_file_var, 
                                   width=60, state='readonly')
        error_file_path.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Error batch file output
        error_batch_label = ttk.Label(output_files_frame, text="Error Batch File:")
        error_batch_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        error_batch_path = ttk.Entry(output_files_frame, textvariable=self.error_batch_var, 
                                    width=60, state='readonly')
        error_batch_path.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Results")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # SQL statements count
        sql_count_label = ttk.Label(results_frame, text="SQL Statements:")
        sql_count_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        sql_count_value = ttk.Label(results_frame, textvariable=self.sql_count_var)
        sql_count_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Error count
        error_count_label = ttk.Label(results_frame, text="Error Entries:")
        error_count_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        error_count_value = ttk.Label(results_frame, textvariable=self.error_count_var)
        error_count_value.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(self.frame, text="Process JSONL to DB", 
                               command=self.run_jsonl_to_db)
        run_button.grid(row=8, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.jsonl_to_db_progress = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, 
                                                   length=300, mode='determinate')
        self.jsonl_to_db_progress.grid(row=9, column=0, columnspan=3, pady=5, sticky=tk.EW)
    
    def browse_jsonl_file(self):
        file_path = filedialog.askopenfilename(
            title="Select JSONL Results File",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")]
        )
        if file_path:
            self.jsonl_path_var.set(file_path)
            self.frame.update_idletasks()
            
            # Try to extract database name from filename
            base_name = os.path.basename(file_path)
            if "_output.jsonl" in base_name:
                db_name = base_name.replace("_output.jsonl", "")
            else:
                db_name = os.path.splitext(base_name)[0]
            self.db_name_var.set(db_name)
            
            # Log the file selection to confirm it's working
            self.log(f"Selected JSONL Results file: {file_path}", "info")
            
            # Try to guess the sent file if it exists in the same directory
            base_dir = os.path.dirname(file_path)
            if "_output.jsonl" in base_name:
                potential_sent_file = os.path.join(base_dir, 
                                                  base_name.replace("_output.jsonl", "_sent.jsonl"))
                if os.path.exists(potential_sent_file):
                    self.jsonl_sent_path_var.set(potential_sent_file)
                    self.log(f"Auto-detected JSONL Sent file: {potential_sent_file}", "info")
    
    def browse_jsonl_sent_file(self):
        file_path = filedialog.askopenfilename(
            title="Select JSONL Sent File",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")]
        )
        if file_path:
            self.jsonl_sent_path_var.set(file_path)
    
    def browse_jsonl_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.db_output_dir_var.set(dir_path)
    
    def update_progress(self, value, max_value=100):
        """Update this tab's progress bar"""
        progress = int((value / max_value) * 100)
        self.jsonl_to_db_progress['value'] = progress
        self.frame.update_idletasks()
    
    def run_jsonl_to_db(self):
        """Execute the JSONL to DB conversion"""
        try:
            # Get parameters
            jsonl_path = self.jsonl_path_var.get()
            if not jsonl_path:
                messagebox.showerror("Error", "Please select a JSONL results file")
                return
                
            # Get sent file path - use the manually selected path
            jsonl_sent_path = self.jsonl_sent_path_var.get()
            if not jsonl_sent_path:
                messagebox.showwarning("Warning", 
                                      "No JSONL sent file selected. This may cause errors if the file is required.")
                
            db_name = self.db_name_var.get()
            if not db_name:
                db_name = os.path.splitext(os.path.basename(jsonl_path))[0]
                
            output_dir = self.db_output_dir_var.get()
            model_id = self.jsonl_model_id_var.get()
            
            # Reset progress bar and fields
            self.jsonl_to_db_progress['value'] = 0
            self.sql_file_var.set("")
            self.error_file_var.set("")
            self.error_batch_var.set("")
            self.sql_count_var.set("0")
            self.error_count_var.set("0")
            self.frame.update_idletasks()
            
            # Process JSONL file
            self.update_status("Processing JSONL results...")
            self.log(f"Starting conversion of {jsonl_path} to database format...")
            
            # Import jsonl_to_db here to avoid circular imports
            from jsonl_to_db import jsonl_to_db
            
            sql_path, error_path, batch_path, sql_count, error_count = jsonl_to_db(
                jsonl_path, 
                db_name,
                output_dir,
                model_id,
                progress_callback=self.update_progress,
                requests_file_path=jsonl_sent_path  # Pass the manually selected sent file path
            )
            
            # Update UI with results
            self.sql_file_var.set(sql_path)
            self.error_file_var.set(error_path)
            self.error_batch_var.set(batch_path)
            self.sql_count_var.set(str(sql_count))
            self.error_count_var.set(str(error_count))
            
            self.update_status("Process completed successfully")
            self.log(f"Successfully created SQL inserts ({sql_count}) at {sql_path}", "success")
            self.log(f"Validation errors ({error_count}) saved to {error_path}", "info")
            self.log(f"Error batch file created at {batch_path}", "info")
            
            messagebox.showinfo("Success", f"JSONL to DB conversion completed successfully!\n\n"
                                          f"SQL Statements: {sql_count}\n"
                                          f"Error Entries: {error_count}")
            
        except Exception as e:
            self.update_status("Error")
            self.log(f"Error in JSONL to DB process: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")