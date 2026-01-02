# 🚀 Quick Start Guide - Agentic AI Backend

## Prerequisites
- Python 3.13+ with virtual environment activated
- Ollama running locally (optional, but recommended)
- OpenWeatherMap API key (required for weather features)

---

## Step 1: Verify Installation ✅

Dependencies are already installed. Verify with:
```powershell
python -c "import chromadb, sentence_transformers; print('✅ Vector Store packages installed')"
```

---

## Step 2: Configure Environment 🔧

### Option 1: GitHub Models (Recommended) ⭐

**Free, fast, and reliable!**

1. **Get a GitHub token:** https://github.com/settings/tokens
2. **Edit `.env`:**
```powershell
Copy-Item .env.template .env
notepad .env
```

3. **Add your tokens:**
```bash
GITHUB_TOKEN=ghp_your_github_token_here
OPENWEATHERMAP_API_KEY=your_weather_api_key_here
```

**See detailed setup:** [GITHUB_MODELS_SETUP.md](GITHUB_MODELS_SETUP.md)

### Option 2: Local with Ollama

If you prefer running locally:

1. **Install a capable Ollama model:**
```powershell
ollama pull llama3.2  # Better than qwen3:0.6b
```

2. **Configure `.env`:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OPENWEATHERMAP_API_KEY=your_weather_api_key_here
```

**Note:** GitHub Models recommended for better reliability and tool calling.

---

## Step 3: Initialize Database 💾

```powershell
python seed_data.py
```

This creates:
- SQLite database (`database.db`)
- 3 sample meetings for testing

Expected output:
```
Database initialized
Sample meetings created successfully
```

---

## Step 4: Run Tests 🧪

```powershell
python test_agents.py
```

This runs 6 comprehensive tests:
1. ✅ Weather Agent - Current weather
2. ✅ Meeting Agent - Weather-conditional scheduling
3. ✅ SQL Agent - Database queries
4. ✅ Document RAG - High confidence retrieval
5. ✅ Web Fallback - Low confidence web search
6. ✅ Specific Retrieval - Precise information extraction

**First run will download the embedding model (~80MB) - this is normal!**

---

## Step 5: Start the API Server 🌐

```powershell
python main.py
```

Server starts at: **http://127.0.0.1:8000**

API docs available at: **http://127.0.0.1:8000/docs**

---

## Step 6: Test API Endpoints 📡

### Test 1: Weather Query
```powershell
$body = @{
    query = "What's the weather in Paris today?"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/chat" `
    -ContentType "application/json" -Body $body
```

### Test 2: Upload Document
```powershell
$filePath = "C:\path\to\your\document.pdf"
curl -X POST "http://127.0.0.1:8000/upload" -F "file=@$filePath"
```

Response will include `file_path` - use it in the next request.

### Test 3: RAG Query
```powershell
$body = @{
    query = "What does the document say about remote work?"
    file_path = "D:\python_workspace\multi-agent\uploads\uuid.pdf"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/chat" `
    -ContentType "application/json" -Body $body
```

### Test 4: Meeting Scheduling
```powershell
$body = @{
    query = "Schedule a team meeting tomorrow at 3 PM in London if weather is good. Include Alice and Bob."
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/chat" `
    -ContentType "application/json" -Body $body
```

### Test 5: SQL Query
```powershell
$body = @{
    query = "Show me all meetings scheduled for this week"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/chat" `
    -ContentType "application/json" -Body $body
```

---

## Expected Behavior 🎯

### Weather Agent
- Returns current temperature, conditions, humidity
- Handles "today", "tomorrow", "yesterday" queries

### Document RAG Agent
- **High confidence (score ≥ 0.7):** Returns answer from document
- **Low confidence (score < 0.7):** Automatically searches web for additional info
- First query ingests document into vector store (takes a few seconds)

### Meeting Agent
- Checks weather forecast
- **Good weather (Clear/Clouds):** ✅ Schedules meeting
- **Bad weather (Rain/Storm):** ❌ Refuses with explanation
- Detects schedule conflicts automatically

### SQL Agent
- Converts natural language to SQL
- Queries SQLite database
- Returns formatted results

---

## Troubleshooting 🔧

### Issue: "No valid LLM configured"
**Solution:** Ensure Ollama is running at http://localhost:11434
```powershell
# Check if Ollama is running
Invoke-WebRequest http://localhost:11434
```

### Issue: "Weather API key not configured"
**Solution:** Add your API key to `.env`:
```bash
OPENWEATHERMAP_API_KEY=your_key_here
```

### Issue: "Document ingestion failed"
**Solution:** Check file format (PDF/TXT/MD/DOCX) and size (<10MB)

### Issue: Slow first RAG query
**Expected:** First run downloads sentence-transformers model (~80MB)
Subsequent queries will be fast.

### Issue: Import errors in IDE
**Normal:** VSCode may show import warnings until packages are fully indexed. Code will run fine.

---

## Understanding the RAG Workflow 📚

```
User uploads document.pdf
         ↓
1. Parse with Docling
         ↓
2. Chunk into 500-char pieces (50-char overlap)
         ↓
3. Generate embeddings with sentence-transformers
         ↓
4. Store in ChromaDB (./chroma_db/)
         ↓
User asks: "What is the policy?"
         ↓
5. Search vector store for similar chunks
         ↓
6. Check similarity score
         ↓
   ┌─────────────┬──────────────┐
   │ Score ≥ 0.7 │ Score < 0.7  │
   │ (confident) │ (uncertain)  │
   └─────────────┴──────────────┘
         │              │
         ↓              ↓
   Return doc      Search web
   answer          + combine
                   results
```

---

## File Structure 📁

```
multi-agent/
├── main.py                 # FastAPI server
├── agents.py              # LangGraph agents
├── tools.py               # Agent tools
├── vector_store.py        # ChromaDB manager (NEW)
├── database.py            # SQLite config
├── models.py              # SQLAlchemy models
├── test_agents.py         # Test suite
├── seed_data.py           # DB initialization
├── .env                   # Your configuration
├── .env.template          # Configuration template
├── database.db            # SQLite database
├── chroma_db/             # Vector store (auto-created)
├── uploads/               # Uploaded documents
└── IMPLEMENTATION_COMPLETE.md  # Full documentation
```

---

## Next Steps 🎯

1. **Explore the API:** Visit http://127.0.0.1:8000/docs
2. **Try different queries:** Test edge cases and complex scenarios
3. **Upload your documents:** Try PDFs, policies, resumes
4. **Check vector store:** Inspect `./chroma_db/` directory
5. **Review logs:** Monitor agent decisions and tool calls

---

## Performance Tips ⚡

- **Vector Store:** First query per document is slow (ingestion). Subsequent queries are fast.
- **LLM:** Ollama with qwen3:0.6b is fast but less accurate. Try larger models like `llama2` for better quality.
- **Weather API:** Free tier has rate limits (60 calls/minute)
- **Document Size:** Keep under 10MB for fast processing

---

## Support 📞

- **Full Documentation:** See `IMPLEMENTATION_COMPLETE.md`
- **Project Overview:** Check `PROJECT_SUMMARY.md`
- **Ollama Setup:** Read `OLLAMA_SETUP.md`

---

**You're all set! 🎉 Start making requests to your AI backend!**
