import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import sqlite3
from datetime import datetime
import hashlib
from PIL import Image, ImageTk
import os
import shutil
from pathlib import Path

# ================= DATABASE SETUP =================
class Database:
    """Handle all database operations for the blog app"""
    
    def __init__(self, db_name="blog_app.db"):
        self.db_name = db_name
        self.create_tables()
    
    def get_connection(self):
        """Create database connection"""
        return sqlite3.connect(self.db_name)
    
    def create_tables(self):
        """Create required database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Blog posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                comment_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Migration: Add image_path column if it doesn't exist
        self.migrate_add_image_path()
    
    def migrate_add_image_path(self):
        """Add image_path column to posts table if it doesn't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if column exists
            cursor.execute("PRAGMA table_info(posts)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'image_path' not in columns:
                cursor.execute('ALTER TABLE posts ADD COLUMN image_path TEXT')
                conn.commit()
                print("✓ Successfully added image_path column to posts table")
            
            conn.close()
        except Exception as e:
            print(f"Migration note: {e}")
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, email, password, full_name):
        """Register a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password, full_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, hashed_password, full_name))
            
            conn.commit()
            conn.close()
            return True, "Registration successful!"
        except sqlite3.IntegrityError:
            return False, "Username or email already exists!"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def login_user(self, username, password):
        """Authenticate user login"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            
            cursor.execute('''
                SELECT user_id, full_name FROM users 
                WHERE username = ? AND password = ?
            ''', (username, hashed_password))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, result
            else:
                return False, None
        except Exception as e:
            return False, str(e)
    
    def get_user_by_id(self, user_id):
        """Get user details by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username, email, full_name FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def create_post(self, user_id, title, content, category, image_path=None):
        """Create a new blog post with optional image"""
        try:
            # Create images directory if it doesn't exist
            img_dir = Path("post_images")
            img_dir.mkdir(exist_ok=True)
            
            stored_image_path = None
            if image_path and os.path.exists(image_path):
                # Copy image to post_images directory
                filename = os.path.basename(image_path)
                stored_image_path = str(img_dir / filename)
                shutil.copy2(image_path, stored_image_path)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO posts (user_id, title, content, category, image_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, title, content, category, stored_image_path))
            
            conn.commit()
            post_id = cursor.lastrowid
            conn.close()
            return True, post_id
        except Exception as e:
            return False, str(e)
    
    def get_all_posts(self):
        """Get all blog posts with user information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT posts.post_id, posts.title, posts.content, posts.category,
                   posts.created_at, users.username, users.full_name, posts.image_path
            FROM posts
            JOIN users ON posts.user_id = users.user_id
            ORDER BY posts.created_at DESC
        ''')
        result = cursor.fetchall()
        conn.close()
        return result
    
    def get_user_posts(self, user_id):
        """Get all posts by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT post_id, title, content, category, created_at, image_path
            FROM posts
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        result = cursor.fetchall()
        conn.close()
        return result
    
    def get_post_details(self, post_id):
        """Get specific post details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT posts.post_id, posts.title, posts.content, posts.category,
                   posts.created_at, users.username, users.full_name, posts.user_id, posts.image_path
            FROM posts
            JOIN users ON posts.user_id = users.user_id
            WHERE posts.post_id = ?
        ''', (post_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_post(self, post_id, title, content, category):
        """Update a blog post"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE posts
                SET title = ?, content = ?, category = ?, updated_at = CURRENT_TIMESTAMP
                WHERE post_id = ?
            ''', (title, content, category, post_id))
            conn.commit()
            conn.close()
            return True, "Post updated successfully!"
        except Exception as e:
            return False, str(e)
    
    def delete_post(self, post_id):
        """Delete a blog post"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM posts WHERE post_id = ?', (post_id,))
            conn.commit()
            conn.close()
            return True, "Post deleted successfully!"
        except Exception as e:
            return False, str(e)
    
    def add_comment(self, post_id, user_id, comment_text):
        """Add a comment to a post"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO comments (post_id, user_id, comment_text)
                VALUES (?, ?, ?)
            ''', (post_id, user_id, comment_text))
            conn.commit()
            conn.close()
            return True, "Comment added!"
        except Exception as e:
            return False, str(e)
    
    def get_post_comments(self, post_id):
        """Get all comments for a post"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT comments.comment_id, comments.comment_text, users.username, comments.created_at
            FROM comments
            JOIN users ON comments.user_id = users.user_id
            WHERE comments.post_id = ?
            ORDER BY comments.created_at DESC
        ''', (post_id,))
        result = cursor.fetchall()
        conn.close()
        return result


# ================= MAIN APPLICATION =================
class BlogApp(tk.Tk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        self.title("Advanced Blog Posting Application")
        self.geometry("1000x700")
        self.resizable(True, True)
        
        # Database initialization
        self.db = Database()
        self.current_user = None
        
        # Configure style
        self.setup_styles()
        
        # Create menu bar with dropdown menus
        self.create_menu_bar()
        
        # Create container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # Create all pages
        for F in (LoginPage, SignupPage, HomePage, AboutPage, ContactPage, BlogPage, MyPostsPage, PostDetailPage, GalleryPage, PostsTreeviewPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(LoginPage)
    
    def create_menu_bar(self):
        """Create dropdown menus"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Home", command=lambda: self.show_frame(HomePage))
        file_menu.add_command(label="New Post", command=lambda: self.show_frame(BlogPage))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Gallery", command=lambda: self.show_frame(GalleryPage))
        view_menu.add_command(label="Posts (Treeview)", command=lambda: self.show_frame(PostsTreeviewPage))
        view_menu.add_command(label="My Posts", command=lambda: self.show_frame(MyPostsPage))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="About", command=lambda: self.show_frame(AboutPage))
        tools_menu.add_command(label="Contact", command=lambda: self.show_frame(ContactPage))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Application", 
                             command=lambda: messagebox.showinfo("About", "Advanced Blog Application v1.0\nBuilt with Python & Tkinter"))
        help_menu.add_command(label="Documentation",
                             command=lambda: messagebox.showinfo("Documentation", "Features:\n- Create & Edit Posts\n- Add Images\n- Comment on Posts\n- Gallery View\n- Advanced Widgets"))
    
    def setup_styles(self):
        """Setup ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Define colors
        self.bg_color = "#f0f0f0"
        self.fg_color = "#333333"
        self.accent_color = "#2E86AB"
        self.highlight_color = "#06A77D"
        
        # Configure styles
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("Accent.TButton", font=("Helvetica", 10))
        style.configure("TEntry", font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 18, "bold"), background=self.bg_color)
    
    def show_frame(self, cont):
        """Display the requested frame"""
        frame = self.frames[cont]
        # Refresh HomePage posts whenever it's displayed
        if cont == HomePage:
            frame.load_posts()
        frame.tkraise()
    
    def set_user(self, user_id, username):
        """Set current logged-in user"""
        self.current_user = {"user_id": user_id, "username": username}
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.show_frame(LoginPage)


# ================= LOGIN PAGE =================
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
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
                  command=lambda: controller.show_frame(SignupPage)).pack(side="left", padx=5)
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        success, result = self.db.login_user(username, password)
        if success:
            user_id, full_name = result
            self.controller.set_user(user_id, full_name)
            messagebox.showinfo("Success", f"Welcome, {full_name}!")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.controller.show_frame(HomePage)
        else:
            messagebox.showerror("Error", "Invalid username or password!")


# ================= SIGNUP PAGE =================
class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        # Header
        header = tk.Frame(self, bg="#06A77D")
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="📝 Create Account", font=("Helvetica", 24, "bold"), 
                bg="#06A77D", fg="white").pack(pady=20)
        
        # Form frame
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        ttk.Label(form_frame, text="Full Name:", font=("Helvetica", 11)).pack(anchor="w", pady=(0, 5))
        self.fullname_entry = ttk.Entry(form_frame, font=("Helvetica", 10), width=30)
        self.fullname_entry.pack(anchor="w", pady=(0, 12))
        
        ttk.Label(form_frame, text="Email:", font=("Helvetica", 11)).pack(anchor="w", pady=(0, 5))
        self.email_entry = ttk.Entry(form_frame, font=("Helvetica", 10), width=30)
        self.email_entry.pack(anchor="w", pady=(0, 12))
        
        ttk.Label(form_frame, text="Username:", font=("Helvetica", 11)).pack(anchor="w", pady=(0, 5))
        self.username_entry = ttk.Entry(form_frame, font=("Helvetica", 10), width=30)
        self.username_entry.pack(anchor="w", pady=(0, 12))
        
        ttk.Label(form_frame, text="Password:", font=("Helvetica", 11)).pack(anchor="w", pady=(0, 5))
        self.password_entry = ttk.Entry(form_frame, show="•", font=("Helvetica", 10), width=30)
        self.password_entry.pack(anchor="w", pady=(0, 12))
        
        ttk.Label(form_frame, text="Confirm Password:", font=("Helvetica", 11)).pack(anchor="w", pady=(0, 5))
        self.confirm_entry = ttk.Entry(form_frame, show="•", font=("Helvetica", 10), width=30)
        self.confirm_entry.pack(anchor="w", pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Sign Up", command=self.signup).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back to Login", 
                  command=lambda: controller.show_frame(LoginPage)).pack(side="left", padx=5)
    
    def signup(self):
        """Handle signup"""
        fullname = self.fullname_entry.get().strip()
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not all([fullname, email, username, password, confirm]):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
        
        success, message = self.db.register_user(username, email, password, fullname)
        if success:
            messagebox.showinfo("Success", message)
            self.clear_fields()
            self.controller.show_frame(LoginPage)
        else:
            messagebox.showerror("Error", message)
    
    def clear_fields(self):
        """Clear all input fields"""
        self.fullname_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_entry.delete(0, tk.END)


# ================= HOME PAGE =================
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        # Header
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x", padx=0, pady=0)
        
        header_content = tk.Frame(header, bg="#2E86AB")
        header_content.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header_content, text="📚 Blog Home", font=("Helvetica", 22, "bold"), 
                bg="#2E86AB", fg="white").pack(side="left")
        
        button_frame = tk.Frame(header, bg="#2E86AB")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ttk.Button(button_frame, text="My Posts", 
                  command=lambda: controller.show_frame(MyPostsPage)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="New Post", 
                  command=lambda: controller.show_frame(BlogPage)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="About", 
                  command=lambda: controller.show_frame(AboutPage)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Contact", 
                  command=lambda: controller.show_frame(ContactPage)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", 
                  command=self.load_posts).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Logout", 
                  command=self.logout).pack(side="right", padx=5)
        
        # Content area
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(self.content_frame, yscrollcommand=scrollbar.set, bg="white", height=400)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        self.posts_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.posts_frame, anchor="nw")
        
        self.load_posts()
    
    def load_posts(self):
        """Load all blog posts"""
        # Clear existing widgets
        for widget in self.posts_frame.winfo_children():
            widget.destroy()
        
        posts = self.db.get_all_posts()
        
        if not posts:
            tk.Label(self.posts_frame, text="No posts yet. Be the first to write!", 
                    font=("Helvetica", 12), bg="white").pack(pady=20)
            return
        
        for post in posts:
            post_id, title, content, category, created_at, username, full_name, image_path = post
            self.create_post_widget(post_id, title, content, category, created_at, username, image_path)
        
        self.posts_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def create_post_widget(self, post_id, title, content, category, created_at, username, image_path=None):
        """Create a post display widget with optional image"""
        post_widget = tk.Frame(self.posts_frame, bg="#f9f9f9", relief="solid", bd=1)
        post_widget.pack(fill="x", pady=10, padx=5)
        
        # Post image (if exists)
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail((600, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(post_widget, image=photo, bg="#f9f9f9")
                img_label.image = photo  # Keep a reference
                img_label.pack(fill="x", padx=0, pady=0)
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Post header
        header = tk.Frame(post_widget, bg="#f9f9f9")
        header.pack(fill="x", padx=15, pady=(10, 5))
        
        tk.Label(header, text=title, font=("Helvetica", 14, "bold"), bg="#f9f9f9").pack(anchor="w")
        
        # Post meta
        meta = tk.Frame(post_widget, bg="#f9f9f9")
        meta.pack(fill="x", padx=15, pady=(0, 10))
        
        tk.Label(meta, text=f"By {username} • {created_at[:10]} • {category}", 
                font=("Helvetica", 9), bg="#f9f9f9", fg="#666").pack(anchor="w")
        
        # Post preview
        preview = content[:200] + "..." if len(content) > 200 else content
        tk.Label(post_widget, text=preview, font=("Helvetica", 10), bg="#f9f9f9", 
                wraplength=600, justify="left").pack(anchor="w", padx=15, pady=(0, 10))
        
        # Read more button
        ttk.Button(post_widget, text="Read More", 
                  command=lambda: self.view_post(post_id)).pack(anchor="w", padx=15, pady=(0, 10))
    
    def view_post(self, post_id):
        """Navigate to post detail page"""
        self.controller.frames[PostDetailPage].set_post_id(post_id)
        self.controller.show_frame(PostDetailPage)
    
    def logout(self):
        """Logout user"""
        self.controller.logout()


# ================= BLOG PAGE (CREATE/EDIT POST) =================
class BlogPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        # Header
        header = tk.Frame(self, bg="#06A77D")
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="✍️ Create New Post", font=("Helvetica", 22, "bold"), 
                bg="#06A77D", fg="white").pack(pady=15)
        
        # Form frame
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Title
        ttk.Label(form_frame, text="Post Title:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.title_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=50)
        self.title_entry.pack(anchor="w", pady=(0, 15), fill="x")
        
        # Category
        ttk.Label(form_frame, text="Category:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, 
                                       values=["Technology", "Lifestyle", "Business", "Health", "Other"],
                                       state="readonly", width=47)
        category_combo.pack(anchor="w", pady=(0, 15), fill="x")
        
        # Image upload
        ttk.Label(form_frame, text="Post Image (Optional):", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.image_path = None
        image_button_frame = ttk.Frame(form_frame)
        image_button_frame.pack(anchor="w", pady=(0, 15), fill="x")
        ttk.Button(image_button_frame, text="Upload Image", command=self.upload_image).pack(side="left", padx=5)
        self.image_label = ttk.Label(image_button_frame, text="No image selected", foreground="gray")
        self.image_label.pack(side="left", padx=5)
        
        # Content
        ttk.Label(form_frame, text="Post Content:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.content_text = scrolledtext.ScrolledText(form_frame, font=("Helvetica", 10), 
                                                       height=12, width=60)
        self.content_text.pack(anchor="w", pady=(0, 15), fill="both", expand=True)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Post", command=self.create_post).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back", 
                  command=lambda: controller.show_frame(HomePage)).pack(side="left", padx=5)
    
    def upload_image(self):
        """Upload image for post"""
        file_path = filedialog.askopenfilename(
            title="Select Post Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*")]
        )
        if file_path:
            self.image_path = file_path
            filename = os.path.basename(file_path)
            self.image_label.config(text=f"✓ {filename}", foreground="green")
    
    def create_post(self):
        """Create a new post"""
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please log in first!")
            return
        
        title = self.title_entry.get().strip()
        category = self.category_var.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        
        if not title or not category or not content:
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        user_id = self.controller.current_user["user_id"]
        success, result = self.db.create_post(user_id, title, content, category, self.image_path)
        
        if success:
            messagebox.showinfo("Success", "Post created successfully!")
            self.title_entry.delete(0, tk.END)
            self.category_var.set("")
            self.content_text.delete("1.0", tk.END)
            self.image_path = None
            self.image_label.config(text="No image selected", foreground="gray")
            self.controller.show_frame(HomePage)
        else:
            messagebox.showerror("Error", f"Failed to create post: {result}")


# ================= MY POSTS PAGE =================
class MyPostsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        # Header
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x", padx=0, pady=0)
        
        header_content = tk.Frame(header, bg="#2E86AB")
        header_content.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header_content, text="📋 My Posts", font=("Helvetica", 22, "bold"), 
                bg="#2E86AB", fg="white").pack(side="left")
        
        ttk.Button(header_content, text="Home", 
                  command=lambda: controller.show_frame(HomePage)).pack(side="right", padx=5)
        ttk.Button(header_content, text="New Post", 
                  command=lambda: controller.show_frame(BlogPage)).pack(side="right", padx=5)
        
        # Content area
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(self.content_frame, yscrollcommand=scrollbar.set, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        self.posts_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.posts_frame, anchor="nw")
        
        self.load_posts()
    
    def load_posts(self):
        """Load user's posts"""
        for widget in self.posts_frame.winfo_children():
            widget.destroy()
        
        if not self.controller.current_user:
            tk.Label(self.posts_frame, text="Please log in to view your posts!", 
                    font=("Helvetica", 12), bg="white").pack(pady=20)
            return
        
        user_id = self.controller.current_user["user_id"]
        posts = self.db.get_user_posts(user_id)
        
        if not posts:
            tk.Label(self.posts_frame, text="You haven't created any posts yet!", 
                    font=("Helvetica", 12), bg="white").pack(pady=20)
            return
        
        for post in posts:
            post_id, title, content, category, created_at = post
            self.create_post_widget(post_id, title, content, category, created_at)
        
        self.posts_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def create_post_widget(self, post_id, title, content, category, created_at):
        """Create post widget with edit/delete options"""
        post_widget = tk.Frame(self.posts_frame, bg="#f9f9f9", relief="solid", bd=1)
        post_widget.pack(fill="x", pady=10, padx=5)
        
        # Post header
        header = tk.Frame(post_widget, bg="#f9f9f9")
        header.pack(fill="x", padx=15, pady=(10, 5))
        
        tk.Label(header, text=title, font=("Helvetica", 14, "bold"), bg="#f9f9f9").pack(anchor="w", side="left")
        
        # Action buttons
        action_frame = tk.Frame(post_widget, bg="#f9f9f9")
        action_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ttk.Button(action_frame, text="Edit", 
                  command=lambda: self.edit_post(post_id)).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", 
                  command=lambda: self.delete_post(post_id)).pack(side="left", padx=3)
        
        # Post meta
        tk.Label(action_frame, text=f"{created_at[:10]} • {category}", 
                font=("Helvetica", 9), bg="#f9f9f9", fg="#666").pack(anchor="w", pady=(5, 0))
    
    def edit_post(self, post_id):
        """Edit a post (implementation needed)"""
        messagebox.showinfo("Edit", "Edit functionality coming soon!")
    
    def delete_post(self, post_id):
        """Delete a post"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this post?"):
            success, message = self.db.delete_post(post_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_posts()
            else:
                messagebox.showerror("Error", message)


# ================= POST DETAIL PAGE =================
class PostDetailPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.post_id = None
        
        # Header
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x", padx=0, pady=0)
        
        header_content = tk.Frame(header, bg="#2E86AB")
        header_content.pack(fill="x", padx=20, pady=15)
        
        ttk.Button(header_content, text="← Back", 
                  command=lambda: controller.show_frame(HomePage)).pack(side="left", padx=5)
        
        # Content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = tk.Canvas(self.content_frame, yscrollcommand=scrollbar.set, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        self.main_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
    
    def set_post_id(self, post_id):
        """Set and load post"""
        self.post_id = post_id
        self.load_post()
    
    def load_post(self):
        """Load post details"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        post = self.db.get_post_details(self.post_id)
        if not post:
            tk.Label(self.main_frame, text="Post not found!", bg="white").pack(pady=20)
            return
        
        post_id, title, content, category, created_at, username, full_name, user_id, image_path = post
        
        # Display image if exists (Canvas with image)
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail((700, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                canvas = tk.Canvas(self.main_frame, bg="white", height=400, highlightthickness=0)
                canvas.pack(fill="x", padx=20, pady=(20, 10))
                canvas.create_image(0, 0, image=photo, anchor="nw")
                canvas.config(height=img.height)
                canvas.image = photo  # Keep a reference
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Title
        tk.Label(self.main_frame, text=title, font=("Helvetica", 18, "bold"), 
                bg="white", wraplength=600, justify="left").pack(anchor="w", padx=20, pady=(20, 10))
        
        # Meta
        tk.Label(self.main_frame, text=f"By {full_name} • {created_at[:10]} • {category}", 
                font=("Helvetica", 10), bg="white", fg="#666").pack(anchor="w", padx=20, pady=(0, 20))
        
        # Content
        tk.Label(self.main_frame, text=content, font=("Helvetica", 11), bg="white", 
                wraplength=600, justify="left").pack(anchor="w", padx=20, pady=(0, 30))
        
        # Comments section
        tk.Label(self.main_frame, text="Comments:", font=("Helvetica", 12, "bold"), 
                bg="white").pack(anchor="w", padx=20, pady=(0, 10))
        
        # Add comment
        if self.controller.current_user:
            comment_frame = tk.Frame(self.main_frame, bg="white")
            comment_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            tk.Label(comment_frame, text="Your comment:", font=("Helvetica", 10), bg="white").pack(anchor="w")
            self.comment_entry = scrolledtext.ScrolledText(comment_frame, font=("Helvetica", 10), height=4, width=60)
            self.comment_entry.pack(anchor="w", pady=(5, 10))
            
            ttk.Button(comment_frame, text="Post Comment", 
                      command=lambda: self.add_comment()).pack(anchor="w")
        
        # Display comments
        comments = self.db.get_post_comments(self.post_id)
        if comments:
            for comment in comments:
                comment_id, comment_text, comment_username, comment_date = comment
                self.display_comment(comment_text, comment_username, comment_date)
        else:
            tk.Label(self.main_frame, text="No comments yet. Be the first!", 
                    font=("Helvetica", 10), bg="white", fg="#999").pack(anchor="w", padx=20)
        
        self.main_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def display_comment(self, comment_text, username, date):
        """Display a comment"""
        comment_widget = tk.Frame(self.main_frame, bg="#f9f9f9")
        comment_widget.pack(fill="x", padx=20, pady=10)
        
        tk.Label(comment_widget, text=f"{username} • {date[:10]}", 
                font=("Helvetica", 9, "bold"), bg="#f9f9f9").pack(anchor="w", padx=10, pady=(5, 0))
        
        tk.Label(comment_widget, text=comment_text, font=("Helvetica", 10), bg="#f9f9f9", 
                wraplength=550, justify="left").pack(anchor="w", padx=10, pady=(0, 5))
    
    def add_comment(self):
        """Add comment to post"""
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please log in to comment!")
            return
        
        comment_text = self.comment_entry.get("1.0", tk.END).strip()
        if not comment_text:
            messagebox.showerror("Error", "Comment cannot be empty!")
            return
        
        user_id = self.controller.current_user["user_id"]
        success, message = self.db.add_comment(self.post_id, user_id, comment_text)
        
        if success:
            messagebox.showinfo("Success", message)
            self.comment_entry.delete("1.0", tk.END)
            self.load_post()
        else:
            messagebox.showerror("Error", message)


# ================= ABOUT PAGE =================
class AboutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        header = tk.Frame(self, bg="#06A77D")
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="ℹ️ About Us", font=("Helvetica", 22, "bold"), 
                bg="#06A77D", fg="white").pack(pady=20)
        
        # Content
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=40, pady=30)
        
        about_text = """
Welcome to Advanced Blog Platform!

Our mission is to provide a simple yet powerful platform for bloggers and writers 
to share their thoughts, ideas, and experiences with the world.

Features:
• Create and publish blog posts
• Organize posts by categories
• Read and comment on other users' posts
• User-friendly interface built with Python Tkinter
• Secure user authentication
• SQLite database for reliable data storage

Whether you're a professional writer, a hobby blogger, or someone with a story to tell, 
our platform makes it easy to get started.

Join our community today and start sharing your voice!

Version: 1.0
Built with Python & Tkinter
        """
        
        tk.Label(content, text=about_text, font=("Helvetica", 11), bg="#f0f0f0", 
                justify="left", wraplength=600).pack(anchor="w", pady=20)
        
        # Back button
        ttk.Button(content, text="Back to Home", 
                  command=lambda: controller.show_frame(HomePage)).pack(anchor="w", pady=10)


# ================= CONTACT PAGE =================
class ContactPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x", padx=0, pady=0)
        tk.Label(header, text="📧 Contact Us", font=("Helvetica", 22, "bold"), 
                bg="#2E86AB", fg="white").pack(pady=20)
        
        # Form frame
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        ttk.Label(form_frame, text="Name:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.name_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=50)
        self.name_entry.pack(anchor="w", pady=(0, 15), fill="x")
        
        ttk.Label(form_frame, text="Email:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.email_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=50)
        self.email_entry.pack(anchor="w", pady=(0, 15), fill="x")
        
        ttk.Label(form_frame, text="Subject:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.subject_entry = ttk.Entry(form_frame, font=("Helvetica", 11), width=50)
        self.subject_entry.pack(anchor="w", pady=(0, 15), fill="x")
        
        ttk.Label(form_frame, text="Message:", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.message_text = scrolledtext.ScrolledText(form_frame, font=("Helvetica", 10), 
                                                       height=10, width=60)
        self.message_text.pack(anchor="w", pady=(0, 15), fill="both", expand=True)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(button_frame, text="Send Message", command=self.send_message).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Back to Home", 
                  command=lambda: controller.show_frame(HomePage)).pack(side="left", padx=5)
    
    def send_message(self):
        """Handle contact form submission"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        subject = self.subject_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        if not all([name, email, subject, message]):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        messagebox.showinfo("Success", f"Thank you, {name}! Your message has been sent.")
        
        # Clear fields
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.message_text.delete("1.0", tk.END)


# ================= GALLERY PAGE (WITH LISTBOX) =================
class GalleryPage(tk.Frame):
    """Gallery page showcasing posts with images using Listbox widget"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        # Header
        header = tk.Frame(self, bg="#2E86AB")
        header.pack(fill="x", padx=0, pady=0)
        
        header_content = tk.Frame(header, bg="#2E86AB")
        header_content.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header_content, text="🖼️ Image Gallery", font=("Helvetica", 22, "bold"), 
                bg="#2E86AB", fg="white").pack(side="left")
        
        ttk.Button(header_content, text="Home", 
                  command=lambda: controller.show_frame(HomePage)).pack(side="right", padx=5)
        
        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Listbox for selecting posts with images
        ttk.Label(content_frame, text="Posts with Images:", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 5))
        
        listbox_frame = ttk.Frame(content_frame)
        listbox_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=("Helvetica", 10), height=10)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        
        # Image display area (Canvas)
        tk.Label(content_frame, text="Preview:", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.canvas = tk.Canvas(content_frame, bg="white", height=300, relief="sunken", bd=2)
        self.canvas.pack(fill="both", expand=True, pady=(0, 15))
        
        # Button frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="View Full Post", 
                  command=self.view_selected_post).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", 
                  command=self.load_gallery).pack(side="left", padx=5)
        
        self.load_gallery()
    
    def load_gallery(self):
        """Load posts with images into listbox"""
        self.listbox.delete(0, tk.END)
        self.post_data = []
        
        posts = self.db.get_all_posts()
        for post in posts:
            post_id, title, content, category, created_at, username, full_name, image_path = post
            if image_path and os.path.exists(image_path):
                self.listbox.insert(tk.END, f"{title} - by {username}")
                self.post_data.append((post_id, title, image_path))
        
        if self.listbox.size() == 0:
            self.listbox.insert(tk.END, "No posts with images yet!")
    
    def on_listbox_select(self, event):
        """Handle listbox selection"""
        selection = self.listbox.curselection()
        if selection and len(self.post_data) > 0:
            index = selection[0]
            if index < len(self.post_data):
                post_id, title, image_path = self.post_data[index]
                self.display_image(image_path)
    
    def display_image(self, image_path):
        """Display image on canvas"""
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img.thumbnail((500, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.canvas.delete("all")
                self.canvas.create_image(250, 150, image=photo)
                self.canvas.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Cannot display image: {e}")
    
    def view_selected_post(self):
        """View the selected post in detail"""
        selection = self.listbox.curselection()
        if selection and len(self.post_data) > 0:
            index = selection[0]
            if index < len(self.post_data):
                post_id, title, image_path = self.post_data[index]
                self.controller.frames[PostDetailPage].set_post_id(post_id)
                self.controller.show_frame(PostDetailPage)


# ================= POSTS TREEVIEW PAGE =================
class PostsTreeviewPage(tk.Frame):
    """Posts page with Treeview widget for hierarchical display"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        # Header
        header = tk.Frame(self, bg="#06A77D")
        header.pack(fill="x", padx=0, pady=0)
        
        header_content = tk.Frame(header, bg="#06A77D")
        header_content.pack(fill="x", padx=20, pady=15)
        
        tk.Label(header_content, text="🌳 Posts Tree View", font=("Helvetica", 22, "bold"), 
                bg="#06A77D", fg="white").pack(side="left")
        
        ttk.Button(header_content, text="Home", 
                  command=lambda: controller.show_frame(HomePage)).pack(side="right", padx=5)
        
        # Content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Treeview for hierarchical post display
        tk.Label(content_frame, text="Posts Organized by Category:", font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        treeview_frame = ttk.Frame(content_frame)
        treeview_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        scrollbar = ttk.Scrollbar(treeview_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create Treeview with columns
        self.tree = ttk.Treeview(treeview_frame, yscrollcommand=scrollbar.set, height=20)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Define columns
        self.tree['columns'] = ('author', 'date')
        self.tree.column("#0", width=300, minwidth=200)
        self.tree.column('author', width=150, minwidth=100)
        self.tree.column('date', width=150, minwidth=100)
        
        # Create headings
        self.tree.heading('#0', text='Title', anchor='w')
        self.tree.heading('author', text='Author', anchor='w')
        self.tree.heading('date', text='Date', anchor='w')
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_treeview_double_click)
        
        # Button frame
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Expand All", 
                  command=self.expand_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Collapse All", 
                  command=self.collapse_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", 
                  command=self.load_treeview).pack(side="left", padx=5)
        
        self.load_treeview()
    
    def load_treeview(self):
        """Load posts into treeview organized by category"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        posts = self.db.get_all_posts()
        
        # Group posts by category
        categories = {}
        for post in posts:
            post_id, title, content, category, created_at, username, full_name, image_path = post
            if category not in categories:
                categories[category] = []
            categories[category].append((post_id, title, username, created_at[:10]))
        
        # Add to treeview
        for category, posts_in_cat in sorted(categories.items()):
            cat_id = self.tree.insert("", "end", text=category, open=False)
            for post_id, title, username, date in posts_in_cat:
                self.tree.insert(cat_id, "end", text=title, values=(username, date))
        
        if not categories:
            self.tree.insert("", "end", text="No posts available")
    
    def on_treeview_double_click(self, event):
        """Handle double-click on treeview item"""
        item = self.tree.selection()
        if item:
            # Get parent to check if it's a post (has a parent category)
            parent = self.tree.parent(item[0])
            if parent:
                # This is a post, find its post_id
                posts = self.db.get_all_posts()
                selected_text = self.tree.item(item[0])['text']
                for post in posts:
                    post_id, title, content, category, created_at, username, full_name, image_path = post
                    if title == selected_text:
                        self.controller.frames[PostDetailPage].set_post_id(post_id)
                        self.controller.show_frame(PostDetailPage)
                        break
    
    def expand_all(self):
        """Expand all items in treeview"""
        self._expand_tree(self.tree.get_children()[0] if self.tree.get_children() else "")
    
    def collapse_all(self):
        """Collapse all items in treeview"""
        self._collapse_tree(self.tree.get_children()[0] if self.tree.get_children() else "")
    
    def _expand_tree(self, item):
        """Recursively expand tree items"""
        if item:
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                self._expand_tree(child)
    
    def _collapse_tree(self, item):
        """Recursively collapse tree items"""
        if item:
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                self._collapse_tree(child)


# ================= MAIN ENTRY POINT =================
if __name__ == "__main__":
    app = BlogApp()
    app.mainloop()
