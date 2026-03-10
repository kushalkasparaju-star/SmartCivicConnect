"""
Complaint management module for Neighborhood Complaint & Feedback System
Handles complaint creation, retrieval, updates, and status management
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from database.db_connection import db

class ComplaintManager:
    """Manages complaint operations and status updates"""
    
    def __init__(self):
        self.status_options = ['Pending', 'In Progress', 'Resolved', 'Closed']
        self.priority_options = ['Low', 'Medium', 'High', 'Urgent']
    
    def add_complaint(self, user_id: int, category: str, title: str, 
                     description: str, location: str, priority: str = 'Medium',
                     image_path: str = None) -> Tuple[bool, str, Optional[int]]:
        """
        Add a new complaint
        
        Args:
            user_id (int): ID of the user submitting the complaint
            category (str): Complaint category
            title (str): Complaint title
            description (str): Detailed description
            location (str): Location of the issue
            priority (str): Priority level
            image_path (str): Path to attached image (optional)
            
        Returns:
            Tuple: (success, message, complaint_id)
        """
        try:
            # Validate inputs
            if not title.strip():
                return False, "Title is required", None
            
            if not description.strip():
                return False, "Description is required", None
            
            if not location.strip():
                return False, "Location is required", None
            
            if priority not in self.priority_options:
                priority = 'Medium'
            
            # Insert complaint
            complaint_id = db.execute_insert(
                """INSERT INTO complaints 
                   (user_id, category, title, description, location, priority, image_path, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, category, title.strip(), description.strip(), 
                 location.strip(), priority, image_path, 'Pending')
            )
            
            # Add initial status update
            self.add_status_update(complaint_id, user_id, None, 'Pending', 
                                 'Complaint submitted')
            
            return True, "Complaint submitted successfully", complaint_id
            
        except Exception as e:
            return False, f"Failed to submit complaint: {str(e)}", None
    
    def get_user_complaints(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all complaints for a specific user
        
        Args:
            user_id (int): User ID
            
        Returns:
            List[Dict]: List of user's complaints
        """
        try:
            complaints = db.execute_query(
                """SELECT c.*, u.name as user_name, u.email as user_email
                   FROM complaints c
                   JOIN users u ON c.user_id = u.id
                   WHERE c.user_id = ?
                   ORDER BY c.created_at DESC""",
                (user_id,)
            )
            
            return [dict(complaint) for complaint in complaints]
            
        except Exception as e:
            print(f"Error fetching user complaints: {e}")
            return []
    
    def get_all_complaints(self, status_filter: str = None, 
                          category_filter: str = None) -> List[Dict[str, Any]]:
        """
        Get all complaints with optional filtering
        
        Args:
            status_filter (str): Filter by status (optional)
            category_filter (str): Filter by category (optional)
            
        Returns:
            List[Dict]: List of complaints
        """
        try:
            query = """SELECT c.*, u.name as user_name, u.email as user_email,
                              a.name as assigned_to_name
                       FROM complaints c
                       JOIN users u ON c.user_id = u.id
                       LEFT JOIN users a ON c.assigned_to = a.id
                       WHERE 1=1"""
            
            params = []
            
            if status_filter:
                query += " AND c.status = ?"
                params.append(status_filter)
            
            if category_filter:
                query += " AND c.category = ?"
                params.append(category_filter)
            
            query += " ORDER BY c.created_at DESC"
            
            complaints = db.execute_query(query, tuple(params))
            return [dict(complaint) for complaint in complaints]
            
        except Exception as e:
            print(f"Error fetching complaints: {e}")
            return []
    
    def get_complaint_by_id(self, complaint_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific complaint by ID
        
        Args:
            complaint_id (int): Complaint ID
            
        Returns:
            Optional[Dict]: Complaint data or None if not found
        """
        try:
            complaint = db.execute_query(
                """SELECT c.*, u.name as user_name, u.email as user_email,
                          a.name as assigned_to_name
                   FROM complaints c
                   JOIN users u ON c.user_id = u.id
                   LEFT JOIN users a ON c.assigned_to = a.id
                   WHERE c.id = ?""",
                (complaint_id,)
            )
            
            return dict(complaint[0]) if complaint else None
            
        except Exception as e:
            print(f"Error fetching complaint: {e}")
            return None
    
    def update_complaint_status(self, complaint_id: int, new_status: str, 
                               updated_by: int, notes: str = None,
                               assigned_to: int = None) -> Tuple[bool, str]:
        """
        Update complaint status
        
        Args:
            complaint_id (int): Complaint ID
            new_status (str): New status
            updated_by (int): User ID who is updating
            notes (str): Update notes (optional)
            assigned_to (int): Assign to user ID (optional)
            
        Returns:
            Tuple: (success, message)
        """
        try:
            if new_status not in self.status_options:
                return False, "Invalid status"
            
            # Get current complaint
            complaint = self.get_complaint_by_id(complaint_id)
            if not complaint:
                return False, "Complaint not found"
            
            old_status = complaint['status']
            
            # Update complaint
            update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
            params = [new_status]
            
            if assigned_to:
                update_fields.append("assigned_to = ?")
                params.append(assigned_to)
            
            if new_status == 'Resolved':
                update_fields.append("resolved_at = CURRENT_TIMESTAMP")
                if notes:
                    update_fields.append("resolution_notes = ?")
                    params.append(notes)
            
            params.append(complaint_id)
            
            query = f"UPDATE complaints SET {', '.join(update_fields)} WHERE id = ?"
            rows_affected = db.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                # Add status update record
                self.add_status_update(complaint_id, updated_by, old_status, 
                                     new_status, notes)
                
                return True, "Status updated successfully"
            else:
                return False, "Failed to update status"
                
        except Exception as e:
            return False, f"Status update failed: {str(e)}"
    
    def add_status_update(self, complaint_id: int, updated_by: int, 
                         old_status: str, new_status: str, 
                         update_notes: str = None) -> bool:
        """
        Add a status update record
        
        Args:
            complaint_id (int): Complaint ID
            updated_by (int): User ID who made the update
            old_status (str): Previous status
            new_status (str): New status
            update_notes (str): Update notes (optional)
            
        Returns:
            bool: Success status
        """
        try:
            db.execute_insert(
                """INSERT INTO status_updates 
                   (complaint_id, updated_by, old_status, new_status, update_notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (complaint_id, updated_by, old_status, new_status, update_notes)
            )
            return True
            
        except Exception as e:
            print(f"Error adding status update: {e}")
            return False
    
    def get_status_updates(self, complaint_id: int) -> List[Dict[str, Any]]:
        """
        Get status update history for a complaint
        
        Args:
            complaint_id (int): Complaint ID
            
        Returns:
            List[Dict]: List of status updates
        """
        try:
            updates = db.execute_query(
                """SELECT su.*, u.name as updated_by_name
                   FROM status_updates su
                   JOIN users u ON su.updated_by = u.id
                   WHERE su.complaint_id = ?
                   ORDER BY su.created_at ASC""",
                (complaint_id,)
            )
            
            return [dict(update) for update in updates]
            
        except Exception as e:
            print(f"Error fetching status updates: {e}")
            return []
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all complaint categories
        
        Returns:
            List[Dict]: List of categories
        """
        try:
            categories = db.execute_query(
                "SELECT * FROM categories ORDER BY name"
            )
            return [dict(category) for category in categories]
            
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []
    
    def get_complaint_statistics(self) -> Dict[str, Any]:
        """
        Get complaint statistics for dashboard
        
        Returns:
            Dict: Statistics data
        """
        try:
            # Total complaints
            total = db.execute_query("SELECT COUNT(*) as count FROM complaints")[0]['count']
            
            # Complaints by status
            status_stats = {}
            for status in self.status_options:
                count = db.execute_query(
                    "SELECT COUNT(*) as count FROM complaints WHERE status = ?", 
                    (status,)
                )[0]['count']
                status_stats[status] = count
            
            # Complaints by category
            category_stats = db.execute_query(
                """SELECT category, COUNT(*) as count 
                   FROM complaints 
                   GROUP BY category 
                   ORDER BY count DESC"""
            )
            
            # Recent complaints (last 7 days)
            recent = db.execute_query(
                """SELECT COUNT(*) as count 
                   FROM complaints 
                   WHERE created_at >= datetime('now', '-7 days')"""
            )[0]['count']
            
            return {
                'total_complaints': total,
                'status_breakdown': status_stats,
                'category_breakdown': [dict(stat) for stat in category_stats],
                'recent_complaints': recent
            }
            
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return {
                'total_complaints': 0,
                'status_breakdown': {},
                'category_breakdown': [],
                'recent_complaints': 0
            }
    
    def search_complaints(self, search_term: str, user_id: int = None) -> List[Dict[str, Any]]:
        """
        Search complaints by title, description, or location
        
        Args:
            search_term (str): Search term
            user_id (int): Filter by user ID (optional)
            
        Returns:
            List[Dict]: List of matching complaints
        """
        try:
            query = """SELECT c.*, u.name as user_name, u.email as user_email
                       FROM complaints c
                       JOIN users u ON c.user_id = u.id
                       WHERE (c.title LIKE ? OR c.description LIKE ? OR c.location LIKE ?)"""
            
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            
            if user_id:
                query += " AND c.user_id = ?"
                params.append(user_id)
            
            query += " ORDER BY c.created_at DESC"
            
            complaints = db.execute_query(query, tuple(params))
            return [dict(complaint) for complaint in complaints]
            
        except Exception as e:
            print(f"Error searching complaints: {e}")
            return []

# Global complaint manager instance
complaint_manager = ComplaintManager()

def add_complaint(user_id: int, category: str, title: str, description: str, 
                 location: str, priority: str = 'Medium', 
                 image_path: str = None) -> Tuple[bool, str, Optional[int]]:
    """Add a new complaint"""
    return complaint_manager.add_complaint(user_id, category, title, description, 
                                         location, priority, image_path)

def get_user_complaints(user_id: int) -> List[Dict[str, Any]]:
    """Get user's complaints"""
    return complaint_manager.get_user_complaints(user_id)

def get_all_complaints(status_filter: str = None, 
                      category_filter: str = None) -> List[Dict[str, Any]]:
    """Get all complaints with filtering"""
    return complaint_manager.get_all_complaints(status_filter, category_filter)

def get_complaint_by_id(complaint_id: int) -> Optional[Dict[str, Any]]:
    """Get complaint by ID"""
    return complaint_manager.get_complaint_by_id(complaint_id)

def update_complaint_status(complaint_id: int, new_status: str, updated_by: int, 
                           notes: str = None, assigned_to: int = None) -> Tuple[bool, str]:
    """Update complaint status"""
    return complaint_manager.update_complaint_status(complaint_id, new_status, 
                                                   updated_by, notes, assigned_to)

def get_status_updates(complaint_id: int) -> List[Dict[str, Any]]:
    """Get status updates for a complaint"""
    return complaint_manager.get_status_updates(complaint_id)

def get_categories() -> List[Dict[str, Any]]:
    """Get all categories"""
    return complaint_manager.get_categories()

def get_complaint_statistics() -> Dict[str, Any]:
    """Get complaint statistics"""
    return complaint_manager.get_complaint_statistics()

def search_complaints(search_term: str, user_id: int = None) -> List[Dict[str, Any]]:
    """Search complaints"""
    return complaint_manager.search_complaints(search_term, user_id)

