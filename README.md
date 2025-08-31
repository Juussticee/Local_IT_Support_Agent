# IT Support Agent System

A comprehensive IT support ticketing system with AI-powered assistance, built with Flask and designed for easy deployment and configuration.

## 🚀 Features

### Core Functionality
- **Ticket Management**: Create, view, update, and track IT support tickets
- **AI Assistant**: Intelligent chatbot that provides policy-based guidance
- **Multi-LLM Support**: Easily switch between OpenAI, OpenRouter, or other providers
- **Policy-Based Responses**: AI cites official IT policies and procedures
- **Real-time Updates**: Live status updates and notifications
- **Search & Filtering**: Find tickets by status, priority, or content
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### AI Agent Capabilities
- Password reset guidance with approval workflows
- Software installation request processing
- Network troubleshooting step-by-step instructions
- Security policy explanations
- Automatic ticket creation suggestions
- Transparent reasoning with policy citations

### Admin Features
- Easy LLM provider configuration via `.env` file
- Comprehensive logging and audit trails
- Ticket statistics and reporting
- Policy document management
- No-code configuration for most settings

## 📋 Requirements

- Python 3.8+
- Flask 3.0+
- SQLite (included with Python)
- Internet connection for AI features
- Modern web browser

## 🛠️ Installation

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd ChimeraHackathon
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy the example environment file and configure your settings:

```bash
# Create .env file in backend directory
cd backend
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edit the `.env` file:
```env
# Choose your LLM provider: openrouter, openai, gemini
LLM_PROVIDER=openrouter

# Add your API key for the chosen provider
OPENROUTER_API_KEY=your_openrouter_key_here
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### 5. Run the Application
```bash
cd backend
python app.py
```

The application will start at `http://localhost:5000`

## 🔧 Configuration

### Switching LLM Providers

To switch between AI providers, simply edit the `.env` file:

**For OpenRouter (Free tier available):**
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**For OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
```

**For Gemini:**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key-here
```

No code changes required! Just restart the application.

### Adding New Policies

1. Create a new `.txt` file in `backend/policies/`
2. Add your policy content in plain text
3. Restart the application
4. The AI agent will automatically include the new policy in its knowledge base

### Customizing the Interface

- **Logo/Branding**: Edit `backend/templates/base.html`
- **Colors/Styling**: Modify `backend/static/style.css`
- **Additional Pages**: Create new templates in `backend/templates/`

## 📖 Usage Guide

### For Employees

1. **Creating a Ticket**:
   - Click "New Ticket" from the dashboard
   - Fill in your name and describe the issue
   - Select appropriate priority level
   - Submit the ticket

2. **Using the AI Assistant**:
   - Click "AI Assistant" from the menu
   - Type your IT question in plain English
   - Follow the step-by-step guidance provided
   - Create a ticket if suggested by the AI

3. **Tracking Tickets**:
   - View all tickets in the "Tickets" section
   - Click on any ticket to see detailed information
   - Track status changes and resolution progress

### For IT Staff

1. **Managing Tickets**:
   - View all tickets with filtering and search
   - Update ticket status (New → In Progress → Resolved → Closed)
   - Assign tickets to team members
   - Add resolution notes

2. **Monitoring System**:
   - Dashboard shows real-time statistics
   - Search tickets by employee, content, or status
   - View AI interaction logs for transparency

### For Administrators

1. **LLM Configuration**:
   - Edit `.env` file to change AI provider
   - No coding required for basic configuration
   - Restart application to apply changes

2. **Policy Management**:
   - Add new policy files to `backend/policies/`
   - Edit existing policies as needed
   - AI automatically uses updated policies

## 🏗️ Architecture

### Project Structure
```
ChimeraHackathon/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── database.py         # Database operations
│   ├── ticket.py          # Ticket management logic
│   ├── llm_client.py      # AI agent integration
│   ├── .env               # Configuration file
│   ├── policies/          # IT policy documents
│   │   ├── password_reset.txt
│   │   ├── software_install.txt
│   │   └── network_issues.txt
│   ├── templates/         # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── agent.html
│   │   ├── tickets.html
│   │   └── create_ticket.html
│   └── static/           # CSS, JavaScript, images
│       ├── style.css
│       └── script.js
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── venv/                # Virtual environment
```

### Key Components

1. **Flask Web Server** (`app.py`):
   - Routes for web pages and API endpoints
   - Handles HTTP requests and responses
   - Coordinates between frontend and backend

2. **Database Layer** (`database.py`):
   - SQLite database for ticket storage
   - CRUD operations with proper error handling
   - Automatic logging of all changes

3. **Business Logic** (`ticket.py`):
   - Ticket lifecycle management
   - Validation and business rules
   - Statistics and reporting

4. **AI Integration** (`llm_client.py`):
   - Multi-provider LLM support
   - Policy document loading and searching
   - Response generation with citations

5. **Frontend** (Templates + Static files):
   - Responsive web interface
   - Real-time updates with JavaScript
   - Modern UI with Bootstrap

## 🔍 API Endpoints

### Tickets API
- `POST /api/tickets` - Create new ticket
- `GET /api/tickets` - Get all tickets (with filters)
- `PUT /api/tickets/<id>` - Update ticket
- `GET /api/tickets/<id>` - Get specific ticket

### AI Agent API
- `POST /api/agent/ask` - Ask AI assistant a question

### System API
- `GET /api/stats` - Get system statistics

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
- Check that you're in the `backend` directory
- Ensure virtual environment is activated
- Verify all dependencies are installed

**AI agent not working:**
- Check your API key in `.env` file
- Verify the LLM provider is set correctly
- Check internet connection
- Look at console logs for error messages

**Database errors:**
- Delete `it_support.db` to reset database
- Check file permissions in the directory
- Ensure SQLite is available (included with Python)

**Templates not loading:**
- Verify you're running from `backend` directory
- Check that `templates` folder exists
- Restart the application

### Getting Help

1. **Check the logs**: Look at the console output when running the app
2. **Create a test ticket**: Use the system to create a simple ticket
3. **Test AI separately**: Try the AI assistant with a simple question
4. **Check configuration**: Verify your `.env` file settings

## 🚧 Development

### Running in Development Mode
```bash
cd backend
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

### Adding New Features

1. **New API endpoints**: Add routes to `app.py`
2. **Database changes**: Modify `database.py` schema
3. **New templates**: Create HTML files in `templates/`
4. **Styling**: Edit `static/style.css`
5. **Client-side logic**: Modify `static/script.js`

### Testing

Basic testing can be done by:
1. Creating test tickets through the web interface
2. Asking the AI assistant various questions
3. Testing different ticket statuses and updates
4. Verifying policy citations are working

## 📈 Production Deployment

For production use:

1. **Use a production WSGI server** (Gunicorn, uWSGI)
2. **Set up a reverse proxy** (Nginx, Apache)
3. **Use environment variables** for sensitive configuration
4. **Set up proper logging** and monitoring
5. **Regular backups** of the SQLite database
6. **SSL/HTTPS** for secure communication

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🙋 Support

For support or questions:

1. **Check this README** for common solutions
2. **Create a ticket** using the system itself
3. **Ask the AI assistant** for help with IT questions
4. **Contact the development team**

---

**Built with ❤️ for the IT support community**
