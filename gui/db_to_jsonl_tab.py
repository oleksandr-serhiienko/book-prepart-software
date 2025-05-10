import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .base_tab import BaseTab
from db_to_jsonl import convert_db_to_jsonl
from jsonl_fixer import fix_sequence_numbers


class DBToJSONLTab(BaseTab):
    def __init__(self, parent, app):
        # Initialize variables
        self.db_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set(os.path.join(os.getcwd(), "output"))
        self.language_var = tk.StringVar()
        self.language_var.set("de")
        self.book_name_var = tk.StringVar()
        self.word_trans_db_path_var = tk.StringVar()
        self.fix_numbers_var = tk.BooleanVar()
        self.fix_numbers_var.set(True)
        self.db_to_jsonl_progress = None
        
        super().__init__(parent, app)
    
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self.frame, text="Convert Database to JSONL", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Database selection
        db_label = ttk.Label(self.frame, text="Database File:")
        db_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        db_entry = ttk.Entry(self.frame, textvariable=self.db_path_var, width=50)
        db_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        db_button = ttk.Button(self.frame, text="Browse...", command=self.browse_db_file)
        db_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Output directory
        output_label = ttk.Label(self.frame, text="Output Directory:")
        output_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        output_entry = ttk.Entry(self.frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        output_button = ttk.Button(self.frame, text="Browse...", command=self.browse_output_dir)
        output_button.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language selection
        lang_label = ttk.Label(self.frame, text="Language:")
        lang_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        lang_combo = ttk.Combobox(self.frame, textvariable=self.language_var, 
                                  values=["de", "en", "fr", "es", "it"])
        lang_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Book name
        book_label = ttk.Label(self.frame, text="Book Name:")
        book_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        book_entry = ttk.Entry(self.frame, textvariable=self.book_name_var, width=50)
        book_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Fix numbers checkbox
        fix_numbers_check = ttk.Checkbutton(self.frame, text="Fix number sequences", 
                                            variable=self.fix_numbers_var)
        fix_numbers_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Run button
        run_button = ttk.Button(self.frame, text="Process DB to JSONL", 
                                command=self.run_db_to_jsonl)
        run_button.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.db_to_jsonl_progress = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, 
                                                   length=300, mode='determinate')
        self.db_to_jsonl_progress.grid(row=7, column=0, columnspan=3, pady=5, sticky=tk.EW)
    
    def browse_db_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            self.db_path_var.set(file_path)
            # Auto-populate book name from filename
            base_name = os.path.basename(file_path)
            book_name = os.path.splitext(base_name)[0]
            self.book_name_var.set(book_name)
    
    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def browse_word_trans_db(self):
        file_path = filedialog.askopenfilename(
            title="Select Target Database File",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            self.word_trans_db_path_var.set(file_path)
            
            # Extract book name from database path if needed
            base_name = os.path.basename(file_path)
            book_name = os.path.splitext(base_name)[0]
            # Store book name in a hidden variable if needed for file naming
            self.word_trans_book_name = book_name
    
    def update_progress(self, value, max_value=100):
        """Update this tab's progress bar"""
        progress = int((value / max_value) * 100)
        self.db_to_jsonl_progress['value'] = progress
        self.frame.update_idletasks()
    
    def run_db_to_jsonl(self):
        """Execute the DB to JSONL conversion chain"""
        try:
            # Get parameters
            db_path = self.db_path_var.get()
            if not db_path:
                messagebox.showerror("Error", "Please select a database file")
                return
                
            language = self.language_var.get()
            book_name = self.book_name_var.get()
            if not book_name:
                book_name = os.path.splitext(os.path.basename(db_path))[0]
                
            output_dir = self.output_dir_var.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # Construct output paths
            interim_output_path = os.path.join(output_dir, f"{book_name}.jsonl")
            final_output_path = os.path.join(output_dir, f"{language}/{book_name}_fixed.jsonl")
            
            # Reset progress bars
            self.db_to_jsonl_progress['value'] = 0
            self.frame.update_idletasks()
            
            # Step 1: Convert DB to JSONL
            self.update_status("Converting database to JSONL...")
            self.log(f"Starting conversion of {db_path} to JSONL...")
            result_path = convert_db_to_jsonl(db_path, interim_output_path, 
                                             progress_callback=self.update_progress)
            
            # Step 2: Fix sequence numbers if requested
            if self.fix_numbers_var.get():
                self.update_status("Fixing number sequences...")
                self.log(f"Fixing number sequences in {result_path}...")
                os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
                fix_sequence_numbers(result_path, final_output_path, 
                                    progress_callback=self.update_progress)
                self.log(f"Successfully created fixed JSONL at {final_output_path}", "success")
            
            self.update_status("Process completed successfully")
            messagebox.showinfo("Success", "DB to JSONL conversion completed successfully!")
            
        except Exception as e:
            self.update_status("Error")
            self.log(f"Error in DB to JSONL process: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")