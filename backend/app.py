"""
This is the main application file that creates our web interface.
It handles HTTP requests, serves web pages, and coordinates between
the database, AI agent, and user interface.

Key Concepts:
- Flask: A Python web framework for building web applications
- Routes: URL endpoints that handle different types of requests
- Templates: HTML files that create the user interface
- API Endpoints: URLs that return JSON data for frontend JavaScript
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from database import authenticate_user
import os
import sys
from datetime import datetime

# Add current directory to Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
from database import (init_database, create_ticket, get_all_tickets, get_ticket, 
                     update_ticket, search_tickets, add_ticket_message, 
                     get_ticket_messages, has_new_messages, update_ticket_view)
from ticket import TicketManager
from llm_client import get_agent

# Create Flask application instance
app = Flask(__name__, 
                   template_folder='../frontend/templates',
                   static_folder='../frontend/static')
app.secret_key = 'your-secret-key-here'  # Change this in production!

# Initialize our components
ticket_manager = TicketManager()
ai_agent = None  # Will be initialized when first needed

def get_ai_agent():
    """
    Lazy loading of AI agent - only create it when needed.
    This prevents errors if API keys are not configured.
    """
    global ai_agent
    if ai_agent is None:
        try:
            ai_agent = get_agent()
        except Exception as e:
            print(f"Warning: Could not initialize AI agent: {e}")
            ai_agent = None
    return ai_agent

# --- Admin Authentication & Dashboard Routes ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Admin login page (GET) and login handler (POST).
    """
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        user = authenticate_user(username, password)
        if user and user.get('role') == 'admin':
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Log out the admin user."""
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """
    Admin dashboard page for IT staff to manage tickets.
    """
    if 'role' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    # Get filter parameters
    status_filter = request.args.get('status', 'Active')
    assignee_filter = request.args.get('assignee', '')
    priority_filter = request.args.get('priority', '')
    
    stats = ticket_manager.get_ticket_statistics()
    
    # Get all tickets and apply filters
    all_tickets = ticket_manager.get_all_tickets()
    
    # Add new message indicators
    current_user = session.get('username', 'admin')
    for ticket in all_tickets:
        ticket['has_new_messages'] = has_new_messages(ticket['ticket_id'], current_user)
    
    filtered_tickets = []
    
    for ticket in all_tickets:
        # Status filter
        if status_filter == 'Active':
            if ticket.get('status') not in ['New', 'In Progress']:
                continue
        elif status_filter != 'All' and ticket.get('status') != status_filter:
            continue
        
        # Assignee filter
        if assignee_filter:
            if assignee_filter == 'unassigned':
                if ticket.get('assigned_to'):
                    continue
            elif ticket.get('assigned_to') != assignee_filter:
                continue
        
        # Priority filter
        if priority_filter and ticket.get('priority') != priority_filter:
            continue
        
        filtered_tickets.append(ticket)
    
    # Limit to recent tickets for dashboard (latest 20)
    recent_tickets = sorted(filtered_tickets, key=lambda x: x.get('created_at', ''), reverse=True)[:20]
    
    user = {
        'username': session.get('username'),
        'full_name': session.get('full_name'),
        'role': session.get('role')
    }
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_tickets=recent_tickets, 
                         user=user,
                         status_filter=status_filter,
                         assignee_filter=assignee_filter,
                         priority_filter=priority_filter)

@app.route('/')
def index():
    """
    Home page - shows dashboard with ticket statistics and quick actions.
    
    This is the main landing page users see when they visit the website.
    """
    try:
        # Get ticket statistics for dashboard
        stats = ticket_manager.get_ticket_statistics()
        
        # Get recent tickets (last 5)
        recent_tickets = ticket_manager.get_all_tickets()[:5]
        
        return render_template('index.html', 
                             stats=stats, 
                             recent_tickets=recent_tickets)
    except Exception as e:
        return render_template('index.html', 
                             error=f"Error loading dashboard: {e}",
                             stats={}, 
                             recent_tickets=[])

@app.route('/tickets')
def tickets():
    """
    Tickets page - shows all tickets with filtering options.
    
    This page allows users to view, search, and filter tickets.
    """
    # Get filter parameters from URL
    status_filter = request.args.get('status', 'Active')  # Default to Active
    search_query = request.args.get('search', '')
    priority_filter = request.args.get('priority', '')
    assigned_filter = request.args.get('assigned', '')
    
    try:
        if search_query:
            # Search tickets
            tickets_list = ticket_manager.search_tickets(search_query)
        else:
            # Get all tickets
            tickets_list = ticket_manager.get_all_tickets()
        
        # Add new message indicators
        current_user = session.get('username', 'guest')
        for ticket in tickets_list:
            ticket['has_new_messages'] = has_new_messages(ticket['ticket_id'], current_user)
        
        # Apply filters
        filtered_tickets = []
        for ticket in tickets_list:
            # Status filter
            if status_filter == 'Active':
                if ticket.get('status') not in ['New', 'In Progress']:
                    continue
            elif status_filter != 'All' and ticket.get('status') != status_filter:
                continue
            
            # Priority filter
            if priority_filter and ticket.get('priority') != priority_filter:
                continue
            
            # Assignment filter
            if assigned_filter:
                if assigned_filter == 'unassigned':
                    if ticket.get('assigned_to'):
                        continue
                elif ticket.get('assigned_to') != assigned_filter:
                    continue
            
            filtered_tickets.append(ticket)
        
        return render_template('tickets.html', 
                             tickets=filtered_tickets,
                             status_filter=status_filter,
                             search_query=search_query,
                             priority_filter=priority_filter,
                             assigned_filter=assigned_filter)
    except Exception as e:
        return render_template('tickets.html', 
                             error=f"Error loading tickets: {e}",
                             tickets=[],
                             status_filter=status_filter,
                             search_query=search_query)

@app.route('/ticket/<int:ticket_id>')
def ticket_detail(ticket_id):
    """
    Individual ticket detail page.
    
    Shows full ticket information including history and allows updates.
    """
    try:
        ticket = ticket_manager.get_ticket_details(ticket_id)
        if not ticket:
            return render_template('error.html', 
                                 message=f"Ticket #{ticket_id} not found"), 404
        
        # Mark ticket as viewed by current user
        current_user = session.get('username', 'guest')
        update_ticket_view(ticket_id, current_user)
        
        return render_template('ticket_detail.html', ticket=ticket)
    except Exception as e:
        return render_template('error.html', 
                             message=f"Error loading ticket: {e}"), 500

@app.route('/admin/ticket/<int:ticket_id>')
def admin_ticket_detail(ticket_id):
    """
    Admin ticket detail page with full administrative controls.
    """
    if 'role' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    try:
        ticket = ticket_manager.get_ticket_details(ticket_id)
        if not ticket:
            return render_template('error.html', 
                                 message=f"Ticket #{ticket_id} not found"), 404
        
        # Mark ticket as viewed by current admin
        current_user = session.get('username', 'admin')
        update_ticket_view(ticket_id, current_user)
        
        return render_template('admin_ticket_detail.html', ticket=ticket)
    except Exception as e:
        return render_template('error.html', 
                             message=f"Error loading ticket: {e}"), 500

@app.route('/agent')
def agent():
    """
    AI Agent chat interface page.
    
    This is where users can ask IT questions and get AI-powered guidance.
    """
    # Ensure we have a user session
    if 'username' not in session:
        # Create a guest session if none exists
        import uuid
        session['username'] = f'guest_{str(uuid.uuid4())[:8]}'
        session['role'] = 'guest'
    
    # Check if we're viewing a specific ticket
    ticket_id = request.args.get('ticket_id')
    if ticket_id:
        try:
            ticket_id = int(ticket_id)
            # Mark ticket as viewed when accessing through agent
            current_user = session.get('username', 'guest')
            update_ticket_view(ticket_id, current_user)
        except (ValueError, TypeError):
            pass  # Invalid ticket_id, ignore
    
    return render_template('agent.html')

@app.route('/create_ticket')
def create_ticket_form():
    """
    Show the create ticket form.
    """
    return render_template('create_ticket.html')


# API Endpoints (for AJAX requests and external integrations)

@app.route('/api/tickets', methods=['POST'])
def api_create_ticket():
    """
    API endpoint to create a new ticket.
    
    Expects JSON data:
    {
        "employee_name": "John Doe",
        "issue_description": "Can't log into email",
        "priority": "High"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['employee_name', 'issue_description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create ticket using our ticket manager
        result = ticket_manager.create_ticket(
            employee_name=data['employee_name'],
            issue_description=data['issue_description'],
            priority=data.get('priority', 'Medium')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to create ticket: {str(e)}'}), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def api_get_ticket(ticket_id):
    """
    API endpoint to get a specific ticket.
    """
    try:
        ticket = ticket_manager.get_ticket_details(ticket_id)
        if ticket:
            return jsonify({
                'success': True,
                'ticket': ticket
            })
        else:
            return jsonify({'error': 'Ticket not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to get ticket: {str(e)}'}), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
def api_update_ticket(ticket_id):
    """
    API endpoint to update a ticket.
    
    Expects JSON data with fields to update:
    {
        "status": "In Progress",
        "assigned_to": "John Smith",
        "notes": "Working on password reset"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Handle different types of updates
        if 'status' in data:
            result = ticket_manager.update_ticket_status(
                ticket_id=ticket_id,
                new_status=data['status'],
                assigned_to=data.get('assigned_to'),
                notes=data.get('notes')
            )
        elif 'resolution_code' in data:
            result = ticket_manager.resolve_ticket(
                ticket_id=ticket_id,
                resolution_code=data['resolution_code'],
                resolved_by=data.get('resolved_by', 'Unknown')
            )
        else:
            return jsonify({'error': 'No valid update fields provided'}), 400
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to update ticket: {str(e)}'}), 500

@app.route('/api/tickets', methods=['GET'])
def api_get_tickets():
    """
    API endpoint to get all tickets.
    
    Query parameters:
    - status: Filter by status
    - search: Search query
    """
    try:
        status_filter = request.args.get('status')
        search_query = request.args.get('search')
        
        if search_query:
            tickets_list = ticket_manager.search_tickets(search_query)
        else:
            tickets_list = ticket_manager.get_all_tickets(status_filter)
        
        return jsonify({
            'success': True,
            'tickets': tickets_list,
            'count': len(tickets_list)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get tickets: {str(e)}'}), 500

@app.route('/api/agent/ask', methods=['POST'])
def api_ask_agent():
    """
    API endpoint for AI agent questions.
    
    Expects JSON data:
    {
        "question": "How do I reset my password?",
        "ticket_id": 123  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('question'):
            return jsonify({'error': 'Question is required'}), 400
        
        # Get AI agent
        agent = get_ai_agent()
        if not agent:
            return jsonify({
                'error': 'AI agent not available. Please check configuration.',
                'suggestion': 'Contact IT administrator to configure AI settings.'
            }), 503
        
        question = data['question']
        ticket_id = data.get('ticket_id')
        
        # Get current user from session
        current_user = session.get('username', 'guest')
        
        # If ticket_id is provided, save the user's question as a message
        if ticket_id:
            try:
                add_ticket_message(ticket_id, current_user, 'user', question)
            except Exception as e:
                print(f"Warning: Failed to save user message to ticket {ticket_id}: {e}")
        
        # Get AI guidance
        result = agent.get_ai_guidance(
            question=question,
            ticket_id=ticket_id
        )
        
        # If ticket_id is provided and AI response is successful, save the AI response as a message
        if ticket_id and result.get('success') and result.get('ai_response'):
            try:
                add_ticket_message(ticket_id, 'AI Assistant', 'assistant', result['ai_response'])
            except Exception as e:
                print(f"Warning: Failed to save AI response to ticket {ticket_id}: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'AI agent error: {str(e)}'}), 500

@app.route('/api/stats')
def api_get_stats():
    """
    API endpoint to get ticket statistics for dashboard.
    """
    try:
        stats = ticket_manager.get_ticket_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get statistics: {str(e)}'}), 500

@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    """
    API endpoint for admin authentication.
    """
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = authenticate_user(username, password)
        if user and user.get('role') == 'admin':
            # Store user info in session
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role': user['role']
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/tickets/<int:ticket_id>/status', methods=['POST'])
def api_update_ticket_status(ticket_id):
    """
    API endpoint to update ticket status.
    """
    if 'role' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        result = ticket_manager.update_ticket_status(
            ticket_id=ticket_id,
            new_status=new_status,
            assigned_to=session.get('username')
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500

@app.route('/api/tickets/<int:ticket_id>/assign', methods=['POST'])
def api_assign_ticket(ticket_id):
    """
    API endpoint to assign ticket to admin.
    """
    if 'role' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        assigned_to = data.get('assigned_to')
        
        result = ticket_manager.update_ticket_assignment(
            ticket_id=ticket_id,
            assigned_to=assigned_to
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Failed to assign ticket: {str(e)}'}), 500

@app.route('/api/tickets/assign-unassigned', methods=['POST'])
def api_assign_unassigned_tickets():
    """
    API endpoint to assign all unassigned tickets to current admin.
    """
    if 'role' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        assigned_to = data.get('assigned_to', session.get('username'))
        
        # Get all unassigned tickets
        all_tickets = ticket_manager.get_all_tickets()
        unassigned_tickets = [t for t in all_tickets if not t.get('assigned_to')]
        
        count = 0
        for ticket in unassigned_tickets:
            result = ticket_manager.update_ticket_status(
                ticket_id=ticket['ticket_id'],
                new_status=None,  # Don't change status
                assigned_to=assigned_to
            )
            if result['success']:
                count += 1
        
        return jsonify({
            'success': True,
            'count': count,
            'message': f'Assigned {count} tickets to {assigned_to}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to assign tickets: {str(e)}'}), 500

@app.route('/api/tickets/<int:ticket_id>/messages', methods=['GET'])
def api_get_ticket_messages(ticket_id):
    """
    API endpoint to get messages for a specific ticket.
    """
    try:
        messages = get_ticket_messages(ticket_id)
        
        # Mark ticket as viewed when messages are accessed
        current_user = session.get('username', 'guest')
        update_ticket_view(ticket_id, current_user)
        
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get messages: {str(e)}'}), 500

@app.route('/api/tickets/<int:ticket_id>/messages', methods=['POST'])
def api_add_ticket_message(ticket_id):
    """
    API endpoint to add a message to a ticket.
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({'error': 'Message content required'}), 400
        
        # Default values if not provided
        sender_name = data.get('sender_name', 'Anonymous')
        sender_type = data.get('sender_type', 'user')
        
        message_id = add_ticket_message(
            ticket_id=ticket_id,
            sender_name=sender_name,
            sender_type=sender_type,
            message=data['message']
        )
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'message': 'Message added successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to add message: {str(e)}'}), 500

# Error handlers

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with a custom page."""
    return render_template('error.html', 
                         message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with a custom page."""
    return render_template('error.html', 
                         message="Internal server error"), 500

# Main application entry point
if __name__ == '__main__':
    # Initialize database when starting the application
    print("🚀 Starting IT Support Agent System...")
    
    try:
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Check if AI agent can be initialized
    try:
        test_agent = get_ai_agent()
        if test_agent:
            print("✅ AI agent initialized successfully")
        else:
            print("⚠️  AI agent not available - check .env configuration")
    except Exception as e:
        print(f"⚠️  AI agent warning: {e}")
    
    print("🌐 Starting web server...")
    print("📱 Open your browser to: http://localhost:5000")
    
    # Run the Flask application
    # Debug=True enables hot reloading and detailed error messages
    # Only use debug=True in development, never in production!
    app.run(debug=True, host='0.0.0.0', port=5000)
