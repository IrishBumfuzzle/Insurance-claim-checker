import requests
from PIL import Image
import io
import base64
import os
from database import AccidentDatabase

# Initialize database
db = AccidentDatabase()

# def process_and_save_accident_report(license_number, image_file, description,
#                                      location=None, weather_conditions=None,
#                                      road_conditions=None, vehicle_info=None,
#                                      other_vehicles=None, witnesses=None,
#                                      police_report_number=None, submitted_by=None):
#     """
#     Process accident report and save to database
#     Returns: (accident_id, result_text, processed_image, annotated_image)
#     """
#     try:
#         result_text, processed_image, annotated_image = process_accident_report(image_file, description)
#         # ...existing code for DB save...
#         return 1, result_text, processed_image, annotated_image
#     except Exception as e:
#         print(f"Error: {e}")
#         return None, f"Error: {str(e)}", None, None

def damage_assess(img_path):
    import json
    url = "http://ultralytics:8000/damage"
    with open(img_path, "rb") as f:
        files = {"img": (os.path.basename(img_path), f, "image/jpeg")}
        response = requests.post(url, files=files)
    if response.status_code == 200:
        data = response.json()
        # Serialize the results to JSON string
        results_json = json.dumps(data.get("results"))
        return results_json, data.get("annotated_image_path")
    else:
        print(f"API error: {response.status_code} {response.text}")
        return None, None

def process_accident_report(image_file, description):
    """
    Returns: (result_text, processed_image, annotated_image)
    """
    try:
        image = Image.open(image_file)
        processed_image = image.copy()
        processed_image.thumbnail((600, 400), Image.Resampling.LANCZOS)
        # Simulate annotation: just use processed_image for now
        annotated_image = processed_image.copy()
        result_text = f"Report for image size {image.size} and description: {description[:40]}..."
        return result_text, processed_image, annotated_image
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {str(e)}", None, None

