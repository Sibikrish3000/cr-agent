import os
from typing import Annotated, Literal, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from tools import get_current_weather, get_weather_forecast, duckduckgo_search, read_document_with_docling

# LLM Configuration with Fallback
def get_llm(temperature=0):
    """Get LLM with fallback support for OpenAI, Google GenAI, and Ollama."""
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
    
    # Check for placeholder strings
    is_openai_valid = openai_key and "your_openai_api_key" not in openai_key and len(openai_key) > 20
    is_google_valid = google_key and "your_google_genai_api_key" not in google_key and len(google_key) > 20

    
    # Try OpenAI first if valid
    if is_openai_valid:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                temperature=temperature,
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
        except Exception as e:
            print(f"OpenAI initialization failed: {e}")
    
    # Fallback to Google GenAI if valid
    if is_google_valid:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model="gemma-3-12b", temperature=temperature)
        except Exception as e:
            print(f"Google GenAI initialization failed: {e}")
    
    # Fallback to Ollama if configured
    if ollama_base_url:
        try:
            from langchain_ollama import ChatOllama
            print(f"Using Ollama fallback: {ollama_model} at {ollama_base_url}")
            return ChatOllama(model=ollama_model, base_url=ollama_base_url, temperature=temperature)
        except Exception as e:
            print(f"Ollama initialization failed: {e}")
    
    # If all invalid or fail, but keys exist, try anyway (last resort)
    if openai_key:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(temperature=temperature,model=os.getenv("OPENAI_MODEL","gpt-4o"),base_url=os.getenv("OPENAI_BASE_URL","https://api.openai.com/v1"))
    if google_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemma-3-12b", temperature=temperature)

    raise ValueError("No valid LLM configured. Set OPENAI_API_KEY, GOOGLE_API_KEY, or OLLAMA_BASE_URL in .env")

from database import engine, get_session
from models import Meeting
from sqlmodel import select, Session

# --- SQL Tool for Agent 4 ---
# We implement this manually or use LangChain's SQLDatabase, 
# but since we use SQLModel/DuckDB, we can write a specific tool/chain.
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

# Setup SQL Database for LangChain (Moved inside query_db_node to avoid top-level inspection issues)
from datetime import datetime, timedelta


def query_db_node(state):
    """Agent 4: NL to SQL."""
    # Initialize SQLDatabase lazily
    db = SQLDatabase(engine)
    
    messages = state["messages"]
    last_user_message = messages[-1].content
    
    # We'll use a simple chain here with SQLite-specific guidance
    llm = get_llm(temperature=0)
    
    # Create a custom prompt that emphasizes SQLite syntax
    from langchain_core.prompts import PromptTemplate
    
    # Get current date for SQL queries (to avoid timezone issues with SQLite's 'now')
    from datetime import datetime
    current_date = datetime.now().strftime('%Y-%m-%d')
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    sqlite_prompt = PromptTemplate.from_template(
        """Given an input question, create a syntactically correct SQLite query to run.
        
CONTEXT:
- Today's date is: {current_date}
- Tomorrow's date is: {tomorrow_date}

TABLE NAME:
- The table name is 'meeting' (singular).

COLUMNS:
- id, title, description, start_time, end_time, participants

DATE FILTERING RULES:
- To find meetings for a specific day, use: WHERE date(start_time) = 'YYYY-MM-DD'
- For tomorrow's meetings, use: WHERE date(start_time) = '{tomorrow_date}'
- For today's meetings, use: WHERE date(start_time) = '{current_date}'

Database schema:
{{table_info}}

Question: {{input}}

Return ONLY the SQL query. No markdown, no explanations.
SQLQuery: """
    )
    
    try:
        # Get table info
        table_info = db.get_table_info()
        
        # Generate query with SQLite-specific prompt
        prompt_input = {
            "input": last_user_message,
            "table_info": table_info,
            "current_date": current_date,
            "tomorrow_date": tomorrow_date
        }
        response = llm.invoke([SystemMessage(content=sqlite_prompt.format(**prompt_input))])
        
        # Extract SQL from response
        sql_query = response.content.strip()
        
        # Clean up the query
        if "SQLQuery:" in sql_query:
            sql_query = sql_query.split("SQLQuery:")[-1].strip()
        
        # Remove markdown code blocks if present
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        sql_query = sql_query.rstrip(';').strip()
        
        # Execute the cleaned query
        result = db.run(sql_query)
        
        # Format results into natural language
        if result and result != "[]":
            # Parse the result string (it's typically a string representation of a list of tuples)
            import ast
            try:
                parsed_result = ast.literal_eval(result)
                if isinstance(parsed_result, list) and len(parsed_result) > 0:
                    # Format based on what's being queried
                    if "meeting" in last_user_message.lower():
                        formatted_results = []
                        for row in parsed_result:
                            # Handle both tuple and dict results (SQLDatabase can return both depending on config)
                            if isinstance(row, dict):
                                title = row.get("title", "Meeting")
                                description = row.get("description", "")
                                location = row.get("location", "")
                                start_time = row.get("start_time", "")
                                end_time = row.get("end_time", "")
                                participants = row.get("participants", "")
                            elif len(row) >= 7:
                                # id, title, description, location, start_time, end_time, participants
                                meeting_id, title, description, location, start_time, end_time, participants = row[:7]
                            elif len(row) >= 6:
                                # id, title, description, start_time, end_time, participants (old schema)
                                meeting_id, title, description, start_time, end_time, participants = row[:6]
                                location = ""
                            else:
                                # Fallback for partial selects
                                title = row[0] if len(row) > 0 else "Meeting"
                                start_time = row[1] if len(row) > 1 else ""
                                description = ""
                                location = ""
                                end_time = ""
                                participants = ""
                                
                            # Format datetime to human-readable format
                            try:
                                from datetime import datetime as dt
                                # Handle various formats
                                start_str = str(start_time).replace('.000000', '')
                                if ' ' in start_str:
                                    start_dt = dt.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                                else:
                                    start_dt = dt.fromisoformat(start_str)
                                    
                                end_str = str(end_time).replace('.000000', '')
                                if ' ' in end_str:
                                    end_dt = dt.strptime(end_str, "%Y-%m-%d %H:%M:%S")
                                else:
                                    end_dt = dt.fromisoformat(end_str)
                                
                                # Format as "Jan 3, 2026 at 2:00 PM"
                                start_formatted = start_dt.strftime("%b %d, %Y at %I:%M %p")
                                end_formatted = end_dt.strftime("%I:%M %p")
                                time_display = f"{start_formatted} to {end_formatted}"
                            except Exception as e:
                                # Fallback if parsing fails
                                time_display = f"{start_time} to {end_time}"
                            
                            # Format location display
                            location_display = f"\n   Location: {location}" if location else ""
                            
                            formatted_results.append(
                                f"📅 **{title}**"
                                f"\n\n{time_display}{location_display}"
                                f"\n\n{description}"
                                f"\n\nParticipants: {participants}"
                            )
                        response_text = f"Found {len(parsed_result)} meeting(s):\n\n" + "\n\n".join(formatted_results)
                    else:
                        # Generic formatting for other queries
                        response_text = f"Found {len(parsed_result)} result(s):\n\n"
                        for row in parsed_result:
                            response_text += f"• {', '.join(str(item) for item in row)}\n"
                else:
                    response_text = f"Query executed successfully.\n\nResult: {result}"
            except (ValueError, SyntaxError):
                # If parsing fails, use LLM to format the result
                format_prompt = f"""Format this SQL query result into natural language:

Query: {sql_query}
Raw Result: {result}

Provide a clear, human-readable response."""
                format_response = llm.invoke([SystemMessage(content=format_prompt)])
                response_text = format_response.content
        else:
            response_text = "No results found."
            
    except Exception as e:
        response_text = f"Error querying database: {e}"
        
    return {"messages": [AIMessage(content=response_text)]}

# We need a `schedule_meeting` tool for Agent 3.
from langchain_core.tools import tool

@tool
def schedule_meeting(title: str, start_time_str: str, end_time_str: str, participants: str = "", city: str = "") -> str:
    """
    Schedule a meeting in the database after checking weather conditions.
    Only schedules if weather is good (Clear, Clouds, Fair conditions).
    
    Args:
        title: Meeting title
        start_time_str: Start time in ISO format (YYYY-MM-DDTHH:MM:SS)
        end_time_str: End time in ISO format (YYYY-MM-DDTHH:MM:SS)
        participants: Comma-separated list of participants
        city: City to check weather for (required for weather-conditional scheduling)
        
    Returns:
        Success or failure message with reasoning
    """
    from datetime import datetime
    import requests
    
    try:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
    except ValueError:
        return "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)."
    
    # Check weather if city is provided
    if city:
        api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if api_key:
            try:
                url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # Check forecast for the meeting time
                    weather_condition = "unknown"
                    
                    # Look for forecast closest to meeting time
                    if 'list' in data and len(data['list']) > 0:
                        # Get main weather condition from first available forecast
                        weather_condition = data['list'][0]['weather'][0]['main']
                        
                        # Evaluate if weather is good
                        bad_conditions = ['Rain', 'Drizzle', 'Thunderstorm', 'Snow', 'Mist', 'Fog']
                        good_conditions = ['Clear', 'Clouds']
                        
                        if weather_condition in bad_conditions:
                            return f"❌ Meeting NOT scheduled. Weather condition '{weather_condition}' is unfavorable in {city}. Recommendation: Reschedule to a day with better weather."
                        elif weather_condition not in good_conditions:
                            return f"⚠️ Meeting NOT scheduled. Weather condition '{weather_condition}' is uncertain in {city}. Recommendation: Check forecast again closer to meeting time."
            
            except Exception as e:
                return f"Weather check failed: {e}. Meeting not scheduled for safety."

    # Check for schedule conflicts
    with Session(engine) as session:
        statement = select(Meeting).where(
            (Meeting.start_time < end_time) & (Meeting.end_time > start_time)
        )
        conflicts = session.exec(statement).all()
        if conflicts:
            conflict_details = ", ".join([f"'{m.title}' ({m.start_time} - {m.end_time})" for m in conflicts])
            return f"❌ Meeting conflict detected with: {conflict_details}. Please choose a different time slot."
        
        # Schedule the meeting
        meeting = Meeting(
            title=title,
            start_time=start_time,
            end_time=end_time,
            participants=participants,
            description=f"Weather-checked meeting in {city}" if city else None
        )
        session.add(meeting)
        session.commit()
        
        weather_note = f" (Weather in {city} is favorable)" if city else ""
        return f"✅ Meeting '{title}' scheduled successfully from {start_time} to {end_time}{weather_note}."

# --- State ---
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    file_path: str | None # For Agent 2

# --- Router ---
def router(state) -> Literal["weather_agent", "doc_agent", "meeting_agent", "sql_agent", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    
    # Simple keyword based or specific routing LLM.
    # For robust agentic behavior, we should use a router chain. 
    # But to follow the "Agent" boxes in the diagram, let's explicitely route.
    
    # We can use an LLM to classify.
    llm = get_llm(temperature=0)
    system = """You are a router. Classify the user query into ONE of these agents:

1. 'weather_agent': ONLY for standalone weather questions (no meeting scheduling).
   Examples: "What's the weather?", "Will it rain tomorrow?"

2. 'meeting_agent': For scheduling/creating NEW meetings OR cancelling/deleting meetings.
   Examples: "Schedule a meeting", "Book a team meeting", "Cancel all meetings", "Unschedule tomorrow's meetings"
   
3. 'sql_agent': For querying EXISTING meetings (show, list, find).
   Examples: "Show all meetings", "What meetings do I have tomorrow?", "List scheduled meetings"

4. 'doc_agent': For document analysis or general knowledge.
   Examples: "What's in this PDF?", "Explain the policy", "What are AI trends?"

CRITICAL: "Schedule", "book", "cancel", "unschedule", "delete" → meeting_agent, NOT sql_agent!

Return ONLY ONE agent name."""
    
    # We can use structured output or just string.
    response = llm.invoke([SystemMessage(content=system), last_message])
    decision = response.content.strip().lower()
    
    # Priority routing (order matters!)
    if "meeting" in decision and ("schedule" in last_message.content.lower() or "book" in last_message.content.lower() or "create" in last_message.content.lower()):
        return "meeting_agent"
    if "meeting_agent" in decision:
        return "meeting_agent"
    if "weather_agent" in decision:
        return "weather_agent"
    if "sql_agent" in decision:
        return "sql_agent"
    if "doc_agent" in decision:
        return "doc_agent"
    
    # Keyword fallback
    query_lower = last_message.content.lower()
    if any(word in query_lower for word in ["schedule", "book", "arrange", "set up", "cancel", "unschedule", "delete", "remove"]) and "meeting" in query_lower:
        return "meeting_agent"
    if any(word in query_lower for word in ["show", "list", "display", "find", "get"]) and "meeting" in query_lower:
        return "sql_agent"
    if "weather" in query_lower and "meeting" not in query_lower:
        return "weather_agent"
    
    # Default fallback
    return "doc_agent" 

# --- Agent Nodes ---

def weather_agent_node(state):
    llm = get_llm(temperature=0)
    tools = [get_current_weather, get_weather_forecast]
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def doc_agent_node(state):
    """Document + Web Intelligence Agent with FORCED RAG execution."""
    llm = get_llm(temperature=0.1)
    file_path = state.get("file_path")
    
    # If file uploaded, FORCE tool execution instead of asking model
    if file_path:
        import os
        from tools import ingest_document_to_vector_store, search_vector_store, duckduckgo_search
        
        doc_id = os.path.basename(file_path).replace('.', '_')
        user_query = state["messages"][-1].content
        
        # STEP 1: Force ingest (deterministic)
        print(f"🔴 FORCING ingest_document_to_vector_store('{file_path}', '{doc_id}', is_temporary=True)")
        try:
            ingest_result = ingest_document_to_vector_store.invoke({
                "file_path": file_path, 
                "document_id": doc_id,
                "is_temporary": True
            })
            print(f"✅ Ingest result: {ingest_result}")
        except Exception as e:
            print(f"❌ Ingest failed: {e}")
            ingest_result = f"Error: {e}"
        
        # STEP 2: Force search (deterministic)
        print(f"🔴 FORCING search_vector_store('{user_query}', '{doc_id}', search_type='temporary')")
        try:
            search_results = search_vector_store.invoke({
                "query": user_query, 
                "document_id": doc_id, 
                "top_k": 3,
                "search_type": "temporary"
            })
            print(f"✅ Search results: {search_results[:200]}...")
            
            # Parse similarity score from results
            import re
            scores = re.findall(r'Similarity: ([\d\.]+)', search_results)
            max_score = float(scores[0]) if scores else 0.0
            print(f"📊 Best similarity score: {max_score}")
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            search_results = f"Error: {e}"
            max_score = 0.0
        
        # STEP 3: Decide if we need web search (< 0.7 threshold)
        web_results = ""
        if max_score < 0.7:
            print(f"⚠️ Low confidence ({max_score} < 0.7), calling web search")
            try:
                web_results = duckduckgo_search.invoke({"query": user_query})
                print(f"🌐 Web search results: {web_results[:200]}...")
            except Exception as e:
                print(f"❌ Web search failed: {e}")
                web_results = f"Web search error: {e}"
        
        # STEP 4: Ask LLM to synthesize answer from results
        synthesis_prompt = f"""You are answering based on the following information:

DOCUMENT SEARCH RESULTS (Similarity: {max_score:.2f}):
{search_results}

{f'WEB SEARCH RESULTS (fallback):{chr(10)}{web_results}' if web_results else ''}

USER QUESTION: {user_query}

Provide a clear, accurate answer based on the information above."""
        
        response = llm.invoke([SystemMessage(content=synthesis_prompt)])
        return {"messages": [response]}
    
    # No file uploaded - search persistent documents first, then web
    else:
        from tools import search_vector_store, duckduckgo_search
        user_query = state["messages"][-1].content
        
        # Try searching all persistent documents first (empty string searches all)
        print(f"🔍 No file uploaded, searching persistent documents for: {user_query}")
        try:
            search_results = search_vector_store.invoke({
                "query": user_query, 
                "document_id": "", 
                "top_k": 3,
                "search_type": "persistent"
            })
            
            # Parse similarity score
            import re
            scores = re.findall(r'Similarity: ([\d\.]+)', search_results)
            max_score = float(scores[0]) if scores else 0.0
            print(f"📊 Best persistent doc score: {max_score}")
            
            # If good match in persistent docs, use it
            if max_score >= 0.5:  # Lower threshold for persistent docs
                print(f"✅ Found relevant info in persistent documents (score: {max_score})")
                synthesis_prompt = f"""Answer based on company documents:

COMPANY DOCUMENTS:
{search_results}

USER QUESTION: {user_query}

Provide a clear answer based on the company documents above."""
                response = llm.invoke([SystemMessage(content=synthesis_prompt)])
                return {"messages": [response]}
        except Exception as e:
            print(f"⚠️ Persistent doc search failed: {e}")
        
        # Fallback to web search if no good persistent doc match
        print(f"🌐 Using web search for: {user_query}")
        try:
            web_results = duckduckgo_search.invoke({"query": user_query})
            synthesis_prompt = f"""Answer the question using this web search information:

WEB SEARCH RESULTS:
{web_results}

USER QUESTION: {user_query}

Provide a clear answer."""
            response = llm.invoke([SystemMessage(content=synthesis_prompt)])
            return {"messages": [response]}
        except Exception as e:
            response = llm.invoke(state["messages"])
            return {"messages": [response]}

def meeting_agent_node_implementation(state):
    """Meeting Scheduling and Cancellation Agent with FORCED weather check."""
    llm = get_llm(temperature=0.1)
    user_query = state["messages"][-1].content
    
    from tools import get_weather_forecast, schedule_meeting, cancel_meetings
    from datetime import datetime, timedelta
    
    # Check if this is a cancellation request
    query_lower = user_query.lower()
    if any(word in query_lower for word in ["cancel", "unschedule", "delete", "remove"]) and ("meeting" in query_lower or "meetings" in query_lower):
        # Parse cancellation request
        date_filter = "all"
        if "tomorrow" in query_lower:
            date_filter = "tomorrow"
        elif "today" in query_lower:
            date_filter = "today"
        
        print(f"🗑️  FORCING cancel_meetings(date_filter='{date_filter}')")
        try:
            cancel_result = cancel_meetings.invoke({"date_filter": date_filter, "meeting_ids": ""})
            print(f"✅ Cancel result: {cancel_result}")
            return {"messages": [AIMessage(content=cancel_result)]}
        except Exception as e:
            print(f"❌ Cancellation failed: {e}")
            return {"messages": [AIMessage(content=f"❌ Failed to cancel meetings: {e}")]}
    
    # Parse meeting request using LLM
    parse_prompt = f"""Extract meeting details from this request: "{user_query}"

Return ONLY a JSON object with these fields:
- title: str (meeting title)
- date: str ("tomorrow", "today", or "YYYY-MM-DD")
- time: str ("14:00", "2pm", etc.) 
- city: str (default "Chennai" if not mentioned)
- location: str (specific venue or city)
- participants: str (comma-separated names)
- duration_hours: int (default 1)

Example: {{"title": "Team Meeting", "date": "tomorrow", "time": "14:00", "city": "Chennai", "location": "Conference Room A", "participants": "John, Sarah", "duration_hours": 1}}"""
    
    parse_response = llm.invoke([HumanMessage(content=parse_prompt)])
    print(f"📋 Parsed meeting request: {parse_response.content}")
    
    # Extract JSON from response
    import json
    import re
    json_match = re.search(r'\{[^}]+\}', parse_response.content)
    if json_match:
        try:
            meeting_data = json.loads(json_match.group())
            
            # Convert date to actual datetime
            if "tomorrow" in meeting_data.get("date", "").lower():
                meeting_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                days_ahead = 1
            elif "today" in meeting_data.get("date", "").lower():
                meeting_date = datetime.now().strftime("%Y-%m-%d")
                days_ahead = 0
            else:
                meeting_date = meeting_data.get("date", datetime.now().strftime("%Y-%m-%d"))
                days_ahead = (datetime.strptime(meeting_date, "%Y-%m-%d") - datetime.now()).days
            
            # Convert time to 24hr format
            time_str = meeting_data.get("time", "14:00")
            if "pm" in time_str.lower() and "12" not in time_str:
                hour = int(re.findall(r'\d+', time_str)[0]) + 12
                time_24hr = f"{hour:02d}:00"
            else:
                time_24hr = re.sub(r'[^\d:]', '', time_str)
                if len(time_24hr) <= 2:
                    time_24hr = f"{time_24hr}:00"
            
            start_time = f"{meeting_date} {time_24hr}:00"
            end_time = f"{meeting_date} {int(time_24hr.split(':')[0]) + meeting_data.get('duration_hours', 1):02d}:{time_24hr.split(':')[1]}:00"
            city = meeting_data.get("city", "Chennai")
            location = meeting_data.get("location", city)
            
            # STEP 1: Force weather check
            print(f"🌤️  FORCING get_weather_forecast('{city}', {days_ahead})")
            try:
                weather_data = get_weather_forecast.invoke({"city": city})
                
                # Extract weather description from forecast data
                if isinstance(weather_data, dict) and 'list' in weather_data:
                    # Get first forecast entry (next 3 hours)
                    first_forecast = weather_data['list'][0] if weather_data['list'] else {}
                    weather_desc = first_forecast.get('weather', [{}])[0].get('description', 'unknown')
                    temp = first_forecast.get('main', {}).get('temp', 'N/A')
                    weather_result = f"{weather_desc}, {temp}°C"
                else:
                    weather_result = str(weather_data)[:200]
                
                print(f"✅ Weather: {weather_result}")
                
                # Evaluate weather
                bad_conditions = ["rain", "drizzle", "thunderstorm", "snow", "mist", "fog"]
                is_bad_weather = any(cond in weather_result.lower() for cond in bad_conditions)
                weather_emoji = "❌" if is_bad_weather else "✅"
                
            except Exception as e:
                print(f"❌ Weather check failed: {e}")
                weather_result = "Unknown"
                weather_emoji = "⚠️"
                is_bad_weather = False
            
            # STEP 2: Schedule meeting (even if bad weather, just warn)
            print(f"📅 FORCING schedule_meeting('{meeting_data.get('title')}', {start_time}, {end_time})")
            try:
                schedule_result = schedule_meeting.invoke({
                    "title": meeting_data.get("title", "Meeting"),
                    "description": f"Weather: {weather_result[:100]}",
                    "start_time": start_time,
                    "end_time": end_time,
                    "participants": meeting_data.get("participants", ""),
                    "location": location
                })
                print(f"✅ Schedule result: {schedule_result}")
                
                # Build response
                response_text = f"{weather_emoji} Meeting scheduled!\n\n"
                response_text += f"Title: {meeting_data.get('title')}\n\n"
                response_text += f"Time: {start_time} to {end_time}\n\n"
                response_text += f"Location: {location}\n\n"
                response_text += f"Participants: {meeting_data.get('participants')}\n\n"
                response_text += f"Weather: {weather_result[:200]}\n\n"
                if is_bad_weather:
                    response_text += "⚠️ Warning: Weather conditions may not be ideal for this meeting."
                
                return {"messages": [AIMessage(content=response_text)]}
                
                return {"messages": [AIMessage(content=response_text)]}
                
            except Exception as e:
                print(f"❌ Scheduling failed: {e}")
                return {"messages": [AIMessage(content=f"❌ Failed to schedule: {e}")]}
                
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            return {"messages": [AIMessage(content=f"Could not parse meeting request: {e}. Please provide title, date, time, and participants.")]}
    
    # Fallback if parsing fails
    return {"messages": [AIMessage(content="Could not understand meeting request. Please specify: title, date/time, and participants.")]}

# --- Graph Construction ---
workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("weather_agent", weather_agent_node)
workflow.add_node("doc_agent", doc_agent_node)
workflow.add_node("meeting_agent", meeting_agent_node_implementation)
workflow.add_node("sql_agent", query_db_node)

# Tool Node (Shared or separate? For simplicity, we can use a generic prebuilt ToolNode 
# but each agent has different tools. So we need to handle tool calls.
# The nodes above (except sql) return an AIMessage which MIGHT have tool_calls.
# We need to execute those tools.

from langgraph.prebuilt import ToolNode

# Import cancel_meetings tool
from tools import cancel_meetings

# Define tool nodes for each agent to ensure they only access their allowed tools
weather_tools_node = ToolNode([get_current_weather, get_weather_forecast])
doc_tools_node = ToolNode([read_document_with_docling, duckduckgo_search])
meeting_tools_node = ToolNode([get_weather_forecast, schedule_meeting, cancel_meetings])

workflow.add_node("weather_tools", weather_tools_node)
workflow.add_node("doc_tools", doc_tools_node)
workflow.add_node("meeting_tools", meeting_tools_node)

# Conditional Edges for tools
def should_continue(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Creating the flow
# Router -> Agent -> (if tool) -> ToolNode -> Agent ...
# To simplify, we'll let the Router pick the start node.

workflow.add_conditional_edges(START, router, {
    "weather_agent": "weather_agent",
    "doc_agent": "doc_agent",
    "meeting_agent": "meeting_agent",
    "sql_agent": "sql_agent"
})

# Weather Flow
workflow.add_conditional_edges("weather_agent", should_continue, {"tools": "weather_tools", END: END})
workflow.add_edge("weather_tools", "weather_agent")

# Doc Flow
workflow.add_conditional_edges("doc_agent", should_continue, {"tools": "doc_tools", END: END})
workflow.add_edge("doc_tools", "doc_agent")

# Meeting Flow
workflow.add_conditional_edges("meeting_agent", should_continue, {"tools": "meeting_tools", END: END})
workflow.add_edge("meeting_tools", "meeting_agent")

# SQL Flow (No tools, just runs)
workflow.add_edge("sql_agent", END)

app = workflow.compile()
