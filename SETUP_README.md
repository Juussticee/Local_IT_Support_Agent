# 🛠️ Local IT Support Agent System

A comprehensive AI-powered IT support system that automates ticket creation, provides policy-based guidance, and manages the complete IT support workflow.

## 🌟 Features

- **Automated Ticket Creation**: Convert user problems into structured tickets
- **AI-Powered Assistance**: Policy-based responses with official IT procedures
- **Complete Lifecycle Management**: New → In Progress → Resolved → Closed
- **Policy Consultation**: AI consults official policies, doesn't invent answers
- **Admin Dashboard**: Full ticket management and oversight
- **Audit Trail**: Complete logging of all actions and decisions
- **Real-time Chat**: Interactive AI assistant for immediate help

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning)

### 1. Download the Project

#### Option A: Download ZIP
1. Download the project as a ZIP file
2. Extract to your desired location
3. Open terminal/command prompt in the project directory

#### Option B: Clone with Git
```bash
git clone https://github.com/Juussticee/Local_IT_Support_Agent.git
cd Local_IT_Support_Agent
```

### 2. Set Up Python Environment

#### Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get Your API Key

The system supports multiple AI providers. Choose one:

#### Option A: OpenAI (Recommended)
1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy your API key (starts with `sk-`)

#### Option B: OpenRouter (Alternative)
1. Go to [OpenRouter](https://openrouter.ai/keys)
2. Create an account
3. Generate an API key
4. Copy your key

#### Option C: Google Gemini
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Copy your key

### 4. Configure Environment

Create a `.env` file in the `backend` directory:

```bash
# Navigate to backend directory
cd backend

# Create .env file (Windows)
echo. > .env

# Or create manually with any text editor
```

Add your API configuration to `.env`:

```env
# Choose your AI provider
LLM_PROVIDER=openai

# Add your API key (choose one)
OPENAI_API_KEY=sk-your-openai-key-here
# OPENROUTER_API_KEY=sk-or-your-openrouter-key
# GEMINI_API_KEY=your-gemini-key-here

# Optional: Customize AI model
OPENAI_MODEL=gpt-3.5-turbo
```

### 5. Run the Application

```bash
# Make sure you're in the backend directory
cd backend

# Start the server
python app.py
```

You should see:
```
✅ Database initialized successfully!
🚀 Starting IT Support Agent System...
✅ IT Support Agent initialized successfully
🌐 Starting web server...
📱 Open your browser to: http://localhost:5000
```

### 6. Access the System

Open your browser and go to:
- **User Portal**: http://localhost:5000
- **Admin Dashboard**: http://localhost:5000/admin/login
  - Username: `admin`
  - Password: `admin123`

## 🎯 How to Use

### For End Users
1. Go to http://localhost:5000
2. Click "Create New Ticket" or "AI Assistant"
3. Describe your IT problem
4. Get instant AI guidance or create a ticket
5. Track your ticket status

### For IT Administrators
1. Login at http://localhost:5000/admin/login
2. View all tickets in the dashboard
3. Assign tickets and update statuses
4. Monitor AI responses and policy compliance
5. Generate reports and statistics

## 📁 Project Structure

```
ChimeraHackathon/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── database.py         # Database operations
│   ├── llm_client.py       # AI provider integration
│   ├── ticket.py           # Ticket management
│   ├── .env               # Environment configuration
│   ├── it_support.db      # SQLite database
│   └── policies/          # IT policy documents
│       ├── password_reset.txt
│       ├── network_issues.txt
│       └── software_install.txt
├── frontend/
│   ├── templates/         # HTML templates
│   └── static/           # CSS and JavaScript
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration Options

### Environment Variables (.env file)

| Variable | Options | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai`, `openrouter`, `gemini` | AI provider to use |
| `OPENAI_API_KEY` | Your OpenAI key | Required if using OpenAI |
| `OPENROUTER_API_KEY` | Your OpenRouter key | Required if using OpenRouter |
| `GEMINI_API_KEY` | Your Gemini key | Required if using Gemini |
| `OPENAI_MODEL` | `gpt-3.5-turbo`, `gpt-4` | OpenAI model (optional) |

### Adding Custom Policies

1. Create new `.txt` files in `backend/policies/`
2. Write clear, structured policy content
3. Restart the application
4. The AI will automatically use new policies

## 🛠️ Troubleshooting

### Common Issues

**"No module named 'xyz'"**
```bash
pip install -r requirements.txt
```

**"API key not found"**
- Check your `.env` file is in the `backend` directory
- Verify your API key is correct
- Make sure there are no spaces around the `=` sign

**"Port 5000 already in use"**
```bash
# Kill any existing processes on port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# macOS/Linux
lsof -ti:5000 | xargs kill
```

**Database errors**
```bash
# Delete and recreate database
rm backend/it_support.db
python backend/app.py
```

### Getting Help

1. Check the terminal output for error messages
2. Verify your API key is working
3. Try refreshing your browser
4. Restart the application

## 🔒 Security Notes

- Change the default admin password in production
- Keep your API keys secure and never commit them to version control
- The `.env` file is ignored by git for security
- Use HTTPS in production environments

## 🏗️ Development

### Running in Development Mode

The application runs in debug mode by default, which provides:
- Automatic reloading on code changes
- Detailed error messages
- Interactive debugger

### Database Management

The system uses SQLite for simplicity. The database is automatically created on first run with:
- Users table (admin accounts)
- Tickets table (support tickets)
- Policies table (IT procedures)
- Ticket messages (chat history)
- Ticket views (read status tracking)

## 📊 System Capabilities

- ✅ **Ticket Creation & Management**: Complete lifecycle management
- ✅ **AI Policy Consultation**: Retrieves and cites official IT policies
- ✅ **Structured Responses**: Step-by-step guidance with approval status
- ✅ **Audit Trail**: Full logging of all actions and decisions
- ✅ **Search & Filtering**: Find tickets by status, priority, assignee
- ✅ **Statistics & Reporting**: Track system usage and metrics
- ✅ **Real-time Chat**: Interactive AI assistant
- ✅ **Admin Dashboard**: Complete administrative control

## 🧹 Cleanup Instructions

### Test Files to Delete (Optional)

These files were created during development and testing. You can safely delete them:

```bash
# Delete test files
rm test_ai_chat.py
rm test_indicators.py
rm test_method.py
rm check_db.py

# Delete development documents (optional)
rm competition_plan.md
rm req.md

# Keep the main database (unless you want to start fresh)
# rm backend/it_support.db
```

Or delete them manually through your file explorer.

## 📝 License

This project is built for educational/hackathon purposes. Please ensure compliance with your organization's policies when deploying in production environments.

---

**Need help?** Check the troubleshooting section above or review the terminal output for specific error messages.
