#!/usr/bin/env python3
"""
Book Data Processor - Application Launcher
"""

import tkinter as tk
from main import BookDataProcessor

if __name__ == "__main__":
    root = tk.Tk()
    app = BookDataProcessor(root)
    root.mainloop()