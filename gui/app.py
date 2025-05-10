import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Import all tabs
from .db_to_jsonl_tab import DBToJSONLTab
from .jsonl_to_db_tab import JSONLToDBTab
from .txt_to_jsonl_tab import TXTToJSONLTab
from .word_processing_tab import WordProcessingTab
from .word_translations_tab import WordTranslationsTab

class BookDataProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Data Processor")
        self.root.geometry("800x600")
        
        self.setup_styles()
        self.setup_main_frame()
        self.setup_tabs()
        self.setup_status_bar()
        self.setup_log_frame()
    
    def setup_styles(self):
        """Set up application styling"""
        self.root.iconbitmap("book_icon.ico") if os.path.exists("book_icon.ico") else None
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Define custom colors
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', background='#4a7abc', foreground='black')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
    
    def setup_main_frame(self):
        """Set up the main container"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
    
    def setup_tabs(self):
        """Set up all tabs"""
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # Create tab instances
        self.db_to_jsonl_tab = DBToJSONLTab(self.tab_control, self)
        self.jsonl_to_db_tab = JSONLToDBTab(self.tab_control, self)
        self.txt_to_jsonl_tab = TXTToJSONLTab(self.tab_control, self)
        self.word_processing_tab = WordProcessingTab(self.tab_control, self)
        self.word_translations_tab = WordTranslationsTab(self.tab_control, self)
        
        # Add tabs to notebook
        self.tab_control.add(self.db_to_jsonl_tab.frame, text="DB → JSONL")
        self.tab_control.add(self.jsonl_to_db_tab.frame, text="JSONL → DB")
        self.tab_control.add(self.txt_to_jsonl_tab.frame, text="TXT → JSONL")
        self.tab_control.add(self.word_processing_tab.frame, text="Word Processing")
        self.tab_control.add(self.word_translations_tab.frame, text="Word Translations")
        
        self.tab_control.pack(expand=1, fill="both")
    
    def setup_status_bar(self):
        """Set up the status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def setup_log_frame(self):
        """Set up the logging frame"""
        # ... (existing log frame setup code)
        pass
    
    def log(self, message, level="info"):
        """Add a message to the log with timestamp"""
        # ... (existing log method code)
        pass