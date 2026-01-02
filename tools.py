import os
from pprint import pprint
import requests
from langchain_core.tools import tool
from vector_store import get_vector_store
try:
    from ddgs import DDGS
except ImportError:
    DDGS = None
try:
    from docling.document_converter import DocumentConverter
except ImportError:
    DocumentConverter = None

# Weather Tools
@tool
def get_current_weather(city: str) -> dict:
    """Get the current weather for a specific city. Returns temperature, condition, etc."""
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return {"error": "Weather API key not configured."}
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"API Error: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_weather_forecast(city: str) -> dict:
    """Get the 5-day weather forecast for a city. Useful for checking future weather."""
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return {"error": "Weather API key not configured."}
    
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"API Error: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

@tool
def schedule_meeting(title: str, description: str, start_time: str, end_time: str, participants: str, location: str = "") -> str:
    """
    Schedule a meeting in the database.
    
    Args:
        title: Meeting title
        description: Meeting description (can include weather info)
        start_time: Start time in format 'YYYY-MM-DD HH:MM:SS'
        end_time: End time in format 'YYYY-MM-DD HH:MM:SS'
        participants: Comma-separated list of participant names
        location: Meeting location
        
    Returns:
        Success or error message
    """
    try:
        from database import engine
        from sqlmodel import Session
        from models import Meeting
        from datetime import datetime
        
        # Convert string datetime to datetime objects for SQLite
        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        
        meeting = Meeting(
            title=title,
            description=description,
            location=location,
            start_time=start_dt,
            end_time=end_dt,
            participants=participants
        )
        
        with Session(engine) as session:
            session.add(meeting)
            session.commit()
            session.refresh(meeting)
            
        return f"✅ Meeting scheduled successfully! ID: {meeting.id}, Title: {title}, Time: {start_time} to {end_time}"
        
    except Exception as e:
        return f"❌ Failed to schedule meeting: {e}"

@tool
def cancel_meetings(date_filter: str = "all", meeting_ids: str = "") -> str:
    """
    Cancel/delete meetings from the database.
    
    Args:
        date_filter: Filter for which meetings to cancel - "all", "today", "tomorrow", or specific date "YYYY-MM-DD"
        meeting_ids: Optional comma-separated list of specific meeting IDs to cancel (e.g., "1,2,3")
        
    Returns:
        Success message with count of cancelled meetings
    """
    try:
        from database import engine
        from sqlmodel import Session, select
        from models import Meeting
        from datetime import datetime, timedelta
        
        with Session(engine) as session:
            # Build query based on filters
            if meeting_ids:
                # Cancel specific meeting IDs
                ids = [int(id.strip()) for id in meeting_ids.split(",")]
                meetings = session.exec(select(Meeting).where(Meeting.id.in_(ids))).all()
            else:
                # Cancel by date filter
                if date_filter == "today":
                    today = datetime.now().date()
                    meetings = session.exec(
                        select(Meeting).where(
                            (Meeting.start_time >= today) & 
                            (Meeting.start_time < today + timedelta(days=1))
                        )
                    ).all()
                elif date_filter == "tomorrow":
                    tomorrow = (datetime.now() + timedelta(days=1)).date()
                    meetings = session.exec(
                        select(Meeting).where(
                            (Meeting.start_time >= tomorrow) & 
                            (Meeting.start_time < tomorrow + timedelta(days=1))
                        )
                    ).all()
                elif date_filter == "all":
                    meetings = session.exec(select(Meeting)).all()
                else:
                    # Try parsing as specific date
                    try:
                        target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                        meetings = session.exec(
                            select(Meeting).where(
                                (Meeting.start_time >= target_date) & 
                                (Meeting.start_time < target_date + timedelta(days=1))
                            )
                        ).all()
                    except ValueError:
                        return f"❌ Invalid date format: {date_filter}. Use 'today', 'tomorrow', 'all', or 'YYYY-MM-DD'"
            
            if not meetings:
                return f"No meetings found to cancel for filter: {date_filter}"
            
            # Delete meetings
            cancelled_titles = [f"'{m.title}' at {m.start_time}" for m in meetings]
            for meeting in meetings:
                session.delete(meeting)
            
            session.commit()
            
            return f"✅ Cancelled {len(meetings)} meeting(s):\n" + "\n".join(f"  • {title}" for title in cancelled_titles)
            
    except Exception as e:
        return f"❌ Failed to cancel meetings: {e}"

# Web Tools
@tool
def duckduckgo_search(query: str) -> str:
    """Perform a DuckDuckGo search and return relevant results."""
    if not DDGS:
        return "DuckDuckGo Search library not installed. Install with: pip install ddgs"
    try:
        with DDGS() as ddgs:
            # Use better search parameters for more relevant results
            results = list(ddgs.text(
                query, 
                region='wt-wt',  # Global results
                safesearch='moderate',
                timelimit='y',   # Last year for fresher results
                max_results=5
            ))
            
            if not results:
                return "No search results found."
            
            # Format results with better structure
            formatted = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                url = result.get('href', 'No URL')
                
                # Truncate body to avoid token overflow
                if len(body) > 300:
                    body = body[:297] + "..."
                
                formatted.append(f"**Result {i}: {title}**\n{body}\nSource: {url}")
            print("\n\n".join(formatted))
            return "\n\n".join(formatted)
    except Exception as e:
        return f"Search failed: {str(e)[:200]}"

# Document Tools
@tool
def read_document_with_docling(file_path: str) -> str:
    """Read and parse a PDF or Text document using Docling to extract text."""
    if not DocumentConverter:
        return "Docling library not installed."
    try:
        converter = DocumentConverter()
        result = converter.convert(file_path)
        return result.document.export_to_markdown()
    except Exception as e:
        return f"Error reading document: {e}"

@tool
def ingest_document_to_vector_store(file_path: str, document_id: str, is_temporary: bool = True) -> str:
    """
    Ingest a document into the vector store for semantic search.
    First parses the document, then chunks and embeds it into ChromaDB.
    
    Args:
        file_path: Path to the document file (PDF or text)
        document_id: Unique identifier for this document
        is_temporary: If True, stores in memory (session only). If False, stores to disk.
        
    Returns:
        Status message with number of chunks created
    """
    try:
        # First parse the document
        if not DocumentConverter:
            return "Docling library not installed."
        
        # Configure lightweight pipeline - no vision models, faster processing
        try:
            from docling.datamodel.base_models import InputFormat
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import PdfFormatOption
            
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False  # Keep OCR for text extraction
            pipeline_options.do_table_structure = False  # Disable table detection (slow)
            # Disable slow enrichment features
            pipeline_options.do_picture_classification = False
            pipeline_options.do_picture_description = False
            pipeline_options.do_code_enrichment = False
            pipeline_options.do_formula_enrichment = False
            pipeline_options.generate_picture_images = False
            
            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        except Exception as config_error:
            # Fallback to simple converter if advanced options fail
            print(f"⚠️ Using simple converter due to: {config_error}")
            converter = DocumentConverter()
        
        result = converter.convert(file_path)
        document_text = result.document.export_to_markdown()
        
        # Ingest into vector store
        # Use temporary store for uploads by default, unless specified otherwise
        vector_store = get_vector_store(is_persistent=not is_temporary)
        
        num_chunks = vector_store.ingest_document(
            document_text=document_text,
            document_id=document_id,
            metadata={"file_path": file_path},
            chunk_size=500,
            chunk_overlap=50
        )
        
        store_type = "temporary (in-memory)" if is_temporary else "persistent (disk)"
        return f"Successfully ingested document '{document_id}' into {store_type} vector store. Created {num_chunks} chunks."
    
    except Exception as e:
        return f"Document ingestion failed: {e}"


@tool
def search_vector_store(query: str, document_id: str = "", top_k: int = 3, search_type: str = "persistent") -> str:
    """
    Search the vector store for relevant document chunks.
    
    Args:
        query: Search query text
        document_id: Optional specific document to search within (empty string searches all documents)
        top_k: Number of top results to return (default: 3)
        search_type: "persistent" (default) or "temporary" (for uploaded files)
        
    Returns:
        Formatted search results with similarity scores
    """
    try:
        is_persistent = (search_type == "persistent")
        vector_store = get_vector_store(is_persistent=is_persistent)
        
        # Convert empty string to None for the vector store
        doc_id = document_id if document_id else None
        
        results = vector_store.similarity_search(
            query=query,
            top_k=top_k,
            document_id=doc_id
        )
        
        if not results:
            return f"No relevant documents found in {search_type} vector store."
        
        # Format results
        output = f"{search_type.capitalize()} Vector Store Search Results:\n\n"
        for i, (chunk_text, score, metadata) in enumerate(results, 1):
            output += f"Result {i} (Similarity: {score:.3f}):\n"
            output += f"{chunk_text}\n"
            output += f"[Document: {metadata.get('document_id', 'unknown')}]\n\n"
        
        return output
    
    except Exception as e:
        return f"Vector store search failed: {e}"