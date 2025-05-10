import tkinter as tk
from gui.app import BookDataProcessor

if __name__ == "__main__":
    root = tk.Tk()
    app = BookDataProcessor(root)
    root.mainloop()