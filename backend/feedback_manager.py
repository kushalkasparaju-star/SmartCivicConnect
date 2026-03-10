"""
Feedback management module for Neighborhood Complaint & Feedback System
Handles feedback submission, retrieval, and rating management
"""

from typing import List, Dict, Any, Optional, Tuple
from database.db_connection import db

class FeedbackManager:
    """Manages feedback operations for resolved complaints"""
    
    def __init__(self):
        self.rating_options = [1, 2, 3, 4, 5]
        self.rating_labels = {
            1: "Very Poor",
            2: "Poor", 
            3: "Average",
            4: "Good",
            5: "Excellent"
        }
    
    def add_feedback(self, complaint_id: int, user_id: int, rating: int, 
                    comment: str = None) -> Tuple[bool, str]:
        """
        Add feedback for a resolved complaint
        
        Args:
            complaint_id (int): ID of the complaint
            user_id (int): ID of the user providing feedback
            rating (int): Rating from 1-5
            comment (str): Optional comment
            
        Returns:
            Tuple: (success, message)
        """
        try:
            # Validate rating
            if rating not in self.rating_options:
                return False, "Rating must be between 1 and 5"
            
            # Check if complaint exists and is resolved
            complaint = db.execute_query(
                "SELECT status, user_id FROM complaints WHERE id = ?", 
                (complaint_id,)
            )
            
            if not complaint:
                return False, "Complaint not found"
            
            if complaint[0]['status'] != 'Resolved':
                return False, "Feedback can only be provided for resolved complaints"
            
            # Check if user is the original complainant
            if complaint[0]['user_id'] != user_id:
                return False, "Only the original complainant can provide feedback"
            
            # Check if feedback already exists
            existing_feedback = db.execute_query(
                "SELECT id FROM feedback WHERE complaint_id = ? AND user_id = ?",
                (complaint_id, user_id)
            )
            
            if existing_feedback:
                return False, "Feedback already provided for this complaint"
            
            # Insert feedback
            db.execute_insert(
                """INSERT INTO feedback (complaint_id, user_id, rating, comment)
                   VALUES (?, ?, ?, ?)""",
                (complaint_id, user_id, rating, comment.strip() if comment else None)
            )
            
            return True, "Feedback submitted successfully"
            
        except Exception as e:
            return False, f"Failed to submit feedback: {str(e)}"
    
    def get_feedback_by_complaint(self, complaint_id: int) -> Optional[Dict[str, Any]]:
        """
        Get feedback for a specific complaint
        
        Args:
            complaint_id (int): Complaint ID
            
        Returns:
            Optional[Dict]: Feedback data or None if not found
        """
        try:
            feedback = db.execute_query(
                """SELECT f.*, u.name as user_name
                   FROM feedback f
                   JOIN users u ON f.user_id = u.id
                   WHERE f.complaint_id = ?""",
                (complaint_id,)
            )
            
            return dict(feedback[0]) if feedback else None
            
        except Exception as e:
            print(f"Error fetching feedback: {e}")
            return None
    
    def get_user_feedback(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all feedback provided by a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            List[Dict]: List of user's feedback
        """
        try:
            feedback_list = db.execute_query(
                """SELECT f.*, c.title as complaint_title, c.category
                   FROM feedback f
                   JOIN complaints c ON f.complaint_id = c.id
                   WHERE f.user_id = ?
                   ORDER BY f.created_at DESC""",
                (user_id,)
            )
            
            return [dict(feedback) for feedback in feedback_list]
            
        except Exception as e:
            print(f"Error fetching user feedback: {e}")
            return []
    
    def get_all_feedback(self) -> List[Dict[str, Any]]:
        """
        Get all feedback in the system
        
        Returns:
            List[Dict]: List of all feedback
        """
        try:
            feedback_list = db.execute_query(
                """SELECT f.*, u.name as user_name, c.title as complaint_title, 
                          c.category, c.status as complaint_status
                   FROM feedback f
                   JOIN users u ON f.user_id = u.id
                   JOIN complaints c ON f.complaint_id = c.id
                   ORDER BY f.created_at DESC"""
            )
            
            return [dict(feedback) for feedback in feedback_list]
            
        except Exception as e:
            print(f"Error fetching all feedback: {e}")
            return []
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        Get feedback statistics
        
        Returns:
            Dict: Feedback statistics
        """
        try:
            # Total feedback count
            total = db.execute_query("SELECT COUNT(*) as count FROM feedback")[0]['count']
            
            # Average rating
            avg_rating = db.execute_query(
                "SELECT AVG(rating) as avg_rating FROM feedback"
            )[0]['avg_rating']
            
            # Rating distribution
            rating_dist = {}
            for rating in self.rating_options:
                count = db.execute_query(
                    "SELECT COUNT(*) as count FROM feedback WHERE rating = ?",
                    (rating,)
                )[0]['count']
                rating_dist[rating] = count
            
            # Feedback with comments
            with_comments = db.execute_query(
                "SELECT COUNT(*) as count FROM feedback WHERE comment IS NOT NULL AND comment != ''"
            )[0]['count']
            
            return {
                'total_feedback': total,
                'average_rating': round(avg_rating, 2) if avg_rating else 0,
                'rating_distribution': rating_dist,
                'feedback_with_comments': with_comments,
                'rating_labels': self.rating_labels
            }
            
        except Exception as e:
            print(f"Error fetching feedback statistics: {e}")
            return {
                'total_feedback': 0,
                'average_rating': 0,
                'rating_distribution': {},
                'feedback_with_comments': 0,
                'rating_labels': self.rating_labels
            }
    
    def get_complaint_rating_summary(self, complaint_id: int) -> Dict[str, Any]:
        """
        Get rating summary for a specific complaint
        
        Args:
            complaint_id (int): Complaint ID
            
        Returns:
            Dict: Rating summary
        """
        try:
            feedback = self.get_feedback_by_complaint(complaint_id)
            
            if not feedback:
                return {
                    'has_feedback': False,
                    'rating': 0,
                    'rating_label': 'No Rating',
                    'comment': None
                }
            
            return {
                'has_feedback': True,
                'rating': feedback['rating'],
                'rating_label': self.rating_labels[feedback['rating']],
                'comment': feedback['comment'],
                'submitted_at': feedback['created_at']
            }
            
        except Exception as e:
            print(f"Error fetching complaint rating summary: {e}")
            return {
                'has_feedback': False,
                'rating': 0,
                'rating_label': 'No Rating',
                'comment': None
            }
    
    def can_provide_feedback(self, complaint_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Check if user can provide feedback for a complaint
        
        Args:
            complaint_id (int): Complaint ID
            user_id (int): User ID
            
        Returns:
            Tuple: (can_provide, reason)
        """
        try:
            # Check if complaint exists
            complaint = db.execute_query(
                "SELECT status, user_id FROM complaints WHERE id = ?",
                (complaint_id,)
            )
            
            if not complaint:
                return False, "Complaint not found"
            
            complaint_data = complaint[0]
            
            # Check if complaint is resolved
            if complaint_data['status'] != 'Resolved':
                return False, "Complaint must be resolved before providing feedback"
            
            # Check if user is the original complainant
            if complaint_data['user_id'] != user_id:
                return False, "Only the original complainant can provide feedback"
            
            # Check if feedback already exists
            existing_feedback = db.execute_query(
                "SELECT id FROM feedback WHERE complaint_id = ? AND user_id = ?",
                (complaint_id, user_id)
            )
            
            if existing_feedback:
                return False, "Feedback already provided for this complaint"
            
            return True, "Can provide feedback"
            
        except Exception as e:
            return False, f"Error checking feedback eligibility: {str(e)}"
    
    def update_feedback(self, feedback_id: int, user_id: int, rating: int = None,
                       comment: str = None) -> Tuple[bool, str]:
        """
        Update existing feedback
        
        Args:
            feedback_id (int): Feedback ID
            user_id (int): User ID (for verification)
            rating (int): New rating (optional)
            comment (str): New comment (optional)
            
        Returns:
            Tuple: (success, message)
        """
        try:
            # Check if feedback exists and belongs to user
            feedback = db.execute_query(
                "SELECT user_id FROM feedback WHERE id = ?",
                (feedback_id,)
            )
            
            if not feedback:
                return False, "Feedback not found"
            
            if feedback[0]['user_id'] != user_id:
                return False, "You can only update your own feedback"
            
            # Validate rating if provided
            if rating is not None and rating not in self.rating_options:
                return False, "Rating must be between 1 and 5"
            
            # Build update query
            updates = []
            params = []
            
            if rating is not None:
                updates.append("rating = ?")
                params.append(rating)
            
            if comment is not None:
                updates.append("comment = ?")
                params.append(comment.strip() if comment else None)
            
            if not updates:
                return False, "No updates provided"
            
            params.append(feedback_id)
            
            query = f"UPDATE feedback SET {', '.join(updates)} WHERE id = ?"
            rows_affected = db.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                return True, "Feedback updated successfully"
            else:
                return False, "Failed to update feedback"
                
        except Exception as e:
            return False, f"Failed to update feedback: {str(e)}"

# Global feedback manager instance
feedback_manager = FeedbackManager()

def add_feedback(complaint_id: int, user_id: int, rating: int, 
                comment: str = None) -> Tuple[bool, str]:
    """Add feedback for a complaint"""
    return feedback_manager.add_feedback(complaint_id, user_id, rating, comment)

def get_feedback_by_complaint(complaint_id: int) -> Optional[Dict[str, Any]]:
    """Get feedback for a complaint"""
    return feedback_manager.get_feedback_by_complaint(complaint_id)

def get_user_feedback(user_id: int) -> List[Dict[str, Any]]:
    """Get user's feedback"""
    return feedback_manager.get_user_feedback(user_id)

def get_all_feedback() -> List[Dict[str, Any]]:
    """Get all feedback"""
    return feedback_manager.get_all_feedback()

def get_feedback_statistics() -> Dict[str, Any]:
    """Get feedback statistics"""
    return feedback_manager.get_feedback_statistics()

def get_complaint_rating_summary(complaint_id: int) -> Dict[str, Any]:
    """Get rating summary for a complaint"""
    return feedback_manager.get_complaint_rating_summary(complaint_id)

def can_provide_feedback(complaint_id: int, user_id: int) -> Tuple[bool, str]:
    """Check if user can provide feedback"""
    return feedback_manager.can_provide_feedback(complaint_id, user_id)

def update_feedback(feedback_id: int, user_id: int, rating: int = None,
                   comment: str = None) -> Tuple[bool, str]:
    """Update feedback"""
    return feedback_manager.update_feedback(feedback_id, user_id, rating, comment)

