import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class PostDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- Header ---
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x")
        
        ttk.Button(header, text="← Back", 
                  command=lambda: messagebox.showinfo("Nav", "Going back...")).pack(side="left", padx=10, pady=10)
        tk.Label(header, text="Reading Post", font=("Helvetica", 16, "bold"), 
                bg="#2E86AB", fg="white").pack(side="left", padx=10)

        # --- Scrollable Area ---
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(container, bg="white")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="white")

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Post Content ---
        tk.Label(self.scroll_frame, text="The Future of Python in 2026", 
                 font=("Helvetica", 22, "bold"), bg="white", wraplength=500, justify="left").pack(anchor="w", pady=(10, 5))
        
        tk.Label(self.scroll_frame, text="By Admin • Jan 26, 2026 • Technology", 
                 font=("Helvetica", 10), bg="white", fg="#666").pack(anchor="w", pady=(0, 20))

        content = ("Python remains the king of data science and AI. In 2026, we see even more "
                   "integration with high-performance libraries. The simplicity of the syntax "
                   "continues to attract new developers every day...")
        
        tk.Label(self.scroll_frame, text=content, font=("Helvetica", 12), bg="white", 
                 wraplength=550, justify="left").pack(anchor="w", pady=10)

        # --- Comment Section ---
        # FIXED: Changed tk.Separator to ttk.Separator
        ttk.Separator(self.scroll_frame, orient='horizontal').pack(fill='x', pady=20)
        
        tk.Label(self.scroll_frame, text="Comments", font=("Helvetica", 14, "bold"), bg="white").pack(anchor="w")
        
        self.comment_entry = tk.Entry(self.scroll_frame, font=("Helvetica", 11), width=50)
        self.comment_entry.pack(anchor="w", pady=10)
        
        ttk.Button(self.scroll_frame, text="Post Comment", 
                  command=lambda: messagebox.showinfo("Success", "Comment added!")).pack(anchor="w")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Post Detail View")
    root.geometry("600x700")
    app = PostDetailPage(root, root)
    app.pack(fill="both", expand=True)
    root.mainloop()

