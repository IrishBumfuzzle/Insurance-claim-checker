import streamlit as st
from PIL import Image
import time
from car import damage_assess
import os
import requests, io

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

    /* Make all Streamlit components have black background */
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

    .stForm {
        background-color: #000000 !important;
    }

    .stMarkdown {
        background-color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def init_database():
    """Initialize database with caching"""
    try:
        from database import AccidentDatabase
        return AccidentDatabase()
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return None


def main():
    # Initialize session state for page control
    if 'page_state' not in st.session_state:
        st.session_state.page_state = 'form'
    if 'report_data' not in st.session_state:
        st.session_state.report_data = None

    # Initialize database
    db = init_database()
    if db is None:
        st.error("Failed to initialize database. Please check your setup.")
        return

    # Header
    st.markdown('<h1 class="main-header">🚗 Car Accident Report System</h1>', unsafe_allow_html=True)

    # Current time info
    current_time = "2025-10-12 03:47:27"
    current_user = "ParthSharma901"

    st.markdown(f"""
    <div class="info-box">
        Submit accident reports for analysis and database storage.
    </div>
    """, unsafe_allow_html=True)

    # Page routing
    if st.session_state.page_state == 'form':
        new_report_page(db, current_user)
    elif st.session_state.page_state == 'results':
        show_results_page()


def new_report_page(db, current_user):
    st.header("📝 Submit New Accident Report")

    # Create form
    with st.form("accident_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚗 Vehicle Information")
            license_number = st.text_input("License Plate Number *", placeholder="ABC-1234")
            owner_name = st.text_input("Owner Name", placeholder="John Doe")
            vehicle_make = st.text_input("Make", placeholder="Toyota")
            vehicle_model = st.text_input("Model", placeholder="Camry")
            vehicle_year = st.number_input("Year", min_value=1990, max_value=2025, value=2020)
            vehicle_color = st.text_input("Color", placeholder="Blue")

        with col2:
            st.subheader("📍 Accident Details")
            location = st.text_input("Accident Location *", placeholder="Main St & 1st Ave")

            # Multiple image upload
            st.subheader("📷 Upload Vehicle Images")
            uploaded_images = st.file_uploader(
                "Choose multiple images",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                help="Upload multiple images showing different angles of the damage"
            )

            # Display uploaded images
            if uploaded_images:
                st.write(f"**{len(uploaded_images)} image(s) uploaded:**")

                # Create columns for image display
                cols = st.columns(min(len(uploaded_images), 3))  # Max 3 columns

                for idx, uploaded_image in enumerate(uploaded_images):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        try:
                            image = Image.open(uploaded_image)
                            st.image(image, caption=f"Image {idx + 1}: {uploaded_image.name}", width=200)

                            # Show image details
                            file_size = len(uploaded_image.getvalue()) / 1024  # KB
                            st.caption(f"Size: {file_size:.1f} KB")
                        except Exception as e:
                            st.error(f"Error loading {uploaded_image.name}")

        # Description
        st.subheader("📝 Accident Description")
        description = st.text_area(
            "Describe what happened *",
            placeholder="Describe the accident, damaged parts, time of incident, and circumstances...\n\nExample: At 3:30 PM on Main Street, I was rear-ended while stopped at a red light. The impact damaged my rear bumper and taillights.",
            height=120
        )

        # Character counter
        if description:
            char_count = len(description)
            st.caption(f"Characters: {char_count} (minimum: 20)")

        # Submit button
        submitted = st.form_submit_button("📊 Generate Analysis Report", type="primary", use_container_width=True)

        if submitted:
            # Validation
            if not license_number or not description or not location or not uploaded_images:
                st.markdown(
                    '<div class="error-box">❌ Please fill in all required fields (*) and upload at least one image</div>',
                    unsafe_allow_html=True)
            elif len(description) < 20:
                st.markdown('<div class="error-box">❌ Description must be at least 20 characters</div>',
                            unsafe_allow_html=True)
            else:
                # Process report
                with st.spinner(f"🔄 Processing accident report with {len(uploaded_images)} image(s)..."):
                    try:
                        results_list = []
                        images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'images'))
                        os.makedirs(images_dir, exist_ok=True)
                        
                        for idx, uploaded_image in enumerate(uploaded_images):
                            # Save uploaded image to ../images folder
                            image_filename = f"upload_{idx}_{uploaded_image.name}"
                            image_path = os.path.join(images_dir, image_filename)
                            with open(image_path, "wb") as f:
                                f.write(uploaded_image.getvalue())
                            # Call damage_assess
                            yolo_results, annotated_image_path = damage_assess(image_path)
                            results_list.append((image_path, yolo_results, annotated_image_path))
                        # Display results for each image
                        for idx, (img_path, yolo_results, annotated_image_path) in enumerate(results_list):
                            st.markdown(f"<div class='report-box'><b>Image {idx+1}: {img_path}</b></div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='info-box'><b>YOLO Results:</b> {yolo_results}</div>", unsafe_allow_html=True)
                            # Fetch annotated image from GET API
                            try:
                                api_url = f"http://ultralytics:8000/damage?img_path={img_path}"
                                response = requests.get(api_url)
                                if response.status_code == 200:
                                    annotated_img = Image.open(io.BytesIO(response.content))
                                    st.image(annotated_img, caption=f"Annotated Image {idx+1} (via API)", width=300)
                                else:
                                    st.warning(f"API error fetching annotated image for {img_path}: {response.status_code}")
                            except Exception as e:
                                st.warning(f"Error displaying annotated image from API: {e}")
                    except Exception as e:
                        st.markdown(f'<div class="error-box">❌ Error processing report: {str(e)}</div>',
                                    unsafe_allow_html=True)


def show_results_page():
    st.header("📊 Accident Report Results")

    # Get report data from session state
    report_data = st.session_state.report_data

    if report_data:
        # Success message
        st.markdown(f"""
        <div class="success-box">
            ✅ <strong>Report Successfully Processed!</strong><br>
            Report ID: <strong>{report_data['accident_id']}</strong><br>
            License Plate: <strong>{report_data['license_number']}</strong><br>
            Images Processed: <strong>{report_data['image_count']}</strong><br>
            User: <strong>{report_data['current_user']}</strong><br>
            Timestamp: <strong>2025-10-12 03:47:27 UTC</strong>
        </div>
        """, unsafe_allow_html=True)

        # Display report
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.markdown("### 📋 Accident Analysis Report")
        st.text(report_data['report_text'])
        st.markdown('</div>', unsafe_allow_html=True)

        # Next steps
        st.markdown("### ✅ Next Steps")
        col1, col2 = st.columns(2)
        with col1:
            st.info("📞 Contact your insurance provider with this report")
        with col2:
            st.info("💾 Report saved securely in database")

    # Action buttons
    st.markdown("---")
    st.markdown("### 🔄 What would you like to do next?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📝 Submit Another Report", type="primary", use_container_width=True):
            # Clear session state and go back to form
            st.session_state.page_state = 'form'
            st.session_state.report_data = None
            st.rerun()

    with col2:
        if st.button("📋 View This Report Again", type="secondary", use_container_width=True):
            # Stay on results page, just refresh
            st.rerun()

    with col3:
        if st.button("🔄 Reset All Data", type="secondary", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page_state = 'form'
            st.rerun()


if __name__ == "__main__":
    main()