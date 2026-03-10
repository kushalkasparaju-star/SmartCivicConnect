"""
Main entry point for Neighborhood Complaint & Feedback System
Initializes the application and handles the main flow control
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import application modules
from database.create_tables import create_tables
from gui.login_gui import LoginWindow
from utils.helper_functions import messages

class NeighborhoodComplaintSystem:
    """Main application class"""
    
    def __init__(self):
        self.root = None
        self.login_window = None
        
    def initialize_database(self):
        """Initialize database tables"""
        try:
            print("🔄 Initializing database...")
            create_tables()
            print("✅ Database initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            messages.show_error(f"Failed to initialize database: {str(e)}")
            return False
    
    def show_splash_screen(self):
        """Show splash screen during initialization"""
        splash = tk.Tk()
        splash.title("Neighborhood Complaint System")
        splash.geometry("400x300")
        splash.resizable(False, False)
        
        # Center splash screen
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        splash.geometry(f"400x300+{x}+{y}")
        
        # Remove window decorations
        splash.overrideredirect(True)
        
        # Splash content
        splash_frame = tk.Frame(splash, bg='#2c3e50')
        splash_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Title
        title_label = tk.Label(
            splash_frame,
            text="🏘️",
            font=("Arial", 48),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=(50, 10))
        
        app_title = tk.Label(
            splash_frame,
            text="Neighborhood Complaint System",
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='white'
        )
        app_title.pack(pady=(0, 10))
        
        subtitle = tk.Label(
            splash_frame,
            text="Connecting Communities",
            font=("Arial", 12),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        subtitle.pack(pady=(0, 30))
        
        # Loading message
        loading_label = tk.Label(
            splash_frame,
            text="Initializing system...",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        loading_label.pack(pady=(0, 20))
        
        # Progress bar
        progress_frame = tk.Frame(splash_frame, bg='#2c3e50')
        progress_frame.pack(pady=(0, 20))
        
        progress_bar = tk.Frame(progress_frame, bg='#3498db', height=4, width=200)
        progress_bar.pack()
        
        # Version info
        version_label = tk.Label(
            splash_frame,
            text="Version 1.0.0",
            font=("Arial", 8),
            bg='#2c3e50',
            fg='#7f8c8d'
        )
        version_label.pack(side=tk.BOTTOM, pady=(0, 20))
        
        # Update splash screen
        splash.update()
        
        return splash
    
    def run(self):
        """Run the application"""
        try:
            # Show splash screen
            splash = self.show_splash_screen()
            
            # Initialize database
            splash.update()
            if not self.initialize_database():
                splash.destroy()
                return False
            
            # Close splash screen
            splash.destroy()
            
            # Create main root window (hidden)
            self.root = tk.Tk()
            self.root.withdraw()  # Hide the root window
            
            # Show login window
            self.login_window = LoginWindow(self.root)
            self.login_window.show()
            
            # Start main event loop
            self.root.mainloop()
            
            return True
            
        except Exception as e:
            print(f"❌ Application startup failed: {e}")
            messages.show_error(f"Application startup failed: {str(e)}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")

def main():
    """Main function"""
    print("🚀 Starting Neighborhood Complaint & Feedback System...")
    print("=" * 60)
    
    app = NeighborhoodComplaintSystem()
    
    try:
        success = app.run()
        if success:
            print("✅ Application completed successfully")
        else:
            print("❌ Application failed to start")
            return 1
    except KeyboardInterrupt:
        print("\n⚠️ Application interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    finally:
        app.cleanup()
        print("🔄 Application cleanup completed")
    
    return 0

if __name__ == "__main__":
    # Set up error handling
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print(f"❌ Uncaught exception: {exc_type.__name__}: {exc_value}")
        import traceback
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = handle_exception
    
    # Run the application
    exit_code = main()
    sys.exit(exit_code)

