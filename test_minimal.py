"""
Minimal test script for Neighborhood Complaint & Feedback System
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_basic_functionality():
    """Test basic functionality"""
    print("Testing basic functionality...")
    
    try:
        # Test database initialization
        from database.create_tables import create_tables
        create_tables()
        print("Database initialization: OK")
        
        # Test database connection
        from database.db_connection import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Database connection: OK (Users: {user_count})")
        
        # Test authentication
        from backend.auth import register_user, login_user
        
        # Register a test user
        success, message = register_user("Test User", "test@example.com", "testpass123")
        if success:
            print("User registration: OK")
        else:
            print(f"User registration: FAILED - {message}")
            return False
        
        # Login test user
        success, message, user_data = login_user("test@example.com", "testpass123")
        if success:
            print("User login: OK")
            print(f"  User: {user_data['name']} ({user_data['email']})")
        else:
            print(f"User login: FAILED - {message}")
            return False
        
        # Test complaint management
        from backend.complaint_manager import add_complaint, get_categories
        
        categories = get_categories()
        print(f"Categories loaded: OK ({len(categories)} categories)")
        
        # Add a test complaint
        success, message, complaint_id = add_complaint(
            user_data['id'], "Roads & Infrastructure", "Test Complaint",
            "This is a test complaint", "Test Location", "Medium"
        )
        
        if success:
            print(f"Complaint creation: OK (ID: {complaint_id})")
        else:
            print(f"Complaint creation: FAILED - {message}")
            return False
        
        print("\nAll basic tests passed!")
        return True
        
    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Neighborhood Complaint System - Basic Test")
    print("=" * 50)
    
    success = test_basic_functionality()
    
    if success:
        print("\nSystem is working correctly!")
        sys.exit(0)
    else:
        print("\nSystem has issues that need to be fixed.")
        sys.exit(1)

