import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .base_tab import BaseTab


class WordProcessingTab(BaseTab):
    def __init__(self, parent, app):
        # Initialize variables
        self.word_input_var = tk.StringVar()
        self.word_db_var = tk.StringVar()
        self.word_language_var = tk.StringVar()
        self.word_language_var.set("de")
        self.word_book_name_var = tk.StringVar()
        self.word_output_dir_var = tk.StringVar()
        self.word_output_dir_var.set(os.path.join(os.getcwd(), "output"))
        self.word_model_id_var = tk.StringVar()
        self.word_model_id_var.set("ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BJJAaWzW")
        
        # Results variables
        self.total_words_var = tk.StringVar()
        self.total_words_var.set("0")
        self.new_words_var = tk.StringVar()
        self.new_words_var.set("0")
        self.word_output_file_var = tk.StringVar()
        
        self.word_processing_progress = None
        
        super().__init__(parent, app)
    
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self.frame, text="Word-Level Processing", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Input text file selection
        input_label = ttk.Label(self.frame, text="Text File:")
        input_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        input_entry = ttk.Entry(self.frame, textvariable=self.word_input_var, width=50)
        input_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        input_button = ttk.Button(self.frame, text="Browse...", command=self.browse_word_input)
        input_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Database selection for comparison
        db_label = ttk.Label(self.frame, text="Database File (for comparison):")
        db_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        db_entry = ttk.Entry(self.frame, textvariable=self.word_db_var, width=50)
        db_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        db_button = ttk.Button(self.frame, text="Browse...", command=self.browse_word_db)
        db_button.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language selection
        word_lang_label = ttk.Label(self.frame, text="Language:")
        word_lang_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        word_lang_combo = ttk.Combobox(self.frame, textvariable=self.word_language_var, 
                                       values=["de", "en", "fr", "es", "it"])
        word_lang_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Book name
        book_label = ttk.Label(self.frame, text="Book Name:")
        book_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        book_entry = ttk.Entry(self.frame, textvariable=self.word_book_name_var, width=50)
        book_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Output directory
        word_output_label = ttk.Label(self.frame, text="Output Directory:")
        word_output_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        word_output_entry = ttk.Entry(self.frame, textvariable=self.word_output_dir_var, width=50)
        word_output_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        word_output_button = ttk.Button(self.frame, text="Browse...", 
                                        command=self.browse_word_output_dir)
        word_output_button.grid(row=5, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Model ID field
        model_label = ttk.Label(self.frame, text="Model ID:")
        model_label.grid(row=6, column=0, sticky=tk.W, pady=5)
        
        model_entry = ttk.Entry(self.frame, textvariable=self.word_model_id_var, width=50)
        model_entry.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Results")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # Total words found
        total_words_label = ttk.Label(results_frame, text="Total Words Found:")
        total_words_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        total_words_value = ttk.Label(results_frame, textvariable=self.total_words_var)
        total_words_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # New words count
        new_words_label = ttk.Label(results_frame, text="New Words for Translation:")
        new_words_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        new_words_value = ttk.Label(results_frame, textvariable=self.new_words_var)
        new_words_value.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Output file path
        output_file_label = ttk.Label(results_frame, text="Output File:")
        output_file_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        output_file_path = ttk.Entry(results_frame, textvariable=self.word_output_file_var, 
                                     width=60, state='readonly')
        output_file_path.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(self.frame, text="Process Words", command=self.run_word_processing)
        run_button.grid(row=8, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.word_processing_progress = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, 
                                                       length=300, mode='determinate')
        self.word_processing_progress.grid(row=9, column=0, columnspan=3, pady=5, sticky=tk.EW)
    
    def browse_word_input(self):
        """Browse for text input file"""
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.word_input_var.set(file_path)
            # Auto-populate book name from filename if not already set
            if not self.word_book_name_var.get():
                book_name = os.path.splitext(os.path.basename(file_path))[0]
                self.word_book_name_var.set(book_name)
    
    def browse_word_db(self):
        """Browse for database file for word comparison"""
        file_path = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            self.word_db_var.set(file_path)

    def browse_word_output_dir(self):
        """Browse for word processing output directory"""
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.word_output_dir_var.set(dir_path)
    
    def update_progress(self, value, max_value=100):
        """Update this tab's progress bar"""
        progress = int((value / max_value) * 100)
        self.word_processing_progress['value'] = progress
        self.frame.update_idletasks()
    
    def run_word_processing(self):
        """Execute the word processing functionality"""
        try:
            # Get parameters
            text_file = self.word_input_var.get()
            if not text_file:
                messagebox.showerror("Error", "Please select a text file")
                return
                
            db_file = self.word_db_var.get()
            if not db_file:
                messagebox.showerror("Error", "Please select a database file for comparison")
                return
                
            language = self.word_language_var.get()
            book_name = self.word_book_name_var.get()
            
            if not book_name:
                book_name = os.path.splitext(os.path.basename(text_file))[0]
                self.word_book_name_var.set(book_name)
                
            output_dir = self.word_output_dir_var.get()
            model_id = self.word_model_id_var.get()
            
            # Reset progress bar and counters
            self.word_processing_progress['value'] = 0
            self.total_words_var.set("0")
            self.new_words_var.set("0")
            self.word_output_file_var.set("")
            self.frame.update_idletasks()
            
            # Start processing
            self.update_status("Extracting words from text file...")
            self.log(f"Starting word extraction from {text_file}...")
            
            # Import the word processor module
            from word_processor import process_text_to_batch
            
            # Process the text file
            total_words, new_words_count, output_file = process_text_to_batch(
                text_file=text_file,
                db_file=db_file,
                language=language,
                book_name=book_name,
                output_dir=output_dir,
                model_id=model_id,
                progress_callback=self.update_progress
            )
            
            # Update UI with results
            self.total_words_var.set(str(total_words))
            self.new_words_var.set(str(new_words_count))
            self.word_output_file_var.set(output_file)
            
            # Update status
            self.log(f"Found {total_words} unique words in the text file", "info")
            self.log(f"Found {new_words_count} new words not in the database", "info")
            self.log(f"Successfully created batch file at {output_file} with {new_words_count} words", 
                    "success")
            
            self.update_status("Word processing completed successfully")
            
            # Show success message
            messagebox.showinfo("Success", f"Word processing completed successfully!\n\n"
                                         f"Total words found: {total_words}\n"
                                         f"New words for translation: {new_words_count}\n"
                                         f"Output file: {output_file}")
            
        except Exception as e:
            self.update_status("Error")
            self.log(f"Error in word processing: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")