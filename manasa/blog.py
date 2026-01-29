import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext,filedialog

class CreatePostPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- Header ---
        header = tk.Frame(self, bg="#06A77D")
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="✍️ Create New Post", font=("Helvetica", 22, "bold"), 
                bg="#06A77D", fg="white").pack(pady=20)
        
        # --- Form area ---
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Title Input
        ttk.Label(form_frame, text="Post Title:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.title_entry = ttk.Entry(form_frame, font=("Helvetica", 12), width=50)
        self.title_entry.pack(anchor="w", pady=(0, 15), fill="x")
        
        # Category Dropdown
        ttk.Label(form_frame, text="Category:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, 
                                     values=["Technology", "Lifestyle", "Business", "Health", "Other"],
                                     state="readonly", font=("Helvetica", 11))
        category_combo.pack(anchor="w", pady=(0, 15), fill="x")
        category_combo.set("Technology") # Default value

        ttk.Button(form_frame, text="📸 Upload Image", command=lambda: filedialog.askopenfilename()).pack(anchor="w", pady=5)
        
        # Content Area (Multi-line)
        ttk.Label(form_frame, text="Post Content:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.content_text = scrolledtext.ScrolledText(form_frame, font=("Helvetica", 11), 
                                                     height=12, wrap="word")
        self.content_text.pack(anchor="w", pady=(0, 15), fill="both", expand=True)
        
        # --- Buttons ---
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Publish Post", command=self.publish_post).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Discard", command=self.discard_post).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back to Home", 
                  command=self.back_to_home).pack(side="right", padx=5)

    def publish_post(self):
        """Simulate saving the post"""
        title = self.title_entry.get().strip()
        cat = self.category_var.get()
        content = self.content_text.get("1.0", tk.END).strip()
        
        if not title or not content:
            messagebox.showerror("Error", "Please provide a title and content!")
            return
            
        messagebox.showinfo("Success", f"Post '{title}' published in {cat}!")
        print(f"PUBLISHED:\nTitle: {title}\nCategory: {cat}\nContent: {content[:50]}...")
        self.clear_fields()

    def discard_post(self):
        """Clear the form"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear your draft?"):
            self.clear_fields()

    def clear_fields(self):
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)

    def back_to_home(self):
        print("Navigation Triggered: Returning to Home Feed...")
        messagebox.showinfo("Navigation", "Returning to Home Page.")

# ================= EXECUTABLE SECTION =================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Blog App - Create Post")
    root.geometry("600x650")

    # Standalone execution
    app = CreatePostPage(parent=root, controller=root)
    app.pack(fill="both", expand=True)

    root.mainloop()