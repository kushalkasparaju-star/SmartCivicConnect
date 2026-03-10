"""
Authentication module for Neighborhood Complaint & Feedback System
Handles user registration, login, and authentication logic
"""

import hashlib
import re
from typing import Optional, Dict, Any
from database.db_connection import db

class AuthenticationManager:
    """Manages user authentication and registration"""
    
    def __init__(self):
        self.current_user: Optional[Dict[str, Any]] = None
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if email is valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password (str): Password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if not re.search(r'[A-Za-z]', password):
            return False, "Password must contain at least one letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, ""
    
    def register_user(self, name: str, email: str, password: str, 
                     phone: str = "", address: str = "") -> tuple[bool, str]:
        """
        Register a new user
        
        Args:
            name (str): User's full name
            email (str): User's email address
            password (str): User's password
            phone (str): User's phone number (optional)
            address (str): User's address (optional)
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Validate inputs
            if not name.strip():
                return False, "Name is required"
            
            if not self.validate_email(email):
                return False, "Invalid email format"
            
            is_valid_password, password_error = self.validate_password(password)
            if not is_valid_password:
                return False, password_error
            
            # Check if user already exists
            existing_user = db.execute_query(
                "SELECT id FROM users WHERE email = ?", (email.lower(),)
            )
            
            if existing_user:
                return False, "User with this email already exists"
            
            # Hash password and insert user
            hashed_password = self.hash_password(password)
            
            user_id = db.execute_insert(
                """INSERT INTO users (name, email, password, phone, address, role)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name.strip(), email.lower(), hashed_password, phone.strip(), 
                 address.strip(), 'user')
            )
            
            return True, f"User registered successfully! User ID: {user_id}"
            
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
    
    def login_user(self, email: str, password: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticate user login
        
        Args:
            email (str): User's email address
            password (str): User's password
            
        Returns:
            tuple: (success, message, user_data)
        """
        try:
            # Validate email format
            if not self.validate_email(email):
                return False, "Invalid email format", None
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Query user
            user = db.execute_query(
                """SELECT id, name, email, password, role, phone, address, created_at
                   FROM users WHERE email = ? AND password = ?""",
                (email.lower(), hashed_password)
            )
            
            if not user:
                return False, "Invalid email or password", None
            
            user_data = dict(user[0])
            self.current_user = user_data
            
            return True, "Login successful", user_data
            
        except Exception as e:
            return False, f"Login failed: {str(e)}", None
    
    def logout_user(self):
        """Logout current user"""
        self.current_user = None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current logged-in user data
        
        Returns:
            Optional[Dict]: Current user data or None if not logged in
        """
        return self.current_user
    
    def is_admin(self) -> bool:
        """
        Check if current user is admin
        
        Returns:
            bool: True if current user is admin, False otherwise
        """
        return (self.current_user and 
                self.current_user.get('role', '').lower() == 'admin')
    
    def update_user_profile(self, user_id: int, name: str = None, 
                           phone: str = None, address: str = None) -> tuple[bool, str]:
        """
        Update user profile information
        
        Args:
            user_id (int): User ID to update
            name (str): New name (optional)
            phone (str): New phone (optional)
            address (str): New address (optional)
            
        Returns:
            tuple: (success, message)
        """
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name.strip())
            
            if phone is not None:
                updates.append("phone = ?")
                params.append(phone.strip())
            
            if address is not None:
                updates.append("address = ?")
                params.append(address.strip())
            
            if not updates:
                return False, "No updates provided"
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            
            rows_affected = db.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                # Update current user data if it's the same user
                if self.current_user and self.current_user['id'] == user_id:
                    if name is not None:
                        self.current_user['name'] = name.strip()
                    if phone is not None:
                        self.current_user['phone'] = phone.strip()
                    if address is not None:
                        self.current_user['address'] = address.strip()
                
                return True, "Profile updated successfully"
            else:
                return False, "User not found or no changes made"
                
        except Exception as e:
            return False, f"Profile update failed: {str(e)}"
    
    def change_password(self, user_id: int, old_password: str, 
                       new_password: str) -> tuple[bool, str]:
        """
        Change user password
        
        Args:
            user_id (int): User ID
            old_password (str): Current password
            new_password (str): New password
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Validate new password
            is_valid, error_msg = self.validate_password(new_password)
            if not is_valid:
                return False, error_msg
            
            # Verify old password
            old_hashed = self.hash_password(old_password)
            user = db.execute_query(
                "SELECT password FROM users WHERE id = ?", (user_id,)
            )
            
            if not user or user[0]['password'] != old_hashed:
                return False, "Current password is incorrect"
            
            # Update password
            new_hashed = self.hash_password(new_password)
            rows_affected = db.execute_update(
                "UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_hashed, user_id)
            )
            
            if rows_affected > 0:
                return True, "Password changed successfully"
            else:
                return False, "Failed to update password"
                
        except Exception as e:
            return False, f"Password change failed: {str(e)}"

# Global authentication manager instance
auth_manager = AuthenticationManager()

def register_user(name: str, email: str, password: str, 
                 phone: str = "", address: str = "") -> tuple[bool, str]:
    """Register a new user"""
    return auth_manager.register_user(name, email, password, phone, address)

def login_user(email: str, password: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
    """Login user"""
    return auth_manager.login_user(email, password)

def logout_user():
    """Logout current user"""
    auth_manager.logout_user()

def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current user"""
    return auth_manager.get_current_user()

def is_admin() -> bool:
    """Check if current user is admin"""
    return auth_manager.is_admin()

