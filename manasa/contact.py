import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class ContactPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x")
        tk.Label(header, text="📧 Contact Us", font=("Helvetica", 22, "bold"), 
                bg="#2E86AB", fg="white").pack(pady=20)
        
        form = ttk.Frame(self)
        form.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Name
        ttk.Label(form, text="Name:", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.name_entry = ttk.Entry(form, width=50)
        self.name_entry.pack(fill="x", pady=(5, 15))
        
        # Subject
        ttk.Label(form, text="Subject:", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.sub_entry = ttk.Entry(form, width=50)
        self.sub_entry.pack(fill="x", pady=(5, 15))
        
        # Message
        ttk.Label(form, text="Message:", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.msg_text = scrolledtext.ScrolledText(form, height=10)
        self.msg_text.pack(fill="both", expand=True, pady=(5, 20))
        
        btn_frame = ttk.Frame(form)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Send Message", 
                  command=self.send).pack(side="left")
        ttk.Button(btn_frame, text="Home", 
                  command=lambda: messagebox.showinfo("Nav", "Back Home")).pack(side="right")

    def send(self):
        if not self.name_entry.get() or not self.msg_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Please fill required fields!")
        else:
            messagebox.showinfo("Sent", "Message sent successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x600")
    app = ContactPage(root, root)
    app.pack(fill="both", expand=True)
    root.mainloop()