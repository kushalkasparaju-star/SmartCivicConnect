"""
Database connection module for Neighborhood Complaint & Feedback System
Handles SQLite database connection and provides connection management
"""

import sqlite3
import os
from typing import Optional

class DatabaseConnection:
    """Manages database connection and provides connection methods"""
    
    def __init__(self, db_path: str = "neighborhood_complaints.db"):
        """
        Initialize database connection
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """
        Establish connection to SQLite database
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            return self.connection
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get existing connection or create new one
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        if self.connection is None:
            return self.connect()
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute a SELECT query and return results
        
        Args:
            query (str): SQL SELECT query
            params (tuple): Query parameters
            
        Returns:
            list: Query results
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query
        
        Args:
            query (str): SQL query
            params (tuple): Query parameters
            
        Returns:
            int: Number of affected rows
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error executing update: {e}")
            conn.rollback()
            raise
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT query and return the last row ID
        
        Args:
            query (str): SQL INSERT query
            params (tuple): Query parameters
            
        Returns:
            int: Last inserted row ID
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error executing insert: {e}")
            conn.rollback()
            raise

# Global database instance
db = DatabaseConnection()

def get_db_connection() -> sqlite3.Connection:
    """
    Get database connection instance
    
    Returns:
        sqlite3.Connection: Database connection
    """
    return db.get_connection()

def close_db_connection():
    """Close database connection"""
    db.close()

