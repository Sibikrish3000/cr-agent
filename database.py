import os
from sqlmodel import SQLModel, create_engine, Session

# Persistent SQLite database in the project directory
# Using absolute path to ensure data persists across runs
project_dir = os.path.dirname(os.path.abspath(__file__))
db_file_path = os.path.join(project_dir, "meeting_database.db")

database_url = f"sqlite:///{db_file_path}"

# Connect with persistent storage
engine = create_engine(
    database_url, 
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)

print(f"✓ Database configured at: {db_file_path}")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
