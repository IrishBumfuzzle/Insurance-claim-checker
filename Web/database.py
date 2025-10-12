import sqlite3
import json
import base64
from datetime import datetime
from PIL import Image
import io


class AccidentDatabase:
    """
    Database manager for accident reports and vehicle information
    """

    def __init__(self, db_path='accident_reports.db'):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """
        Initialize the SQLite database with required tables
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create main vehicles table with license number as primary key
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                license_number TEXT PRIMARY KEY,
                owner_name TEXT,
                vehicle_make TEXT,
                vehicle_model TEXT,
                vehicle_year INTEGER,
                vehicle_color TEXT,
                insurance_provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create accidents table linked to vehicles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accidents (
                accident_id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_number TEXT NOT NULL,
                accident_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT NOT NULL,
                location TEXT,
                weather_conditions TEXT,
                road_conditions TEXT,
                severity TEXT,
                damaged_parts TEXT,  -- JSON string of list
                confidence REAL,
                estimated_cost TEXT,
                repair_time TEXT,
                accident_type TEXT,
                severity_level TEXT,
                image_data TEXT,  -- Base64 encoded image
                report_text TEXT,
                other_vehicles_involved TEXT,  -- JSON string of list
                witnesses TEXT,  -- JSON string of list
                police_report_number TEXT,
                insurance_claim_number TEXT,
                status TEXT DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submitted_by TEXT,
                FOREIGN KEY (license_number) REFERENCES vehicles (license_number)
            )
        ''')

        # Create index for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_license_number ON accidents(license_number)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_accident_date ON accidents(accident_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_severity ON accidents(severity)')

        conn.commit()
        conn.close()

    def save_vehicle(self, license_number, owner_name=None, vehicle_make=None,
                     vehicle_model=None, vehicle_year=None, vehicle_color=None,
                     insurance_provider=None):
        """
        Save or update vehicle information

        Args:
            license_number: Vehicle license number (primary key)
            owner_name: Owner's name
            vehicle_make: Vehicle manufacturer
            vehicle_model: Vehicle model
            vehicle_year: Vehicle year
            vehicle_color: Vehicle color
            insurance_provider: Insurance company name

        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Check if vehicle exists
            cursor.execute('SELECT license_number FROM vehicles WHERE license_number = ?',
                           (license_number,))
            exists = cursor.fetchone()

            if exists:
                # Update existing vehicle (only update non-None values)
                update_fields = []
                update_values = []

                if owner_name is not None:
                    update_fields.append('owner_name = ?')
                    update_values.append(owner_name)
                if vehicle_make is not None:
                    update_fields.append('vehicle_make = ?')
                    update_values.append(vehicle_make)
                if vehicle_model is not None:
                    update_fields.append('vehicle_model = ?')
                    update_values.append(vehicle_model)
                if vehicle_year is not None:
                    update_fields.append('vehicle_year = ?')
                    update_values.append(vehicle_year)
                if vehicle_color is not None:
                    update_fields.append('vehicle_color = ?')
                    update_values.append(vehicle_color)
                if insurance_provider is not None:
                    update_fields.append('insurance_provider = ?')
                    update_values.append(insurance_provider)

                if update_fields:
                    update_fields.append('updated_at = CURRENT_TIMESTAMP')
                    update_values.append(license_number)

                    query = f"UPDATE vehicles SET {', '.join(update_fields)} WHERE license_number = ?"
                    cursor.execute(query, update_values)
            else:
                # Insert new vehicle
                cursor.execute('''
                    INSERT INTO vehicles 
                    (license_number, owner_name, vehicle_make, vehicle_model, 
                     vehicle_year, vehicle_color, insurance_provider)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (license_number, owner_name, vehicle_make, vehicle_model,
                      vehicle_year, vehicle_color, insurance_provider))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error saving vehicle: {e}")
            if 'conn' in locals():
                conn.close()
            return False

    def save_accident(self, license_number, description, location=None,
                      weather_conditions=None, road_conditions=None, severity=None,
                      damaged_parts=None, confidence=None, estimated_cost=None,
                      repair_time=None, accident_type=None, severity_level=None,
                      image_data=None, report_text=None, other_vehicles=None,
                      witnesses=None, police_report_number=None,
                      insurance_claim_number=None, submitted_by=None):
        """
        Save accident information to database

        Returns:
            int: Accident ID if successful, None if failed
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Ensure vehicle exists
            cursor.execute('SELECT license_number FROM vehicles WHERE license_number = ?',
                           (license_number,))
            if not cursor.fetchone():
                # Create basic vehicle record if it doesn't exist
                cursor.execute('''
                    INSERT INTO vehicles (license_number) VALUES (?)
                ''', (license_number,))

            # Convert lists to JSON strings
            damaged_parts_json = json.dumps(damaged_parts) if damaged_parts else None
            other_vehicles_json = json.dumps(other_vehicles) if other_vehicles else None
            witnesses_json = json.dumps(witnesses) if witnesses else None

            cursor.execute('''
                INSERT INTO accidents 
                (license_number, description, location, weather_conditions, 
                 road_conditions, severity, damaged_parts, confidence, 
                 estimated_cost, repair_time, accident_type, severity_level, 
                 image_data, report_text, other_vehicles_involved, witnesses,
                 police_report_number, insurance_claim_number, submitted_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (license_number, description, location, weather_conditions,
                  road_conditions, severity, damaged_parts_json, confidence,
                  estimated_cost, repair_time, accident_type, severity_level,
                  image_data, report_text, other_vehicles_json, witnesses_json,
                  police_report_number, insurance_claim_number, submitted_by))

            accident_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return accident_id

        except Exception as e:
            print(f"Error saving accident: {e}")
            if 'conn' in locals():
                conn.close()
            return None

    def get_vehicle_accidents(self, license_number):
        """
        Retrieve all accidents for a specific vehicle

        Args:
            license_number: Vehicle license number

        Returns:
            list: List of accident records
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT a.*, v.owner_name, v.vehicle_make, v.vehicle_model, 
                       v.vehicle_year, v.vehicle_color, v.insurance_provider
                FROM accidents a
                LEFT JOIN vehicles v ON a.license_number = v.license_number
                WHERE a.license_number = ?
                ORDER BY a.accident_date DESC
            ''', (license_number,))

            accidents = cursor.fetchall()
            conn.close()
            return accidents

        except Exception as e:
            print(f"Error retrieving accidents: {e}")
            return []

    def get_accident_details(self, accident_id):
        """
        Get detailed information about a specific accident

        Args:
            accident_id: Accident ID

        Returns:
            dict: Accident details with decoded data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT a.*, v.owner_name, v.vehicle_make, v.vehicle_model, 
                       v.vehicle_year, v.vehicle_color, v.insurance_provider
                FROM accidents a
                LEFT JOIN vehicles v ON a.license_number = v.license_number
                WHERE a.accident_id = ?
            ''', (accident_id,))

            result = cursor.fetchone()

            if result:
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                accident_dict = dict(zip(columns, result))

                # Decode JSON fields
                if accident_dict.get('damaged_parts'):
                    try:
                        accident_dict['damaged_parts'] = json.loads(accident_dict['damaged_parts'])
                    except (json.JSONDecodeError, TypeError):
                        accident_dict['damaged_parts'] = []

                if accident_dict.get('other_vehicles_involved'):
                    try:
                        accident_dict['other_vehicles_involved'] = json.loads(accident_dict['other_vehicles_involved'])
                    except (json.JSONDecodeError, TypeError):
                        accident_dict['other_vehicles_involved'] = []

                if accident_dict.get('witnesses'):
                    try:
                        accident_dict['witnesses'] = json.loads(accident_dict['witnesses'])
                    except (json.JSONDecodeError, TypeError):
                        accident_dict['witnesses'] = []

                # Decode image from base64
                if accident_dict.get('image_data'):
                    try:
                        image_data = base64.b64decode(accident_dict['image_data'])
                        accident_dict['image'] = Image.open(io.BytesIO(image_data))
                    except Exception as e:
                        print(f"Error decoding image: {e}")
                        accident_dict['image'] = None

                conn.close()
                return accident_dict

            conn.close()
            return None

        except Exception as e:
            print(f"Error getting accident details: {e}")
            return None

    def get_vehicle_info(self, license_number):
        """
        Get vehicle information

        Args:
            license_number: Vehicle license number

        Returns:
            dict: Vehicle information
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM vehicles WHERE license_number = ?
            ''', (license_number,))

            result = cursor.fetchone()

            if result:
                columns = [desc[0] for desc in cursor.description]
                vehicle_dict = dict(zip(columns, result))
                conn.close()
                return vehicle_dict

            conn.close()
            return None

        except Exception as e:
            print(f"Error getting vehicle info: {e}")
            return None

    def update_accident_status(self, accident_id, status):
        """
        Update accident status

        Args:
            accident_id: Accident ID
            status: New status ('Open', 'In Progress', 'Closed', 'Settled')

        Returns:
            bool: True if successful
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE accidents 
                SET status = ?
                WHERE accident_id = ?
            ''', (status, accident_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error updating accident status: {e}")
            return False

    def get_accident_statistics(self, license_number=None):
        """
        Get accident statistics

        Args:
            license_number: Optional license number to filter by

        Returns:
            dict: Statistics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if license_number:
                # Statistics for specific vehicle
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_accidents,
                        COUNT(CASE WHEN severity = 'Minor' THEN 1 END) as minor_accidents,
                        COUNT(CASE WHEN severity = 'Moderate' THEN 1 END) as moderate_accidents,
                        COUNT(CASE WHEN severity = 'Severe' THEN 1 END) as severe_accidents,
                        COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_cases,
                        COUNT(CASE WHEN status = 'Closed' THEN 1 END) as closed_cases
                    FROM accidents 
                    WHERE license_number = ?
                ''', (license_number,))
            else:
                # Overall statistics
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_accidents,
                        COUNT(CASE WHEN severity = 'Minor' THEN 1 END) as minor_accidents,
                        COUNT(CASE WHEN severity = 'Moderate' THEN 1 END) as moderate_accidents,
                        COUNT(CASE WHEN severity = 'Severe' THEN 1 END) as severe_accidents,
                        COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_cases,
                        COUNT(CASE WHEN status = 'Closed' THEN 1 END) as closed_cases,
                        COUNT(DISTINCT license_number) as total_vehicles
                    FROM accidents
                ''')

            result = cursor.fetchone()

            if result:
                columns = [desc[0] for desc in cursor.description]
                stats_dict = dict(zip(columns, result))
                conn.close()
                return stats_dict

            conn.close()
            return {}

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}

    def search_accidents(self, search_term, search_type='description'):
        """
        Search accidents by various criteria

        Args:
            search_term: Term to search for
            search_type: Type of search ('description', 'location', 'license', 'severity')

        Returns:
            list: List of matching accidents
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if search_type == 'description':
                query = '''
                    SELECT a.*, v.owner_name, v.vehicle_make, v.vehicle_model
                    FROM accidents a
                    LEFT JOIN vehicles v ON a.license_number = v.license_number
                    WHERE a.description LIKE ?
                    ORDER BY a.accident_date DESC
                '''
                cursor.execute(query, (f'%{search_term}%',))
            elif search_type == 'location':
                query = '''
                    SELECT a.*, v.owner_name, v.vehicle_make, v.vehicle_model
                    FROM accidents a
                    LEFT JOIN vehicles v ON a.license_number = v.license_number
                    WHERE a.location LIKE ?
                    ORDER BY a.accident_date DESC
                '''
                cursor.execute(query, (f'%{search_term}%',))
            elif search_type == 'license':
                query = '''
                    SELECT a.*, v.owner_name, v.vehicle_make, v.vehicle_model
                    FROM accidents a
                    LEFT JOIN vehicles v ON a.license_number = v.license_number
                    WHERE a.license_number LIKE ?
                    ORDER BY a.accident_date DESC
                '''
                cursor.execute(query, (f'%{search_term}%',))
            elif search_type == 'severity':
                query = '''
                    SELECT a.*, v.owner_name, v.vehicle_make, v.vehicle_model
                    FROM accidents a
                    LEFT JOIN vehicles v ON a.license_number = v.license_number
                    WHERE a.severity = ?
                    ORDER BY a.accident_date DESC
                '''
                cursor.execute(query, (search_term,))

            results = cursor.fetchall()
            conn.close()
            return results

        except Exception as e:
            print(f"Error searching accidents: {e}")
            return []


# Test function
def test_database():
    """
    Test the database functionality
    """
    print("Initializing database...")
    db = AccidentDatabase()

    # Test vehicle saving
    print("Testing vehicle save...")
    success = db.save_vehicle("TEST123", "Test User", "Toyota", "Camry", 2020, "Blue", "Test Insurance")
    print(f"Vehicle save result: {success}")

    # Test accident saving
    print("Testing accident save...")
    accident_id = db.save_accident(
        license_number="TEST123",
        description="Test accident for database verification",
        location="Test Location",
        weather_conditions="Clear",
        road_conditions="Dry",
        severity="Minor",
        damaged_parts=["Test part"],
        confidence=0.85,
        estimated_cost="$1000",
        repair_time="2 days",
        accident_type="Test collision",
        severity_level="Low",
        submitted_by="TestUser"
    )
    print(f"Accident ID: {accident_id}")

    # Test retrieval
    if accident_id:
        print("Testing data retrieval...")
        accidents = db.get_vehicle_accidents("TEST123")
        print(f"Found {len(accidents)} accidents")

        details = db.get_accident_details(accident_id)
        print(f"Accident details retrieved: {details is not None}")

    print("Database test completed!")


if __name__ == "__main__":
    test_database()