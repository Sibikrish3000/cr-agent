---
title: Multi Agent Chat
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# 🤖 Multi-Agent AI System with React Frontend

A production-ready **Agentic AI backend** powered by **FastAPI + LangGraph** with a beautiful **React.js chat interface**.

## ✨ What's Included

✅ **React Frontend** - Modern gradient UI with chat memory  
✅ **4 AI Agents** - Weather, Documents+RAG, Meetings, SQL  
✅ **Vector Store RAG** - ChromaDB with semantic search  
✅ **Deterministic Tools** - 100% reliable tool execution  
✅ **File Upload** - PDF/TXT/MD/DOCX processing  
✅ **One-Command Start** - `.\start.bat` launches everything

## 🚀 Quick Start

```powershell
# Windows
.\start.bat

# Linux/Mac  
chmod +x start.sh && ./start.sh
```

Opens at http://localhost:3000

## 📖 Full Documentation

- **[COMPLETE_SETUP.md](COMPLETE_SETUP.md)** - Full setup guide  
- **[FRONTEND_SETUP.md](FRONTEND_SETUP.md)** - React frontend details  
- **[TOOL_CALLING_ISSUE.md](TOOL_CALLING_ISSUE.md)** - Technical analysis

## 💻 Manual Setup

### Backend
```powershell
uv run uvicorn main:app --reload
```

### Frontend
```powershell
cd frontend
npm install
npm start
```

## 🎯 Usage Examples

**Weather:** "What's the weather in Chennai?"  
**Documents:** Upload PDF → Ask "What is the policy?"  
**Meetings:** "Schedule team meeting tomorrow at 2pm"  
**Database:** "Show all meetings scheduled tomorrow"

## 📊 Architecture

```
React UI (3000) → FastAPI (8000) → LangGraph
                                      ↓
                  ┌──────────┬────────┬─────────┬────────┐
                  │ Weather  │ Docs   │ Meeting │  SQL   │
                  │  Agent   │ +RAG   │  Agent  │ Agent  │
                  └──────────┴────────┴─────────┴────────┘
```

## 🔑 Configuration (.env)

```bash
GITHUB_TOKEN=ghp_...              # Recommended (free)
OPENWEATHERMAP_API_KEY=...        # Required for weather
```

Get tokens:
- GitHub: https://github.com/settings/tokens
- Weather: https://openweathermap.org/api

## 📁 Project Structure

```
multi-agent/
├── agents.py              # AI agents
├── main.py                # FastAPI server
├── tools.py               # Tool implementations
├── vector_store.py        # ChromaDB RAG
├── start.bat              # One-command startup
└── frontend/              # React UI
    ├── src/App.js
    └── package.json
```

## ✅ Test Results

- ✅ Weather Agent: Working
- ✅ Document RAG: Working (similarity: 0.59-0.70)
- ✅ SQL Agent: Working
- ⚠️ Meeting Agent: Needs fix

## 🛠️ Tech Stack

- FastAPI + LangGraph + ChromaDB
- React 18 + Axios
- sentence-transformers
- Docling (lightweight config)

## 📚 Learn More

See [COMPLETE_SETUP.md](COMPLETE_SETUP.md) for detailed documentation.

---

**Made with ❤️ using FastAPI, LangGraph, React, and ChromaDB**
