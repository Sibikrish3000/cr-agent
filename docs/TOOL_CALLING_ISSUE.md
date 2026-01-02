# ⚠️ Tool Calling Reliability Issue

## Problem Summary
The tests show that `openai/gpt-4o-mini` via GitHub Models API is **not reliably calling tools** despite explicit instructions. This is a known limitation with some OpenAI-compatible endpoints when used through LangChain's `bind_tools()` approach.

## Evidence from Test Output
```
TEST: Document Agent - RAG with High Confidence
✅ Response:
It seems that there's an issue with the tools required for processing your request.
```

The model is **making excuses** instead of calling the `ingest_document_to_vector_store` and `search_vector_store` tools, even though:
- ✅ Tools are properly bound with `llm.bind_tools(tools, tool_choice="auto")`
- ✅ System prompt explicitly instructs: "🔴 FIRST TOOL CALL: ingest_document_to_vector_store(...)"
- ✅ Temperature lowered to 0.1 for deterministic behavior
- ✅ File path provided in state

## Why This Happens
1. **Model Refusal**: Some models refuse to call tools if they think they can answer without them
2. **Endpoint Compatibility**: GitHub Models API may not fully support OpenAI's tool calling protocol
3. **LangChain Binding**: The `bind_tools()` approach with `tool_choice="auto"` is a "suggestion", not a requirement

## Solutions (In Order of Effectiveness)

### Option 1: Use OpenAI API Directly ✅ RECOMMENDED
```bash
# Get API key from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-...
```
**Pros**: Native OpenAI tool calling, most reliable
**Cons**: Costs $0.15 per 1M input tokens

### Option 2: Larger Ollama Models
```bash
ollama pull qwen2.5:7b      # 4.7GB, better tool calling
ollama pull mistral:7b       # 4.1GB, good for agentic workflows  
ollama pull llama3.1:8b      # 4.7GB, excellent tool calling

# Update .env:
OLLAMA_MODEL=qwen2.5:7b
```
**Pros**: Free, local, reliable tool calling
**Cons**: Requires 8GB+ RAM, slower than cloud APIs

### Option 3: Google GenAI (Gemini)
```bash
# Get API key from https://aistudio.google.com/apikey
GOOGLE_API_KEY=AIzaSy...
```
**Pros**: Free tier available (60 requests/minute), good tool calling
**Cons**: Different API structure, may need adjustments

### Option 4: Use Function Calling Pattern (Code Change)
Instead of `bind_tools(tool_choice="auto")`, use `bind_tools(tool_choice="required")` or implement a ReAct-style prompt pattern:

```python
# In agents.py, modify doc_agent_node:
llm_with_tools = llm.bind_tools(tools, tool_choice="required")  # Force tool call
```

**Pros**: Forces model to call at least one tool
**Cons**: May call wrong tool, requires multi-turn conversation handling

### Option 5: Custom Tool Orchestration
Instead of relying on the model to decide when to call tools, explicitly call them in a fixed workflow:

```python
def doc_agent_node(state):
    llm = get_llm(temperature=0.1)
    file_path = state.get("file_path")
    
    if file_path:
        # Force tool execution instead of asking model
        from tools import ingest_document_to_vector_store, search_vector_store
        doc_id = os.path.basename(file_path).replace('.', '_')
        
        # ALWAYS call these tools
        ingest_result = ingest_document_to_vector_store(file_path, doc_id)
        search_result = search_vector_store(state["messages"][-1].content, doc_id)
        
        # Then ask LLM to synthesize the answer
        system = f"Document ingested. Search results: {search_result}. Answer user's question."
        response = llm.invoke([SystemMessage(content=system)] + state["messages"])
        return {"messages": [response]}
```

**Pros**: 100% reliable, deterministic workflow
**Cons**: Less flexible, can't adapt to different query types

## Recommended Action

**For immediate testing**: Use **Option 1 (OpenAI)** or **Option 2 (Larger Ollama Model)**

**For production**: Implement **Option 5 (Custom Orchestration)** with OpenAI API for reliability

## Current Test Results

| Test | Status | Issue |
|------|--------|-------|
| Weather Agent | ✅ PASS | Tool calling works |
| Meeting Agent | ⚠️ PARTIAL | Not calling weather tools |
| SQL Agent | ✅ PASS | Query execution works |
| Document RAG (Ingest+Search) | ❌ FAIL | Not calling ingest/search tools |
| Web Search Fallback | ❌ FAIL | Not calling search tool |
| Specific Retrieval | ❌ FAIL | Not calling any tools |

**Success Rate with GitHub Models (gpt-4o-mini)**: ~33% (2/6 tests fully working)

## Next Steps

1. **Try OpenAI API** with your own API key:
   ```bash
   # Get key from https://platform.openai.com/api-keys
   echo "OPENAI_API_KEY=sk-proj-..." >> .env
   uv run test_agents.py
   ```

2. **OR use larger Ollama model**:
   ```bash
   ollama pull qwen2.5:7b
   # Update .env: OLLAMA_MODEL=qwen2.5:7b
   uv run test_agents.py
   ```

3. **OR implement Option 5** (custom orchestration) for guaranteed tool execution

---

**Note**: This is a common issue with LLM-based agentic systems. Even with perfect prompts and configuration, some models/endpoints will refuse to call tools. The solution is either to use more capable models or implement deterministic tool orchestration.
