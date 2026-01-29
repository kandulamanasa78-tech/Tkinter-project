import tkinter as tk
from tkinter import ttk

class AboutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        header = tk.Frame(self, bg="#06A77D")
        header.pack(fill="x")
        tk.Label(header, text="ℹ️ About This App", font=("Helvetica", 22, "bold"), 
                bg="#06A77D", fg="white").pack(pady=20)
        
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=40, pady=30)
        
        info_text = (
            "Welcome to the Advanced Blog Platform.\n\n"
            "This application is designed to demonstrate a full-featured "
            "desktop GUI using Python and Tkinter.\n\n"
            "Key Features:\n"
            "• Secure User Authentication\n"
            "• Dynamic Post Feed\n"
            "• Real-time Commenting\n"
            "• SQLite Database Integration\n\n"
            "Developed for the Python Community 2026."
        )
        
        tk.Label(content, text=info_text, font=("Helvetica", 12), 
                 justify="left", wraplength=400).pack(pady=20)
        
        ttk.Button(content, text="Back to Home", 
                  command=lambda: print("Home triggered")).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x500")
    app = AboutPage(root, root)
    app.pack(fill="both", expand=True)
    root.mainloop()