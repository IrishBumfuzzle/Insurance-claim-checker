import sqlite3
import json


class AccidentDatabase:
    """Database for accident reports with multiple image support"""

    def __init__(self, db_path='accident_reports.db'):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if accidents table exists and get its structure
        cursor.execute("PRAGMA table_info(accidents)")
        existing_columns = [column[1] for column in cursor.fetchall()]

        # Vehicles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                license_number TEXT PRIMARY KEY,
                owner_name TEXT,
                vehicle_make TEXT,
                vehicle_model TEXT,
                vehicle_year INTEGER,
                vehicle_color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Accidents table - check if it exists first
        if not existing_columns:
            # Create new table with all columns
            cursor.execute('''
                CREATE TABLE accidents (
                    accident_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_number TEXT NOT NULL,
                    accident_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT NOT NULL,
                    location TEXT,
                    severity TEXT,
                    damaged_parts TEXT,
                    confidence REAL,
                    estimated_cost TEXT,
                    repair_time TEXT,
                    accident_type TEXT,
                    image_data TEXT,
                    image_count INTEGER DEFAULT 1,
                    report_text TEXT,
                    status TEXT DEFAULT 'Reported',
                    FOREIGN KEY (license_number) REFERENCES vehicles (license_number)
                )
            ''')
        else:
            # Table exists, add missing columns if needed
            if 'image_count' not in existing_columns:
                cursor.execute('ALTER TABLE accidents ADD COLUMN image_count INTEGER DEFAULT 1')

        # Create indexes only for columns that exist
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_license ON accidents(license_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON accidents(accident_date)')

        # Check if image_count column exists before creating index
        cursor.execute("PRAGMA table_info(accidents)")
        current_columns = [column[1] for column in cursor.fetchall()]
        if 'image_count' in current_columns:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_count ON accidents(image_count)')

        conn.commit()
        conn.close()

    def save_vehicle(self, license_number, owner_name=None, vehicle_make=None,
                     vehicle_model=None, vehicle_year=None, vehicle_color=None):
        """Save vehicle information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Check if exists
            cursor.execute('SELECT license_number FROM vehicles WHERE license_number = ?', (license_number,))
            exists = cursor.fetchone()

            if exists:
                # Update existing
                cursor.execute('''
                    UPDATE vehicles SET owner_name = ?, vehicle_make = ?, vehicle_model = ?,
                    vehicle_year = ?, vehicle_color = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE license_number = ?
                ''', (owner_name, vehicle_make, vehicle_model, vehicle_year, vehicle_color, license_number))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO vehicles (license_number, owner_name, vehicle_make, 
                    vehicle_model, vehicle_year, vehicle_color)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (license_number, owner_name, vehicle_make, vehicle_model, vehicle_year, vehicle_color))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving vehicle: {e}")
            return False

    def save_accident(self, license_number, description, location=None,
                      severity=None, damaged_parts=None, confidence=None, estimated_cost=None,
                      repair_time=None, accident_type=None, image_data=None, report_text=None,
                      image_count=1):
        """Save accident report with multiple image support"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Ensure vehicle record exists
            cursor.execute('SELECT license_number FROM vehicles WHERE license_number = ?', (license_number,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO vehicles (license_number) VALUES (?)', (license_number,))

            # Convert damaged parts to JSON
            damaged_parts_json = json.dumps(damaged_parts) if damaged_parts else None

            # Check if image_count column exists
            cursor.execute("PRAGMA table_info(accidents)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'image_count' in columns:
                # New table structure with image_count
                cursor.execute('''
                    INSERT INTO accidents (license_number, description, location,
                    severity, damaged_parts, confidence, estimated_cost, repair_time, accident_type,
                    image_data, image_count, report_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (license_number, description, location, severity,
                      damaged_parts_json, confidence, estimated_cost, repair_time, accident_type,
                      image_data, image_count, report_text))
            else:
                # Old table structure without image_count
                cursor.execute('''
                    INSERT INTO accidents (license_number, description, location,
                    severity, damaged_parts, confidence, estimated_cost, repair_time, accident_type,
                    image_data, report_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (license_number, description, location, severity,
                      damaged_parts_json, confidence, estimated_cost, repair_time, accident_type,
                      image_data, report_text))

            accident_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return accident_id

        except Exception as e:
            print(f"Error saving accident: {e}")
            return None


if __name__ == "__main__":
    db = AccidentDatabase()
    print("Database initialized for multi-image accident reports")