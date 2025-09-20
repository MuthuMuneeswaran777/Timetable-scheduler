"""
Database migration script to add new fields to existing tables.
This script is safe for SQLite and MySQL: it inspects the schema and only
adds a column if it doesn't already exist. It also updates some defaults.
"""

from sqlalchemy import text, inspect
from backend.database import engine


def column_exists(inspector, table: str, column: str) -> bool:
    cols = inspector.get_columns(table)
    names = {c["name"] for c in cols}
    return column in names


def migrate_database():
    inspector = inspect(engine)
    dialect = engine.dialect.name
    print(f"Running migration on dialect: {dialect}")

    add_columns = [
        ("teachers", "max_sessions_per_week", "INTEGER DEFAULT 10"),
        ("subjects", "max_sessions_per_day", "INTEGER DEFAULT 2"),
        ("subjects", "lab_duration", "INTEGER DEFAULT 3"),
        ("subject_offerings", "max_sessions_per_day", "INTEGER DEFAULT 2"),
        ("subject_offerings", "priority", "INTEGER DEFAULT 1"),
        ("timetable_entries", "is_lab_session", "BOOLEAN DEFAULT 0"),
        ("timetable_entries", "lab_session_part", "INTEGER"),
    ]
    
    # Create admin table if it doesn't exist
    create_tables = [
        ("admins", """
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INTEGER PRIMARY KEY,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        """)
    ]

    try:
        with engine.begin() as connection:
            # Create new tables
            for table_name, create_sql in create_tables:
                print(f"Creating table: {table_name}")
                connection.execute(text(create_sql))
            
            # Add new columns to existing tables
            for table, col, col_def in add_columns:
                # Skip if table doesn't exist
                if table not in inspector.get_table_names():
                    print(f"Skipping table '{table}' (does not exist yet)")
                    continue
                if column_exists(inspector, table, col):
                    print(f"Column already exists: {table}.{col}")
                    continue
                # SQLite/MySQL both support simple ADD COLUMN without IF NOT EXISTS
                alter_sql = f"ALTER TABLE {table} ADD COLUMN {col} {col_def}"
                print(f"Executing: {alter_sql}")
                connection.execute(text(alter_sql))

            # Data updates (safe if columns already present)
            if "subjects" in inspector.get_table_names() and column_exists(inspector, "subjects", "sessions_per_week"):
                connection.execute(text("UPDATE subjects SET sessions_per_week = 5 WHERE sessions_per_week = 3"))
            if (
                "subject_offerings" in inspector.get_table_names()
                and column_exists(inspector, "subject_offerings", "sessions_per_week")
            ):
                connection.execute(text("UPDATE subject_offerings SET sessions_per_week = 5 WHERE sessions_per_week = 3"))

        print("✅ Database migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    migrate_database()
