"""
Login GUI module for Neighborhood Complaint & Feedback System
Provides user login interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from backend.auth import login_user, get_current_user
from utils.helper_functions import validation, messages, ui
from gui.register_gui import RegisterWindow
from gui.user_dashboard import UserDashboard
from gui.admin_dashboard import AdminDashboard

class LoginWindow:
    """Login window class"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.register_window = None
        
    def show(self):
        """Show login window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Neighborhood Complaint System - Login")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Center window
        ui.center_window(self.window, 400, 500)
        
        # Configure window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        
        # Focus on email entry
        self.email_entry.focus()
        
        # Start main loop if this is the main window
        if not self.parent:
            self.window.mainloop()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#f8f9fa', padx=40, pady=40)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Neighborhood Complaint System",
            font=("Arial", 18, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            main_frame,
            text="Login to your account",
            font=("Arial", 12),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Login form frame
        form_frame = tk.Frame(main_frame, bg='#f8f9fa')
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Email field
        email_label = tk.Label(
            form_frame,
            text="Email Address:",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        email_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.email_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=35,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.email_entry.pack(pady=(0, 15))
        
        # Password field
        password_label = tk.Label(
            form_frame,
            text="Password:",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=35,
            show="*",
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.password_entry.pack(pady=(0, 20))
        
        # Login button
        self.login_button = tk.Button(
            form_frame,
            text="Login",
            font=("Arial", 11, "bold"),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2',
            command=self.handle_login
        )
        self.login_button.pack(pady=(0, 15))
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.handle_login())
        
        # Register link
        register_frame = tk.Frame(main_frame, bg='#f8f9fa')
        register_frame.pack(fill=tk.X)
        
        register_label = tk.Label(
            register_frame,
            text="Don't have an account?",
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        register_label.pack(side=tk.LEFT)
        
        self.register_link = tk.Label(
            register_frame,
            text="Register here",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#3498db',
            cursor='hand2'
        )
        self.register_link.pack(side=tk.LEFT, padx=(5, 0))
        self.register_link.bind("<Button-1>", lambda e: self.show_register())
        
        # Demo credentials info
        demo_frame = tk.Frame(main_frame, bg='#f8f9fa')
        demo_frame.pack(fill=tk.X, pady=(30, 0))
        
        demo_label = tk.Label(
            demo_frame,
            text="Demo Credentials:",
            font=("Arial", 9, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        demo_label.pack(anchor=tk.W)
        
        admin_label = tk.Label(
            demo_frame,
            text="Admin: admin@neighborhood.com / admin123",
            font=("Arial", 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        admin_label.pack(anchor=tk.W, pady=(2, 0))
        
        user_label = tk.Label(
            demo_frame,
            text="User: Register a new account",
            font=("Arial", 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        user_label.pack(anchor=tk.W, pady=(2, 0))
    
    def handle_login(self):
        """Handle login button click"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate inputs
        is_valid_email, email_error = validation.validate_email(email)
        if not is_valid_email:
            messages.show_error(email_error)
            self.email_entry.focus()
            return
        
        if not password:
            messages.show_error("Password is required")
            self.password_entry.focus()
            return
        
        # Disable login button during processing
        self.login_button.config(state=tk.DISABLED, text="Logging in...")
        self.window.update()
        
        try:
            # Attempt login
            success, message, user_data = login_user(email, password)
            
            if success:
                messages.show_success("Login successful!")
                self.window.destroy()
                
                # Open appropriate dashboard based on user role
                if user_data['role'].lower() == 'admin':
                    admin_dashboard = AdminDashboard()
                    admin_dashboard.show()
                else:
                    user_dashboard = UserDashboard()
                    user_dashboard.show()
            else:
                messages.show_error(message)
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
                
        except Exception as e:
            messages.show_error(f"Login failed: {str(e)}")
        finally:
            # Re-enable login button
            self.login_button.config(state=tk.NORMAL, text="Login")
    
    def show_register(self):
        """Show registration window"""
        if not self.register_window or not self.register_window.window.winfo_exists():
            self.register_window = RegisterWindow(self.window)
            self.register_window.show()
        else:
            self.register_window.window.lift()
    
    def on_closing(self):
        """Handle window closing"""
        if not self.parent:
            # If this is the main window, exit the application
            self.window.quit()
        else:
            # If this is a child window, just destroy it
            self.window.destroy()

def main():
    """Main function for testing"""
    login_window = LoginWindow()
    login_window.show()

if __name__ == "__main__":
    main()

