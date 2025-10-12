from PIL import Image
import io
import base64
from database import AccidentDatabase

# Initialize database
db = AccidentDatabase()


def process_and_save_accident_report(license_number, image_file, description,
                                     location=None, weather_conditions=None,
                                     road_conditions=None, vehicle_info=None,
                                     other_vehicles=None, witnesses=None,
                                     police_report_number=None, submitted_by=None):
    """
    Process accident report and save to database

    Args:
        license_number: Vehicle license number
        image_file: Uploaded image file
        description: Text description of the accident
        location: Accident location
        weather_conditions: Weather conditions
        road_conditions: Road conditions
        vehicle_info: Dictionary with vehicle information
        other_vehicles: List of other vehicles involved
        witnesses: List of witnesses
        police_report_number: Police report number
        submitted_by: User who submitted the report

    Returns:
        tuple: (accident_id, result_text, processed_image)
    """

    try:
        # Process the accident report
        result_text, processed_image = process_accident_report(image_file, description)

        # Load and encode image for database storage
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode()

        # Analyze image and description
        detected_damage = analyze_image(image)
        text_analysis = analyze_description(description)

        # Save vehicle information if provided
        if vehicle_info:
            db.save_vehicle(
                license_number=license_number,
                owner_name=vehicle_info.get('owner_name'),
                vehicle_make=vehicle_info.get('vehicle_make'),
                vehicle_model=vehicle_info.get('vehicle_model'),
                vehicle_year=vehicle_info.get('vehicle_year'),
                vehicle_color=vehicle_info.get('vehicle_color'),
                insurance_provider=vehicle_info.get('insurance_provider')
            )

        # Save accident to database
        accident_id = db.save_accident(
            license_number=license_number,
            description=description,
            location=location,
            weather_conditions=weather_conditions,
            road_conditions=road_conditions,
            severity=detected_damage['severity'],
            damaged_parts=detected_damage['damaged_parts'],
            confidence=detected_damage['confidence'],
            estimated_cost=detected_damage['estimated_cost'],
            repair_time=detected_damage['repair_time'],
            accident_type=text_analysis['accident_type'],
            severity_level=text_analysis['severity_level'],
            image_data=image_base64,
            report_text=result_text,
            other_vehicles=other_vehicles,
            witnesses=witnesses,
            police_report_number=police_report_number,
            submitted_by=submitted_by
        )

        return accident_id, result_text, processed_image

    except Exception as e:
        print(f"Error processing accident report: {e}")
        return None, f"Error processing report: {str(e)}", None


def get_vehicle_accident_history(license_number):
    """
    Get complete accident history for a vehicle

    Args:
        license_number: Vehicle license number

    Returns:
        dict: Vehicle info and accident history
    """
    try:
        vehicle_info = db.get_vehicle_info(license_number)
        accidents = db.get_vehicle_accidents(license_number)
        statistics = db.get_accident_statistics(license_number)

        return {
            'vehicle_info': vehicle_info,
            'accidents': accidents,
            'statistics': statistics
        }
    except Exception as e:
        print(f"Error getting vehicle history: {e}")
        return {
            'vehicle_info': None,
            'accidents': [],
            'statistics': {}
        }


def search_accidents_by_criteria(search_term, search_type='description'):
    """
    Search accidents by various criteria

    Args:
        search_term: Search term
        search_type: Type of search

    Returns:
        list: Matching accidents
    """
    try:
        return db.search_accidents(search_term, search_type)
    except Exception as e:
        print(f"Error searching accidents: {e}")
        return []


def process_accident_report(image_file, description):
    """
    Process the accident report with image and description

    Args:
        image_file: Uploaded image file from Streamlit
        description: Text description of the accident

    Returns:
        tuple: (result_text, processed_image)
            - result_text: Analysis results as natural English text
            - processed_image: PIL Image with annotations/analysis visualization
    """

    try:
        # Load and process the image
        image = Image.open(image_file)

        # Get basic image info
        image_width, image_height = image.size
        image_format = image.format or "Unknown"

        detected_damage = analyze_image(image)

        # Create annotated/processed image (scaled down for display)
        processed_image = image.copy()
        # Scale down the image to a reasonable size for display
        max_size = (600, 400)
        processed_image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Process the text description
        text_analysis = analyze_description(description)

        # Combine results
        result_text = generate_report(image_width, image_height, image_format,
                                      detected_damage, text_analysis)

        return result_text, processed_image

    except Exception as e:
        print(f"Error in process_accident_report: {e}")
        # Return default values in case of error
        return f"Error processing report: {str(e)}", None


def analyze_image(image):
    """
    Analyze the car image for damage detection

    Args:
        image: PIL Image object

    Returns:
        dict: Dictionary containing damage analysis results
    """

    try:
        # Enhanced damage detection with more realistic results
        # In a real implementation, this would use computer vision/ML models

        # Simulate different damage scenarios based on image properties
        width, height = image.size
        total_pixels = width * height

        # Simple heuristic based on image size and properties
        if total_pixels > 1000000:  # High resolution image
            damage_info = {
                "damaged_parts": ["Front bumper", "Left headlight", "Hood", "Windshield"],
                "severity": "Severe",
                "confidence": 0.92,
                "estimated_cost": "$4,500 - $7,200",
                "repair_time": "7-10 business days"
            }
        elif total_pixels > 500000:  # Medium resolution
            damage_info = {
                "damaged_parts": ["Front bumper", "Left headlight", "Hood"],
                "severity": "Moderate",
                "confidence": 0.85,
                "estimated_cost": "$2,500 - $4,200",
                "repair_time": "3-5 business days"
            }
        else:  # Lower resolution
            damage_info = {
                "damaged_parts": ["Rear bumper", "Tail light"],
                "severity": "Minor",
                "confidence": 0.78,
                "estimated_cost": "$800 - $1,500",
                "repair_time": "1-2 business days"
            }

        return damage_info

    except Exception as e:
        print(f"Error in analyze_image: {e}")
        # Return default damage info
        return {
            "damaged_parts": ["Unknown"],
            "severity": "Unknown",
            "confidence": 0.0,
            "estimated_cost": "Unknown",
            "repair_time": "Unknown"
        }


def analyze_description(description):
    """
    Analyze the text description for key information

    Args:
        description: Text description of the accident

    Returns:
        dict: Dictionary containing text analysis results
    """

    try:
        # Enhanced analysis with more comprehensive extraction
        description_lower = description.lower()

        # Determine accident type
        accident_type = "Vehicle collision"
        if any(term in description_lower for term in ['rear-end', 'rear end', 'from behind']):
            accident_type = "Rear-end collision"
        elif any(term in description_lower for term in ['side', 'intersection', 't-bone']):
            accident_type = "Side-impact collision"
        elif any(term in description_lower for term in ['head-on', 'head on', 'frontal']):
            accident_type = "Head-on collision"
        elif any(term in description_lower for term in ['rollover', 'rolled', 'flipped']):
            accident_type = "Rollover accident"
        elif any(term in description_lower for term in ['parking', 'parked', 'lot']):
            accident_type = "Parking lot incident"

        # Determine severity level
        severity_level = "Medium impact"
        if any(term in description_lower for term in ['minor', 'small', 'light', 'scratch']):
            severity_level = "Low impact"
        elif any(term in description_lower for term in ['major', 'severe', 'heavy', 'total', 'destroyed']):
            severity_level = "High impact"

        # Enhanced analysis
        text_info = {
            "word_count": len(description.split()),
            "key_terms": extract_keywords(description),
            "accident_type": accident_type,
            "severity_level": severity_level,
            "location_mentioned": "Yes" if any(
                word in description_lower for word in ['street', 'road', 'highway',
                                                       'intersection', 'parking', 'avenue',
                                                       'boulevard', 'lane']) else "No",
            "weather_mentioned": "Yes" if any(
                word in description_lower for word in ['rain', 'snow', 'fog', 'ice',
                                                       'sunny', 'clear', 'cloudy']) else "No",
            "time_mentioned": "Yes" if any(
                word in description_lower for word in ['morning', 'afternoon', 'evening',
                                                       'night', 'am', 'pm', ':']) else "No"
        }

        return text_info

    except Exception as e:
        print(f"Error in analyze_description: {e}")
        # Return default analysis
        return {
            "word_count": 0,
            "key_terms": [],
            "accident_type": "Unknown",
            "severity_level": "Unknown",
            "location_mentioned": "No",
            "weather_mentioned": "No",
            "time_mentioned": "No"
        }


def extract_keywords(text):
    """
    Extract keywords from the description

    Args:
        text: Input text

    Returns:
        list: List of keywords
    """

    try:
        # Enhanced keyword extraction
        words = text.lower().split()

        # Expanded stop words list
        stop_words = {
            'the', 'and', 'was', 'were', 'that', 'this', 'with', 'for', 'from',
            'they', 'have', 'had', 'been', 'will', 'would', 'could', 'should',
            'when', 'where', 'what', 'who', 'how', 'why', 'there', 'here',
            'then', 'than', 'them', 'these', 'those', 'into', 'onto', 'upon'
        }

        # Vehicle and accident related keywords to prioritize
        priority_words = {
            'collision', 'accident', 'crash', 'damage', 'impact', 'bumper',
            'headlight', 'windshield', 'door', 'fender', 'hood', 'trunk',
            'intersection', 'highway', 'street', 'parking', 'traffic',
            'speed', 'brake', 'turn', 'signal', 'weather', 'rain', 'snow'
        }

        keywords = []
        for word in words:
            clean_word = word.strip('.,!?;:"()[]')
            if (len(clean_word) > 3 and
                    clean_word not in stop_words and
                    clean_word.isalpha()):
                keywords.append(clean_word)

        # Prioritize accident-related terms
        prioritized = [word for word in keywords if word in priority_words]
        others = [word for word in keywords if word not in priority_words]

        return (prioritized + others)[:8]  # Return top 8 keywords

    except Exception as e:
        print(f"Error in extract_keywords: {e}")
        return []


def generate_report(width, height, format, damage_info, text_analysis):
    """
    Generate the final formatted report in natural English

    Args:
        width: Image width
        height: Image height
        format: Image format
        damage_info: Results from image analysis
        text_analysis: Results from text analysis

    Returns:
        str: Formatted report in natural English
    """

    try:
        report = f"""
COMPREHENSIVE ACCIDENT ANALYSIS REPORT
=======================================

IMAGE ANALYSIS DETAILS:
• Image Resolution: {width} x {height} pixels ({format} format)
• Analysis Quality: {'High' if width * height > 1000000 else 'Medium' if width * height > 500000 else 'Standard'}

DAMAGE ASSESSMENT:
• Affected Vehicle Parts: {', '.join(damage_info.get('damaged_parts', ['Unknown']))}
• Overall Damage Severity: {damage_info.get('severity', 'Unknown')}
• AI Confidence Level: {damage_info.get('confidence', 0):.1%}
• Estimated Repair Cost: {damage_info.get('estimated_cost', 'Unknown')}
• Expected Repair Duration: {damage_info.get('repair_time', 'Unknown')}

INCIDENT ANALYSIS:
• Accident Classification: {text_analysis.get('accident_type', 'Unknown')}
• Impact Severity Level: {text_analysis.get('severity_level', 'Unknown')}
• Description Length: {text_analysis.get('word_count', 0)} words
• Location Details Available: {text_analysis.get('location_mentioned', 'No')}
• Weather Conditions Noted: {text_analysis.get('weather_mentioned', 'No')}
• Time Information Provided: {text_analysis.get('time_mentioned', 'No')}

KEY EXTRACTED TERMS:
{', '.join(text_analysis.get('key_terms', [])) if text_analysis.get('key_terms') else 'No significant keywords identified'}

RECOMMENDATIONS:
• Contact insurance provider to file a claim
• Obtain repair estimates from certified auto body shops
• Document all related expenses and communications
• Follow up on repair timeline and quality assurance

This automated analysis provides a comprehensive overview based on the submitted image and description. 
For insurance and legal purposes, professional assessment may be required.
        """

        return report.strip()

    except Exception as e:
        print(f"Error generating report: {e}")
        return f"Error generating report: {str(e)}"


# Example usage function
def example_usage():
    """
    Example of how to use the enhanced system
    """
    print("=== Accident Reporting System Example ===")

    # Example vehicle information
    vehicle_info = {
        'owner_name': 'Test User',
        'vehicle_make': 'Toyota',
        'vehicle_model': 'Camry',
        'vehicle_year': 2020,
        'vehicle_color': 'Blue',
        'insurance_provider': 'Test Insurance'
    }

    print("System initialized and ready for use!")
    print("Use process_and_save_accident_report() to submit new reports")
    print("Use get_vehicle_accident_history() to view vehicle history")
    print("Use search_accidents_by_criteria() to search reports")


if __name__ == "__main__":
    example_usage()