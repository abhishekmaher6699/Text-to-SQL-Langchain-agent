from sqlalchemy import create_engine, text

def create_connection():
    try:
        database_url = f"sqlite:///backend/databases/tables.db"
        engine = create_engine(database_url)
        print("Connection to SQLite established successfully!")
        return engine
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
     
def show_all_tables():
    try:
        engine = create_connection()
        with engine.connect() as connection:
            tables = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            table_list = [table[0] for table in tables]
        
        return table_list
    except Exception as e:
        print(f"Error showing tables: {e}")