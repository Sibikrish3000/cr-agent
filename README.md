---
title: Multi Agent Chat
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---
# 🤖 Multi-Agent AI System

**Production-ready AI backend (FastAPI + LangGraph) with a modern React.js chat frontend.**
## Try on Huggingface Space
<p>
<a href="https://sibikrish-cr-agent.hf.space/"><img src="https://img.shields.io/badge/Huggingface-white?style=flat&logo=huggingface&logoSize=amd" alt="huggingface" width="160" height="50"></a>
</p>

## API SwaggerUI
<a href="https://sibikrish-cr-agent.hf.space/docs"><img src="https://img.shields.io/badge/Huggingface-white?style=flat&logo=swagger&logoSize=amd" alt="huggingface" width="160" height="50"></a>
</p>
---

## Features

- **React Frontend**: Gradient UI, chat memory
- **Four AI Agents**: Weather, Documents (RAG), Meetings, SQL
- **Vector Store RAG**: ChromaDB semantic search
- **Reliable Tool Execution**: Deterministic tool calls
- **File Upload**: PDF, TXT, MD, DOCX support
- **One-Command Start**: `start.bat` or `start.sh`

## Quick Start

**Windows:**
```powershell
./start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh && ./start.sh
```

Frontend: [http://localhost:3000](http://localhost:3000)
Backend: [http://localhost:7860](http://localhost:7860)

## Manual Setup

**Backend:**
```powershell
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

## Usage Examples

- **Weather:** "What's the weather in Chennai?"
- **Documents:** Upload PDF → Ask "What is the policy?"
- **Meetings:** "Schedule team meeting tomorrow at 2pm"
- **Database:** "Show all meetings scheduled tomorrow"

## Architecture

```
React UI (3000) → FastAPI (7860) → LangGraph
                                 ↓
           ┌──────────┬────────┬─────────┬────────┐
           │ Weather  │ Docs   │ Meeting │  SQL   │
           │  Agent   │ +RAG   │  Agent  │ Agent  │
           └──────────┴────────┴─────────┴────────┘
```

## Configuration (.env)

```env
GITHUB_TOKEN=ghp_...              # Optional (GitHub search)
OPENWEATHERMAP_API_KEY=...        # Required for weather
```

Get tokens:
- [GitHub](https://github.com/settings/tokens)
- [OpenWeather](https://openweathermap.org/api)

## Project Structure

```
cr-agent/
├── agents.py              # AI agents
├── main.py                # FastAPI server
├── tools.py               # Tool implementations
├── vector_store.py        # ChromaDB RAG
├── start.bat              # One-command startup
└── frontend/              # React UI
    ├── src/App.js
    └── package.json
```

## Documentation

- [COMPLETE_SETUP.md](docs/COMPLETE_SETUP.md): Full setup guide
- [FRONTEND_SETUP.md](docs/FRONTEND_SETUP.md): Frontend details
- [TOOL_CALLING_ISSUE.md](docs/TOOL_CALLING_ISSUE.md): Technical analysis

## Test Results

- Weather Agent: ✅ Working
- Document RAG: ✅ Working (similarity: 0.59-0.70)
- SQL Agent: ✅ Working
- Meeting Agent: ✅ Working

## Tech Stack

- FastAPI, LangGraph, ChromaDB
- React 18, Axios
- sentence-transformers
- Docling

---

**Made with ❤️ using FastAPI, LangGraph, React, and ChromaDB**
