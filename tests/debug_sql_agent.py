import os
from sqlalchemy import create_engine, text, inspect
from database import engine

def debug_db():
    print(f"Database URL: {engine.url}")
    
    # Inspect tables
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(f"Tables found: {table_names}")
    
    with engine.connect() as connection:
        for table in table_names:
            print(f"\n--- Content of table '{table}' ---")
            try:
                # Get all rows
                result = connection.execute(text(f"SELECT * FROM {table}"))
                rows = result.fetchall()
                if not rows:
                    print("  (Empty)")
                for row in rows:
                    print(f"  {row}")
                    
                # Check start_time format specifically if it exists
                columns = [col['name'] for col in inspector.get_columns(table)]
                if 'start_time' in columns:
                    print(f"\n  Checking date(start_time) for '{table}':")
                    date_query = f"SELECT id, start_time, date(start_time) as date_val FROM {table}"
                    date_result = connection.execute(text(date_query))
                    for dr in date_result:
                        print(f"    ID: {dr[0]}, Raw: '{dr[1]}', date(): '{dr[2]}'")
            except Exception as e:
                print(f"  Error querying table {table}: {e}")

if __name__ == "__main__":
    debug_db()
