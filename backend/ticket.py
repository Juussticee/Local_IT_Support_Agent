"""
Ticket Management Module for IT Support Agent System

This module contains the business logic for ticket operations.
Business logic = the rules and processes that define how your application works.

Think of this as the "brain" that coordinates between the database and the web interface.
"""

from typing import Dict, List, Optional
from datetime import datetime
import database as db

class TicketManager:
    """
    A class that manages all ticket operations.
    
    Classes in Python are like blueprints for creating objects.
    This class encapsulates (bundles together) all ticket-related functionality.
    """
    
    def __init__(self):
        """Initialize the ticket manager and ensure database is ready."""
        db.init_database()
    
    def create_ticket(self, employee_name: str, issue_description: str, 
                     priority: str = 'Medium') -> Dict:
        """
        Create a new support ticket with validation.
        
        Validation = checking that the input data is correct before saving it.
        
        Args:
            employee_name: Name of person reporting issue
            issue_description: Description of the problem
            priority: Priority level
            
        Returns:
            Dictionary with ticket information and success status
        """
        # Input validation - make sure we have required information
        if not employee_name or not employee_name.strip():
            return {
                'success': False,
                'error': 'Employee name is required',
                'ticket_id': None
            }
        
        if not issue_description or not issue_description.strip():
            return {
                'success': False,
                'error': 'Issue description is required',
                'ticket_id': None
            }
        
        # Validate priority level
        valid_priorities = ['Low', 'Medium', 'High', 'Critical']
        if priority not in valid_priorities:
            priority = 'Medium'  # Default fallback
        
        try:
            # Create the ticket in the database
            ticket_id = db.create_ticket(
                employee_name.strip(),
                issue_description.strip(),
                priority
            )
            
            return {
                'success': True,
                'message': f'Ticket #{ticket_id} created successfully',
                'ticket_id': ticket_id,
                'employee_name': employee_name.strip(),
                'issue_description': issue_description.strip(),
                'priority': priority,
                'status': 'New'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create ticket: {str(e)}',
                'ticket_id': None
            }
    
    def get_ticket_details(self, ticket_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific ticket.
        
        Args:
            ticket_id: The ID of the ticket to retrieve
            
        Returns:
            Ticket details or None if not found
        """
        try:
            ticket = db.get_ticket(ticket_id)
            if ticket:
                # Parse the log JSON for easier handling
                import json
                ticket['log'] = json.loads(ticket.get('log', '[]'))
            return ticket
        except Exception as e:
            print(f"Error retrieving ticket {ticket_id}: {e}")
            return None
    
    def update_ticket_status(self, ticket_id: int, new_status: str, 
                           assigned_to: str = None, notes: str = None) -> Dict:
        """
        Update a ticket's status and optionally assign it to someone.
        
        Args:
            ticket_id: The ticket to update
            new_status: New status (New, In Progress, Resolved, Closed)
            assigned_to: IT staff member to assign to (optional)
            notes: Additional notes about the update (optional)
            
        Returns:
            Dictionary with update result
        """
        # Validate status
        valid_statuses = ['New', 'In Progress', 'Resolved', 'Closed']
        if new_status not in valid_statuses:
            return {
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }
        
        try:
            # Prepare update data
            updates = {'status': new_status}
            if assigned_to:
                updates['assigned_to'] = assigned_to.strip()
            
            # Update the ticket
            success = db.update_ticket(ticket_id, **updates)
            
            if success:
                # Add detailed log entry
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'status_updated',
                    'old_status': 'Unknown',  # We could fetch this if needed
                    'new_status': new_status,
                    'assigned_to': assigned_to,
                    'notes': notes
                }
                db.add_log_entry(ticket_id, log_entry)
                
                return {
                    'success': True,
                    'message': f'Ticket #{ticket_id} updated to {new_status}',
                    'ticket_id': ticket_id,
                    'new_status': new_status
                }
            else:
                return {
                    'success': False,
                    'error': f'Ticket #{ticket_id} not found or could not be updated'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to update ticket: {str(e)}'
            }
    
    def resolve_ticket(self, ticket_id: int, resolution_code: str, 
                      resolved_by: str) -> Dict:
        """
        Mark a ticket as resolved with resolution details.
        
        Args:
            ticket_id: The ticket to resolve
            resolution_code: How the issue was resolved
            resolved_by: Who resolved it
            
        Returns:
            Dictionary with resolution result
        """
        if not resolution_code or not resolution_code.strip():
            return {
                'success': False,
                'error': 'Resolution code is required'
            }
        
        try:
            updates = {
                'status': 'Resolved',
                'resolution_code': resolution_code.strip(),
                'assigned_to': resolved_by.strip() if resolved_by else None
            }
            
            success = db.update_ticket(ticket_id, **updates)
            
            if success:
                # Add resolution log entry
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'ticket_resolved',
                    'resolved_by': resolved_by,
                    'resolution_code': resolution_code.strip(),
                    'details': 'Ticket marked as resolved'
                }
                db.add_log_entry(ticket_id, log_entry)
                
                return {
                    'success': True,
                    'message': f'Ticket #{ticket_id} resolved successfully',
                    'ticket_id': ticket_id,
                    'resolution_code': resolution_code.strip()
                }
            else:
                return {
                    'success': False,
                    'error': f'Ticket #{ticket_id} not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to resolve ticket: {str(e)}'
            }
    
    def get_all_tickets(self, status_filter: str = None) -> List[Dict]:
        """
        Get all tickets, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of tickets
        """
        try:
            tickets = db.get_all_tickets()
            
            # Apply status filter if provided
            if status_filter and status_filter != 'All':
                tickets = [t for t in tickets if t.get('status') == status_filter]
            
            # Parse log JSON for each ticket
            import json
            for ticket in tickets:
                ticket['log'] = json.loads(ticket.get('log', '[]'))
            
            return tickets
            
        except Exception as e:
            print(f"Error retrieving tickets: {e}")
            return []
    
    def search_tickets(self, query: str) -> List[Dict]:
        """
        Search tickets by employee name or issue description.
        
        Args:
            query: Search term
            
        Returns:
            List of matching tickets
        """
        try:
            tickets = db.search_tickets(query)
            
            # Parse log JSON for each ticket
            import json
            for ticket in tickets:
                ticket['log'] = json.loads(ticket.get('log', '[]'))
            
            return tickets
            
        except Exception as e:
            print(f"Error searching tickets: {e}")
            return []
    
    def get_ticket_statistics(self) -> Dict:
        """
        Get statistics about tickets for dashboard/reporting.
        
        Returns:
            Dictionary with various statistics
        """
        try:
            all_tickets = self.get_all_tickets()
            
            # Calculate statistics
            total_tickets = len(all_tickets)
            status_counts = {}
            priority_counts = {}
            
            for ticket in all_tickets:
                # Count by status
                status = ticket.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count by priority
                priority = ticket.get('priority', 'Unknown')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            return {
                'total_tickets': total_tickets,
                'status_breakdown': status_counts,
                'priority_breakdown': priority_counts,
                'open_tickets': status_counts.get('New', 0) + status_counts.get('In Progress', 0),
                'resolved_tickets': status_counts.get('Resolved', 0),
                'closed_tickets': status_counts.get('Closed', 0)
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return {
                'total_tickets': 0,
                'status_breakdown': {},
                'priority_breakdown': {},
                'open_tickets': 0,
                'resolved_tickets': 0,
                'closed_tickets': 0
            }

    def update_ticket_assignment(self, ticket_id: int, assigned_to: str) -> Dict:
        """Update ticket assignment and status."""
        try:
            updates = {
                'assigned_to': assigned_to,
                'status': 'In Progress' if assigned_to else 'Open'
            }
            
            success = db.update_ticket(ticket_id, **updates)
            
            if success:
                action = f"assigned to {assigned_to}" if assigned_to else "unassigned"
                
                # Add log entry
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'assignment_updated',
                    'assigned_to': assigned_to,
                    'details': f'Ticket {action}'
                }
                db.add_log_entry(ticket_id, log_entry)
                
                return {
                    'success': True,
                    'message': f'Ticket #{ticket_id} {action} successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to assign ticket: Ticket not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to assign ticket: {str(e)}'
            }


# Example usage and testing
if __name__ == '__main__':
    # Create a ticket manager instance
    tm = TicketManager()
    
    # Test creating a ticket
    result = tm.create_ticket(
        "John Doe", 
        "Can't log into email account", 
        "High"
    )
    print("Create ticket result:", result)
    
    # Test getting all tickets
    tickets = tm.get_all_tickets()
    print(f"Total tickets: {len(tickets)}")
    
    # Test statistics
    stats = tm.get_ticket_statistics()
    print("Statistics:", stats)
