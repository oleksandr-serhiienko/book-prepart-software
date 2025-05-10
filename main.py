import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

# Import our processing modules
from db_to_jsonl import convert_db_to_jsonl
from jsonl_fixer import fix_sequence_numbers
from txt_to_jsonl import txt_to_jsonl_batch
# NOTE: jsonl_to_db is imported in the run_jsonl_to_db function to avoid circular imports

class BookDataProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Data Processor")
        self.root.geometry("800x600")
        
        # Set application icon and styling
        self.root.iconbitmap("book_icon.ico") if os.path.exists("book_icon.ico") else None
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use a modern theme
        
        # Define custom colors
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', background='#4a7abc', foreground='black')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tab control
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # Create tabs
        self.tab_db_to_jsonl = ttk.Frame(self.tab_control)
        self.tab_txt_to_jsonl = ttk.Frame(self.tab_control)
        self.tab_jsonl_to_db = ttk.Frame(self.tab_control)
        self.tab_word_processing = ttk.Frame(self.tab_control)
        self.tab_word_translations = ttk.Frame(self.tab_control)
        
        # Add tabs to notebook
        self.tab_control.add(self.tab_db_to_jsonl, text="DB → JSONL")
        self.tab_control.add(self.tab_txt_to_jsonl, text="TXT → JSONL")
        self.tab_control.add(self.tab_jsonl_to_db, text="JSONL → DB")
        self.tab_control.add(self.tab_word_processing, text="Word Processing")
        self.tab_control.add(self.tab_word_translations, text="Word Translations")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Initialize tabs
        self.setup_db_to_jsonl_tab()
        self.setup_jsonl_to_db_tab()
        self.setup_txt_to_jsonl_tab()
        self.setup_word_processing_tab()
        self.setup_word_translations_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Log frame
        self.setup_log_frame()
    
    def setup_log_frame(self):
        # Log frame at the bottom
        self.log_frame = ttk.LabelFrame(self.root, text="Log")
        self.log_frame.pack(fill=tk.X, padx=10, pady=5, before=self.status_bar)
        
        # Scrolled text widget for logs
        self.log_text = tk.Text(self.log_frame, height=6, width=80, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for log text
        log_scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Configure text tags
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
        
        # Make log read-only
        self.log_text.config(state=tk.DISABLED)
    
    def log(self, message, level="info"):
        """Add a message to the log with timestamp"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def setup_db_to_jsonl_tab(self):
        # DB to JSONL tab content
        frame = ttk.Frame(self.tab_db_to_jsonl, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(frame, text="Convert Database to JSONL", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Database selection
        db_label = ttk.Label(frame, text="Database File:")
        db_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.db_path_var = tk.StringVar()
        db_entry = ttk.Entry(frame, textvariable=self.db_path_var, width=50)
        db_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        db_button = ttk.Button(frame, text="Browse...", command=self.browse_db_file)
        db_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Output directory
        output_label = ttk.Label(frame, text="Output Directory:")
        output_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.output_dir_var = tk.StringVar()
        self.output_dir_var.set(os.path.join(os.getcwd(), "output"))
        output_entry = ttk.Entry(frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        output_button = ttk.Button(frame, text="Browse...", command=self.browse_output_dir)
        output_button.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language selection
        lang_label = ttk.Label(frame, text="Language:")
        lang_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.language_var = tk.StringVar()
        self.language_var.set("de")
        lang_combo = ttk.Combobox(frame, textvariable=self.language_var, values=["de", "en", "fr", "es", "it"])
        lang_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Book name
        db_label = ttk.Label(frame, text="Target Database File:")
        db_label.grid(row=3, column=0, sticky=tk.W, pady=5)

        self.word_trans_db_path_var = tk.StringVar()
        db_entry = ttk.Entry(frame, textvariable=self.word_trans_db_path_var, width=50)
        db_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        db_button = ttk.Button(frame, text="Browse...", command=self.browse_word_trans_db)
        db_button.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Fix numbers checkbox
        self.fix_numbers_var = tk.BooleanVar()
        self.fix_numbers_var.set(True)
        fix_numbers_check = ttk.Checkbutton(frame, text="Fix number sequences", variable=self.fix_numbers_var)
        fix_numbers_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Run button
        run_button = ttk.Button(frame, text="Process DB to JSONL", command=self.run_db_to_jsonl)
        run_button.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.db_to_jsonl_progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.db_to_jsonl_progress.grid(row=7, column=0, columnspan=3, pady=5, sticky=tk.EW)
    
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
    
    def setup_jsonl_to_db_tab(self):
        # JSONL to DB tab
        frame = ttk.Frame(self.tab_jsonl_to_db, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(frame, text="Convert JSONL Results to Database", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # JSONL results selection
        jsonl_label = ttk.Label(frame, text="JSONL Results File:")
        jsonl_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.jsonl_path_var = tk.StringVar()
        jsonl_entry = ttk.Entry(frame, textvariable=self.jsonl_path_var, width=50)
        jsonl_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        jsonl_button = ttk.Button(frame, text="Browse...", command=self.browse_jsonl_file)
        jsonl_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # JSONL sent file selection
        sent_label = ttk.Label(frame, text="JSONL Sent File:")
        sent_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.jsonl_sent_path_var = tk.StringVar()
        sent_entry = ttk.Entry(frame, textvariable=self.jsonl_sent_path_var, width=50)
        sent_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        sent_button = ttk.Button(frame, text="Browse...", command=self.browse_jsonl_sent_file)
        sent_button.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Database name
        db_label = ttk.Label(frame, text="Database Name:")
        db_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.db_name_var = tk.StringVar()
        db_name_entry = ttk.Entry(frame, textvariable=self.db_name_var, width=50)
        db_name_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Output directory
        jsonl_output_label = ttk.Label(frame, text="Output Directory:")
        jsonl_output_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.db_output_dir_var = tk.StringVar()
        self.db_output_dir_var.set(os.path.join(os.getcwd(), "output"))
        jsonl_output_entry = ttk.Entry(frame, textvariable=self.db_output_dir_var, width=50)
        jsonl_output_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        jsonl_output_button = ttk.Button(frame, text="Browse...", command=self.browse_jsonl_output_dir)
        jsonl_output_button.grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Model ID field
        model_label = ttk.Label(frame, text="Model ID (for error batch):")
        model_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.jsonl_model_id_var = tk.StringVar()
        self.jsonl_model_id_var.set("ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BHa7AxGJ")
        model_entry = ttk.Entry(frame, textvariable=self.jsonl_model_id_var, width=50)
        model_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Output files frame
        output_files_frame = ttk.LabelFrame(frame, text="Output Files")
        output_files_frame.grid(row=6, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # SQL file output
        self.sql_file_var = tk.StringVar()
        sql_file_label = ttk.Label(output_files_frame, text="SQL Insert File:")
        sql_file_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        sql_file_path = ttk.Entry(output_files_frame, textvariable=self.sql_file_var, width=60, state='readonly')
        sql_file_path.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Error file output
        self.error_file_var = tk.StringVar()
        error_file_label = ttk.Label(output_files_frame, text="Error File:")
        error_file_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        error_file_path = ttk.Entry(output_files_frame, textvariable=self.error_file_var, width=60, state='readonly')
        error_file_path.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Error batch file output
        self.error_batch_var = tk.StringVar()
        error_batch_label = ttk.Label(output_files_frame, text="Error Batch File:")
        error_batch_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        error_batch_path = ttk.Entry(output_files_frame, textvariable=self.error_batch_var, width=60, state='readonly')
        error_batch_path.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Results")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # SQL statements count
        self.sql_count_var = tk.StringVar()
        self.sql_count_var.set("0")
        sql_count_label = ttk.Label(results_frame, text="SQL Statements:")
        sql_count_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        sql_count_value = ttk.Label(results_frame, textvariable=self.sql_count_var)
        sql_count_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Error count
        self.error_count_var = tk.StringVar()
        self.error_count_var.set("0")
        error_count_label = ttk.Label(results_frame, text="Error Entries:")
        error_count_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        error_count_value = ttk.Label(results_frame, textvariable=self.error_count_var)
        error_count_value.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(frame, text="Process JSONL to DB", command=self.run_jsonl_to_db)
        run_button.grid(row=8, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.jsonl_to_db_progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.jsonl_to_db_progress.grid(row=9, column=0, columnspan=3, pady=5, sticky=tk.EW)
        
    def browse_jsonl_sent_file(self):
        file_path = filedialog.askopenfilename(
            title="Select JSONL Sent File",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")]
        )
        if file_path:
            self.jsonl_sent_path_var.set(file_path)
    
    def setup_txt_to_jsonl_tab(self):
        # TXT to JSONL tab 
        frame = ttk.Frame(self.tab_txt_to_jsonl, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(frame, text="Convert Text File to Batch JSONL", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Text file selection
        txt_label = ttk.Label(frame, text="Text File:")
        txt_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.txt_path_var = tk.StringVar()
        txt_entry = ttk.Entry(frame, textvariable=self.txt_path_var, width=50)
        txt_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        txt_button = ttk.Button(frame, text="Browse...", command=self.browse_txt_file)
        txt_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language selection
        txt_lang_label = ttk.Label(frame, text="Language:")
        txt_lang_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.txt_language_var = tk.StringVar()
        self.txt_language_var.set("de")
        txt_lang_combo = ttk.Combobox(frame, textvariable=self.txt_language_var, values=["de", "en", "fr", "es", "it"])
        txt_lang_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Model ID field
        model_label = ttk.Label(frame, text="Model ID:")
        model_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.model_id_var = tk.StringVar()
        self.model_id_var.set("ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BHa7AxGJ")
        model_entry = ttk.Entry(frame, textvariable=self.model_id_var, width=50)
        model_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Output directory
        txt_output_label = ttk.Label(frame, text="Output Directory:")
        txt_output_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.txt_output_dir_var = tk.StringVar()
        self.txt_output_dir_var.set(os.path.join(os.getcwd(), "output"))
        txt_output_entry = ttk.Entry(frame, textvariable=self.txt_output_dir_var, width=50)
        txt_output_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        txt_output_button = ttk.Button(frame, text="Browse...", command=self.browse_txt_output_dir)
        txt_output_button.grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Processing options frame
        options_frame = ttk.LabelFrame(frame, text="Processing Options")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # Options
        self.process_sentences_var = tk.BooleanVar(value=True)
        sentences_check = ttk.Checkbutton(options_frame, text="Process sentences", variable=self.process_sentences_var)
        sentences_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.auto_number_var = tk.BooleanVar(value=True)
        number_check = ttk.Checkbutton(options_frame, text="Auto-number elements", variable=self.auto_number_var)
        number_check.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(frame, text="Process TXT to Batch JSONL", command=self.run_txt_to_jsonl)
        run_button.grid(row=6, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.txt_to_jsonl_progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.txt_to_jsonl_progress.grid(row=7, column=0, columnspan=3, pady=5, sticky=tk.EW)
    
    def setup_word_processing_tab(self):
        # Word Processing tab
        frame = ttk.Frame(self.tab_word_processing, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(frame, text="Word-Level Processing", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Input text file selection
        input_label = ttk.Label(frame, text="Text File:")
        input_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.word_input_var = tk.StringVar()
        input_entry = ttk.Entry(frame, textvariable=self.word_input_var, width=50)
        input_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        input_button = ttk.Button(frame, text="Browse...", command=self.browse_word_input)
        input_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Database selection for comparison
        db_label = ttk.Label(frame, text="Database File (for comparison):")
        db_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.word_db_var = tk.StringVar()
        db_entry = ttk.Entry(frame, textvariable=self.word_db_var, width=50)
        db_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        db_button = ttk.Button(frame, text="Browse...", command=self.browse_word_db)
        db_button.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language selection
        word_lang_label = ttk.Label(frame, text="Language:")
        word_lang_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.word_language_var = tk.StringVar()
        self.word_language_var.set("de")
        word_lang_combo = ttk.Combobox(frame, textvariable=self.word_language_var, values=["de", "en", "fr", "es", "it"])
        word_lang_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Book name
        book_label = ttk.Label(frame, text="Book Name:")
        book_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.word_book_name_var = tk.StringVar()
        book_entry = ttk.Entry(frame, textvariable=self.word_book_name_var, width=50)
        book_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Output directory
        word_output_label = ttk.Label(frame, text="Output Directory:")
        word_output_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.word_output_dir_var = tk.StringVar()
        self.word_output_dir_var.set(os.path.join(os.getcwd(), "output"))
        word_output_entry = ttk.Entry(frame, textvariable=self.word_output_dir_var, width=50)
        word_output_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        word_output_button = ttk.Button(frame, text="Browse...", command=self.browse_word_output_dir)
        word_output_button.grid(row=5, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Model ID field
        model_label = ttk.Label(frame, text="Model ID:")
        model_label.grid(row=6, column=0, sticky=tk.W, pady=5)
        
        self.word_model_id_var = tk.StringVar()
        self.word_model_id_var.set("ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BJJAaWzW")
        model_entry = ttk.Entry(frame, textvariable=self.word_model_id_var, width=50)
        model_entry.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Results")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # Total words found
        self.total_words_var = tk.StringVar()
        self.total_words_var.set("0")
        total_words_label = ttk.Label(results_frame, text="Total Words Found:")
        total_words_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        total_words_value = ttk.Label(results_frame, textvariable=self.total_words_var)
        total_words_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # New words count
        self.new_words_var = tk.StringVar()
        self.new_words_var.set("0")
        new_words_label = ttk.Label(results_frame, text="New Words for Translation:")
        new_words_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        new_words_value = ttk.Label(results_frame, textvariable=self.new_words_var)
        new_words_value.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Output file path
        self.word_output_file_var = tk.StringVar()
        output_file_label = ttk.Label(results_frame, text="Output File:")
        output_file_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        output_file_path = ttk.Entry(results_frame, textvariable=self.word_output_file_var, width=60, state='readonly')
        output_file_path.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(frame, text="Process Words", command=self.run_word_processing)
        run_button.grid(row=8, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.word_processing_progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.word_processing_progress.grid(row=9, column=0, columnspan=3, pady=5, sticky=tk.EW)

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
            self.root.update_idletasks()
            
            # Start processing
            self.status_var.set("Extracting words from text file...")
            self.log(f"Starting word extraction from {text_file}...")
            
            # Import the word processor module
            from word_processor import process_text_to_batch  # Fixed typo: word_precessor -> word_processor
            
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
            self.log(f"Successfully created batch file at {output_file} with {new_words_count} words", "success")
            
            self.status_var.set("Word processing completed successfully")
            
            # Show success message
            messagebox.showinfo("Success", f"Word processing completed successfully!\n\n"
                            f"Total words found: {total_words}\n"
                            f"New words for translation: {new_words_count}\n"
                            f"Output file: {output_file}")
            
        except Exception as e:
            self.status_var.set("Error")
            self.log(f"Error in word processing: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    # File browser functions
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
            
    def browse_txt_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.txt_output_dir_var.set(dir_path)
    
    def browse_jsonl_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.db_output_dir_var.set(dir_path)
    
    def browse_jsonl_file(self):
        file_path = filedialog.askopenfilename(
            title="Select JSONL Results File",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")]
        )
        if file_path:
            print(f"Selected file path: {file_path}")  # Debug print
            self.jsonl_path_var.set(file_path)
            self.root.update_idletasks()  # Force update of UI
            print(f"After setting: {self.jsonl_path_var.get()}")  # Debug print
            
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
            if hasattr(self, 'jsonl_sent_path_var'):  # Check if attribute exists
                base_dir = os.path.dirname(file_path)
                if "_output.jsonl" in base_name:
                    potential_sent_file = os.path.join(base_dir, base_name.replace("_output.jsonl", "_sent.jsonl"))
                    if os.path.exists(potential_sent_file):
                        self.jsonl_sent_path_var.set(potential_sent_file)
                        self.log(f"Auto-detected JSONL Sent file: {potential_sent_file}", "info")
       
    
    def browse_db_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Database As",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            defaultextension=".db"
        )
        if file_path:
            self.db_out_path_var.set(file_path)
    
    def browse_txt_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.txt_path_var.set(file_path)
    
    def browse_jsonl_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Save JSONL As",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")],
            defaultextension=".jsonl"
        )
        if file_path:
            self.jsonl_out_path_var.set(file_path)
    
    def browse_word_input(self):
        file_path = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[
                ("All Supported Files", "*.db *.jsonl *.txt"),
                ("SQLite Database", "*.db"),
                ("JSONL Files", "*.jsonl"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.word_input_var.set(file_path)
            # Detect file type
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.db':
                self.input_type_var.set("database")
            elif ext == '.jsonl':
                self.input_type_var.set("jsonl")
            elif ext == '.txt':
                self.input_type_var.set("text")
    
    # Processing functions
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
            self.root.update_idletasks()
            
            # Step 1: Convert DB to JSONL
            self.status_var.set("Converting database to JSONL...")
            self.log(f"Starting conversion of {db_path} to JSONL...")
            result_path = convert_db_to_jsonl(db_path, interim_output_path, 
                                             progress_callback=self.update_progress)
            
            # Step 2: Fix sequence numbers if requested
            if self.fix_numbers_var.get():
                self.status_var.set("Fixing number sequences...")
                self.log(f"Fixing number sequences in {result_path}...")
                os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
                fix_sequence_numbers(result_path, final_output_path, 
                                    progress_callback=self.update_progress)
                self.log(f"Successfully created fixed JSONL at {final_output_path}", "success")
            
            self.status_var.set("Process completed successfully")
            messagebox.showinfo("Success", "DB to JSONL conversion completed successfully!")
            
        except Exception as e:
            self.status_var.set("Error")
            self.log(f"Error in DB to JSONL process: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
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
                messagebox.showwarning("Warning", "No JSONL sent file selected. This may cause errors if the file is required.")
                
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
            self.root.update_idletasks()
            
            # Process JSONL file
            self.status_var.set("Processing JSONL results...")
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
            
            self.status_var.set("Process completed successfully")
            self.log(f"Successfully created SQL inserts ({sql_count}) at {sql_path}", "success")
            self.log(f"Validation errors ({error_count}) saved to {error_path}", "info")
            self.log(f"Error batch file created at {batch_path}", "info")
            
            messagebox.showinfo("Success", f"JSONL to DB conversion completed successfully!\n\n"
                                        f"SQL Statements: {sql_count}\n"
                                        f"Error Entries: {error_count}")
            
        except Exception as e:
            self.status_var.set("Error")
            self.log(f"Error in JSONL to DB process: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            """Execute the JSONL to DB conversion"""
            try:
                # Get parameters
                jsonl_path = self.jsonl_path_var.get()
                if not jsonl_path:
                    messagebox.showerror("Error", "Please select a JSONL results file")
                    return
                    
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
                self.root.update_idletasks()
                
                # Process JSONL file
                self.status_var.set("Processing JSONL results...")
                self.log(f"Starting conversion of {jsonl_path} to database format...")
                
                # Import jsonl_to_db here to avoid circular imports
                from jsonl_to_db import jsonl_to_db
                
                sql_path, error_path, batch_path, sql_count, error_count = jsonl_to_db(
                    jsonl_path, 
                    db_name,
                    output_dir,
                    model_id,
                    progress_callback=self.update_progress
                )
                
                # Update UI with results
                self.sql_file_var.set(sql_path)
                self.error_file_var.set(error_path)
                self.error_batch_var.set(batch_path)
                self.sql_count_var.set(str(sql_count))
                self.error_count_var.set(str(error_count))
                
                self.status_var.set("Process completed successfully")
                self.log(f"Successfully created SQL inserts ({sql_count}) at {sql_path}", "success")
                self.log(f"Validation errors ({error_count}) saved to {error_path}", "info")
                self.log(f"Error batch file created at {batch_path}", "info")
                
                messagebox.showinfo("Success", f"JSONL to DB conversion completed successfully!\n\n"
                                            f"SQL Statements: {sql_count}\n"
                                            f"Error Entries: {error_count}")
                
            except Exception as e:
                self.status_var.set("Error")
                self.log(f"Error in JSONL to DB process: {str(e)}", "error")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
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
            self.root.update_idletasks()
            
            # Process text file
            self.status_var.set("Converting text to batch JSONL...")
            self.log(f"Starting conversion of {txt_path} to batch JSONL...")
            
            result_path = txt_to_jsonl_batch(
                txt_path, 
                output_path, 
                language, 
                model_id,
                progress_callback=self.update_progress
            )
            
            self.status_var.set("Process completed successfully")
            self.log(f"Successfully created batch JSONL at {result_path}", "success")
            messagebox.showinfo("Success", "Text to Batch JSONL conversion completed successfully!")
            
        except Exception as e:
            self.status_var.set("Error")
            self.log(f"Error in TXT to JSONL process: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def update_progress(self, value, max_value=100):
        """Update progress bar"""
        progress = int((value / max_value) * 100)
        # Get the current active tab
        current_tab = self.tab_control.index(self.tab_control.select())
        
        # Update the appropriate progress bar
        if current_tab == 0:  # DB to JSONL tab
            self.db_to_jsonl_progress['value'] = progress
        elif current_tab == 1:  # TXT to JSONL tab
            self.txt_to_jsonl_progress['value'] = progress
        elif current_tab == 2:  # JSONL to DB tab
            self.jsonl_to_db_progress['value'] = progress
        elif current_tab == 3:  # Word processing tab
            self.word_processing_progress['value'] = progress
        elif current_tab == 4:  # Word translations tab
            self.word_trans_progress['value'] = progress
            
        self.root.update_idletasks()
    
    def setup_word_translations_tab(self):
        # Word Translations tab
        frame = ttk.Frame(self.tab_word_translations, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(frame, text="Process Word Translations", style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # JSONL results selection
        jsonl_label = ttk.Label(frame, text="Word JSONL Results File:")
        jsonl_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.word_jsonl_path_var = tk.StringVar()
        jsonl_entry = ttk.Entry(frame, textvariable=self.word_jsonl_path_var, width=50)
        jsonl_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        jsonl_button = ttk.Button(frame, text="Browse...", command=self.browse_word_jsonl_file)
        jsonl_button.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Language selection
        lang_label = ttk.Label(frame, text="Language:")
        lang_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.word_trans_language_var = tk.StringVar()
        self.word_trans_language_var.set("de")
        lang_combo = ttk.Combobox(frame, textvariable=self.word_trans_language_var, values=["de", "en", "fr", "es", "it"])
        lang_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Book name
        db_label = ttk.Label(frame, text="Target Database File:")
        db_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.word_trans_db_path_var = tk.StringVar()
        db_entry = ttk.Entry(frame, textvariable=self.word_trans_db_path_var, width=50)
        db_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        db_button = ttk.Button(frame, text="Browse...", command=self.browse_word_trans_db)
        db_button.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Output directory
        output_label = ttk.Label(frame, text="Output Directory:")
        output_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.word_trans_output_dir_var = tk.StringVar()
        self.word_trans_output_dir_var.set(os.path.join(os.getcwd(), "output"))
        output_entry = ttk.Entry(frame, textvariable=self.word_trans_output_dir_var, width=50)
        output_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        output_button = ttk.Button(frame, text="Browse...", command=self.browse_word_trans_output_dir)
        output_button.grid(row=4, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Model ID field
        model_label = ttk.Label(frame, text="Model ID (for error batch):")
        model_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.word_trans_model_id_var = tk.StringVar()
        self.word_trans_model_id_var.set("ft:gpt-4o-mini-2024-07-18:oleksandrserhiienko::BJJAaWzW")
        model_entry = ttk.Entry(frame, textvariable=self.word_trans_model_id_var, width=50)
        model_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Output files frame
        output_files_frame = ttk.LabelFrame(frame, text="Output Files")
        output_files_frame.grid(row=6, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # SQL file output
        self.word_sql_file_var = tk.StringVar()
        sql_file_label = ttk.Label(output_files_frame, text="SQL File:")
        sql_file_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        sql_file_path = ttk.Entry(output_files_frame, textvariable=self.word_sql_file_var, width=60, state='readonly')
        sql_file_path.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Error batch file output
        self.word_error_batch_var = tk.StringVar()
        error_batch_label = ttk.Label(output_files_frame, text="Error Batch File:")
        error_batch_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        error_batch_path = ttk.Entry(output_files_frame, textvariable=self.word_error_batch_var, width=60, state='readonly')
        error_batch_path.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(frame, text="Results")
        results_frame.grid(row=7, column=0, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        
        # Successful translations count
        self.word_success_count_var = tk.StringVar()
        self.word_success_count_var.set("0")
        success_count_label = ttk.Label(results_frame, text="Successful Translations:")
        success_count_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        success_count_value = ttk.Label(results_frame, textvariable=self.word_success_count_var)
        success_count_value.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Failed translations count
        self.word_failed_count_var = tk.StringVar()
        self.word_failed_count_var.set("0")
        failed_count_label = ttk.Label(results_frame, text="Failed Translations:")
        failed_count_label.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        failed_count_value = ttk.Label(results_frame, textvariable=self.word_failed_count_var)
        failed_count_value.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Run button
        run_button = ttk.Button(frame, text="Process Word Translations", command=self.run_word_translations)
        run_button.grid(row=8, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.word_trans_progress = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.word_trans_progress.grid(row=9, column=0, columnspan=3, pady=5, sticky=tk.EW)

    def browse_word_jsonl_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Word JSONL Results File",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")]
        )
        if file_path:
            self.word_jsonl_path_var.set(file_path)
            
            # Try to extract book name from filename
            base_name = os.path.basename(file_path)
            if "_word_output.jsonl" in base_name:
                book_name = base_name.replace("_word_output.jsonl", "")
            else:
                book_name = os.path.splitext(base_name)[0]
            self.word_trans_book_name_var.set(book_name)
            
            self.log(f"Selected Word JSONL Results file: {file_path}", "info")

    def browse_word_trans_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.word_trans_output_dir_var.set(dir_path)

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
            self.root.update_idletasks()
            
            # Process JSONL file
            self.status_var.set("Processing Word Translations...")
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
            
            self.status_var.set("Word translations processing completed successfully")
            self.log(f"Successfully created SQL file with {success_count} translations at {sql_path}", "success")
            self.log(f"Failed translations ({failed_count}) saved to error batch at {error_path}", "info")
            
            messagebox.showinfo("Success", f"Word translations processing completed successfully!\n\n"
                            f"Successful Translations: {success_count}\n"
                            f"Failed Translations: {failed_count}")
            
        except Exception as e:
            self.status_var.set("Error")
            self.log(f"Error in Word Translations process: {str(e)}", "error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookDataProcessor(root)
    root.mainloop()