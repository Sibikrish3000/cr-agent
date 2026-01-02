
# ⚠️ Tool Calling Reliability

## Problem
Some LLM endpoints (e.g., GitHub Models API, small Ollama models) do not reliably call tools, even with explicit instructions and proper binding. This affects agentic workflows that depend on tool execution.

## Why?
1. **Model refusal:** Some models answer directly instead of calling tools
2. **Endpoint compatibility:** Not all APIs fully support OpenAI's tool calling protocol
3. **LangChain binding:** `bind_tools(tool_choice="auto")` is a suggestion, not a requirement

## Solutions

### 1. Use OpenAI API (Recommended)
```bash
OPENAI_API_KEY=sk-...
# Most reliable tool calling
```

### 2. Use Larger Ollama Models
```bash
ollama pull qwen2.5:7b
ollama pull mistral
ollama pull llama3.2
# Update .env: OLLAMA_MODEL=qwen2.5:7b
```

### 3. Use Google GenAI (Gemini)
```bash
GOOGLE_API_KEY=AIzaSy...
# Free tier, good tool calling
```

### 4. Force Tool Calling in Code
Use `bind_tools(tool_choice="required")` or custom orchestration:
```python
def doc_agent_node(state):
   # Always call tools, then synthesize answer
   ingest_result = ingest_document_to_vector_store(...)
   search_result = search_vector_store(...)
   # Ask LLM to synthesize
```

## Recommended Action
- For testing: Use OpenAI or a larger Ollama model
- For production: Implement deterministic tool orchestration

## Test Results

| Test                | Status   | Issue                        |
|---------------------|----------|------------------------------|
| Weather Agent       | ✅ PASS  | Tool calling works           |
| Meeting Agent       | ⚠️ PARTIAL| Not calling weather tools    |
| SQL Agent           | ✅ PASS  | Query execution works        |
| Document RAG        | ❌ FAIL  | Not calling ingest/search    |
| Web Search Fallback | ❌ FAIL  | Not calling search tool      |
| Specific Retrieval  | ❌ FAIL  | Not calling any tools        |

Success rate with GitHub Models (gpt-4o-mini): ~33%

## Next Steps
1. Try OpenAI API: add your key to `.env` and rerun tests
2. Use a larger Ollama model: pull and update `.env`
3. Implement deterministic tool orchestration in agents

---

**Note:** This is a common issue in agentic LLM systems. Deterministic tool orchestration or more capable models are required for reliability.
