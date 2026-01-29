import tkinter as tk
from tkinter import ttk, messagebox

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="🔐 MIST DASHBOARD", font=("Helvetica", 24, "bold"), 
                bg="#2E86AB", fg="white").pack(pady=20)
        
        # Form frame
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        ttk.Label(form_frame, text="First Name:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.firstname_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=30)
        self.firstname_entry.pack(anchor="w", pady=(0, 15))

        ttk.Label(form_frame, text="Last Name:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.lastname_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=30)
        self.lastname_entry.pack(anchor="w", pady=(0, 15))

        ttk.Label(form_frame, text="Section:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))

        self.section_var = tk.StringVar()
        self.section_dropdown = ttk.Combobox(
     form_frame,
     textvariable=self.section_var,
     values=["CSE", "CSM"],
     font=("Helvetica", 11),
     width=28,
     state="readonly"
)
        self.section_dropdown.pack(anchor="w", pady=(0, 15))
        self.section_dropdown.set("Select Section")
        
        ttk.Label(form_frame, text="Descrption:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.descrption_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=30)
        self.descrption_entry.pack(anchor="w", pady=(0, 15))

         # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        ttk.Button(button_frame, text="Upload image", command=self.login).pack(side="left", padx=5)


        ttk.Label(form_frame, text="Percentage:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.percentage_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=30)
        self.percentage_entry.pack(anchor="w", pady=(0, 15))
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(button_frame, text="Submit", command=self.login).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Return to login", 
                  command=self.signup_clicked).pack(side="left", padx=5)
    
    def login(self):
        """Handle login simulation"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        # Basic simulation since database logic is removed
        if username == "admin" and password == "password":
            messagebox.showinfo("Success", f"Welcome, {username}!")
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def signup_clicked(self):
        """Simulate navigation to signup"""
        print("Navigation Triggered: Redirecting to Signup Page...")
        messagebox.showinfo("Navigation", "In the full app, this would open the Signup Page.")

# ================= EXECUTABLE SECTION =================


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Blog App - Signup Only")
    root.geometry("450x650") # Slightly taller to fit more fields

   # We pass 'root' as the controller to satisfy the _init_ arguments
    login_page = LoginPage(parent=root, controller=root)
    login_page.pack(fill="both", expand=True)

    root.mainloop()