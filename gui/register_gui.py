"""
Registration GUI module for Neighborhood Complaint & Feedback System
Provides user registration interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
from backend.auth import register_user
from utils.helper_functions import validation, messages, ui

class RegisterWindow:
    """Registration window class"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        
    def show(self):
        """Show registration window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Neighborhood Complaint System - Register")
        self.window.geometry("450x600")
        self.window.resizable(False, False)
        
        # Center window
        ui.center_window(self.window, 450, 600)
        
        # Configure window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        
        # Focus on name entry
        self.name_entry.focus()
        
        # Start main loop if this is the main window
        if not self.parent:
            self.window.mainloop()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main frame with scrollbar
        main_frame = tk.Frame(self.window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable frame
        scrollable_frame, scrollbar = ui.create_scrollable_frame(main_frame)
        
        # Content frame
        content_frame = tk.Frame(scrollable_frame, bg='#f8f9fa', padx=40, pady=30)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text="Create New Account",
            font=("Arial", 18, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            content_frame,
            text="Join the neighborhood complaint system",
            font=("Arial", 12),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Registration form frame
        form_frame = tk.Frame(content_frame, bg='#f8f9fa')
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Name field
        name_label = tk.Label(
            form_frame,
            text="Full Name: *",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.name_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=40,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.name_entry.pack(pady=(0, 15))
        
        # Email field
        email_label = tk.Label(
            form_frame,
            text="Email Address: *",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        email_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.email_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=40,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.email_entry.pack(pady=(0, 15))
        
        # Password field
        password_label = tk.Label(
            form_frame,
            text="Password: *",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=40,
            show="*",
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.password_entry.pack(pady=(0, 5))
        
        # Password requirements
        password_help = tk.Label(
            form_frame,
            text="Password must be at least 6 characters with letters and numbers",
            font=("Arial", 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        password_help.pack(anchor=tk.W, pady=(0, 15))
        
        # Confirm Password field
        confirm_password_label = tk.Label(
            form_frame,
            text="Confirm Password: *",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        confirm_password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.confirm_password_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=40,
            show="*",
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.confirm_password_entry.pack(pady=(0, 15))
        
        # Phone field
        phone_label = tk.Label(
            form_frame,
            text="Phone Number:",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        phone_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.phone_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=40,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.phone_entry.pack(pady=(0, 15))
        
        # Address field
        address_label = tk.Label(
            form_frame,
            text="Address:",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        address_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.address_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=40,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.address_entry.pack(pady=(0, 20))
        
        # Register button
        self.register_button = tk.Button(
            form_frame,
            text="Create Account",
            font=("Arial", 11, "bold"),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2',
            command=self.handle_register
        )
        self.register_button.pack(pady=(0, 15))
        
        # Bind Enter key to register
        self.window.bind('<Return>', lambda e: self.handle_register())
        
        # Login link
        login_frame = tk.Frame(content_frame, bg='#f8f9fa')
        login_frame.pack(fill=tk.X)
        
        login_label = tk.Label(
            login_frame,
            text="Already have an account?",
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        login_label.pack(side=tk.LEFT)
        
        self.login_link = tk.Label(
            login_frame,
            text="Login here",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#3498db',
            cursor='hand2'
        )
        self.login_link.pack(side=tk.LEFT, padx=(5, 0))
        self.login_link.bind("<Button-1>", lambda e: self.show_login())
        
        # Required fields note
        required_note = tk.Label(
            content_frame,
            text="* Required fields",
            font=("Arial", 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        required_note.pack(pady=(20, 0))
    
    def handle_register(self):
        """Handle registration button click"""
        # Get form data
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()
        
        # Validate inputs
        is_valid_name, name_error = validation.validate_name(name)
        if not is_valid_name:
            messages.show_error(name_error)
            self.name_entry.focus()
            return
        
        is_valid_email, email_error = validation.validate_email(email)
        if not is_valid_email:
            messages.show_error(email_error)
            self.email_entry.focus()
            return
        
        is_valid_password, password_error = validation.validate_password(password)
        if not is_valid_password:
            messages.show_error(password_error)
            self.password_entry.focus()
            return
        
        if password != confirm_password:
            messages.show_error("Passwords do not match")
            self.confirm_password_entry.focus()
            return
        
        is_valid_phone, phone_error = validation.validate_phone(phone)
        if not is_valid_phone:
            messages.show_error(phone_error)
            self.phone_entry.focus()
            return
        
        # Disable register button during processing
        self.register_button.config(state=tk.DISABLED, text="Creating Account...")
        self.window.update()
        
        try:
            # Attempt registration
            success, message = register_user(name, email, password, phone, address)
            
            if success:
                messages.show_success("Account created successfully! You can now login.")
                self.window.destroy()
            else:
                messages.show_error(message)
                
        except Exception as e:
            messages.show_error(f"Registration failed: {str(e)}")
        finally:
            # Re-enable register button
            self.register_button.config(state=tk.NORMAL, text="Create Account")
    
    def show_login(self):
        """Show login window"""
        self.window.destroy()
        # The parent window (login) will be shown automatically
    
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
    register_window = RegisterWindow()
    register_window.show()

if __name__ == "__main__":
    main()

