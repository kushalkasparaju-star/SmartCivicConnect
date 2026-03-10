"""
Status View GUI module for Neighborhood Complaint & Feedback System
Provides interface for tracking complaint status and progress
"""

import tkinter as tk
from tkinter import ttk, messagebox
from backend.complaint_manager import get_user_complaints, get_status_updates, get_complaint_by_id
from backend.feedback_manager import can_provide_feedback, get_feedback_by_complaint
from utils.helper_functions import validation, messages, ui, dates, status
from gui.feedback_form import FeedbackFormWindow

class StatusViewWindow:
    """Status view window class"""
    
    def __init__(self, parent, user_id):
        self.parent = parent
        self.user_id = user_id
        self.window = None
        self.feedback_form_window = None
        # Store per-row data keyed by Treeview item id
        self._item_id_to_complaint = {}
        
    def show(self):
        """Show status view window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Track Complaint Status")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Center window
        ui.center_window(self.window, 800, 600)
        
        # Configure window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        self.load_complaints()
        
        # Start main loop if this is the main window
        if not self.parent:
            self.window.mainloop()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Track Complaint Status",
            font=("Arial", 18, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Filter frame
        filter_frame = tk.Frame(main_frame, bg='#f8f9fa')
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status filter
        status_label = tk.Label(
            filter_frame,
            text="Filter by Status:",
            font=("Arial", 10, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        status_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_var,
            values=["All", "Pending", "In Progress", "Resolved", "Closed"],
            state="readonly",
            width=15
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 20))
        status_combo.bind("<<ComboboxSelected>>", self.filter_complaints)
        
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
        list_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for complaints
        columns = ("ID", "Title", "Category", "Status", "Priority", "Created", "Actions")
        self.complaints_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.complaints_tree.heading("ID", text="ID")
        self.complaints_tree.heading("Title", text="Title")
        self.complaints_tree.heading("Category", text="Category")
        self.complaints_tree.heading("Status", text="Status")
        self.complaints_tree.heading("Priority", text="Priority")
        self.complaints_tree.heading("Created", text="Created")
        self.complaints_tree.heading("Actions", text="Actions")
        
        # Set column widths
        self.complaints_tree.column("ID", width=50, minwidth=50)
        self.complaints_tree.column("Title", width=200, minwidth=150)
        self.complaints_tree.column("Category", width=120, minwidth=100)
        self.complaints_tree.column("Status", width=100, minwidth=80)
        self.complaints_tree.column("Priority", width=80, minwidth=70)
        self.complaints_tree.column("Created", width=120, minwidth=100)
        self.complaints_tree.column("Actions", width=100, minwidth=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.complaints_tree.yview)
        self.complaints_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.complaints_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.complaints_tree.bind("<Double-1>", self.on_complaint_double_click)
        
        # Status details frame (initially hidden)
        self.details_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        self.details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Initially hide details frame
        self.details_frame.pack_forget()
    
    def load_complaints(self):
        """Load user complaints"""
        try:
            # Clear existing items
            for item in self.complaints_tree.get_children():
                self.complaints_tree.delete(item)
            # Reset row data mapping
            self._item_id_to_complaint = {}
            
            # Get user complaints
            user_complaints = get_user_complaints(self.user_id)
            
            # Filter by status if selected
            status_filter = self.status_var.get()
            if status_filter != "All":
                user_complaints = [c for c in user_complaints if c['status'] == status_filter]
            
            # Add complaints to treeview
            for complaint in user_complaints:
                # Format created date
                created_date = dates.format_datetime(complaint['created_at'], "short")
                
                # Determine action text
                action_text = ""
                if complaint['status'] == 'Resolved':
                    # Check if feedback can be provided
                    can_feedback, _ = can_provide_feedback(complaint['id'], self.user_id)
                    if can_feedback:
                        action_text = "Give Feedback"
                    else:
                        # Check if feedback already exists
                        existing_feedback = get_feedback_by_complaint(complaint['id'])
                        if existing_feedback:
                            action_text = "Feedback Given"
                        else:
                            action_text = "View Details"
                else:
                    action_text = "View Details"
                
                # Insert item
                item = self.complaints_tree.insert("", tk.END, values=(
                    complaint['id'],
                    complaint['title'][:30] + "..." if len(complaint['title']) > 30 else complaint['title'],
                    complaint['category'],
                    complaint['status'],
                    complaint['priority'],
                    created_date,
                    action_text
                ))
                
                # Store complaint data by item id
                self._item_id_to_complaint[item] = complaint
                
        except Exception as e:
            messages.show_error(f"Failed to load complaints: {str(e)}")
    
    def filter_complaints(self, event=None):
        """Filter complaints by status"""
        self.load_complaints()
    
    def on_complaint_double_click(self, event):
        """Handle double-click on complaint"""
        selection = self.complaints_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        complaint_data = self._item_id_to_complaint.get(item)
        
        if not complaint_data:
            return
        
        # Get full complaint details
        complaint_id = complaint_data['id']
        complaint = get_complaint_by_id(complaint_id)
        
        if not complaint:
            messages.show_error("Complaint not found")
            return
        
        # Show complaint details
        self.show_complaint_details(complaint)
    
    def show_complaint_details(self, complaint):
        """Show detailed complaint information"""
        # Clear details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Show details frame
        self.details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Details content
        details_content = tk.Frame(self.details_frame, bg='white')
        details_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Title
        title_label = tk.Label(
            details_content,
            text=f"Complaint #{complaint['id']}: {complaint['title']}",
            font=("Arial", 14, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Basic info frame
        info_frame = tk.Frame(details_content, bg='white')
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Left column
        left_col = tk.Frame(info_frame, bg='white')
        left_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Category
        category_label = tk.Label(
            left_col,
            text=f"Category: {complaint['category']}",
            font=("Arial", 10),
            bg='white',
            fg='#2c3e50'
        )
        category_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Location
        location_label = tk.Label(
            left_col,
            text=f"Location: {complaint['location']}",
            font=("Arial", 10),
            bg='white',
            fg='#2c3e50'
        )
        location_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Priority
        priority_color = status.get_priority_color(complaint['priority'])
        priority_label = tk.Label(
            left_col,
            text=f"Priority: {complaint['priority']}",
            font=("Arial", 10, "bold"),
            bg='white',
            fg=priority_color
        )
        priority_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Right column
        right_col = tk.Frame(info_frame, bg='white')
        right_col.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Status
        status_color = status.get_status_color(complaint['status'])
        status_label = tk.Label(
            right_col,
            text=f"Status: {complaint['status']}",
            font=("Arial", 10, "bold"),
            bg='white',
            fg=status_color
        )
        status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Created date
        created_label = tk.Label(
            right_col,
            text=f"Created: {dates.format_datetime(complaint['created_at'])}",
            font=("Arial", 10),
            bg='white',
            fg='#7f8c8d'
        )
        created_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Updated date
        if complaint['updated_at']:
            updated_label = tk.Label(
                right_col,
                text=f"Updated: {dates.format_datetime(complaint['updated_at'])}",
                font=("Arial", 10),
                bg='white',
                fg='#7f8c8d'
            )
            updated_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Description
        desc_label = tk.Label(
            details_content,
            text="Description:",
            font=("Arial", 11, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        desc_label.pack(anchor=tk.W, pady=(10, 5))
        
        desc_text = tk.Text(
            details_content,
            font=("Arial", 10),
            height=4,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=1,
            bg='#f8f9fa'
        )
        desc_text.pack(fill=tk.X, pady=(0, 15))
        desc_text.insert("1.0", complaint['description'])
        desc_text.config(state=tk.DISABLED)
        
        # Status updates section
        updates_label = tk.Label(
            details_content,
            text="Status Updates:",
            font=("Arial", 11, "bold"),
            bg='white',
            fg='#2c3e50'
        )
        updates_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Load and display status updates
        self.load_status_updates(details_content, complaint['id'])
        
        # Action buttons
        buttons_frame = tk.Frame(details_content, bg='white')
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Feedback button (if applicable)
        if complaint['status'] == 'Resolved':
            can_feedback, _ = can_provide_feedback(complaint['id'], self.user_id)
            if can_feedback:
                feedback_btn = tk.Button(
                    buttons_frame,
                    text="⭐ Provide Feedback",
                    font=("Arial", 10, "bold"),
                    bg='#f39c12',
                    fg='white',
                    relief=tk.FLAT,
                    padx=20,
                    pady=8,
                    cursor='hand2',
                    command=lambda: self.show_feedback_form(complaint['id'])
                )
                feedback_btn.pack(side=tk.LEFT)
            else:
                # Check if feedback already exists
                existing_feedback = get_feedback_by_complaint(complaint['id'])
                if existing_feedback:
                    feedback_label = tk.Label(
                        buttons_frame,
                        text="✅ Feedback Already Provided",
                        font=("Arial", 10, "bold"),
                        bg='white',
                        fg='#27ae60'
                    )
                    feedback_label.pack(side=tk.LEFT)
        
        # Close details button
        close_btn = tk.Button(
            buttons_frame,
            text="Close Details",
            font=("Arial", 10),
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.hide_details
        )
        close_btn.pack(side=tk.RIGHT)
    
    def load_status_updates(self, parent, complaint_id):
        """Load and display status updates"""
        try:
            status_updates = get_status_updates(complaint_id)
            
            if not status_updates:
                no_updates_label = tk.Label(
                    parent,
                    text="No status updates available",
                    font=("Arial", 10),
                    bg='white',
                    fg='#7f8c8d'
                )
                no_updates_label.pack(anchor=tk.W)
                return
            
            # Create updates frame
            updates_frame = tk.Frame(parent, bg='white')
            updates_frame.pack(fill=tk.X, pady=(0, 10))
            
            for update in status_updates:
                update_frame = tk.Frame(updates_frame, bg='#f8f9fa', relief=tk.RAISED, bd=1)
                update_frame.pack(fill=tk.X, pady=(0, 5))
                
                update_content = tk.Frame(update_frame, bg='#f8f9fa')
                update_content.pack(fill=tk.X, padx=10, pady=8)
                
                # Update header
                header_frame = tk.Frame(update_content, bg='#f8f9fa')
                header_frame.pack(fill=tk.X)
                
                # Status change
                status_text = f"{update['old_status'] or 'New'} → {update['new_status']}"
                status_label = tk.Label(
                    header_frame,
                    text=status_text,
                    font=("Arial", 10, "bold"),
                    bg='#f8f9fa',
                    fg='#2c3e50'
                )
                status_label.pack(side=tk.LEFT)
                
                # Date
                date_label = tk.Label(
                    header_frame,
                    text=dates.format_datetime(update['created_at']),
                    font=("Arial", 9),
                    bg='#f8f9fa',
                    fg='#7f8c8d'
                )
                date_label.pack(side=tk.RIGHT)
                
                # Update notes
                if update['update_notes']:
                    notes_label = tk.Label(
                        update_content,
                        text=f"Notes: {update['update_notes']}",
                        font=("Arial", 9),
                        bg='#f8f9fa',
                        fg='#2c3e50',
                        wraplength=600,
                        justify=tk.LEFT
                    )
                    notes_label.pack(anchor=tk.W, pady=(5, 0))
                
        except Exception as e:
            error_label = tk.Label(
                parent,
                text=f"Error loading status updates: {str(e)}",
                font=("Arial", 10),
                bg='white',
                fg='#e74c3c'
            )
            error_label.pack(anchor=tk.W)
    
    def show_feedback_form(self, complaint_id):
        """Show feedback form for resolved complaint"""
        if not self.feedback_form_window or not self.feedback_form_window.window.winfo_exists():
            self.feedback_form_window = FeedbackFormWindow(self.window, complaint_id, self.user_id)
            self.feedback_form_window.show()
        else:
            self.feedback_form_window.window.lift()
    
    def hide_details(self):
        """Hide details frame"""
        self.details_frame.pack_forget()
    
    def on_closing(self):
        """Handle window closing"""
        self.window.destroy()

def main():
    """Main function for testing"""
    status_window = StatusViewWindow(None, 1)
    status_window.show()

if __name__ == "__main__":
    main()
