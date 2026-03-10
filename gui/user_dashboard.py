"""
User Dashboard GUI module for Neighborhood Complaint & Feedback System
Provides main user interface with navigation and complaint management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from backend.auth import get_current_user, logout_user
from backend.complaint_manager import get_user_complaints, get_categories
from backend.feedback_manager import get_user_feedback
from utils.helper_functions import validation, messages, ui, dates, status
from gui.complaint_form import ComplaintFormWindow
from gui.status_view import StatusViewWindow
from gui.feedback_form import FeedbackFormWindow

class UserDashboard:
    """User dashboard class"""
    
    def __init__(self):
        self.window = None
        self.current_user = None
        self.complaint_form_window = None
        self.status_view_window = None
        self.feedback_form_window = None
        
    def show(self):
        """Show user dashboard"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        # Get current user
        self.current_user = get_current_user()
        if not self.current_user:
            messages.show_error("No user logged in")
            return
        
        self.window = tk.Tk()
        self.window.title(f"Neighborhood Complaint System - Welcome {self.current_user['name']}")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Center window
        ui.center_window(self.window, 1000, 700)
        
        # Configure window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        self.refresh_data()
        
        # Start main loop
        self.window.mainloop()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main container
        main_container = tk.Frame(self.window, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        header_frame = tk.Frame(main_container, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg='#2c3e50')
        header_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Welcome message
        welcome_label = tk.Label(
            header_content,
            text=f"Welcome, {self.current_user['name']}",
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        welcome_label.pack(side=tk.LEFT)
        
        # User info
        user_info = tk.Label(
            header_content,
            text=f"Email: {self.current_user['email']} | Role: {self.current_user['role'].title()}",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        user_info.pack(side=tk.LEFT, padx=(20, 0))
        
        # Logout button
        logout_button = tk.Button(
            header_content,
            text="Logout",
            font=("Arial", 10, "bold"),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.handle_logout
        )
        logout_button.pack(side=tk.RIGHT)
        
        # Main content frame
        content_frame = tk.Frame(main_container, bg='#f8f9fa')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Navigation
        left_panel = tk.Frame(content_frame, bg='white', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Navigation title
        nav_title = tk.Label(
            left_panel,
            text="Navigation",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        nav_title.pack(pady=(20, 10))
        
        # Navigation buttons
        nav_buttons_frame = tk.Frame(left_panel, bg='white')
        nav_buttons_frame.pack(fill=tk.X, padx=20)
        
        # New Complaint button
        self.new_complaint_btn = tk.Button(
            nav_buttons_frame,
            text="📝 New Complaint",
            font=("Arial", 11, "bold"),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_complaint_form
        )
        self.new_complaint_btn.pack(fill=tk.X, pady=(0, 10))
        
        # My Complaints button
        self.my_complaints_btn = tk.Button(
            nav_buttons_frame,
            text="📋 My Complaints",
            font=("Arial", 11, "bold"),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_my_complaints
        )
        self.my_complaints_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Track Status button
        self.track_status_btn = tk.Button(
            nav_buttons_frame,
            text="🔍 Track Status",
            font=("Arial", 11, "bold"),
            bg='#f39c12',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_status_tracking
        )
        self.track_status_btn.pack(fill=tk.X, pady=(0, 10))
        
        # My Feedback button
        self.my_feedback_btn = tk.Button(
            nav_buttons_frame,
            text="⭐ My Feedback",
            font=("Arial", 11, "bold"),
            bg='#9b59b6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_my_feedback
        )
        self.my_feedback_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(
            nav_buttons_frame,
            text="🔄 Refresh",
            font=("Arial", 10),
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.refresh_data
        )
        refresh_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Right panel - Content area
        right_panel = tk.Frame(content_frame, bg='white')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content title
        self.content_title = tk.Label(
            right_panel,
            text="Dashboard Overview",
            font=("Arial", 16, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        self.content_title.pack(pady=(20, 10))
        
        # Content area with scrollbar
        self.content_frame, self.content_scrollbar = ui.create_scrollable_frame(right_panel)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Initialize with dashboard overview
        self.show_dashboard_overview()
    
    def show_dashboard_overview(self):
        """Show dashboard overview"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.content_title.config(text="Dashboard Overview")
        
        # Statistics frame
        stats_frame = tk.Frame(self.content_frame, bg='white')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Get user statistics
        user_complaints = get_user_complaints(self.current_user['id'])
        user_feedback = get_user_feedback(self.current_user['id'])
        
        total_complaints = len(user_complaints)
        pending_complaints = len([c for c in user_complaints if c['status'] == 'Pending'])
        in_progress_complaints = len([c for c in user_complaints if c['status'] == 'In Progress'])
        resolved_complaints = len([c for c in user_complaints if c['status'] == 'Resolved'])
        total_feedback = len(user_feedback)
        
        # Statistics cards
        stats_cards_frame = tk.Frame(stats_frame, bg='white')
        stats_cards_frame.pack(fill=tk.X)
        
        # Total Complaints card
        total_card = tk.Frame(stats_cards_frame, bg='#3498db', relief=tk.RAISED, bd=1)
        total_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(total_card, text="Total Complaints", font=("Arial", 10, "bold"), 
                bg='#3498db', fg='white').pack(pady=(10, 5))
        tk.Label(total_card, text=str(total_complaints), font=("Arial", 24, "bold"), 
                bg='#3498db', fg='white').pack(pady=(0, 10))
        
        # Pending card
        pending_card = tk.Frame(stats_cards_frame, bg='#f39c12', relief=tk.RAISED, bd=1)
        pending_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(pending_card, text="Pending", font=("Arial", 10, "bold"), 
                bg='#f39c12', fg='white').pack(pady=(10, 5))
        tk.Label(pending_card, text=str(pending_complaints), font=("Arial", 24, "bold"), 
                bg='#f39c12', fg='white').pack(pady=(0, 10))
        
        # In Progress card
        progress_card = tk.Frame(stats_cards_frame, bg='#17a2b8', relief=tk.RAISED, bd=1)
        progress_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(progress_card, text="In Progress", font=("Arial", 10, "bold"), 
                bg='#17a2b8', fg='white').pack(pady=(10, 5))
        tk.Label(progress_card, text=str(in_progress_complaints), font=("Arial", 24, "bold"), 
                bg='#17a2b8', fg='white').pack(pady=(0, 10))
        
        # Resolved card
        resolved_card = tk.Frame(stats_cards_frame, bg='#28a745', relief=tk.RAISED, bd=1)
        resolved_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(resolved_card, text="Resolved", font=("Arial", 10, "bold"), 
                bg='#28a745', fg='white').pack(pady=(10, 5))
        tk.Label(resolved_card, text=str(resolved_complaints), font=("Arial", 24, "bold"), 
                bg='#28a745', fg='white').pack(pady=(0, 10))
        
        # Recent complaints section
        recent_frame = tk.Frame(self.content_frame, bg='white')
        recent_frame.pack(fill=tk.BOTH, expand=True)
        
        recent_title = tk.Label(
            recent_frame,
            text="Recent Complaints",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        recent_title.pack(anchor=tk.W, pady=(0, 10))
        
        if user_complaints:
            # Show recent complaints
            for complaint in user_complaints[:5]:  # Show last 5
                self.create_complaint_card(recent_frame, complaint)
        else:
            no_complaints_label = tk.Label(
                recent_frame,
                text="No complaints submitted yet. Click 'New Complaint' to get started!",
                font=("Arial", 12),
                bg='white',
                fg='#7f8c8d'
            )
            no_complaints_label.pack(pady=20)
    
    def create_complaint_card(self, parent, complaint):
        """Create a complaint card widget"""
        card_frame = tk.Frame(parent, bg='#f8f9fa', relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Card content
        content_frame = tk.Frame(card_frame, bg='#f8f9fa')
        content_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Title and status
        title_frame = tk.Frame(content_frame, bg='#f8f9fa')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text=complaint['title'],
            font=("Arial", 12, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(side=tk.LEFT)
        
        # Status badge
        status_color = status.get_status_color(complaint['status'])
        status_label = tk.Label(
            title_frame,
            text=complaint['status'],
            font=("Arial", 9, "bold"),
            bg=status_color,
            fg='white',
            padx=8,
            pady=2
        )
        status_label.pack(side=tk.RIGHT)
        
        # Category and date
        info_frame = tk.Frame(content_frame, bg='#f8f9fa')
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        category_label = tk.Label(
            info_frame,
            text=f"Category: {complaint['category']}",
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        category_label.pack(side=tk.LEFT)
        
        date_label = tk.Label(
            info_frame,
            text=f"Submitted: {dates.format_datetime(complaint['created_at'])}",
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        date_label.pack(side=tk.RIGHT)
        
        # Description preview
        description = complaint['description']
        if len(description) > 100:
            description = description[:100] + "..."
        
        desc_label = tk.Label(
            content_frame,
            text=description,
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#2c3e50',
            wraplength=600,
            justify=tk.LEFT
        )
        desc_label.pack(anchor=tk.W, pady=(5, 0))
    
    def show_my_complaints(self):
        """Show user's complaints"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.content_title.config(text="My Complaints")
        
        # Get user complaints
        user_complaints = get_user_complaints(self.current_user['id'])
        
        if not user_complaints:
            no_complaints_label = tk.Label(
                self.content_frame,
                text="No complaints found. Click 'New Complaint' to submit your first complaint!",
                font=("Arial", 12),
                bg='white',
                fg='#7f8c8d'
            )
            no_complaints_label.pack(pady=50)
            return
        
        # Complaints list
        for complaint in user_complaints:
            self.create_complaint_card(self.content_frame, complaint)
    
    def show_my_feedback(self):
        """Show user's feedback"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.content_title.config(text="My Feedback")
        
        # Get user feedback
        user_feedback = get_user_feedback(self.current_user['id'])
        
        if not user_feedback:
            no_feedback_label = tk.Label(
                self.content_frame,
                text="No feedback provided yet. Provide feedback for resolved complaints!",
                font=("Arial", 12),
                bg='white',
                fg='#7f8c8d'
            )
            no_feedback_label.pack(pady=50)
            return
        
        # Feedback list
        for feedback in user_feedback:
            self.create_feedback_card(self.content_frame, feedback)
    
    def create_feedback_card(self, parent, feedback):
        """Create a feedback card widget"""
        card_frame = tk.Frame(parent, bg='#f8f9fa', relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Card content
        content_frame = tk.Frame(card_frame, bg='#f8f9fa')
        content_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Title and rating
        title_frame = tk.Frame(content_frame, bg='#f8f9fa')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text=feedback['complaint_title'],
            font=("Arial", 12, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(side=tk.LEFT)
        
        # Rating stars
        rating_text = "★" * feedback['rating'] + "☆" * (5 - feedback['rating'])
        rating_label = tk.Label(
            title_frame,
            text=rating_text,
            font=("Arial", 14),
            bg='#f8f9fa',
            fg='#f39c12'
        )
        rating_label.pack(side=tk.RIGHT)
        
        # Category and date
        info_frame = tk.Frame(content_frame, bg='#f8f9fa')
        info_frame.pack(fill=tk.X, pady=(5, 0))
        
        category_label = tk.Label(
            info_frame,
            text=f"Category: {feedback['category']}",
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        category_label.pack(side=tk.LEFT)
        
        date_label = tk.Label(
            info_frame,
            text=f"Provided: {dates.format_datetime(feedback['created_at'])}",
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        date_label.pack(side=tk.RIGHT)
        
        # Comment
        if feedback['comment']:
            comment_label = tk.Label(
                content_frame,
                text=f"Comment: {feedback['comment']}",
                font=("Arial", 10),
                bg='#f8f9fa',
                fg='#2c3e50',
                wraplength=600,
                justify=tk.LEFT
            )
            comment_label.pack(anchor=tk.W, pady=(5, 0))
    
    def show_complaint_form(self):
        """Show complaint form window"""
        if not self.complaint_form_window or not self.complaint_form_window.window.winfo_exists():
            self.complaint_form_window = ComplaintFormWindow(self.window, self.current_user['id'])
            self.complaint_form_window.show()
        else:
            self.complaint_form_window.window.lift()
    
    def show_status_tracking(self):
        """Show status tracking window"""
        if not self.status_view_window or not self.status_view_window.window.winfo_exists():
            self.status_view_window = StatusViewWindow(self.window, self.current_user['id'])
            self.status_view_window.show()
        else:
            self.status_view_window.window.lift()
    
    def refresh_data(self):
        """Refresh dashboard data"""
        self.show_dashboard_overview()
    
    def handle_logout(self):
        """Handle logout"""
        if messages.ask_confirmation("Are you sure you want to logout?"):
            logout_user()
            self.window.destroy()
            # Show login window
            from gui.login_gui import LoginWindow
            login_window = LoginWindow()
            login_window.show()
    
    def on_closing(self):
        """Handle window closing"""
        if messages.ask_confirmation("Are you sure you want to exit?"):
            logout_user()
            self.window.quit()

def main():
    """Main function for testing"""
    dashboard = UserDashboard()
    dashboard.show()

if __name__ == "__main__":
    main()

