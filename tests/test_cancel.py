"""Test script for meeting cancellation"""
from tools import cancel_meetings
from database import engine
from sqlmodel import Session, select
from models import Meeting

# Show current meetings
print("📋 Current meetings in database:")
with Session(engine) as session:
    meetings = session.exec(select(Meeting)).all()
    for m in meetings:
        print(f"  - ID {m.id}: {m.title} at {m.start_time}")
    if not meetings:
        print("  (No meetings found)")

# Test cancellation
print("\n🗑️  Testing cancel_meetings(date_filter='tomorrow')...")
result = cancel_meetings.invoke({"date_filter": "tomorrow", "meeting_ids": ""})
print(result)

# Show remaining meetings
print("\n📋 Remaining meetings:")
with Session(engine) as session:
    meetings = session.exec(select(Meeting)).all()
    for m in meetings:
        print(f"  - ID {m.id}: {m.title} at {m.start_time}")
    if not meetings:
        print("  (No meetings found)")
