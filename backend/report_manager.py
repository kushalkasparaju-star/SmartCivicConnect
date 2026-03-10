"""
Report generation module for Neighborhood Complaint & Feedback System
Handles report generation, analytics, and data export functionality
"""

import csv
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from database.db_connection import db
from backend.complaint_manager import complaint_manager
from backend.feedback_manager import feedback_manager
from backend.admin_manager import admin_manager

class ReportManager:
    """Manages report generation and analytics"""
    
    def __init__(self):
        self.report_types = ['complaints', 'feedback', 'users', 'analytics']
    
    def generate_complaints_report(self, start_date: str = None, end_date: str = None,
                                  status_filter: str = None, category_filter: str = None,
                                  format: str = 'json') -> Dict[str, Any]:
        """
        Generate comprehensive complaints report
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            status_filter (str): Filter by status
            category_filter (str): Filter by category
            format (str): Output format ('json', 'csv')
            
        Returns:
            Dict: Report data
        """
        try:
            # Get complaints data
            complaints = admin_manager.export_complaints_report(start_date, end_date)
            
            # Apply additional filters
            if status_filter:
                complaints = [c for c in complaints if c['status'] == status_filter]
            
            if category_filter:
                complaints = [c for c in complaints if c['category'] == category_filter]
            
            # Generate summary statistics
            total_complaints = len(complaints)
            status_breakdown = {}
            category_breakdown = {}
            priority_breakdown = {}
            
            for complaint in complaints:
                # Status breakdown
                status = complaint['status']
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
                
                # Category breakdown
                category = complaint['category']
                category_breakdown[category] = category_breakdown.get(category, 0) + 1
                
                # Priority breakdown
                priority = complaint['priority']
                priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
            
            # Calculate resolution time for resolved complaints
            resolution_times = []
            for complaint in complaints:
                if complaint['status'] == 'Resolved' and complaint['resolved_at']:
                    created = datetime.fromisoformat(complaint['created_at'].replace('Z', '+00:00'))
                    resolved = datetime.fromisoformat(complaint['resolved_at'].replace('Z', '+00:00'))
                    resolution_time = (resolved - created).days
                    resolution_times.append(resolution_time)
            
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            report_data = {
                'report_info': {
                    'generated_at': datetime.now().isoformat(),
                    'date_range': {
                        'start_date': start_date,
                        'end_date': end_date
                    },
                    'filters': {
                        'status': status_filter,
                        'category': category_filter
                    },
                    'total_complaints': total_complaints
                },
                'summary': {
                    'status_breakdown': status_breakdown,
                    'category_breakdown': category_breakdown,
                    'priority_breakdown': priority_breakdown,
                    'average_resolution_time_days': round(avg_resolution_time, 2)
                },
                'complaints': complaints
            }
            
            if format == 'csv':
                return self._convert_to_csv(report_data, 'complaints')
            
            return report_data
            
        except Exception as e:
            return {'error': f"Failed to generate complaints report: {str(e)}"}
    
    def generate_feedback_report(self, start_date: str = None, end_date: str = None,
                                format: str = 'json') -> Dict[str, Any]:
        """
        Generate feedback report
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            format (str): Output format ('json', 'csv')
            
        Returns:
            Dict: Report data
        """
        try:
            # Get feedback data
            query = """SELECT f.*, u.name as user_name, c.title as complaint_title,
                              c.category, c.status as complaint_status
                       FROM feedback f
                       JOIN users u ON f.user_id = u.id
                       JOIN complaints c ON f.complaint_id = c.id
                       WHERE 1=1"""
            
            params = []
            
            if start_date:
                query += " AND DATE(f.created_at) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(f.created_at) <= ?"
                params.append(end_date)
            
            query += " ORDER BY f.created_at DESC"
            
            feedback_data = db.execute_query(query, tuple(params))
            feedback_list = [dict(feedback) for feedback in feedback_data]
            
            # Generate summary statistics
            total_feedback = len(feedback_list)
            rating_breakdown = {}
            category_breakdown = {}
            
            total_rating = 0
            for feedback in feedback_list:
                rating = feedback['rating']
                rating_breakdown[rating] = rating_breakdown.get(rating, 0) + 1
                total_rating += rating
                
                category = feedback['category']
                category_breakdown[category] = category_breakdown.get(category, 0) + 1
            
            avg_rating = total_rating / total_feedback if total_feedback > 0 else 0
            
            # Feedback with comments
            feedback_with_comments = len([f for f in feedback_list if f['comment']])
            
            report_data = {
                'report_info': {
                    'generated_at': datetime.now().isoformat(),
                    'date_range': {
                        'start_date': start_date,
                        'end_date': end_date
                    },
                    'total_feedback': total_feedback
                },
                'summary': {
                    'average_rating': round(avg_rating, 2),
                    'rating_breakdown': rating_breakdown,
                    'category_breakdown': category_breakdown,
                    'feedback_with_comments': feedback_with_comments,
                    'feedback_without_comments': total_feedback - feedback_with_comments
                },
                'feedback': feedback_list
            }
            
            if format == 'csv':
                return self._convert_to_csv(report_data, 'feedback')
            
            return report_data
            
        except Exception as e:
            return {'error': f"Failed to generate feedback report: {str(e)}"}
    
    def generate_analytics_report(self, period: str = '30_days') -> Dict[str, Any]:
        """
        Generate analytics report
        
        Args:
            period (str): Time period ('7_days', '30_days', '90_days', '1_year')
            
        Returns:
            Dict: Analytics data
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            if period == '7_days':
                start_date = end_date - timedelta(days=7)
            elif period == '30_days':
                start_date = end_date - timedelta(days=30)
            elif period == '90_days':
                start_date = end_date - timedelta(days=90)
            elif period == '1_year':
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Get system statistics
            system_stats = admin_manager.get_system_statistics()
            
            # Get complaints trend
            complaints_trend = self._get_complaints_trend(start_date_str, end_date_str)
            
            # Get feedback trend
            feedback_trend = self._get_feedback_trend(start_date_str, end_date_str)
            
            # Get user registration trend
            user_trend = self._get_user_trend(start_date_str, end_date_str)
            
            # Get top performing categories (by resolution time)
            top_categories = self._get_category_performance(start_date_str, end_date_str)
            
            # Get response time analysis
            response_time_analysis = self._get_response_time_analysis(start_date_str, end_date_str)
            
            analytics_data = {
                'report_info': {
                    'generated_at': datetime.now().isoformat(),
                    'period': period,
                    'date_range': {
                        'start_date': start_date_str,
                        'end_date': end_date_str
                    }
                },
                'system_overview': system_stats,
                'trends': {
                    'complaints': complaints_trend,
                    'feedback': feedback_trend,
                    'users': user_trend
                },
                'performance': {
                    'top_categories': top_categories,
                    'response_time_analysis': response_time_analysis
                }
            }
            
            return analytics_data
            
        except Exception as e:
            return {'error': f"Failed to generate analytics report: {str(e)}"}
    
    def _get_complaints_trend(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get complaints trend over time"""
        try:
            trend_data = db.execute_query(
                """SELECT DATE(created_at) as date, COUNT(*) as count
                   FROM complaints
                   WHERE DATE(created_at) BETWEEN ? AND ?
                   GROUP BY DATE(created_at)
                   ORDER BY date""",
                (start_date, end_date)
            )
            
            return [dict(day) for day in trend_data]
        except Exception as e:
            print(f"Error getting complaints trend: {e}")
            return []
    
    def _get_feedback_trend(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get feedback trend over time"""
        try:
            trend_data = db.execute_query(
                """SELECT DATE(created_at) as date, COUNT(*) as count, AVG(rating) as avg_rating
                   FROM feedback
                   WHERE DATE(created_at) BETWEEN ? AND ?
                   GROUP BY DATE(created_at)
                   ORDER BY date""",
                (start_date, end_date)
            )
            
            return [dict(day) for day in trend_data]
        except Exception as e:
            print(f"Error getting feedback trend: {e}")
            return []
    
    def _get_user_trend(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get user registration trend over time"""
        try:
            trend_data = db.execute_query(
                """SELECT DATE(created_at) as date, COUNT(*) as count
                   FROM users
                   WHERE DATE(created_at) BETWEEN ? AND ?
                   GROUP BY DATE(created_at)
                   ORDER BY date""",
                (start_date, end_date)
            )
            
            return [dict(day) for day in trend_data]
        except Exception as e:
            print(f"Error getting user trend: {e}")
            return []
    
    def _get_category_performance(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get category performance metrics"""
        try:
            performance_data = db.execute_query(
                """SELECT category, 
                          COUNT(*) as total_complaints,
                          AVG(CASE WHEN status = 'Resolved' AND resolved_at IS NOT NULL 
                              THEN (julianday(resolved_at) - julianday(created_at)) 
                              ELSE NULL END) as avg_resolution_days,
                          COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_count
                   FROM complaints
                   WHERE DATE(created_at) BETWEEN ? AND ?
                   GROUP BY category
                   ORDER BY avg_resolution_days ASC""",
                (start_date, end_date)
            )
            
            return [dict(cat) for cat in performance_data]
        except Exception as e:
            print(f"Error getting category performance: {e}")
            return []
    
    def _get_response_time_analysis(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get response time analysis"""
        try:
            # Get complaints with status updates
            response_data = db.execute_query(
                """SELECT c.id, c.created_at, su.created_at as first_update
                   FROM complaints c
                   JOIN status_updates su ON c.id = su.complaint_id
                   WHERE DATE(c.created_at) BETWEEN ? AND ?
                   AND su.old_status = 'Pending'
                   GROUP BY c.id
                   HAVING MIN(su.created_at)""",
                (start_date, end_date)
            )
            
            response_times = []
            for row in response_data:
                created = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                updated = datetime.fromisoformat(row['first_update'].replace('Z', '+00:00'))
                response_time = (updated - created).total_seconds() / 3600  # hours
                response_times.append(response_time)
            
            if response_times:
                return {
                    'average_response_time_hours': round(sum(response_times) / len(response_times), 2),
                    'min_response_time_hours': round(min(response_times), 2),
                    'max_response_time_hours': round(max(response_times), 2),
                    'total_analyzed': len(response_times)
                }
            else:
                return {
                    'average_response_time_hours': 0,
                    'min_response_time_hours': 0,
                    'max_response_time_hours': 0,
                    'total_analyzed': 0
                }
                
        except Exception as e:
            print(f"Error getting response time analysis: {e}")
            return {}
    
    def _convert_to_csv(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Convert report data to CSV format"""
        try:
            csv_data = []
            
            if report_type == 'complaints':
                # Add summary row
                csv_data.append(['SUMMARY'])
                csv_data.append(['Total Complaints', report_data['report_info']['total_complaints']])
                csv_data.append([''])
                
                # Add status breakdown
                csv_data.append(['STATUS BREAKDOWN'])
                for status, count in report_data['summary']['status_breakdown'].items():
                    csv_data.append([status, count])
                csv_data.append([''])
                
                # Add category breakdown
                csv_data.append(['CATEGORY BREAKDOWN'])
                for category, count in report_data['summary']['category_breakdown'].items():
                    csv_data.append([category, count])
                csv_data.append([''])
                
                # Add complaints data
                csv_data.append(['COMPLAINTS DATA'])
                if report_data['complaints']:
                    headers = list(report_data['complaints'][0].keys())
                    csv_data.append(headers)
                    for complaint in report_data['complaints']:
                        csv_data.append([complaint.get(header, '') for header in headers])
            
            elif report_type == 'feedback':
                # Add summary row
                csv_data.append(['SUMMARY'])
                csv_data.append(['Total Feedback', report_data['report_info']['total_feedback']])
                csv_data.append(['Average Rating', report_data['summary']['average_rating']])
                csv_data.append([''])
                
                # Add rating breakdown
                csv_data.append(['RATING BREAKDOWN'])
                for rating, count in report_data['summary']['rating_breakdown'].items():
                    csv_data.append([f'Rating {rating}', count])
                csv_data.append([''])
                
                # Add feedback data
                csv_data.append(['FEEDBACK DATA'])
                if report_data['feedback']:
                    headers = list(report_data['feedback'][0].keys())
                    csv_data.append(headers)
                    for feedback in report_data['feedback']:
                        csv_data.append([feedback.get(header, '') for header in headers])
            
            # Convert to CSV string
            csv_string = ""
            for row in csv_data:
                csv_string += ','.join([str(cell) for cell in row]) + '\n'
            
            return csv_string
            
        except Exception as e:
            return f"Error converting to CSV: {str(e)}"
    
    def save_report_to_file(self, report_data: Dict[str, Any], filename: str, 
                           format: str = 'json') -> bool:
        """
        Save report to file
        
        Args:
            report_data (Dict): Report data
            filename (str): Filename to save to
            format (str): File format ('json', 'csv')
            
        Returns:
            bool: Success status
        """
        try:
            if format == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, default=str)
            elif format == 'csv':
                with open(filename, 'w', encoding='utf-8', newline='') as f:
                    f.write(report_data)
            
            return True
            
        except Exception as e:
            print(f"Error saving report to file: {e}")
            return False

# Global report manager instance
report_manager = ReportManager()

def generate_complaints_report(start_date: str = None, end_date: str = None,
                              status_filter: str = None, category_filter: str = None,
                              format: str = 'json') -> Dict[str, Any]:
    """Generate complaints report"""
    return report_manager.generate_complaints_report(start_date, end_date, 
                                                   status_filter, category_filter, format)

def generate_feedback_report(start_date: str = None, end_date: str = None,
                            format: str = 'json') -> Dict[str, Any]:
    """Generate feedback report"""
    return report_manager.generate_feedback_report(start_date, end_date, format)

def generate_analytics_report(period: str = '30_days') -> Dict[str, Any]:
    """Generate analytics report"""
    return report_manager.generate_analytics_report(period)

def save_report_to_file(report_data: Dict[str, Any], filename: str, format: str = 'json') -> bool:
    """Save report to file"""
    return report_manager.save_report_to_file(report_data, filename, format)

