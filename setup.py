"""
Setup script for Neighborhood Complaint & Feedback System
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"Python version: {sys.version.split()[0]} ✓")
    return True

def check_tkinter():
    """Check if Tkinter is available"""
    try:
        import tkinter
        print("Tkinter: Available ✓")
        return True
    except ImportError:
        print("Error: Tkinter is not available")
        print("Please install tkinter for your Python distribution")
        return False

def install_dependencies():
    """Install optional dependencies"""
    try:
        print("Installing optional dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully ✓")
        return True
    except subprocess.CalledProcessError:
        print("Warning: Failed to install some optional dependencies")
        print("The system will work with built-in modules only")
        return False

def test_database():
    """Test database initialization"""
    try:
        print("Testing database initialization...")
        from database.create_tables import create_tables
        create_tables()
        print("Database initialization: Success ✓")
        return True
    except Exception as e:
        print(f"Database initialization: Failed - {e}")
        return False

def main():
    """Main setup function"""
    print("Neighborhood Complaint & Feedback System - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check Tkinter
    if not check_tkinter():
        return False
    
    # Install dependencies
    install_dependencies()
    
    # Test database
    if not test_database():
        return False
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo run the application:")
    print("  python main.py")
    print("\nDemo credentials:")
    print("  Admin: admin@neighborhood.com / admin123")
    print("  User: Register a new account")
    print("\nEnjoy using the Neighborhood Complaint System!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
