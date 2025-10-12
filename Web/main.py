import streamlit as st
from PIL import Image
import time
import os
import requests, io
import json
import sys

# Page configuration
st.set_page_config(
    page_title="Car Accident Report System",
    page_icon="🚗",
    layout="wide"
)

# Black background CSS
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .main-header {
        text-align: center;
        color: #2563eb;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        background-color: #000000;
    }
    .success-box {
        background-color: #000000;
        border: 1px solid #a7f3d0;
        border-left: 4px solid #059669;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    .error-box {
        background-color: #000000;
        border: 1px solid #fca5a5;
        border-left: 4px solid #dc2626;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    .warning-box {
        background-color: #000000;
        border: 1px solid #fbbf24;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    .report-box {
        background-color: #000000;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    .info-box {
        background-color: #000000;
        border: 1px solid #93c5fd;
        border-left: 4px solid #2563eb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #ffffff;
    }
    .stSelectbox > div > div {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    .stTextInput > div > div > input {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
    }
    .stTextArea > div > div > textarea {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
    }
    .stNumberInput > div > div > input {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #444444 !important;
    }
</style>
""", unsafe_allow_html=True)

# Use the fraud detection API instead of direct import
import requests

# Define fraud service URL
FRAUD_API_URL = "http://fraud:8000"

def check_fraud_service_available():
    """Check if the fraud detection service is available"""
    try:
        response = requests.get(f"{FRAUD_API_URL}/health", timeout=2)
        if response.status_code == 200:
            status = response.json().get("status")
            if status == "ok":
                st.sidebar.success("✅ Fraud detection loaded")
                return True
            else:
                models = response.json().get("available_models", [])
                st.sidebar.warning(f"⚠️ Fraud service missing models: {', '.join(models) if models else 'all'}")
                return False
        else:
            st.sidebar.warning(f"⚠️ Fraud service responded with status {response.status_code}")
            return False
    except requests.RequestException as e:
        st.sidebar.warning(f"⚠️ Fraud service unavailable: {str(e)[:80]}")
        return False

# Check if fraud service is available
FRAUD_AVAILABLE = check_fraud_service_available()

@st.cache_resource
def init_database():
    """Initialize database with caching"""
    try:
        from database import AccidentDatabase
        return AccidentDatabase()
    except Exception as e:
        return None

def run_fraud_check(image_path, timestamp, lat, lon):
    """Run fraud detection if available"""
    if not FRAUD_AVAILABLE:
        st.warning("⚠️ Fraud detection is disabled - skipping fraud check")
        return None
    
    try:
        # Format timestamp
        ts = timestamp.replace("-", ":") if "-" in timestamp else timestamp
        
        # Extract the filename from the path and clean it
        filename = os.path.basename(image_path)
        
        # We'll send the original path and let the fraud API handle finding the file
        # This is more robust as it will try multiple paths
        
        st.info(f"🔄 Processing image '{filename}' for fraud detection")
        
        # Call fraud API service using the detect-path endpoint
        data = {
            "image_path": image_path,  # Send the original path
            "timestamp": ts,
            "latitude": float(lat or 0),
            "longitude": float(lon or 0)
        }
        
        # Log the request data (but hide sensitive details)
        st.code(f"Processing with timestamp: {ts}, coords: ({lat}, {lon})")
        
        # Make the API call
        response = requests.post(f"{FRAUD_API_URL}/detect-path", json=data, timeout=10)
        
        if response.status_code != 200:
            st.error(f"⚠️ Fraud API error: HTTP {response.status_code}")
            try:
                error_details = response.json()
                st.error(f"Error details: {error_details}")
            except:
                st.error(f"Raw response: {response.text[:500]}")
            return {"success": False, "error": f"API error: {response.status_code}", "risk": "UNKNOWN"}
            
        # Process API response
        result = response.json()
        
        # Log the response for debugging
        st.code(f"API response: {result}", language="json")
        
        # Extract relevant data from API response
        tamper_info = result.get("tamper_detection", {})
        weather_info = result.get("weather_analysis", {})
        
        tamper_class = tamper_info.get("class", "Unknown")
        tamper_conf = tamper_info.get("confidence", 0)
        is_tampered = tamper_info.get("is_tampered", False)
        
        weather_class = weather_info.get("predicted_weather", "Unknown")
        weather_conf = weather_info.get("predicted_confidence", 0)
        actual_weather = weather_info.get("actual_weather", "")
        location = weather_info.get("location", "")
        weather_mismatch = weather_info.get("mismatch", False)
        
        # Get fraud indicators
        indicators = result.get("fraud_indicators", [])
        risk_level = result.get("fraud_risk", "UNKNOWN")
        
        return {
            "success": True,
            "risk": risk_level,
            "tamper": {"class": tamper_class, "conf": tamper_conf, "is_tampered": is_tampered},
            "weather": {"pred": weather_class, "pred_conf": weather_conf, 
                       "actual": actual_weather, "loc": location, "mismatch": weather_mismatch},
            "indicators": indicators
        }
    except Exception as e:
        st.error(f"⚠️ Error in fraud check: {str(e)}")
        import traceback
        st.code(traceback.format_exc(), language="python")
        return {"success": False, "error": str(e), "risk": "UNKNOWN"}

def main():
    if 'page_state' not in st.session_state:
        st.session_state.page_state = 'form'
    
    db = init_database()
    
    st.markdown('<h1 class="main-header">🚗 Car Accident Report System</h1>', unsafe_allow_html=True)
    
    if FRAUD_AVAILABLE:
        st.sidebar.success("✅ Fraud Detection Active")
    else:
        st.sidebar.warning("⚠️ Fraud Detection Disabled")
    
    if st.session_state.page_state == 'form':
        show_form(db)

def show_form(db):
    st.header("📝 Submit New Accident Report")
    
    with st.form("accident_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚗 Vehicle Information")
            license_number = st.text_input("License Plate *", placeholder="ABC-1234")
            owner_name = st.text_input("Owner Name", placeholder="John Doe")
            vehicle_make = st.text_input("Make", placeholder="Toyota")
            vehicle_model = st.text_input("Model", placeholder="Camry")
            vehicle_year = st.number_input("Year", min_value=1990, max_value=2025, value=2020)
            vehicle_color = st.text_input("Color", placeholder="Blue")
        
        with col2:
            st.subheader("📍 Accident Details")
            latitude = st.text_input("Latitude *", placeholder="28.6139")
            longitude = st.text_input("Longitude *", placeholder="77.2090")
            
            st.subheader("📷 Upload Images")
            uploaded_images = st.file_uploader(
                "Choose images",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True
            )
            
            if uploaded_images:
                st.write(f"**{len(uploaded_images)} image(s) uploaded**")
                cols = st.columns(min(len(uploaded_images), 3))
                for idx, img in enumerate(uploaded_images):
                    with cols[idx % 3]:
                        st.image(Image.open(img), caption=f"Image {idx+1}", width=200)
        
        description = st.text_area(
            "Describe the accident *",
            placeholder="Describe damage, time, circumstances...",
            height=120
        )
        
        submitted = st.form_submit_button("📊 Generate Report", type="primary", use_container_width=True)
        
        if submitted:
            if not all([license_number, description, latitude, longitude, uploaded_images]):
                st.error("❌ Please fill all required fields")
                return
            
            if len(description) < 20:
                st.error("❌ Description too short (min 20 chars)")
                return
            
            # Save description
            desc_dir = os.path.join(os.path.dirname(__file__), '..', 'ultralytics', 'description')
            os.makedirs(desc_dir, exist_ok=True)
            
            user_input = {
                "license_number": license_number,
                "owner_name": owner_name,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "vehicle_year": int(vehicle_year),
                "vehicle_color": vehicle_color,
                "latitude": latitude,
                "longitude": longitude,
                "description": description,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(os.path.join(desc_dir, "description.json"), "w") as f:
                json.dump(user_input, f, indent=2)
            
            # Process images
            with st.spinner("Processing..."):
                local_imgs = os.path.join(os.path.dirname(__file__), '..', 'images')
                os.makedirs(local_imgs, exist_ok=True)
                
                fraud_results = []
                damage_results = []
                
                for idx, img in enumerate(uploaded_images):
                    # Save the file with a clean name (no upload prefix)
                    clean_filename = img.name
                    img_path = os.path.join(local_imgs, clean_filename)
                    
                    # Check if file already exists and ensure uniqueness if needed
                    if os.path.exists(img_path):
                        # Add timestamp to ensure uniqueness
                        base_name, ext = os.path.splitext(clean_filename)
                        timestamp_str = time.strftime("%Y%m%d%H%M%S")
                        clean_filename = f"{base_name}_{timestamp_str}{ext}"
                        img_path = os.path.join(local_imgs, clean_filename)
                    
                    # Save file to disk
                    with open(img_path, "wb") as f:
                        f.write(img.getvalue())
                    
                    # Create the path that will work for the fraud container
                    # The fraud container mounts the same directory at /app/images
                    container_path = f"/app/images/{clean_filename}"
                    
                    # Show the saved path (for debugging)
                    st.info(f"📁 Saved image: {clean_filename}")
                    
                    # Fraud detection
                    if FRAUD_AVAILABLE:
                        st.markdown(f"### 🔍 Fraud Check - Image {idx+1}")
                        fraud_res = run_fraud_check(container_path, user_input["timestamp"], latitude, longitude)
                        
                        if fraud_res and fraud_res.get("success"):
                            risk = fraud_res["risk"]
                            box_class = "error-box" if risk == "HIGH" else "success-box"
                            st.markdown(f'<div class="{box_class}"><b>Risk: {risk}</b></div>', unsafe_allow_html=True)
                            
                            if fraud_res["indicators"]:
                                st.warning(f"⚠️ {', '.join(fraud_res['indicators'])}")
                            
                            tamper = fraud_res["tamper"]
                            icon = "🚨" if tamper["is_tampered"] else "✅"
                            st.info(f"{icon} Authenticity: {tamper['class']} ({tamper['conf']}%)")
                            
                            weather = fraud_res["weather"]
                            if weather["loc"]:
                                st.info(f"📍 {weather['loc']}")
                            st.info(f"☁️ Predicted: {weather['pred']} | Actual: {weather['actual']}")
                            
                            fraud_results.append(fraud_res)
                    
                    # Damage assessment
                    img.seek(0)
                    files = {"img": (img.name, img.getvalue(), img.type)}
                    resp = requests.post("http://ultralytics:8000/damage", files=files)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        damage_results.append(data)
                
                # Send description to ultralytics
                requests.post("http://ultralytics:8000/description", json=user_input, timeout=5)
                
                # Generate cost estimate
                st.markdown("---")
                st.markdown("### 💰 Cost Estimation")
                gen_resp = requests.get("http://ultralytics:8000/gen")
                
                if gen_resp.status_code == 200:
                    gen_data = gen_resp.json()
                    cost_json = gen_data.get('cost_conf_json')
                    
                    if cost_json and not cost_json.startswith("Error"):
                        st.json(json.loads(cost_json))
                    
                    # Show grade images
                    st.markdown("### 📊 Damage Grades")
                    for idx, dmg in enumerate(damage_results):
                        img_path = dmg.get('original_image_path', '')
                        grade_path = img_path.replace('/app/images', '/app/grade_cam')
                        
                        try:
                            resp = requests.get(f"http://ultralytics:8000/damage?img_path={grade_path}")
                            if resp.status_code == 200:
                                st.image(Image.open(io.BytesIO(resp.content)), caption=f"Grade {idx+1}", width=400)
                        except:
                            pass
                
                # Fraud summary
                if fraud_results:
                    st.markdown("---")
                    st.markdown("### 🔒 Fraud Summary")
                    high_risk = sum(1 for r in fraud_results if r.get("risk") == "HIGH")
                    
                    if high_risk > 0:
                        st.error(f"🚨 {high_risk} of {len(fraud_results)} images flagged as HIGH RISK")
                    else:
                        st.success(f"✅ All {len(fraud_results)} images passed checks")

if __name__ == "__main__":
    main()