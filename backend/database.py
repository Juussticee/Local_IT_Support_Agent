"""
Database module for IT Support Agent System

This module handles all database operations using SQLite.
SQLite is a lightweight database that stores data in a single file - perfect for prototypes!

Key Concepts:
- Database: A structured way to store and retrieve data
- Table: Like a spreadsheet with rows and columns
- Schema: The structure/blueprint of our tables
- CRUD: Create, Read, Update, Delete operations
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

# Database file path - SQLite stores everything in one file
import os
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'it_support.db')

def init_database():
    """
    Initialize the database and create tables if they don't exist.
    This is like setting up the structure of our filing system.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create tickets table
    # Each field corresponds to our ticket requirements from the plan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing ID
            employee_name TEXT NOT NULL,                   -- Who reported the issue
            issue_description TEXT NOT NULL,               -- What's the problem
            priority TEXT DEFAULT 'Medium',                -- Low, Medium, High, Critical
            status TEXT DEFAULT 'New',                     -- New, In Progress, Resolved, Closed
            assigned_to TEXT,                              -- Which IT staff member
            resolution_code TEXT,                          -- How it was fixed
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- When was it created
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- When was it last updated
            log TEXT DEFAULT '[]'                          -- JSON array of all actions/AI responses
        )
    ''')
    
    # Create policies table to store IT policies and troubleshooting guides
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policies (
            policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create messages table for ticket communications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket_messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            sender_name TEXT NOT NULL,
            sender_type TEXT NOT NULL,  -- 'user', 'admin', 'system'
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id)
        )
    ''')
    
    # Create users table for admin authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',  -- 'user', 'admin', 'super_admin'
            full_name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create ticket_views table to track when tickets were last viewed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket_views (
            view_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,  -- username or session identifier
            last_viewed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticket_id, user_id),
            FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id)
        )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        # Default admin: username=admin, password=admin123 (change in production!)
        import hashlib
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', password_hash, 'admin', 'System Administrator', 'admin@company.com'))
        print("✅ Default admin user created (username: admin, password: admin123)")
    
    # Create sample tickets if none exist
    cursor.execute('SELECT COUNT(*) FROM tickets')
    ticket_count = cursor.fetchone()[0]
    
    if ticket_count == 0:
        sample_tickets = [
            ("John Smith", "Cannot access email - authentication failed error", "High", "New"),
            ("Sarah Johnson", "Computer running very slow, takes 10 minutes to boot", "Medium", "In Progress"), 
            ("Mike Davis", "Need Photoshop installed for marketing project", "Low", "New"),
            ("Lisa Wilson", "WiFi keeps disconnecting every few minutes", "High", "Resolved"),
            ("Tom Brown", "Printer not working - paper jam error", "Medium", "New")
        ]
        
        for employee, issue, priority, status in sample_tickets:
            cursor.execute('''
                INSERT INTO tickets (employee_name, issue_description, priority, status)
                VALUES (?, ?, ?, ?)
            ''', (employee, issue, priority, status))
        
        print("✅ Sample tickets created for testing")
        
        # Add some sample AI chat messages
        cursor.execute('SELECT ticket_id FROM tickets LIMIT 2')
        ticket_ids = cursor.fetchall()
        
        for ticket_id_row in ticket_ids:
            ticket_id = ticket_id_row[0]
            # Add user message
            cursor.execute('''
                INSERT INTO ticket_messages (ticket_id, sender_name, sender_type, message)
                VALUES (?, ?, ?, ?)
            ''', (ticket_id, "User", "user", "I need help with this issue. Can you provide guidance?"))
            
            # Add AI response
            cursor.execute('''
                INSERT INTO ticket_messages (ticket_id, sender_name, sender_type, message)
                VALUES (?, ?, ?, ?)
            ''', (ticket_id, "AI Assistant", "system", "I understand you're having this issue. Let me help you troubleshoot step by step:\n\n1. First, try restarting your computer\n2. Check if all cables are properly connected\n3. Clear your browser cache if it's a web-related issue\n\nIf these steps don't resolve the issue, please let me know what happens when you try each step."))
        
        print("✅ Sample AI chat messages created")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def create_ticket(employee_name: str, issue_description: str, priority: str = 'Medium') -> int:
    """
    Create a new support ticket.
    
    Args:
        employee_name: Name of the person reporting the issue
        issue_description: Description of the problem
        priority: Priority level (Low, Medium, High, Critical)
    
    Returns:
        ticket_id: The ID of the newly created ticket
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Insert new ticket
    cursor.execute('''
        INSERT INTO tickets (employee_name, issue_description, priority)
        VALUES (?, ?, ?)
    ''', (employee_name, issue_description, priority))
    
    ticket_id = cursor.lastrowid  # Get the ID of the ticket we just created
    
    # Add creation log entry
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'ticket_created',
        'details': f'Ticket created by {employee_name}',
        'priority': priority
    }
    add_log_entry(ticket_id, log_entry)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Ticket #{ticket_id} created successfully!")
    return ticket_id

def get_all_tickets() -> List[Dict]:
    """
    Retrieve all tickets from the database.
    
    Returns:
        List of dictionaries, each representing a ticket
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tickets ORDER BY created_at DESC')
    columns = [description[0] for description in cursor.description]
    tickets = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return tickets

def get_ticket(ticket_id: int) -> Optional[Dict]:
    """
    Get a specific ticket by ID.
    
    Args:
        ticket_id: The ID of the ticket to retrieve
    
    Returns:
        Dictionary representing the ticket, or None if not found
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM tickets WHERE ticket_id = ?', (ticket_id,))
    row = cursor.fetchone()
    
    if row:
        columns = [description[0] for description in cursor.description]
        ticket = dict(zip(columns, row))
        conn.close()
        return ticket
    
    conn.close()
    return None

def update_ticket(ticket_id: int, **updates) -> bool:
    """
    Update a ticket with new information.
    
    Args:
        ticket_id: The ID of the ticket to update
        **updates: Keyword arguments of fields to update
    
    Returns:
        True if successful, False otherwise
    """
    if not updates:
        return False
    
    conn = None
    try:
        # Use timeout to prevent lock issues
        conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query
        set_clause = ', '.join([f'{key} = ?' for key in updates.keys()])
        query = f'UPDATE tickets SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?'
        
        values = list(updates.values()) + [ticket_id]
        cursor.execute(query, values)
        
        # Log the update
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'ticket_updated',
            'details': f'Updated: {", ".join(updates.keys())}',
            'changes': updates
        }
        add_log_entry(ticket_id, log_entry)
        
        success = cursor.rowcount > 0
        conn.commit()
        return success
        
    except sqlite3.OperationalError as e:
        if conn:
            conn.rollback()
        print(f"Database lock error: {e}")
        return False
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def add_log_entry(ticket_id: int, log_entry: Dict):
    """
    Add a log entry to a ticket's history.
    This is crucial for tracking all AI interactions and ticket changes.
    
    Args:
        ticket_id: The ID of the ticket
        log_entry: Dictionary containing log information
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
        cursor = conn.cursor()
        
        # Get current log
        cursor.execute('SELECT log FROM tickets WHERE ticket_id = ?', (ticket_id,))
        result = cursor.fetchone()
        
        if result:
            current_log = json.loads(result[0] or '[]')
            current_log.append(log_entry)
            
            # Update the log
            cursor.execute('UPDATE tickets SET log = ? WHERE ticket_id = ?', 
                          (json.dumps(current_log), ticket_id))
            conn.commit()
    except Exception as e:
        print(f"Error adding log entry: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def search_tickets(query: str) -> List[Dict]:
    """
    Search tickets by employee name or issue description.
    
    Args:
        query: Search term
    
    Returns:
        List of matching tickets
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM tickets 
        WHERE employee_name LIKE ? OR issue_description LIKE ?
        ORDER BY created_at DESC
    ''', (f'%{query}%', f'%{query}%'))
    
    columns = [description[0] for description in cursor.description]
    tickets = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return tickets

def add_ticket_message(ticket_id: int, sender_name: str, sender_type: str, message: str) -> int:
    """
    Add a message to a ticket's communication history.
    
    Args:
        ticket_id: The ID of the ticket
        sender_name: Name of the person sending the message
        sender_type: Type of sender ('user', 'admin', 'system')
        message: The message content
    
    Returns:
        message_id: The ID of the newly created message
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ticket_messages (ticket_id, sender_name, sender_type, message)
        VALUES (?, ?, ?, ?)
    ''', (ticket_id, sender_name, sender_type, message))
    
    message_id = cursor.lastrowid
    
    # Update ticket's updated_at timestamp
    cursor.execute('UPDATE tickets SET updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?', (ticket_id,))
    
    conn.commit()
    conn.close()
    
    return message_id

def get_ticket_messages(ticket_id: int) -> List[Dict]:
    """
    Get all messages for a specific ticket.
    
    Args:
        ticket_id: The ID of the ticket
    
    Returns:
        List of message dictionaries
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM ticket_messages 
        WHERE ticket_id = ? 
        ORDER BY timestamp ASC
    ''', (ticket_id,))
    
    columns = [description[0] for description in cursor.description]
    messages = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return messages

def get_ticket_message_count(ticket_id: int) -> int:
    """
    Get the total count of messages for a specific ticket.
    
    Args:
        ticket_id: The ID of the ticket
    
    Returns:
        Number of messages
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM ticket_messages 
        WHERE ticket_id = ?
    ''', (ticket_id,))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_latest_message_timestamp(ticket_id: int) -> Optional[str]:
    """
    Get the timestamp of the latest message for a ticket.
    
    Args:
        ticket_id: The ID of the ticket
    
    Returns:
        Timestamp of latest message or None if no messages
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp FROM ticket_messages 
        WHERE ticket_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''', (ticket_id,))
    
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_ticket_view(ticket_id: int, user_id: str):
    """
    Update the last viewed timestamp for a ticket by a user.
    
    Args:
        ticket_id: The ID of the ticket
        user_id: Username or session identifier
    """
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)
    try:
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO ticket_views (ticket_id, user_id, last_viewed)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (ticket_id, user_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def has_new_messages(ticket_id: int, user_id: str) -> bool:
    """
    Check if a ticket has new messages since the user last viewed it.
    
    Args:
        ticket_id: The ID of the ticket
        user_id: Username or session identifier
    
    Returns:
        True if there are new messages, False otherwise
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get the last viewed timestamp
    cursor.execute('''
        SELECT last_viewed FROM ticket_views 
        WHERE ticket_id = ? AND user_id = ?
    ''', (ticket_id, user_id))
    
    result = cursor.fetchone()
    last_viewed = result[0] if result else None
    
    if not last_viewed:
        # If never viewed, check if there are any messages
        cursor.execute('''
            SELECT COUNT(*) FROM ticket_messages 
            WHERE ticket_id = ?
        ''', (ticket_id,))
        message_count = cursor.fetchone()[0]
        conn.close()
        return message_count > 0
    
    # Check if there are messages newer than last viewed
    cursor.execute('''
        SELECT COUNT(*) FROM ticket_messages 
        WHERE ticket_id = ? AND timestamp > ?
    ''', (ticket_id, last_viewed))
    
    new_message_count = cursor.fetchone()[0]
    conn.close()
    return new_message_count > 0

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user login.
    
    Args:
        username: Username
        password: Plain text password
    
    Returns:
        User dictionary if authentication successful, None otherwise
    """
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', 
                  (username, password_hash))
    row = cursor.fetchone()
    
    if row:
        columns = [description[0] for description in cursor.description]
        user = dict(zip(columns, row))
        conn.close()
        return user
    
    conn.close()
    return None

# Compatibility with existing code
def init_db():
    """Legacy function name - calls init_database()"""
    return init_database()

def insert_ticket(ticket_obj):
    """Legacy function - converts old ticket object to new format"""
    return create_ticket(
        ticket_obj.employee_name,
        ticket_obj.issue_description,
        getattr(ticket_obj, 'priority', 'Medium')
    )

# Initialize database when module is imported
if __name__ == '__main__':
    init_database()
    print("Database module ready!")
