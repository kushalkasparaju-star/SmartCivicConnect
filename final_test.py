"""
Final test script for Neighborhood Complaint & Feedback System
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_system():
    """Test the complete system"""
    print("Neighborhood Complaint System - Final Test")
    print("=" * 50)
    
    try:
        # Test database initialization
        from database.create_tables import create_tables
        create_tables()
        print("Database initialization successful")
        
        # Test database connection
        from database.db_connection import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Database connection successful (Users: {user_count})")
        
        # Test categories
        from backend.complaint_manager import get_categories
        categories = get_categories()
        print(f"Categories loaded successfully ({len(categories)} categories)")
        
        # Test admin login
        from backend.auth import login_user
        success, message, user_data = login_user("admin@neighborhood.com", "admin123")
        if success:
            print(f"Admin login successful ({user_data['name']})")
        else:
            print(f"Admin login failed: {message}")
            return False
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("System is ready for use")
        print("\nTo start the application:")
        print("  python main.py")
        print("\nDemo credentials:")
        print("  Admin: admin@neighborhood.com / admin123")
        print("  User: Register a new account")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_system()
    sys.exit(0 if success else 1)
