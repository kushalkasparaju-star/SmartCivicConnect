"""
Admin Dashboard GUI module for Neighborhood Complaint & Feedback System
Provides comprehensive admin interface for managing complaints, users, and system analytics
"""

import tkinter as tk
from tkinter import ttk, messagebox
from backend.auth import get_current_user, logout_user, is_admin
from backend.complaint_manager import get_all_complaints, update_complaint_status, get_complaint_statistics, get_categories
from backend.admin_manager import get_all_users, get_system_statistics, assign_complaint
from backend.feedback_manager import get_all_feedback, get_feedback_statistics
from backend.report_manager import generate_complaints_report, generate_feedback_report, generate_analytics_report, save_report_to_file
from utils.helper_functions import validation, messages, ui, dates, status
import os

class AdminDashboard:
    """Admin dashboard class"""
    
    def __init__(self):
        self.window = None
        self.current_user = None
        # Maps for Treeview items to their full records
        self._complaints_item_data = {}
        self._users_item_data = {}
        self._feedback_item_data = {}
        
    def show(self):
        """Show admin dashboard"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        # Get current user
        self.current_user = get_current_user()
        if not self.current_user:
            messages.show_error("No user logged in")
            return
        
        if not is_admin():
            messages.show_error("Access denied. Admin privileges required.")
            return
        
        self.window = tk.Tk()
        self.window.title(f"Admin Dashboard - Neighborhood Complaint System")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        
        # Center window
        ui.center_window(self.window, 1200, 800)
        
        # Configure window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        # Default to show complaints management so admins see all complaints immediately
        self.show_complaints_management()
        
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
            text=f"Admin Dashboard - Welcome, {self.current_user['name']}",
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        welcome_label.pack(side=tk.LEFT)
        
        # Admin info
        admin_info = tk.Label(
            header_content,
            text="Administrator | System Management",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        admin_info.pack(side=tk.LEFT, padx=(20, 0))
        
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
            text="Admin Navigation",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        nav_title.pack(pady=(20, 10))
        
        # Navigation buttons
        nav_buttons_frame = tk.Frame(left_panel, bg='white')
        nav_buttons_frame.pack(fill=tk.X, padx=20)
        
        # Dashboard button
        self.dashboard_btn = tk.Button(
            nav_buttons_frame,
            text="📊 Dashboard",
            font=("Arial", 11, "bold"),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_dashboard_overview
        )
        self.dashboard_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Complaints Management button
        self.complaints_btn = tk.Button(
            nav_buttons_frame,
            text="📋 Manage Complaints",
            font=("Arial", 11, "bold"),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_complaints_management
        )
        self.complaints_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Users Management button
        self.users_btn = tk.Button(
            nav_buttons_frame,
            text="👥 Manage Users",
            font=("Arial", 11, "bold"),
            bg='#9b59b6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_users_management
        )
        self.users_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Feedback Management button
        self.feedback_btn = tk.Button(
            nav_buttons_frame,
            text="⭐ Manage Feedback",
            font=("Arial", 11, "bold"),
            bg='#f39c12',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_feedback_management
        )
        self.feedback_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Reports button
        self.reports_btn = tk.Button(
            nav_buttons_frame,
            text="📈 Generate Reports",
            font=("Arial", 11, "bold"),
            bg='#e67e22',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.show_reports
        )
        self.reports_btn.pack(fill=tk.X, pady=(0, 10))
        
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
        
        # Initialize with dashboard overview (will be overridden by show() to complaints)
        self.show_dashboard_overview()
    
    def show_dashboard_overview(self):
        """Show dashboard overview"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.content_title.config(text="Dashboard Overview")
        
        # Get system statistics
        system_stats = get_system_statistics()
        complaint_stats = get_complaint_statistics()
        feedback_stats = get_feedback_statistics()
        
        # Statistics cards frame
        stats_frame = tk.Frame(self.content_frame, bg='white')
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # System overview cards
        overview_cards_frame = tk.Frame(stats_frame, bg='white')
        overview_cards_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Total Users card
        users_card = tk.Frame(overview_cards_frame, bg='#3498db', relief=tk.RAISED, bd=1)
        users_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(users_card, text="Total Users", font=("Arial", 10, "bold"), 
                bg='#3498db', fg='white').pack(pady=(10, 5))
        tk.Label(users_card, text=str(system_stats['users']['total']), font=("Arial", 24, "bold"), 
                bg='#3498db', fg='white').pack(pady=(0, 10))
        
        # Total Complaints card
        complaints_card = tk.Frame(overview_cards_frame, bg='#27ae60', relief=tk.RAISED, bd=1)
        complaints_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(complaints_card, text="Total Complaints", font=("Arial", 10, "bold"), 
                bg='#27ae60', fg='white').pack(pady=(10, 5))
        tk.Label(complaints_card, text=str(complaint_stats['total_complaints']), font=("Arial", 24, "bold"), 
                bg='#27ae60', fg='white').pack(pady=(0, 10))
        
        # Total Feedback card
        feedback_card = tk.Frame(overview_cards_frame, bg='#f39c12', relief=tk.RAISED, bd=1)
        feedback_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(feedback_card, text="Total Feedback", font=("Arial", 10, "bold"), 
                bg='#f39c12', fg='white').pack(pady=(10, 5))
        tk.Label(feedback_card, text=str(feedback_stats['total_feedback']), font=("Arial", 24, "bold"), 
                bg='#f39c12', fg='white').pack(pady=(0, 10))
        
        # Average Rating card
        rating_card = tk.Frame(overview_cards_frame, bg='#9b59b6', relief=tk.RAISED, bd=1)
        rating_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(rating_card, text="Avg Rating", font=("Arial", 10, "bold"), 
                bg='#9b59b6', fg='white').pack(pady=(10, 5))
        tk.Label(rating_card, text=f"{feedback_stats['average_rating']}/5", font=("Arial", 24, "bold"), 
                bg='#9b59b6', fg='white').pack(pady=(0, 10))
        
        # Status breakdown cards
        status_cards_frame = tk.Frame(stats_frame, bg='white')
        status_cards_frame.pack(fill=tk.X)
        
        status_breakdown = complaint_stats['status_breakdown']
        status_colors = {'Pending': '#f39c12', 'In Progress': '#3498db', 'Resolved': '#27ae60', 'Closed': '#95a5a6'}
        
        for status_name, count in status_breakdown.items():
            if status_name in status_colors:
                status_card = tk.Frame(status_cards_frame, bg=status_colors[status_name], relief=tk.RAISED, bd=1)
                status_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
                
                tk.Label(status_card, text=status_name, font=("Arial", 10, "bold"), 
                        bg=status_colors[status_name], fg='white').pack(pady=(10, 5))
                tk.Label(status_card, text=str(count), font=("Arial", 20, "bold"), 
                        bg=status_colors[status_name], fg='white').pack(pady=(0, 10))
        
        # Recent activity section
        recent_frame = tk.Frame(self.content_frame, bg='white')
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        recent_title = tk.Label(
            recent_frame,
            text="Recent Activity",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        recent_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Recent complaints
        recent_complaints = get_all_complaints()[:5]  # Get last 5 complaints
        
        if recent_complaints:
            for complaint in recent_complaints:
                self.create_complaint_summary_card(recent_frame, complaint)
        else:
            no_complaints_label = tk.Label(
                recent_frame,
                text="No complaints found.",
                font=("Arial", 12),
                bg='white',
                fg='#7f8c8d'
            )
            no_complaints_label.pack(pady=20)
    
    def create_complaint_summary_card(self, parent, complaint):
        """Create a complaint summary card"""
        card_frame = tk.Frame(parent, bg='#f8f9fa', relief=tk.RAISED, bd=1)
        card_frame.pack(fill=tk.X, pady=(0, 10))
        
        content_frame = tk.Frame(card_frame, bg='#f8f9fa')
        content_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Title and status
        title_frame = tk.Frame(content_frame, bg='#f8f9fa')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            title_frame,
            text=f"#{complaint['id']}: {complaint['title']}",
            font=("Arial", 11, "bold"),
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
        
        # Details
        details_frame = tk.Frame(content_frame, bg='#f8f9fa')
        details_frame.pack(fill=tk.X, pady=(5, 0))
        
        details_text = f"Category: {complaint['category']} | User: {complaint['user_name']} | Created: {dates.format_datetime(complaint['created_at'], 'short')}"
        details_label = tk.Label(
            details_frame,
            text=details_text,
            font=("Arial", 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        details_label.pack(anchor=tk.W)
    
    def show_complaints_management(self):
        """Show complaints management interface"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.content_title.config(text="Complaints Management")
        
        # Filter frame
        filter_frame = tk.Frame(self.content_frame, bg='white')
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status filter
        status_label = tk.Label(filter_frame, text="Status:", font=("Arial", 10, "bold"), bg='white')
        status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.complaint_status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.complaint_status_var,
            values=["All", "Pending", "In Progress", "Resolved", "Closed"],
            state="readonly",
            width=15
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 20))
        status_combo.bind("<<ComboboxSelected>>", self.filter_complaints)
        
        # Category filter
        category_label = tk.Label(filter_frame, text="Category:", font=("Arial", 10, "bold"), bg='white')
        category_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.complaint_category_var = tk.StringVar(value="All")
        categories = ["All"] + [cat['name'] for cat in get_categories()]
        category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.complaint_category_var,
            values=categories,
            state="readonly",
            width=20
        )
        category_combo.pack(side=tk.LEFT, padx=(0, 20))
        category_combo.bind("<<ComboboxSelected>>", self.filter_complaints)
        
        # Refresh button
        refresh_btn = tk.Button(
            filter_frame,
            text="🔄 Refresh",
            font=("Arial", 10),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.load_complaints
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Complaints list frame
        list_frame = tk.Frame(self.content_frame, bg='white', relief=tk.RAISED, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for complaints
        columns = ("ID", "Title", "User", "Category", "Status", "Priority", "Created", "Actions")
        self.complaints_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        for col in columns:
            self.complaints_tree.heading(col, text=col)
        
        # Set column widths
        self.complaints_tree.column("ID", width=50)
        self.complaints_tree.column("Title", width=200)
        self.complaints_tree.column("User", width=120)
        self.complaints_tree.column("Category", width=120)
        self.complaints_tree.column("Status", width=100)
        self.complaints_tree.column("Priority", width=80)
        self.complaints_tree.column("Created", width=120)
        self.complaints_tree.column("Actions", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.complaints_tree.yview)
        self.complaints_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.complaints_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.complaints_tree.bind("<Double-1>", self.on_complaint_double_click)
        
        # Load complaints
        self.load_complaints()
    
    def load_complaints(self):
        """Load complaints with filtering"""
        try:
            # Clear existing items
            for item in self.complaints_tree.get_children():
                self.complaints_tree.delete(item)
            # Reset item mapping
            self._complaints_item_data = {}
            
            # Get complaints with filters
            status_filter = self.complaint_status_var.get() if self.complaint_status_var.get() != "All" else None
            category_filter = self.complaint_category_var.get() if self.complaint_category_var.get() != "All" else None
            
            complaints = get_all_complaints(status_filter, category_filter)
            
            # Add complaints to treeview
            for complaint in complaints:
                created_date = dates.format_datetime(complaint['created_at'], "short")
                
                item = self.complaints_tree.insert("", tk.END, values=(
                    complaint['id'],
                    complaint['title'][:30] + "..." if len(complaint['title']) > 30 else complaint['title'],
                    complaint['user_name'],
                    complaint['category'],
                    complaint['status'],
                    complaint['priority'],
                    created_date,
                    "Manage"
                ))
                
                # Store item data mapping
                self._complaints_item_data[item] = complaint
                
        except Exception as e:
            messages.show_error(f"Failed to load complaints: {str(e)}")
    
    def filter_complaints(self, event=None):
        """Filter complaints"""
        self.load_complaints()
    
    def on_complaint_double_click(self, event):
        """Handle double-click on complaint"""
        selection = self.complaints_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        complaint_data = self._complaints_item_data.get(item)
        
        if complaint_data:
            self.show_complaint_management_dialog(complaint_data)
    
    def show_complaint_management_dialog(self, complaint):
        """Show complaint management dialog"""
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Manage Complaint #{complaint['id']}")
        dialog.geometry("500x550")
        dialog.resizable(False, False)
        
        # Center dialog
        ui.center_window(dialog, 500, 550)
        
        # Make dialog modal
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Dialog content
        content_frame = tk.Frame(dialog, bg='#f8f9fa')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text=f"Complaint #{complaint['id']}: {complaint['title']}",
            font=("Arial", 14, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 15))
        
        # Complaint details
        details_frame = tk.Frame(content_frame, bg='#f8f9fa')
        details_frame.pack(fill=tk.X, pady=(0, 10))
        
        details_text = f"""
Category: {complaint['category']}
User: {complaint['user_name']} ({complaint['user_email']})
Location: {complaint['location']}
Priority: {complaint['priority']}
Status: {complaint['status']}
Created: {dates.format_datetime(complaint['created_at'])}

Description:
{complaint['description']}
        """
        
        details_label = tk.Label(
            details_frame,
            text=details_text,
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#2c3e50',
            justify=tk.LEFT
        )
        details_label.pack(anchor=tk.W)
        
        # Image preview
        image_frame = tk.Frame(content_frame, bg='#f8f9fa')
        image_frame.pack(fill=tk.X, pady=(0, 10))
        
        image_path = complaint.get('image_path')
        if image_path:
            img_label = tk.Label(image_frame, text=f"Attached Image: {os.path.basename(image_path)}", font=("Arial", 9), bg='#f8f9fa', fg='#7f8c8d')
            img_label.pack(side=tk.LEFT)
            
            def _open_image():
                try:
                    from PIL import Image, ImageTk  # Pillow
                    if not os.path.exists(image_path):
                        messages.show_error("Image file not found on disk")
                        return
                    preview = tk.Toplevel(dialog)
                    preview.title("Complaint Image Preview")
                    # Basic viewer with scroll
                    canvas = tk.Canvas(preview, bg='black')
                    hbar = tk.Scrollbar(preview, orient=tk.HORIZONTAL, command=canvas.xview)
                    vbar = tk.Scrollbar(preview, orient=tk.VERTICAL, command=canvas.yview)
                    canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
                    canvas.grid(row=0, column=0, sticky='nsew')
                    hbar.grid(row=1, column=0, sticky='ew')
                    vbar.grid(row=0, column=1, sticky='ns')
                    preview.grid_rowconfigure(0, weight=1)
                    preview.grid_columnconfigure(0, weight=1)
                    img = Image.open(image_path)
                    # Limit max preview size while keeping aspect
                    max_w, max_h = 900, 700
                    img.thumbnail((max_w, max_h))
                    tk_img = ImageTk.PhotoImage(img)
                    canvas_img = canvas.create_image(0, 0, anchor='nw', image=tk_img)
                    canvas.image = tk_img  # keep reference
                    bbox = canvas.bbox(canvas_img)
                    canvas.configure(scrollregion=bbox)
                except ImportError:
                    # Fallback: attempt to open with default OS viewer
                    try:
                        import subprocess, platform
                        if platform.system() == 'Windows':
                            os.startfile(image_path)
                        elif platform.system() == 'Darwin':
                            subprocess.Popen(['open', image_path])
                        else:
                            subprocess.Popen(['xdg-open', image_path])
                    except Exception as e:
                        messages.show_error(f"Unable to open image: {e}")
                except Exception as e:
                    messages.show_error(f"Failed to preview image: {e}")
            
            view_btn = tk.Button(image_frame, text="View Image", font=("Arial", 10), bg='#3498db', fg='white', relief=tk.FLAT, padx=12, pady=4, cursor='hand2', command=_open_image)
            view_btn.pack(side=tk.RIGHT)
        
        # Status update frame
        update_frame = tk.Frame(content_frame, bg='#f8f9fa')
        update_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status update
        status_label = tk.Label(update_frame, text="Update Status:", font=("Arial", 11, "bold"), bg='#f8f9fa')
        status_label.pack(anchor=tk.W, pady=(0, 5))
        
        status_frame = tk.Frame(update_frame, bg='#f8f9fa')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        new_status_var = tk.StringVar(value=complaint['status'])
        status_combo = ttk.Combobox(
            status_frame,
            textvariable=new_status_var,
            values=["Pending", "In Progress", "Resolved", "Closed"],
            state="readonly",
            width=20
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Notes
        notes_label = tk.Label(update_frame, text="Notes:", font=("Arial", 10, "bold"), bg='#f8f9fa')
        notes_label.pack(anchor=tk.W, pady=(0, 5))
        
        notes_text = tk.Text(
            update_frame,
            font=("Arial", 10),
            height=3,
            wrap=tk.WORD
        )
        notes_text.pack(fill=tk.X, pady=(0, 15))
        
        # Buttons
        buttons_frame = tk.Frame(content_frame, bg='#f8f9fa')
        buttons_frame.pack(fill=tk.X)
        
        def update_status():
            new_status = new_status_var.get()
            notes = notes_text.get("1.0", tk.END).strip()
            
            # Proceed if status changed or notes provided
            if (new_status != complaint['status']) or notes:
                success, message = update_complaint_status(
                    complaint['id'], new_status, self.current_user['id'], notes
                )
                
                if success:
                    messages.show_success(f"Status updated to '{new_status}'")
                    dialog.destroy()
                    self.load_complaints()
                else:
                    messages.show_error(message)
            else:
                messages.show_info("No changes to update")
        
        update_btn = tk.Button(
            buttons_frame,
            text="Update Status",
            font=("Arial", 11, "bold"),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=update_status
        )
        update_btn.pack(side=tk.LEFT)
        
        close_btn = tk.Button(
            buttons_frame,
            text="Close",
            font=("Arial", 11),
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT)
    
    def show_users_management(self):
        """Show users management interface"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.content_title.config(text="Users Management")
        
        # Users list frame
        list_frame = tk.Frame(self.content_frame, bg='white', relief=tk.RAISED, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for users
        columns = ("ID", "Name", "Email", "Role", "Phone", "Created")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        for col in columns:
            self.users_tree.heading(col, text=col)
        
        # Set column widths
        self.users_tree.column("ID", width=50)
        self.users_tree.column("Name", width=150)
        self.users_tree.column("Email", width=200)
        self.users_tree.column("Role", width=100)
        self.users_tree.column("Phone", width=120)
        self.users_tree.column("Created", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load users
        self.load_users()
    
    def load_users(self):
        """Load users"""
        try:
            # Clear existing items
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            # Reset map
            self._users_item_data = {}
            
            users = get_all_users()
            
            for user in users:
                created_date = dates.format_datetime(user['created_at'], "short")
                
                item = self.users_tree.insert("", tk.END, values=(
                    user['id'],
                    user['name'],
                    user['email'],
                    user['role'].title(),
                    user['phone'] or "N/A",
                    created_date
                ))
                
                # Store user data
                self._users_item_data[item] = user
                
        except Exception as e:
            messages.show_error(f"Failed to load users: {str(e)}")
    
    def show_feedback_management(self):
        """Show feedback management interface"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.content_title.config(text="Feedback Management")
        
        # Feedback list frame
        list_frame = tk.Frame(self.content_frame, bg='white', relief=tk.RAISED, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for feedback
        columns = ("ID", "Complaint", "User", "Rating", "Comment", "Date")
        self.feedback_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        for col in columns:
            self.feedback_tree.heading(col, text=col)
        
        # Set column widths
        self.feedback_tree.column("ID", width=50)
        self.feedback_tree.column("Complaint", width=200)
        self.feedback_tree.column("User", width=150)
        self.feedback_tree.column("Rating", width=80)
        self.feedback_tree.column("Comment", width=200)
        self.feedback_tree.column("Date", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.feedback_tree.yview)
        self.feedback_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.feedback_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load feedback
        self.load_feedback()
    
    def load_feedback(self):
        """Load feedback"""
        try:
            # Clear existing items
            for item in self.feedback_tree.get_children():
                self.feedback_tree.delete(item)
            # Reset map
            self._feedback_item_data = {}
            
            feedback_list = get_all_feedback()
            
            for feedback in feedback_list:
                created_date = dates.format_datetime(feedback['created_at'], "short")
                comment = feedback['comment'][:50] + "..." if feedback['comment'] and len(feedback['comment']) > 50 else (feedback['comment'] or "No comment")
                
                item = self.feedback_tree.insert("", tk.END, values=(
                    feedback['id'],
                    feedback['complaint_title'][:30] + "..." if len(feedback['complaint_title']) > 30 else feedback['complaint_title'],
                    feedback['user_name'],
                    "★" * feedback['rating'],
                    comment,
                    created_date
                ))
                
                # Store feedback data
                self._feedback_item_data[item] = feedback
                
        except Exception as e:
            messages.show_error(f"Failed to load feedback: {str(e)}")
    
    def show_reports(self):
        """Show reports interface"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.content_title.config(text="Generate Reports")
        
        # Reports frame
        reports_frame = tk.Frame(self.content_frame, bg='white')
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Report types
        report_types_frame = tk.Frame(reports_frame, bg='white')
        report_types_frame.pack(fill=tk.X, pady=(0, 20))
        
        report_title = tk.Label(
            report_types_frame,
            text="Select Report Type:",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        report_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Report buttons
        buttons_frame = tk.Frame(report_types_frame, bg='white')
        buttons_frame.pack(fill=tk.X)
        
        # Complaints report button
        complaints_report_btn = tk.Button(
            buttons_frame,
            text="📋 Complaints Report",
            font=("Arial", 12, "bold"),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=15,
            cursor='hand2',
            command=lambda: self.generate_report('complaints')
        )
        complaints_report_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Feedback report button
        feedback_report_btn = tk.Button(
            buttons_frame,
            text="⭐ Feedback Report",
            font=("Arial", 12, "bold"),
            bg='#f39c12',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=15,
            cursor='hand2',
            command=lambda: self.generate_report('feedback')
        )
        feedback_report_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Analytics report button
        analytics_report_btn = tk.Button(
            buttons_frame,
            text="📊 Analytics Report",
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=15,
            cursor='hand2',
            command=lambda: self.generate_report('analytics')
        )
        analytics_report_btn.pack(side=tk.LEFT)
    
    def generate_report(self, report_type):
        """Generate and save report"""
        try:
            if report_type == 'complaints':
                report_data = generate_complaints_report()
                filename = "complaints_report.json"
            elif report_type == 'feedback':
                report_data = generate_feedback_report()
                filename = "feedback_report.json"
            elif report_type == 'analytics':
                report_data = generate_analytics_report()
                filename = "analytics_report.json"
            else:
                messages.show_error("Invalid report type")
                return
            
            if 'error' in report_data:
                messages.show_error(f"Failed to generate report: {report_data['error']}")
                return
            
            # Save report to file
            if save_report_to_file(report_data, filename, 'json'):
                messages.show_success(f"Report generated successfully! Saved as {filename}")
            else:
                messages.show_error("Failed to save report file")
                
        except Exception as e:
            messages.show_error(f"Failed to generate report: {str(e)}")
    
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
    dashboard = AdminDashboard()
    dashboard.show()

if __name__ == "__main__":
    main()
