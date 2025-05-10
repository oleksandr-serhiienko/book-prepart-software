import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .base_tab import BaseTab


class WordTranslationsTab(BaseTab):
    def __init__(self, parent, app):
        # Initialize variables
        self.word_jsonl_path_var = tk.StringVar()
        self.word_trans_language_var = tk.StringVar()
        self.word_trans_language_var.set("de")
        self.word_trans_db_path_var = tk.StringVar()
        self.word_trans_output_dir_var = tk.StringVar()
        self.word_trans_output_dir_var.set(os.path.join(os.getcwd(), "output"))
        self.word_trans_model_id_var = tk.StringVar()
        self.word_trans_model_id_var.set("ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BJJAaWzW")
        
        # Output file variables
        self.word_sql_file_var = tk.StringVar()
        self.word_error_batch_var = tk.StringVar()
        
        # Result counters
        self.word_success_count_var = tk.StringVar()
        self.word_success_count_var.set("0")
        self.word_failed_count_var = tk.StringVar()
        self.word_failed_count_var.set("0")
        
        self.word_trans_progress = None
        
        super().__init__(parent, app)
    
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self.frame, text="Process Word Translations", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # JSONL results selection
        jsonl_label = ttk.Label(self.frame, text="Word JSONL Results File:")
        jsonl_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        jsonl_entry = ttk.Entry(self.frame, textvariable=self.word_jsonl_path_var, width=50)
        jsonl_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        jsonl_button = ttk.Button(self.frame, text="Browse...", command=self.browse_word_jsonl_file)
        jsonl_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language selection
        lang_label = ttk.Label(self.frame, text="Language:")
        lang_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        lang_combo = ttk.Combobox(self.frame, textvariable=self.word_trans_language_var, 
                                  values=["de", "en", "fr", "es", "it"])
        lang_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Target database file
        db_label = ttk.Label(self.frame, text="Target Database File:")
        db_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        db_entry = ttk.Entry(self.frame, textvariable=self.word_trans_db_path_var, width=50)
        db_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        db_button = ttk.Button(self.frame, text="Browse...", command=self.browse_word_trans_db)
        db_button.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Output directory
        output_label = ttk.Label(self.frame, text="Output Directory:")
        output_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        output_entry = ttk.Entry(self.frame, textvariable=self.word_trans_output_dir_var, width=50)
        output_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        output_button = ttk.Button(self.frame, text="Browse...", 
                                   command=self.browse_word_trans_output_dir)
        output_button.grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Model ID field
        model_label = ttk.Label(self.frame, text="Model ID (for error batch):")
        model_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        model_entry = ttk.Entry(self.frame, textvariable=self.word_trans_model_id_var, width=50)
        model_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Output files frame
        output_files_frame = ttk.LabelFrame(self.frame, text="Output Files")
        output_files_frame.grid(row=6, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # SQL file output
        sql_file_label = ttk.Label(output_files_frame, text="SQL File:")
        sql_file_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        sql_file_path = ttk.Entry(output_files_frame, textvariable=self.word_sql_file_var, 
                                  width=60, state='readonly')
        sql_file_path.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Error batch file output
        error_batch_label = ttk.Label(output_files_frame, text="Error Batch File:")
        error_batch_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        error_batch_path = ttk.Entry(output_files_frame, textvariable=self.word_error_batch_var, 
                                     width=60, state='readonly')
        error_batch_path.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Results")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # Successful translations count
        success_count_label = ttk.Label(results_frame, text="Successful Translations:")
        success_count_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        success_count_value = ttk.Label(results_frame, textvariable=self.word_success_count_var)
        success_count_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Failed translations count
        failed_count_label = ttk.Label(results_frame, text="Failed Translations:")
        failed_count_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        failed_count_value = ttk.Label(results_frame, textvariable=self.word_failed_count_var)
        failed_count_value.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(self.frame, text="Process Word Translations", 
                                command=self.run_word_translations)
        run_button.grid(row=8, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.word_trans_progress = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, 
                                                   length=300, mode='determinate')
        self.word_trans_progress.grid(row=9, column=0, columnspan=3, pady=5, sticky=tk.EW)

    def browse_word_jsonl_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Word JSONL Results File",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")]
        )
        if file_path:
            self.word_jsonl_path_var.set(file_path)
            self.log(f"Selected Word JSONL Results file: {file_path}", "info")

    def browse_word_trans_db(self):
        file_path = filedialog.askopenfilename(
            title="Select Target Database File",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            self.word_trans_db_path_var.set(file_path)

    def browse_word_trans_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.word_trans_output_dir_var.set(dir_path)
    
    def update_progress(self, value, max_value=100):
        """Update this tab's progress bar"""
        progress = int((value / max_value) * 100)
        self.word_trans_progress['value'] = progress
        self.frame.update_idletasks()

    def run_word_translations(self):
        """Execute the Word Translations processing"""
        try:
            # Get parameters
            jsonl_path = self.word_jsonl_path_var.get()
            if not jsonl_path:
                messagebox.showerror("Error", "Please select a Word JSONL results file")
                return
                
            language = self.word_trans_language_var.get()
            db_path = self.word_trans_db_path_var.get()
            if not db_path:
                messagebox.showerror("Error", "Please select a target database file")
                return
                
            # Extract book name from database path for file naming
            book_name = os.path.splitext(os.path.basename(db_path))[0]
                
            output_dir = self.word_trans_output_dir_var.get()
            model_id = self.word_trans_model_id_var.get()
            
            # Reset progress bar and fields
            self.word_trans_progress['value'] = 0
            self.word_sql_file_var.set("")
            self.word_error_batch_var.set("")
            self.word_success_count_var.set("0")
            self.word_failed_count_var.set("0")
            self.frame.update_idletasks()
            
            # Process JSONL file
            self.update_status("Processing Word Translations...")
            self.log(f"Starting conversion of {jsonl_path} to SQL format...")
            self.log(f"Using database for ID reference: {db_path}")
            
            # Import the word translation processor module
            from word_translation_processor import process_word_translations
            
            sql_path, error_path, success_count, failed_count = process_word_translations(
                input_file=jsonl_path,
                output_dir=output_dir,
                book_name=book_name,
                language=language,
                model_id=model_id,
                progress_callback=self.update_progress,
                db_path=db_path  # Pass the explicit database path
            )
            
            # Update UI with results
            self.word_sql_file_var.set(sql_path)
            self.word_error_batch_var.set(error_path)
            self.word_success_count_var.set(str(success_count))
            self.word_failed_count_var.set(str(failed_count))
            
            self.update_status("Word translations processing completed successfully")
            self.log(f"Successfully created SQL file with {success_count} translations at {sql_path}", 
                    "success")
            self.log(f"Failed translations ({failed_count}) saved to error batch at {error_path}", 
                    "info")
            
            messagebox.showinfo("Success", f"Word translations processing completed successfully!\n\n"
                                         f"Successful Translations: {success_count}\n"
                                         f"Failed Translations: {failed_count}")
            
        except Exception as e:
            self.update_status("Error")
            self.log(f"Error in Word Translations process: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")