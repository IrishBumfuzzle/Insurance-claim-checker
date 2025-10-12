"""
Fraud Detection Wrapper Module
This module provides a clean interface to the fraud detection functionality
"""

import os
import sys
import traceback
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import shutil
import uuid
from pathlib import Path

# Add current directory to path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Create models directory if it doesn't exist
os.makedirs(os.path.join(current_dir, "models"), exist_ok=True)

# Create app with description
app = FastAPI(
    title="Fraud Detection API",
    description="API for detecting potential fraud in accident images",
    version="1.0.0"
)

from main import main_function


def detect_fraud(image_path, timestamp, latitude, longitude):
    """
    Detect fraud indicators in accident images.
    
    Args:
        image_path (str): Path to the image file
        timestamp (str): Timestamp in format "2023:12:01 12:09:65" or "2023-12-01 12:09:65"
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
    
    Returns:
        dict: Fraud detection results containing:
            - tamper_detection: Image tampering analysis
            - weather_analysis: Weather prediction vs actual
            - fraud_risk: Overall fraud risk level (HIGH/LOW/UNKNOWN)
    """
    try:
        # Ensure timestamp is in correct format (with colons)
        if "-" in timestamp and ":" in timestamp:
            # Format: "2023-12-01 12:09:65" -> "2023:12:01 12:09:65"
            timestamp = timestamp.replace("-", ":")
        
        # Run fraud detection from main.py
        ela_result, weather_pred, real_weather = main_function(
            image_path, 
            timestamp, 
            float(latitude), 
            float(longitude)
        )
        
        # Unpack results
        tamper_class, tamper_confidence = ela_result
        weather_class, weather_confidence = weather_pred
        location, actual_weather = real_weather if real_weather else ("", "")
        
        # Determine fraud indicators
        is_tampered = tamper_class.lower() == "tampered"
        
        # Weather mismatch check
        weather_mismatch = False
        mismatch_reason = None
        
        if actual_weather and actual_weather != "" and actual_weather != "NA":
            # Normalize weather strings for comparison
            actual_weather_norm = actual_weather.lower().replace(" ", "").replace("_", "")
            predicted_weather_norm = weather_class.lower().replace(" ", "").replace("_", "")
            
            # Check for mismatch
            # Consider it a match if either string contains the other
            weather_match = (
                actual_weather_norm in predicted_weather_norm or 
                predicted_weather_norm in actual_weather_norm
            )
            
            if not weather_match:
                weather_mismatch = True
                mismatch_reason = f"Predicted '{weather_class}' but actual was '{actual_weather}'"
        
        # Calculate overall fraud risk
        fraud_indicators = []
        if is_tampered:
            fraud_indicators.append("Image tampering detected")
        if weather_mismatch:
            fraud_indicators.append("Weather condition mismatch")
        
        fraud_risk = "HIGH" if fraud_indicators else "LOW"
        
        return {
            "success": True,
            "tamper_detection": {
                "class": tamper_class,
                "confidence": tamper_confidence,
                "is_tampered": is_tampered
            },
            "weather_analysis": {
                "predicted_weather": weather_class,
                "predicted_confidence": weather_confidence,
                "actual_weather": actual_weather if actual_weather else "Not available",
                "location": str(location) if location else "Unknown",
                "mismatch": weather_mismatch,
                "mismatch_reason": mismatch_reason
            },
            "fraud_risk": fraud_risk,
            "fraud_indicators": fraud_indicators,
            "recommendation": get_recommendation(fraud_risk, fraud_indicators)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fraud_risk": "UNKNOWN",
            "recommendation": "Unable to complete fraud analysis. Manual review recommended."
        }


def get_recommendation(risk_level, indicators):
    """Generate recommendation based on fraud risk level"""
    if risk_level == "HIGH":
        return f"⚠️ HIGH FRAUD RISK - Manual investigation required. Indicators: {', '.join(indicators)}"
    elif risk_level == "LOW":
        return "✅ No fraud indicators detected. Claim appears legitimate."
    else:
        return "❓ Unable to assess fraud risk. Additional verification needed."


def batch_detect_fraud(image_paths, timestamps, latitudes, longitudes):
    """
    Run fraud detection on multiple images.
    
    Args:
        image_paths (list): List of image file paths
        timestamps (list): List of timestamps
        latitudes (list): List of latitude values
        longitudes (list): List of longitude values
    
    Returns:
        list: List of fraud detection results for each image
    """
    results = []
    
    for i, img_path in enumerate(image_paths):
        timestamp = timestamps[i] if i < len(timestamps) else None
        lat = latitudes[i] if i < len(latitudes) else 0.0
        lon = longitudes[i] if i < len(longitudes) else 0.0
        
        if timestamp:
            result = detect_fraud(img_path, timestamp, lat, lon)
            result['image_index'] = i
            result['image_path'] = img_path
            results.append(result)
    
    return results


def get_fraud_summary(fraud_results_list):
    """
    Generate a summary of fraud detection results for multiple images.
    
    Args:
        fraud_results_list (list): List of fraud detection results
    
    Returns:
        dict: Summary statistics and overall assessment
    """
    total_images = len(fraud_results_list)
    high_risk_count = sum(1 for r in fraud_results_list if r.get('fraud_risk') == 'HIGH')
    low_risk_count = sum(1 for r in fraud_results_list if r.get('fraud_risk') == 'LOW')
    unknown_count = sum(1 for r in fraud_results_list if r.get('fraud_risk') == 'UNKNOWN')
    
    tampered_count = sum(1 for r in fraud_results_list 
                        if r.get('tamper_detection', {}).get('is_tampered', False))
    weather_mismatch_count = sum(1 for r in fraud_results_list 
                                 if r.get('weather_analysis', {}).get('mismatch', False))
    
    # Overall assessment
    if high_risk_count > 0:
        overall_status = "HIGH_RISK"
        overall_message = f"🚨 {high_risk_count} of {total_images} images flagged for fraud"
    elif unknown_count == total_images:
        overall_status = "UNKNOWN"
        overall_message = f"❓ Unable to assess {total_images} images"
    else:
        overall_status = "LOW_RISK"
        overall_message = f"✅ All {total_images} images passed fraud checks"
    
    return {
        "total_images": total_images,
        "high_risk_count": high_risk_count,
        "low_risk_count": low_risk_count,
        "unknown_count": unknown_count,
        "tampered_count": tampered_count,
        "weather_mismatch_count": weather_mismatch_count,
        "overall_status": overall_status,
        "overall_message": overall_message,
        "requires_investigation": high_risk_count > 0
    }


# API Models
class FraudDetectionRequest(BaseModel):
    timestamp: str
    latitude: float
    longitude: float
    image_path: str

class BatchFraudDetectionRequest(BaseModel):
    image_paths: List[str]
    timestamps: List[str]
    latitudes: List[float]
    longitudes: List[float]

# API Routes
@app.get("/")
async def root():
    return {"message": "Fraud Detection API is running"}

@app.post("/detect")
async def detect_fraud_api(
    image: UploadFile = File(...),
    timestamp: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...)
):
    """
    Detect fraud in a single image
    
    Parameters:
    - image: Image file
    - timestamp: Timestamp in format YYYY-MM-DD HH:MM:SS or YYYY:MM:DD HH:MM:SS
    - latitude: Location latitude
    - longitude: Location longitude
    
    Returns fraud detection results with risk assessment
    """
    # Save the uploaded image to a temp location
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create a unique filename
    file_ext = os.path.splitext(image.filename)[1]
    temp_file = os.path.join(temp_dir, f"{uuid.uuid4()}{file_ext}")
    
    # Save the file
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    # Run fraud detection
    result = detect_fraud(temp_file, timestamp, latitude, longitude)
    
    # Add image info
    result["image_name"] = image.filename
    result["processed_path"] = temp_file
    
    return result

@app.post("/detect-path")
async def detect_fraud_from_path(request: FraudDetectionRequest):
    """
    Detect fraud in an image at the specified path
    
    Parameters:
    - image_path: Path to the image file
    - timestamp: Timestamp in format YYYY-MM-DD HH:MM:SS or YYYY:MM:DD HH:MM:SS
    - latitude: Location latitude
    - longitude: Location longitude
    
    Returns fraud detection results with risk assessment
    """
    # Get the base filename to try multiple possible paths
    base_filename = os.path.basename(request.image_path)
    
    # Strip any 'upload_X_' prefix that the Web app might add
    if base_filename.startswith('upload_'):
        # Extract the part after 'upload_X_'
        stripped_filename = base_filename[base_filename.find('_', 7)+1:] if '_' in base_filename[7:] else base_filename
    else:
        stripped_filename = base_filename
    
    # List of possible paths to check
    possible_paths = [
        request.image_path,                              # Original path
        os.path.join("/app/images", base_filename),      # Direct in images folder
        f"/app/images/{base_filename}",                  # Alternative format
        os.path.join("/app/images", stripped_filename),  # Without upload prefix
        f"/app/images/{stripped_filename}"               # Alternative without prefix
    ]
    
    # For files with spaces, try URL-unquoted versions
    for filename in [base_filename, stripped_filename]:
        if '%20' in filename:
            unquoted_filename = filename.replace('%20', ' ')
            possible_paths.append(os.path.join("/app/images", unquoted_filename))
    
    # List all files in the images directory for potential partial matches
    images_dir = "/app/images"
    all_files = []
    if os.path.exists(images_dir) and os.path.isdir(images_dir):
        all_files = os.listdir(images_dir)
    
    # Look for partial matches (if the target filename is contained within an actual file)
    for actual_file in all_files:
        if stripped_filename in actual_file or base_filename in actual_file:
            possible_paths.append(os.path.join(images_dir, actual_file))
    
    # Try all possible paths
    image_path = None
    for path in possible_paths:
        if os.path.exists(path):
            image_path = path
            break
    
    if image_path is None:
        return JSONResponse(
            status_code=404, 
            content={
                "error": f"Image not found. Tried paths: {possible_paths}",
                "requested_path": request.image_path,
                "base_filename": base_filename,
                "stripped_filename": stripped_filename,
                "available_files": all_files[:10]  # Show first 10 files only
            }
        )
    
    result = detect_fraud(
        image_path, 
        request.timestamp, 
        request.latitude, 
        request.longitude
    )
    
    return result

@app.post("/batch-detect")
async def batch_detect_api(request: BatchFraudDetectionRequest):
    """
    Batch process multiple images for fraud detection
    
    Parameters:
    - image_paths: List of paths to image files
    - timestamps: List of timestamps
    - latitudes: List of latitude values
    - longitudes: List of longitude values
    
    Returns fraud detection results for each image and an overall summary
    """
    # Validate all image paths exist
    missing_images = [path for path in request.image_paths if not os.path.exists(path)]
    
    if missing_images:
        return JSONResponse(
            status_code=404, 
            content={"error": f"Images not found: {missing_images}"}
        )
    
    # Run batch detection
    results = batch_detect_fraud(
        request.image_paths,
        request.timestamps,
        request.latitudes,
        request.longitudes
    )
    
    # Generate summary
    summary = get_fraud_summary(results)
    
    return {
        "results": results,
        "summary": summary
    }

@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running properly"""
    try:
        # Check if models directory exists
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        models_exist = os.path.isdir(models_dir)
        
        # List available models
        available_models = []
        if models_exist:
            available_models = [f for f in os.listdir(models_dir) if f.endswith('.h5')]
        
        # Check images directory
        images_dir = "/app/images"
        images_exist = os.path.isdir(images_dir)
        
        # List a few images for debugging
        available_images = []
        if images_exist:
            try:
                all_images = [f for f in os.listdir(images_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
                available_images = all_images[:5]  # Show just first 5 images
                total_images = len(all_images)
            except Exception as e:
                available_images = [f"Error listing images: {str(e)}"]
                total_images = 0
        
        return {
            "status": "ok" if models_exist and len(available_models) >= 2 else "missing_models",
            "available_models": available_models,
            "required_models": ["model_ela.h5", "Weather_Model.h5"],
            "images_dir_exists": images_exist,
            "available_images": available_images,
            "total_images": total_images if images_exist else 0,
            "service": "fraud_detection"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e)
            }
        )

@app.get("/list-files")
async def list_files():
    """List files in the images directory for debugging"""
    try:
        images_dir = "/app/images"
        if not os.path.exists(images_dir):
            return JSONResponse(
                status_code=404,
                content={"error": f"Directory not found: {images_dir}"}
            )
            
        files = []
        for root, dirs, filenames in os.walk(images_dir):
            for filename in filenames:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    file_path = os.path.join(root, filename)
                    file_size = os.path.getsize(file_path)
                    files.append({
                        "filename": filename,
                        "path": file_path,
                        "size_bytes": file_size,
                        "size_kb": round(file_size / 1024, 2),
                        "exists": os.path.exists(file_path)
                    })
                    
        return {
            "directory": images_dir,
            "exists": os.path.exists(images_dir),
            "is_dir": os.path.isdir(images_dir),
            "file_count": len(files),
            "files": files
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "traceback": str(traceback.format_exc())
            }
        )

# Example usage for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fraud_detector:app", host="0.0.0.0", port=8000)