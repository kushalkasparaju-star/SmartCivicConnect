"""
Feedback Form GUI module for Neighborhood Complaint & Feedback System
Provides interface for submitting feedback on resolved complaints
"""

import tkinter as tk
from tkinter import ttk, messagebox
from backend.feedback_manager import add_feedback, can_provide_feedback, get_feedback_by_complaint
from backend.complaint_manager import get_complaint_by_id
from utils.helper_functions import validation, messages, ui, dates

class FeedbackFormWindow:
    """Feedback form window class"""
    
    def __init__(self, parent, complaint_id, user_id):
        self.parent = parent
        self.complaint_id = complaint_id
        self.user_id = user_id
        self.window = None
        
    def show(self):
        """Show feedback form window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        # Check if feedback can be provided
        can_provide, reason = can_provide_feedback(self.complaint_id, self.user_id)
        if not can_provide:
            messages.show_error(f"Cannot provide feedback: {reason}")
            return
        
        # Check if feedback already exists
        existing_feedback = get_feedback_by_complaint(self.complaint_id)
        if existing_feedback:
            messages.show_info("Feedback has already been provided for this complaint.")
            return
        
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Provide Feedback")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Center window
        ui.center_window(self.window, 500, 600)
        
        # Configure window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        
        # Focus on rating
        self.rating_var.set(5)  # Default to 5 stars
        
        # Start main loop if this is the main window
        if not self.parent:
            self.window.mainloop()
    
    def create_widgets(self):
        """Create and layout widgets"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Provide Feedback",
            font=("Arial", 18, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Get complaint details
        complaint = get_complaint_by_id(self.complaint_id)
        if not complaint:
            messages.show_error("Complaint not found")
            self.window.destroy()
            return
        
        # Complaint info frame
        info_frame = tk.Frame(main_frame, bg='#e8f4f8', relief=tk.RAISED, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        info_content = tk.Frame(info_frame, bg='#e8f4f8')
        info_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Complaint title
        complaint_title = tk.Label(
            info_content,
            text=f"Complaint: {complaint['title']}",
            font=("Arial", 12, "bold"),
            bg='#e8f4f8',
            fg='#2c3e50'
        )
        complaint_title.pack(anchor=tk.W, pady=(0, 5))
        
        # Complaint details
        details_text = f"Category: {complaint['category']} | Location: {complaint['location']}"
        details_label = tk.Label(
            info_content,
            text=details_text,
            font=("Arial", 10),
            bg='#e8f4f8',
            fg='#7f8c8d'
        )
        details_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Resolution date
        if complaint['resolved_at']:
            resolved_text = f"Resolved on: {dates.format_datetime(complaint['resolved_at'])}"
            resolved_label = tk.Label(
                info_content,
                text=resolved_text,
                font=("Arial", 10),
                bg='#e8f4f8',
                fg='#27ae60'
            )
            resolved_label.pack(anchor=tk.W)
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg='#f8f9fa')
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Rating section
        rating_label = tk.Label(
            form_frame,
            text="How would you rate the resolution? *",
            font=("Arial", 12, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        rating_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Rating frame
        rating_frame = tk.Frame(form_frame, bg='#f8f9fa')
        rating_frame.pack(anchor=tk.W, pady=(0, 15))
        
        self.rating_var = tk.IntVar(value=5)
        
        # Rating scale
        scale_frame = tk.Frame(rating_frame, bg='#f8f9fa')
        scale_frame.pack(side=tk.LEFT)
        
        # Rating labels
        rating_labels = ["Very Poor", "Poor", "Average", "Good", "Excellent"]
        
        for i in range(1, 6):
            rating_btn_frame = tk.Frame(scale_frame, bg='#f8f9fa')
            rating_btn_frame.pack(side=tk.LEFT, padx=5)
            
            # Radio button
            rb = tk.Radiobutton(
                rating_btn_frame,
                variable=self.rating_var,
                value=i,
                font=("Arial", 10),
                bg='#f8f9fa',
                fg='#2c3e50',
                activebackground='#f8f9fa'
            )
            rb.pack()
            
            # Star
            star_label = tk.Label(
                rating_btn_frame,
                text="★",
                font=("Arial", 16),
                bg='#f8f9fa',
                fg='#f39c12'
            )
            star_label.pack()
            
            # Label
            label = tk.Label(
                rating_btn_frame,
                text=rating_labels[i-1],
                font=("Arial", 9),
                bg='#f8f9fa',
                fg='#7f8c8d'
            )
            label.pack()
        
        # Rating description
        self.rating_desc_label = tk.Label(
            rating_frame,
            text="Excellent - Very satisfied with the resolution",
            font=("Arial", 10, "italic"),
            bg='#f8f9fa',
            fg='#27ae60'
        )
        self.rating_desc_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Bind rating change
        self.rating_var.trace('w', self.on_rating_change)
        
        # Comment section
        comment_label = tk.Label(
            form_frame,
            text="Additional Comments (Optional):",
            font=("Arial", 12, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        comment_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.comment_text = tk.Text(
            form_frame,
            font=("Arial", 11),
            height=6,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.comment_text.pack(fill=tk.X, pady=(0, 20))
        
        # Placeholder text
        placeholder_text = "Please share any additional thoughts about the resolution process, quality of service, or suggestions for improvement..."
        self.comment_text.insert("1.0", placeholder_text)
        self.comment_text.config(fg='#7f8c8d')
        
        # Bind focus events for placeholder
        self.comment_text.bind("<FocusIn>", self.on_comment_focus_in)
        self.comment_text.bind("<FocusOut>", self.on_comment_focus_out)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#f8f9fa')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Submit button
        self.submit_button = tk.Button(
            buttons_frame,
            text="Submit Feedback",
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2',
            command=self.handle_submit
        )
        self.submit_button.pack(side=tk.LEFT)
        
        # Cancel button
        cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            font=("Arial", 12),
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor='hand2',
            command=self.on_closing
        )
        cancel_button.pack(side=tk.RIGHT)
        
        # Required fields note
        required_note = tk.Label(
            main_frame,
            text="* Required fields",
            font=("Arial", 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        required_note.pack(pady=(10, 0))
    
    def on_rating_change(self, *args):
        """Handle rating change"""
        rating = self.rating_var.get()
        rating_labels = [
            "Very Poor - Completely unsatisfied",
            "Poor - Mostly unsatisfied", 
            "Average - Neither satisfied nor unsatisfied",
            "Good - Mostly satisfied",
            "Excellent - Very satisfied with the resolution"
        ]
        
        colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
        
        self.rating_desc_label.config(
            text=rating_labels[rating-1],
            fg=colors[rating-1]
        )
    
    def on_comment_focus_in(self, event):
        """Handle comment text focus in"""
        if self.comment_text.get("1.0", tk.END).strip() == "Please share any additional thoughts about the resolution process, quality of service, or suggestions for improvement...":
            self.comment_text.delete("1.0", tk.END)
            self.comment_text.config(fg='#2c3e50')
    
    def on_comment_focus_out(self, event):
        """Handle comment text focus out"""
        if not self.comment_text.get("1.0", tk.END).strip():
            self.comment_text.insert("1.0", "Please share any additional thoughts about the resolution process, quality of service, or suggestions for improvement...")
            self.comment_text.config(fg='#7f8c8d')
    
    def handle_submit(self):
        """Handle form submission"""
        # Get form data
        rating = self.rating_var.get()
        comment = self.comment_text.get("1.0", tk.END).strip()
        
        # Validate rating
        is_valid_rating, rating_error = validation.validate_rating(rating)
        if not is_valid_rating:
            messages.show_error(rating_error)
            return
        
        # Check if comment is placeholder text
        if comment == "Please share any additional thoughts about the resolution process, quality of service, or suggestions for improvement...":
            comment = None
        
        # Disable submit button during processing
        self.submit_button.config(state=tk.DISABLED, text="Submitting...")
        self.window.update()
        
        try:
            # Submit feedback
            success, message = add_feedback(self.complaint_id, self.user_id, rating, comment)
            
            if success:
                messages.show_success("Thank you for your feedback! Your input helps us improve our services.")
                self.window.destroy()
            else:
                messages.show_error(message)
                
        except Exception as e:
            messages.show_error(f"Failed to submit feedback: {str(e)}")
        finally:
            # Re-enable submit button
            self.submit_button.config(state=tk.NORMAL, text="Submit Feedback")
    
    def on_closing(self):
        """Handle window closing"""
        self.window.destroy()

def main():
    """Main function for testing"""
    feedback_window = FeedbackFormWindow(None, 1, 1)
    feedback_window.show()

if __name__ == "__main__":
    main()

