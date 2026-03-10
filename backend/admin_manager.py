"""
Admin management module for Neighborhood Complaint & Feedback System
Handles admin-specific operations and user management
"""

from typing import List, Dict, Any, Optional, Tuple
from database.db_connection import db
from backend.complaint_manager import complaint_manager
from backend.feedback_manager import feedback_manager

class AdminManager:
    """Manages admin operations and system administration"""
    
    def __init__(self):
        self.role_options = ['user', 'admin', 'moderator']
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users in the system
        
        Returns:
            List[Dict]: List of all users
        """
        try:
            users = db.execute_query(
                """SELECT id, name, email, role, phone, address, created_at
                   FROM users
                   ORDER BY created_at DESC"""
            )
            
            return [dict(user) for user in users]
            
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id (int): User ID
            
        Returns:
            Optional[Dict]: User data or None if not found
        """
        try:
            user = db.execute_query(
                """SELECT id, name, email, role, phone, address, created_at, updated_at
                   FROM users WHERE id = ?""",
                (user_id,)
            )
            
            return dict(user[0]) if user else None
            
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    def update_user_role(self, user_id: int, new_role: str, 
                        updated_by: int) -> Tuple[bool, str]:
        """
        Update user role
        
        Args:
            user_id (int): User ID to update
            new_role (str): New role
            updated_by (int): Admin user ID making the change
            
        Returns:
            Tuple: (success, message)
        """
        try:
            if new_role not in self.role_options:
                return False, "Invalid role"
            
            # Check if user exists
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Prevent admin from changing their own role
            if user_id == updated_by and new_role != 'admin':
                return False, "Cannot change your own role"
            
            rows_affected = db.execute_update(
                "UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_role, user_id)
            )
            
            if rows_affected > 0:
                return True, f"User role updated to {new_role}"
            else:
                return False, "Failed to update user role"
                
        except Exception as e:
            return False, f"Failed to update user role: {str(e)}"
    
    def delete_user(self, user_id: int, deleted_by: int) -> Tuple[bool, str]:
        """
        Delete a user (soft delete by deactivating)
        
        Args:
            user_id (int): User ID to delete
            deleted_by (int): Admin user ID making the deletion
            
        Returns:
            Tuple: (success, message)
        """
        try:
            # Check if user exists
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            # Prevent admin from deleting themselves
            if user_id == deleted_by:
                return False, "Cannot delete your own account"
            
            # Check if user has active complaints
            active_complaints = db.execute_query(
                "SELECT COUNT(*) as count FROM complaints WHERE user_id = ? AND status != 'Closed'",
                (user_id,)
            )[0]['count']
            
            if active_complaints > 0:
                return False, f"Cannot delete user with {active_complaints} active complaints"
            
            # For now, we'll just change the email to mark as deleted
            # In a production system, you might want a proper soft delete mechanism
            rows_affected = db.execute_update(
                "UPDATE users SET email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (f"deleted_{user_id}@deleted.com", user_id)
            )
            
            if rows_affected > 0:
                return True, "User account deactivated"
            else:
                return False, "Failed to delete user"
                
        except Exception as e:
            return False, f"Failed to delete user: {str(e)}"
    
    def assign_complaint(self, complaint_id: int, assigned_to: int, 
                        assigned_by: int) -> Tuple[bool, str]:
        """
        Assign complaint to a user
        
        Args:
            complaint_id (int): Complaint ID
            assigned_to (int): User ID to assign to
            assigned_by (int): Admin user ID making the assignment
            
        Returns:
            Tuple: (success, message)
        """
        try:
            # Check if complaint exists
            complaint = complaint_manager.get_complaint_by_id(complaint_id)
            if not complaint:
                return False, "Complaint not found"
            
            # Check if assigned user exists and is admin/moderator
            assigned_user = self.get_user_by_id(assigned_to)
            if not assigned_user:
                return False, "Assigned user not found"
            
            if assigned_user['role'] not in ['admin', 'moderator']:
                return False, "Can only assign to admin or moderator users"
            
            # Update complaint assignment
            rows_affected = db.execute_update(
                "UPDATE complaints SET assigned_to = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (assigned_to, complaint_id)
            )
            
            if rows_affected > 0:
                # Add status update
                complaint_manager.add_status_update(
                    complaint_id, assigned_by, complaint['status'], 
                    complaint['status'], f"Complaint assigned to {assigned_user['name']}"
                )
                
                return True, f"Complaint assigned to {assigned_user['name']}"
            else:
                return False, "Failed to assign complaint"
                
        except Exception as e:
            return False, f"Failed to assign complaint: {str(e)}"
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics
        
        Returns:
            Dict: System statistics
        """
        try:
            # User statistics
            total_users = db.execute_query("SELECT COUNT(*) as count FROM users")[0]['count']
            admin_users = db.execute_query(
                "SELECT COUNT(*) as count FROM users WHERE role = 'admin'"
            )[0]['count']
            moderator_users = db.execute_query(
                "SELECT COUNT(*) as count FROM users WHERE role = 'moderator'"
            )[0]['count']
            regular_users = db.execute_query(
                "SELECT COUNT(*) as count FROM users WHERE role = 'user'"
            )[0]['count']
            
            # Complaint statistics
            complaint_stats = complaint_manager.get_complaint_statistics()
            
            # Feedback statistics
            feedback_stats = feedback_manager.get_feedback_statistics()
            
            # Recent activity (last 7 days)
            recent_complaints = db.execute_query(
                """SELECT COUNT(*) as count 
                   FROM complaints 
                   WHERE created_at >= datetime('now', '-7 days')"""
            )[0]['count']
            
            recent_users = db.execute_query(
                """SELECT COUNT(*) as count 
                   FROM users 
                   WHERE created_at >= datetime('now', '-7 days')"""
            )[0]['count']
            
            # Top categories
            top_categories = db.execute_query(
                """SELECT category, COUNT(*) as count 
                   FROM complaints 
                   GROUP BY category 
                   ORDER BY count DESC 
                   LIMIT 5"""
            )
            
            return {
                'users': {
                    'total': total_users,
                    'admins': admin_users,
                    'moderators': moderator_users,
                    'regular_users': regular_users
                },
                'complaints': complaint_stats,
                'feedback': feedback_stats,
                'recent_activity': {
                    'complaints_7_days': recent_complaints,
                    'users_7_days': recent_users
                },
                'top_categories': [dict(cat) for cat in top_categories]
            }
            
        except Exception as e:
            print(f"Error fetching system statistics: {e}")
            return {
                'users': {'total': 0, 'admins': 0, 'moderators': 0, 'regular_users': 0},
                'complaints': {'total_complaints': 0, 'status_breakdown': {}},
                'feedback': {'total_feedback': 0, 'average_rating': 0},
                'recent_activity': {'complaints_7_days': 0, 'users_7_days': 0},
                'top_categories': []
            }
    
    def get_user_activity(self, user_id: int) -> Dict[str, Any]:
        """
        Get activity summary for a specific user
        
        Args:
            user_id (int): User ID
            
        Returns:
            Dict: User activity data
        """
        try:
            # User complaints
            user_complaints = complaint_manager.get_user_complaints(user_id)
            
            # User feedback
            user_feedback = feedback_manager.get_user_feedback(user_id)
            
            # Complaints assigned to user (if admin/moderator)
            assigned_complaints = db.execute_query(
                """SELECT c.*, u.name as user_name
                   FROM complaints c
                   JOIN users u ON c.user_id = u.id
                   WHERE c.assigned_to = ?
                   ORDER BY c.created_at DESC""",
                (user_id,)
            )
            
            return {
                'complaints_submitted': len(user_complaints),
                'feedback_provided': len(user_feedback),
                'complaints_assigned': len(assigned_complaints),
                'recent_complaints': user_complaints[:5],  # Last 5 complaints
                'recent_feedback': user_feedback[:5],  # Last 5 feedback
                'assigned_complaints': [dict(comp) for comp in assigned_complaints[:5]]
            }
            
        except Exception as e:
            print(f"Error fetching user activity: {e}")
            return {
                'complaints_submitted': 0,
                'feedback_provided': 0,
                'complaints_assigned': 0,
                'recent_complaints': [],
                'recent_feedback': [],
                'assigned_complaints': []
            }
    
    def export_complaints_report(self, start_date: str = None, 
                                end_date: str = None) -> List[Dict[str, Any]]:
        """
        Export complaints report for specified date range
        
        Args:
            start_date (str): Start date (YYYY-MM-DD format)
            end_date (str): End date (YYYY-MM-DD format)
            
        Returns:
            List[Dict]: Complaints report data
        """
        try:
            query = """SELECT c.*, u.name as user_name, u.email as user_email,
                              a.name as assigned_to_name
                       FROM complaints c
                       JOIN users u ON c.user_id = u.id
                       LEFT JOIN users a ON c.assigned_to = a.id
                       WHERE 1=1"""
            
            params = []
            
            if start_date:
                query += " AND DATE(c.created_at) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(c.created_at) <= ?"
                params.append(end_date)
            
            query += " ORDER BY c.created_at DESC"
            
            complaints = db.execute_query(query, tuple(params))
            return [dict(complaint) for complaint in complaints]
            
        except Exception as e:
            print(f"Error exporting complaints report: {e}")
            return []

# Global admin manager instance
admin_manager = AdminManager()

def get_all_users() -> List[Dict[str, Any]]:
    """Get all users"""
    return admin_manager.get_all_users()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    return admin_manager.get_user_by_id(user_id)

def update_user_role(user_id: int, new_role: str, updated_by: int) -> Tuple[bool, str]:
    """Update user role"""
    return admin_manager.update_user_role(user_id, new_role, updated_by)

def delete_user(user_id: int, deleted_by: int) -> Tuple[bool, str]:
    """Delete user"""
    return admin_manager.delete_user(user_id, deleted_by)

def assign_complaint(complaint_id: int, assigned_to: int, assigned_by: int) -> Tuple[bool, str]:
    """Assign complaint"""
    return admin_manager.assign_complaint(complaint_id, assigned_to, assigned_by)

def get_system_statistics() -> Dict[str, Any]:
    """Get system statistics"""
    return admin_manager.get_system_statistics()

def get_user_activity(user_id: int) -> Dict[str, Any]:
    """Get user activity"""
    return admin_manager.get_user_activity(user_id)

def export_complaints_report(start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
    """Export complaints report"""
    return admin_manager.export_complaints_report(start_date, end_date)

