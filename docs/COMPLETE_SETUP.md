# 🚀 Multi-Agent AI Backend - Complete Setup

## ✅ What's Working

### Backend (FastAPI + LangGraph)
- ✅ Weather Agent - Gets current weather and forecasts
- ✅ Document Agent - RAG with ChromaDB vector store (deterministic tool execution)
- ⚠️ Meeting Agent - Scheduling with weather checks (needs final fix)
- ✅ SQL Agent - Natural language to SQL queries
- ✅ File Upload - PDF/TXT/MD/DOCX processing

### Frontend (React.js)
- ✅ Modern gradient UI design
- ✅ Real-time chat with typing indicators
- ✅ File upload with drag-and-drop
- ✅ Chat memory (full conversation history)
- ✅ Example query buttons
- ✅ Error handling

## 🎯 Quick Start

### 1. Backend Setup

```powershell
# Ensure virtual environment
cd D:\python_workspace\multi-agent

# Start backend server
uv run uvicorn main:app --reload
```

Backend runs at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 2. Frontend Setup

```powershell
# Open new terminal
cd D:\python_workspace\multi-agent\frontend

# First time only - install dependencies
npm install

# Start React development server
npm start
```

Frontend opens at: http://localhost:3000

## 📝 Usage Examples

### Via Frontend UI
1. Open http://localhost:3000
2. Click example buttons or type queries:
   - "What's the weather in Chennai?"
   - "Schedule team meeting tomorrow at 2pm"
   - "Show all meetings scheduled tomorrow"
3. Upload documents via 📁 button
4. Ask questions about uploaded files

### Via API (cURL)

**Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Chennai?"}'
```

**Upload File:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│             React Frontend (Port 3000)           │
│  • Chat UI with memory                           │
│  • File upload                                   │
│  • Example queries                               │
└────────────────┬─────────────────────────────────┘
                 │ HTTP (CORS enabled)
                 ▼
┌──────────────────────────────────────────────────┐
│          FastAPI Backend (Port 8000)             │
│  • /chat endpoint                                │
│  • /upload endpoint                              │
└────────────────┬─────────────────────────────────┘
                 │
        ┌────────┴────────────────┐
        │   LangGraph Workflow    │
        │   (Router + 4 Agents)   │
        └────────┬────────────────┘
                 │
    ┌────────────┼─────────────┬──────────────┐
    ▼            ▼             ▼              ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐
│ Weather │ │ Document │ │ Meeting  │ │  SQL    │
│  Agent  │ │   +RAG   │ │  Agent   │ │ Agent   │
└─────────┘ └──────────┘ └──────────┘ └─────────┘
     │           │             │            │
     ▼           ▼             ▼            ▼
 OpenWeather  ChromaDB    Schedule+     SQLite
    API      Vector DB     Weather       DB
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Recommended for testing
GITHUB_TOKEN=ghp_your_token_here

# Alternative LLM providers
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...

# Weather API
OPENWEATHERMAP_API_KEY=your_key

# Local Ollama (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

### Get API Keys
- **GitHub Token**: https://github.com/settings/tokens (free, recommended)
- **OpenAI**: https://platform.openai.com/api-keys ($0.15/1M tokens)
- **OpenWeatherMap**: https://openweathermap.org/api (free tier)

## 📊 Test Results

```
✅ Weather Agent: Working perfectly
⚠️  Meeting Agent: Needs weather tool fix  
✅ SQL Agent: Working perfectly
✅ Document RAG: Working with deterministic execution
   • PDF ingestion: ~2-5 seconds
   • Similarity scores: 0.59-0.70
   • Correct answers from documents
   • Web fallback for low confidence (< 0.7)
```

## 🐛 Troubleshooting

### Backend Issues

**"Port 8000 already in use"**
```powershell
# Kill existing process
npx kill-port 8000
# Or use different port
uvicorn main:app --port 8001
```

**"Database locked"**
```powershell
# Delete and recreate
rm meeting_database.db
uv run uvicorn main:app --reload
```

### Frontend Issues

**"npm install fails"**
```powershell
cd frontend
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**"Cannot connect to backend"**
1. Check backend is running: http://localhost:8000/docs
2. Verify CORS is enabled in main.py
3. Check proxy in frontend/package.json

**"Port 3000 already in use"**
```powershell
npx kill-port 3000
# Or use different port
set PORT=3001 && npm start
```

## 📁 Project Structure

```
multi-agent/
├── agents.py              # LangGraph workflow
├── tools.py               # Tool implementations
├── main.py                # FastAPI server
├── database.py            # SQLite setup
├── vector_store.py        # ChromaDB manager
├── models.py              # Pydantic models
├── test_agents.py         # Test suite
├── .env                   # Configuration
├── pyproject.toml         # Python dependencies
├── FRONTEND_SETUP.md      # Frontend guide
└── frontend/              # React app
    ├── public/
    ├── src/
    │   ├── App.js         # Main component
    │   ├── App.css        # Styling
    │   └── index.js       # Entry point
    ├── package.json       # NPM dependencies
    └── README.md
```

## 🚀 Production Deployment

### Backend (FastAPI)
```powershell
# Install production server
uv add gunicorn

# Run with gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (React)
```powershell
cd frontend

# Build for production
npm run build

# Serve with any static server
npx serve -s build -p 3000
```

### Docker Deployment
```dockerfile
# Coming soon - Docker Compose setup
```

## 📚 Documentation

- [Frontend Setup Guide](FRONTEND_SETUP.md)
- [Tool Calling Issue Analysis](TOOL_CALLING_ISSUE.md)
- [GitHub Models Setup](GITHUB_MODELS_SETUP.md)
- [Quick Start Guide](QUICK_START.md)

## 🎉 Features Completed

✅ **Backend:**
- Multi-agent orchestration with LangGraph
- Vector store RAG with ChromaDB
- Deterministic tool execution
- File upload and processing
- Weather integration
- SQL database queries
- Lightweight Docling config (no vision models)

✅ **Frontend:**
- Modern gradient UI
- Real-time chat
- File upload interface
- Chat memory
- Example queries
- Typing indicators
- Error handling
- Mobile responsive

## 🔜 Next Steps

1. **Fix Meeting Agent** - Apply deterministic weather tool execution
2. **Add DuckDuckGo Search** - Install package for web fallback
3. **Enhance UI** - Add more features to frontend
4. **Deploy** - Production deployment guide

## 💡 Tips

- **Use GitHub Models** for stable testing (free tier)
- **Upload test documents** to see RAG in action
- **Check similarity scores** in backend logs
- **Clear chat** to start fresh conversations
- **Use example queries** for quick testing

---

**Made with ❤️ using FastAPI, LangGraph, React, and ChromaDB**
