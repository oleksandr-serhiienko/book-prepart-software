import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .base_tab import BaseTab
from txt_to_jsonl import txt_to_jsonl_batch


class TXTToJSONLTab(BaseTab):
    def __init__(self, parent, app):
        # Initialize variables
        self.txt_path_var = tk.StringVar()
        self.txt_language_var = tk.StringVar()
        self.txt_language_var.set("de")
        self.model_id_var = tk.StringVar()
        self.model_id_var.set("ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BHa7AxGJ")
        self.txt_output_dir_var = tk.StringVar()
        self.txt_output_dir_var.set(os.path.join(os.getcwd(), "output"))
        
        # Processing options
        self.process_sentences_var = tk.BooleanVar(value=True)
        self.auto_number_var = tk.BooleanVar(value=True)
        
        self.txt_to_jsonl_progress = None
        
        super().__init__(parent, app)
    
    def setup_ui(self):
        # Title
        title_label = ttk.Label(self.frame, text="Convert Text File to Batch JSONL", 
                               style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Text file selection
        txt_label = ttk.Label(self.frame, text="Text File:")
        txt_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        txt_entry = ttk.Entry(self.frame, textvariable=self.txt_path_var, width=50)
        txt_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        txt_button = ttk.Button(self.frame, text="Browse...", command=self.browse_txt_file)
        txt_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language selection
        txt_lang_label = ttk.Label(self.frame, text="Language:")
        txt_lang_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        txt_lang_combo = ttk.Combobox(self.frame, textvariable=self.txt_language_var, 
                                      values=["de", "en", "fr", "es", "it"])
        txt_lang_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Model ID field
        model_label = ttk.Label(self.frame, text="Model ID:")
        model_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        model_entry = ttk.Entry(self.frame, textvariable=self.model_id_var, width=50)
        model_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Output directory
        txt_output_label = ttk.Label(self.frame, text="Output Directory:")
        txt_output_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        txt_output_entry = ttk.Entry(self.frame, textvariable=self.txt_output_dir_var, width=50)
        txt_output_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        txt_output_button = ttk.Button(self.frame, text="Browse...", 
                                      command=self.browse_txt_output_dir)
        txt_output_button.grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Processing options frame
        options_frame = ttk.LabelFrame(self.frame, text="Processing Options")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # Options
        sentences_check = ttk.Checkbutton(options_frame, text="Process sentences", 
                                         variable=self.process_sentences_var)
        sentences_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        number_check = ttk.Checkbutton(options_frame, text="Auto-number elements", 
                                      variable=self.auto_number_var)
        number_check.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(self.frame, text="Process TXT to Batch JSONL", 
                               command=self.run_txt_to_jsonl)
        run_button.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.txt_to_jsonl_progress = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, 
                                                    length=300, mode='determinate')
        self.txt_to_jsonl_progress.grid(row=7, column=0, columnspan=3, pady=5, sticky=tk.EW)
    
    def browse_txt_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.txt_path_var.set(file_path)
    
    def browse_txt_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.txt_output_dir_var.set(dir_path)
    
    def update_progress(self, value, max_value=100):
        """Update this tab's progress bar"""
        progress = int((value / max_value) * 100)
        self.txt_to_jsonl_progress['value'] = progress
        self.frame.update_idletasks()
    
    def run_txt_to_jsonl(self):
        """Execute the TXT to Batch JSONL conversion"""
        try:
            # Get parameters
            txt_path = self.txt_path_var.get()
            if not txt_path:
                messagebox.showerror("Error", "Please select a text file")
                return
                
            language = self.txt_language_var.get()
            model_id = self.model_id_var.get()
            
            # Get book name from file name
            book_name = os.path.splitext(os.path.basename(txt_path))[0]
            
            # Create output path
            output_dir = self.txt_output_dir_var.get()
            os.makedirs(output_dir, exist_ok=True)
            
            # Ensure language directory exists
            language_dir = os.path.join(output_dir, language)
            os.makedirs(language_dir, exist_ok=True)
            
            # Create output path
            output_path = os.path.join(language_dir, f"{book_name}_batch.jsonl")
            
            # Reset progress bar
            self.txt_to_jsonl_progress['value'] = 0
            self.frame.update_idletasks()
            
            # Process text file
            self.update_status("Converting text to batch JSONL...")
            self.log(f"Starting conversion of {txt_path} to batch JSONL...")
            
            result_path = txt_to_jsonl_batch(
                txt_path, 
                output_path, 
                language, 
                model_id,
                progress_callback=self.update_progress
            )
            
            self.update_status("Process completed successfully")
            self.log(f"Successfully created batch JSONL at {result_path}", "success")
            messagebox.showinfo("Success", "Text to Batch JSONL conversion completed successfully!")
            
        except Exception as e:
            self.update_status("Error")
            self.log(f"Error in TXT to JSONL process: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")