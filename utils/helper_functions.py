"""
Utility functions for Neighborhood Complaint & Feedback System
Provides common helper functions for validation, messaging, and UI operations
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import re
from typing import Optional, List, Tuple
from datetime import datetime

class ValidationHelper:
    """Helper class for input validation"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format
        
        Args:
            email (str): Email to validate
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if not email or not email.strip():
            return False, "Email is required"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email.strip()):
            return False, "Invalid email format"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password (str): Password to validate
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Validate name format
        
        Args:
            name (str): Name to validate
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Name is required"
        
        if len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        if not re.match(r'^[a-zA-Z\s]+$', name.strip()):
            return False, "Name can only contain letters and spaces"
        
        return True, ""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if not phone or not phone.strip():
            return True, ""  # Phone is optional
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        if len(digits_only) < 10:
            return False, "Phone number must have at least 10 digits"
        
        if len(digits_only) > 15:
            return False, "Phone number cannot have more than 15 digits"
        
        return True, ""
    
    @staticmethod
    def validate_required_field(value: str, field_name: str) -> Tuple[bool, str]:
        """
        Validate required field
        
        Args:
            value (str): Value to validate
            field_name (str): Name of the field
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if not value or not value.strip():
            return False, f"{field_name} is required"
        
        return True, ""
    
    @staticmethod
    def validate_rating(rating: int) -> Tuple[bool, str]:
        """
        Validate rating value
        
        Args:
            rating (int): Rating to validate
            
        Returns:
            Tuple: (is_valid, error_message)
        """
        if not isinstance(rating, int):
            return False, "Rating must be a number"
        
        if rating < 1 or rating > 5:
            return False, "Rating must be between 1 and 5"
        
        return True, ""

class MessageHelper:
    """Helper class for displaying messages"""
    
    @staticmethod
    def show_success(message: str, title: str = "Success"):
        """Show success message"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_error(message: str, title: str = "Error"):
        """Show error message"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_warning(message: str, title: str = "Warning"):
        """Show warning message"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_info(message: str, title: str = "Information"):
        """Show information message"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def ask_confirmation(message: str, title: str = "Confirm") -> bool:
        """Ask for user confirmation"""
        return messagebox.askyesno(title, message)
    
    @staticmethod
    def ask_question(message: str, title: str = "Question") -> bool:
        """Ask a yes/no question"""
        return messagebox.askyesno(title, message)

class FileHelper:
    """Helper class for file operations"""
    
    @staticmethod
    def select_image_file() -> Optional[str]:
        """
        Open file dialog to select image file
        
        Returns:
            Optional[str]: Selected file path or None
        """
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=filetypes
        )
        
        return filename if filename else None
    
    @staticmethod
    def save_file_dialog(title: str = "Save File", 
                        filetypes: List[Tuple[str, str]] = None,
                        default_extension: str = None) -> Optional[str]:
        """
        Open save file dialog
        
        Args:
            title (str): Dialog title
            filetypes (List[Tuple]): File type filters
            default_extension (str): Default file extension
            
        Returns:
            Optional[str]: Selected file path or None
        """
        if filetypes is None:
            filetypes = [("All files", "*.*")]
        
        filename = filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            defaultextension=default_extension
        )
        
        return filename if filename else None
    
    @staticmethod
    def is_valid_image_file(filepath: str) -> bool:
        """
        Check if file is a valid image
        
        Args:
            filepath (str): Path to file
            
        Returns:
            bool: True if valid image file
        """
        if not os.path.exists(filepath):
            return False
        
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        _, ext = os.path.splitext(filepath.lower())
        
        return ext in valid_extensions
    
    @staticmethod
    def get_file_size_mb(filepath: str) -> float:
        """
        Get file size in MB
        
        Args:
            filepath (str): Path to file
            
        Returns:
            float: File size in MB
        """
        try:
            size_bytes = os.path.getsize(filepath)
            return size_bytes / (1024 * 1024)
        except OSError:
            return 0.0

class DateHelper:
    """Helper class for date operations"""
    
    @staticmethod
    def format_datetime(dt_string: str, format_type: str = "display") -> str:
        """
        Format datetime string for display
        
        Args:
            dt_string (str): Datetime string
            format_type (str): Format type ("display", "short", "time")
            
        Returns:
            str: Formatted datetime string
        """
        try:
            if not dt_string:
                return "N/A"
            
            # Parse the datetime string
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            
            if format_type == "display":
                return dt.strftime("%B %d, %Y at %I:%M %p")
            elif format_type == "short":
                return dt.strftime("%Y-%m-%d")
            elif format_type == "time":
                return dt.strftime("%I:%M %p")
            else:
                return dt.strftime("%Y-%m-%d %H:%M:%S")
                
        except (ValueError, TypeError):
            return "Invalid Date"
    
    @staticmethod
    def get_time_ago(dt_string: str) -> str:
        """
        Get human-readable time ago string
        
        Args:
            dt_string (str): Datetime string
            
        Returns:
            str: Time ago string
        """
        try:
            if not dt_string:
                return "Unknown"
            
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            diff = now - dt
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
                
        except (ValueError, TypeError):
            return "Unknown"

class UIHelper:
    """Helper class for UI operations"""
    
    @staticmethod
    def center_window(window: tk.Tk, width: int = 800, height: int = 600):
        """
        Center window on screen
        
        Args:
            window (tk.Tk): Tkinter window
            width (int): Window width
            height (int): Window height
        """
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def create_scrollable_frame(parent: tk.Widget) -> Tuple[tk.Frame, tk.Scrollbar]:
        """
        Create a scrollable frame
        
        Args:
            parent (tk.Widget): Parent widget
            
        Returns:
            Tuple: (frame, scrollbar)
        """
        # Create main frame
        main_frame = tk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas
        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create scrollbar
        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Update scroll region
        def _configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        
        return scrollable_frame, scrollbar
    
    @staticmethod
    def create_tooltip(widget: tk.Widget, text: str):
        """
        Create tooltip for widget
        
        Args:
            widget (tk.Widget): Widget to add tooltip to
            text (str): Tooltip text
        """
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="lightyellow",
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

class StatusHelper:
    """Helper class for status operations"""
    
    STATUS_COLORS = {
        'Pending': '#FFA500',      # Orange
        'In Progress': '#007BFF',   # Blue
        'Resolved': '#28A745',      # Green
        'Closed': '#6C757D'         # Gray
    }
    
    PRIORITY_COLORS = {
        'Low': '#28A745',          # Green
        'Medium': '#FFC107',       # Yellow
        'High': '#FD7E14',         # Orange
        'Urgent': '#DC3545'        # Red
    }
    
    @staticmethod
    def get_status_color(status: str) -> str:
        """Get color for status"""
        return StatusHelper.STATUS_COLORS.get(status, '#6C757D')
    
    @staticmethod
    def get_priority_color(priority: str) -> str:
        """Get color for priority"""
        return StatusHelper.PRIORITY_COLORS.get(priority, '#6C757D')
    
    @staticmethod
    def get_rating_color(rating: int) -> str:
        """Get color for rating"""
        if rating >= 4:
            return '#28A745'  # Green
        elif rating >= 3:
            return '#FFC107'  # Yellow
        else:
            return '#DC3545'  # Red

# Global helper instances
validation = ValidationHelper()
messages = MessageHelper()
files = FileHelper()
dates = DateHelper()
ui = UIHelper()
status = StatusHelper()

