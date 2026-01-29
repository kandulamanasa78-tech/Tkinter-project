import tkinter as tk
from tkinter import ttk, messagebox

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="🔐 Blog App Login", font=("Helvetica", 24, "bold"), 
                bg="#2E86AB", fg="white").pack(pady=20)
        
        # Form frame
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        ttk.Label(form_frame, text="Username:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.username_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=30)
        self.username_entry.pack(anchor="w", pady=(0, 15))
        
        ttk.Label(form_frame, text="Password:", font=("Helvetica", 12)).pack(anchor="w", pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, show="•", font=("Helvetica", 11), width=30)
        self.password_entry.pack(anchor="w", pady=(0, 25))
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Login", command=self.login).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Sign Up", 
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
    root.title("Blog App - Login Only")
    root.geometry("400x500")

    # We pass 'root' as the controller to satisfy the __init__ arguments
    login_page = LoginPage(parent=root, controller=root)
    login_page.pack(fill="both", expand=True)

    root.mainloop()