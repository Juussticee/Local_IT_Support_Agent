# 🚀 IT Support Agent - Quick Setup

A complete AI-powered IT support system with ticket management and policy-based guidance.

## ⚡ Quick Start (5 minutes)

### 0. Download Project
```bash
git clone https://github.com/Juussticee/Local_IT_Support_Agent.git
cd Local_IT_Support_Agent
```

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API Key (Choose One)
- **OpenAI**: https://platform.openai.com/api-keys (create account → "Create new secret key")
- **OpenRouter**: https://openrouter.ai/keys (free tier available)
- **Gemini**: https://makersuite.google.com/app/apikey

### 3. Configure Environment
Create `backend/.env` file:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
```

### 4. Run Application
```bash
cd backend
python app.py
```

### 5. Access System
- **User Portal**: http://localhost:5000
- **Admin Login**: http://localhost:5000/admin/login
  - Username: `admin` 
  - Password: `admin123`

## 🎯 What You Get

✅ **AI Assistant** - Policy-based IT guidance  
✅ **Ticket System** - Complete lifecycle management  
✅ **Admin Dashboard** - Full ticket oversight  
✅ **Search & Filter** - Find tickets quickly  
✅ **Audit Trail** - Complete action logging  

## 🔧 Switch AI Providers

Just edit `backend/.env`:

**OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
```

**OpenRouter:**
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-your-key
```

**Gemini:**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
```

## 🛠️ Troubleshooting

**"Module not found"**: `pip install -r requirements.txt`  
**"API key error"**: Check `.env` file in `backend/` folder  
**"Port in use"**: Kill process on port 5000 or restart computer  

## 📁 Project Structure
```
ChimeraHackathon/
├── backend/          # Main application
│   ├── .env         # Your API configuration
│   └── app.py       # Start here
├── frontend/        # Web interface
└── requirements.txt # Dependencies
```

That's it! Your IT Support Agent is ready! 🎉
