"""
Complaint Form GUI module for Neighborhood Complaint & Feedback System
Provides interface for submitting new complaints
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from backend.complaint_manager import add_complaint, get_categories
from utils.helper_functions import validation, messages, ui, files

class ComplaintFormWindow:
    """Complaint form window class"""
    
    def __init__(self, parent, user_id):
        self.parent = parent
        self.user_id = user_id
        self.window = None
        self.selected_image_path = None
        self.categories_loaded = False
        
    def show(self):
        """Show complaint form window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Submit New Complaint")
        self.window.geometry("600x700")
        self.window.resizable(False, False)
        
        # Center window
        ui.center_window(self.window, 600, 700)
        
        # Configure window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        
        # Focus on title entry
        self.title_entry.focus()
        
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
        content_frame = tk.Frame(scrollable_frame, bg='#f8f9fa', padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text="Submit New Complaint",
            font=("Arial", 18, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(content_frame, bg='#f8f9fa')
        form_frame.pack(fill=tk.X)
        
        # Category field
        category_label = tk.Label(
            form_frame,
            text="Category: *",
            font=("Arial", 11, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        category_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            font=("Arial", 11),
            width=50,
            state="normal"  # Start with normal state
        )
        self.category_combo.pack(pady=(0, 15))
        
        # Load categories
        self.load_categories()
        
        # Title field
        title_label = tk.Label(
            form_frame,
            text="Complaint Title: *",
            font=("Arial", 11, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.title_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=50,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.title_entry.pack(pady=(0, 15))
        
        # Description field
        description_label = tk.Label(
            form_frame,
            text="Description: *",
            font=("Arial", 11, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        description_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.description_text = tk.Text(
            form_frame,
            font=("Arial", 11),
            width=50,
            height=6,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db',
            wrap=tk.WORD
        )
        self.description_text.pack(pady=(0, 15))
        
        # Location field
        location_label = tk.Label(
            form_frame,
            text="Location: *",
            font=("Arial", 11, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        location_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.location_entry = tk.Entry(
            form_frame,
            font=("Arial", 11),
            width=50,
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db'
        )
        self.location_entry.pack(pady=(0, 15))
        
        # Priority field
        priority_label = tk.Label(
            form_frame,
            text="Priority:",
            font=("Arial", 11, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        priority_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.priority_var = tk.StringVar(value="Medium")
        priority_frame = tk.Frame(form_frame, bg='#f8f9fa')
        priority_frame.pack(anchor=tk.W, pady=(0, 15))
        
        priorities = ["Low", "Medium", "High", "Urgent"]
        for priority in priorities:
            rb = tk.Radiobutton(
                priority_frame,
                text=priority,
                variable=self.priority_var,
                value=priority,
                font=("Arial", 10),
                bg='#f8f9fa',
                fg='#2c3e50',
                activebackground='#f8f9fa'
            )
            rb.pack(side=tk.LEFT, padx=(0, 20))
        
        # Image upload section
        image_label = tk.Label(
            form_frame,
            text="Attach Image (Optional):",
            font=("Arial", 11, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        image_label.pack(anchor=tk.W, pady=(0, 5))
        
        image_frame = tk.Frame(form_frame, bg='#f8f9fa')
        image_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.image_path_label = tk.Label(
            image_frame,
            text="No image selected",
            font=("Arial", 10),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        self.image_path_label.pack(side=tk.LEFT)
        
        select_image_btn = tk.Button(
            image_frame,
            text="Select Image",
            font=("Arial", 10),
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.select_image
        )
        select_image_btn.pack(side=tk.RIGHT)
        
        # Buttons frame
        buttons_frame = tk.Frame(content_frame, bg='#f8f9fa')
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Submit button
        self.submit_button = tk.Button(
            buttons_frame,
            text="Submit Complaint",
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
            content_frame,
            text="* Required fields",
            font=("Arial", 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        required_note.pack(pady=(10, 0))
    
    def load_categories(self):
        """Load complaint categories"""
        try:
            categories = get_categories()
            category_names = [cat['name'] for cat in categories]
            
            self.category_combo['values'] = category_names
            if category_names:
                self.category_combo.set(category_names[0])
                self.category_var.set(category_names[0])  # Also set the StringVar
                self.categories_loaded = True
            
            # Set to readonly after loading
            self.category_combo.config(state="readonly")
        except Exception as e:
            messages.show_error(f"Failed to load categories: {str(e)}")
            self.categories_loaded = False
    
    def select_image(self):
        """Select image file"""
        try:
            image_path = files.select_image_file()
            if image_path:
                # Validate image file
                if not files.is_valid_image_file(image_path):
                    messages.show_error("Please select a valid image file (jpg, jpeg, png, gif, bmp)")
                    return
                
                # Check file size (max 5MB)
                file_size_mb = files.get_file_size_mb(image_path)
                if file_size_mb > 5:
                    messages.show_error("Image file size must be less than 5MB")
                    return
                
                self.selected_image_path = image_path
                filename = image_path.split('/')[-1] if '/' in image_path else image_path.split('\\')[-1]
                self.image_path_label.config(text=f"Selected: {filename}", fg='#27ae60')
                
        except Exception as e:
            messages.show_error(f"Failed to select image: {str(e)}")
    
    def handle_submit(self):
        """Handle form submission"""
        # Get form data
        category = self.category_var.get().strip()
        title = self.title_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        location = self.location_entry.get().strip()
        priority = self.priority_var.get()
        
        # Validate inputs
        if not self.categories_loaded:
            messages.show_error("Categories are still loading. Please wait a moment and try again.")
            return
        
        if not category:
            messages.show_error("Please select a category from the dropdown list")
            self.category_combo.focus()
            return
        
        is_valid_title, title_error = validation.validate_required_field(title, "Title")
        if not is_valid_title:
            messages.show_error(title_error)
            self.title_entry.focus()
            return
        
        is_valid_description, description_error = validation.validate_required_field(description, "Description")
        if not is_valid_description:
            messages.show_error(description_error)
            self.description_text.focus()
            return
        
        is_valid_location, location_error = validation.validate_required_field(location, "Location")
        if not is_valid_location:
            messages.show_error(location_error)
            self.location_entry.focus()
            return
        
        # Disable submit button during processing
        self.submit_button.config(state=tk.DISABLED, text="Submitting...")
        self.window.update()
        
        try:
            # Submit complaint
            success, message, complaint_id = add_complaint(
                self.user_id, category, title, description, location, priority, self.selected_image_path
            )
            
            if success:
                messages.show_success(f"Complaint submitted successfully! Complaint ID: {complaint_id}")
                self.clear_form()
            else:
                messages.show_error(message)
                
        except Exception as e:
            messages.show_error(f"Failed to submit complaint: {str(e)}")
        finally:
            # Re-enable submit button
            self.submit_button.config(state=tk.NORMAL, text="Submit Complaint")
    
    def clear_form(self):
        """Clear form fields"""
        self.category_combo.set('')
        self.title_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.location_entry.delete(0, tk.END)
        self.priority_var.set("Medium")
        self.selected_image_path = None
        self.image_path_label.config(text="No image selected", fg='#7f8c8d')
        
        # Load categories again
        self.load_categories()
        
        # Focus on title entry
        self.title_entry.focus()
    
    def on_closing(self):
        """Handle window closing"""
        self.window.destroy()

def main():
    """Main function for testing"""
    form_window = ComplaintFormWindow(None, 1)
    form_window.show()

if __name__ == "__main__":
    main()
