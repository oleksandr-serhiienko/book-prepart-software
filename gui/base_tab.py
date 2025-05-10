import tkinter as tk
from tkinter import ttk

class BaseTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app  # Reference to main app for logging and shared resources
        self.frame = ttk.Frame(parent, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.setup_ui()
    
    def setup_ui(self):
        """Override this method in child classes"""
        pass
    
    def log(self, message, level="info"):
        """Use the main app's logging method"""
        self.app.log(message, level)
    
    def update_status(self, message):
        """Update the main app's status bar"""
        self.app.status_var.set(message)
    
    def update_progress(self, value, max_value=100):
        """Update this tab's progress bar"""
        # Override in child classes if needed
        pass