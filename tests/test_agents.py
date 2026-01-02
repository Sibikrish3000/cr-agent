import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from pathlib import Path

# Ensure we can import modules
sys.path.append(os.getcwd())

load_dotenv()

def run_test(query: str, file_path: str = None, test_name: str = ""):
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}" if test_name else f"Testing Query: {query}")
    print(f"{'='*80}")
    if file_path:
        print(f"File: {file_path}")
        
    try:
        from agents import app
        from database import create_db_and_tables
        
        # Ensure DB exists
        create_db_and_tables()
        
        inputs = {"messages": [HumanMessage(content=query)]}
        if file_path:
            inputs["file_path"] = file_path
            
        result = app.invoke(inputs)
        print("\n✅ Response:")
        print(result["messages"][-1].content)
        print(f"\n{'='*80}\n")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n{'='*80}\n")
        return False

def create_test_document():
    """Create a test document for RAG testing."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        test_file = Path("uploads/test_policy.pdf")
        test_file.parent.mkdir(exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(str(test_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add content
        story.append(Paragraph("Company Policy: Remote Work Guidelines", styles['Title']))
        story.append(Spacer(1, 12))
        
        content = [
            ("Overview", "Our company supports flexible remote work arrangements for all employees."),
            ("Eligibility", "All full-time employees are eligible for remote work. Part-time employees must have manager approval. New hires must complete 3 months probation before remote work eligibility."),
            ("Equipment", "Company provides laptop and monitor for remote work. Employees receive $500 annual stipend for home office setup. VPN access is mandatory for all remote connections."),
            ("Work Hours", "Core hours: 10 AM - 3 PM local time (must be available). Flexible scheduling outside core hours. Minimum 40 hours per week required for full-time employees."),
            ("Communication", "Daily standup at 10 AM via video call. Slack response time: within 1 hour during core hours. Weekly team meeting on Fridays at 2 PM."),
            ("Performance Evaluation", "Remote employees evaluated on deliverables, not hours. Monthly 1-on-1 with manager required. Quarterly performance reviews.")
        ]
        
        for heading, text in content:
            story.append(Paragraph(f"<b>{heading}:</b>", styles['Heading2']))
            story.append(Paragraph(text, styles['BodyText']))
            story.append(Spacer(1, 12))
        
        doc.build(story)
        return str(test_file.absolute())
    
    except ImportError:
        # Fallback: Create markdown file that Docling supports
        print("⚠️  reportlab not available, creating markdown document instead...")
        test_content = """# Company Policy: Remote Work Guidelines

## Overview
Our company supports flexible remote work arrangements for all employees.

## Eligibility
All full-time employees are eligible for remote work. Part-time employees must have manager approval. 
New hires must complete 3 months probation before remote work eligibility.

## Equipment
Company provides laptop and monitor for remote work. Employees receive $500 annual stipend for home office setup. 
VPN access is mandatory for all remote connections.

## Work Hours  
Core hours: 10 AM - 3 PM local time (must be available). Flexible scheduling outside core hours. 
Minimum 40 hours per week required for full-time employees.

## Communication
Daily standup at 10 AM via video call. Slack response time: within 1 hour during core hours. 
Weekly team meeting on Fridays at 2 PM.

## Performance Evaluation
Remote employees evaluated on deliverables, not hours. Monthly 1-on-1 with manager required. 
Quarterly performance reviews.
"""
        
        test_file = Path("uploads/test_policy.md")
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text(test_content)
        return str(test_file.absolute())

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MULTI-AGENT SYSTEM TEST SUITE")
    print("="*80)
    
    # Test 1: Weather Agent
    run_test(
        "What is the weather in Chennai today?",
        test_name="Weather Agent - Current Weather"
    )
    
    # Test 2: Meeting Agent with Weather Logic
    run_test(
        "Schedule a team meeting tomorrow at 2 PM in London if the weather is good. Meeting should be 1 hour long with participants: John, Sarah, Mike",
        test_name="Meeting Agent - Weather-based Scheduling"
    )
    
    # Test 3: SQL Agent
    run_test(
        "Show me all meetings scheduled for tomorrow",
        test_name="SQL Agent - Meeting Query"
    )
    
    # Test 4: Document RAG with Vector Store
    print("\n" + "="*80)
    print("Creating test document for RAG testing...")
    print("="*80)
    test_file_path = create_test_document()
    print(f"Test document created at: {test_file_path}\n")
    
    run_test(
        "What is the remote work equipment policy?",
        file_path=test_file_path,
        test_name="Document Agent - RAG with High Confidence"
    )
    
    # Test 5: RAG with Web Search Fallback (Low confidence query)
    run_test(
        "What are the latest trends in AI for 2026?",
        file_path=test_file_path,
        test_name="Document Agent - Web Search Fallback (query not in document)"
    )
    
    # Test 6: Vector Store Search
    run_test(
        "How many hours per week do remote employees need to work?",
        file_path=test_file_path,
        test_name="Document Agent - Specific Information Retrieval"
    )
    
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80)
    run_test("Show all meetings scheduled tomorrow")
    
    print("\nNote: Agent 2 requires a file upload. Test manually via API or add file path.")
