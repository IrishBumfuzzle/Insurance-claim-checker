import streamlit as st
from PIL import Image
import time
import io

# Configure the page with enhanced settings
st.set_page_config(
    page_title="Car Accident Report System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern professional color theme CSS with fixed file uploader
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Root variables for consistent theming */
    :root {
        --primary-color: #2563eb;
        --primary-hover: #1d4ed8;
        --secondary-color: #64748b;
        --accent-color: #0ea5e9;
        --success-color: #059669;
        --warning-color: #d97706;
        --error-color: #dc2626;
        --background-primary: #ffffff;
        --background-secondary: #f8fafc;
        --background-tertiary: #f1f5f9;
        --text-primary: #1f2937;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --border-color: #e2e8f0;
        --border-accent: #cbd5e1;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --border-radius: 0.5rem;
        --border-radius-lg: 0.75rem;

        /* Dark text area variables */
        --textarea-bg: #1e293b;
        --textarea-bg-focus: #334155;
        --textarea-text: #e2e8f0;
        --textarea-placeholder: #94a3b8;
        --textarea-border: #475569;
        --textarea-border-focus: #0ea5e9;
    }

    /* Global font family */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* COMPLETELY HIDE FILE UPLOADER WHITE BOXES */
    .stFileUploader > div {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stFileUploader > div > div {
        background: none !important;
        border: none !important;
        padding: 0 !important;
    }

    .stFileUploader > div > div > div {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
    }

    .stFileUploader > div > div > div > div {
        display: none !important;
        background: none !important;
    }

    /* Hide default Streamlit file uploader styling */
    .stFileUploader > div > div > div > div {
        display: none !important;
    }

    /* Hide the default file uploader label */
    .stFileUploader > label {
        display: none !important;
    }

    /* Custom file uploader container */
    .stFileUploader {
        position: relative;
        margin: 0 !important;
        padding: 0 !important;
        background: none !important;
        border: none !important;
    }

    /* Style the actual file input */
    .stFileUploader input[type="file"] {
        position: absolute;
        width: 100%;
        height: 100%;
        opacity: 0;
        cursor: pointer;
        z-index: 10;
    }

    /* Remove any white backgrounds from containers */
    div[data-testid="stFileUploader"] {
        background: none !important;
        border: none !important;
    }

    div[data-testid="stFileUploader"] > div {
        background: none !important;
        border: none !important;
    }

    /* Main header styling */
    .main-header {
        text-align: center;
        padding: 2.5rem 0;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: transparent;
        font-size: 3rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin-bottom: 1rem;
    }

    /* Upload section styling - this will replace the white box */
    .upload-section {
        border: 2px dashed var(--border-accent);
        border-radius: var(--border-radius-lg);
        padding: 3rem 2rem;
        text-align: center;
        margin: 1.5rem 0;
        background: linear-gradient(165deg, var(--primary-color) 100%, var(--accent-color) 0%);
        transition: all 0.3s ease;
        position: relative;
        cursor: pointer;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .upload-section:hover {
        border-color: var(--primary-color);
        background: linear-gradient(165deg, var(--primary-color) 100%, var(--accent-color) 0%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    .upload-section.dragover {
        border-color: var(--accent-color);
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        box-shadow: var(--shadow-lg);
    }

    /* Upload icon and text styling */
    .upload-icon {
        font-size: 3rem;
        color: white;
        margin-bottom: 1rem;
    }

    .upload-text {
        font-size: 1.125rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.5rem;
    }

    .upload-subtext {
        font-size: 0.875rem;
        color: white;
        margin-bottom: 1rem;
    }

    .upload-formats {
        font-size: 0.75rem;
        color: #e2e8f0;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 1px solid #a7f3d0;
        border-left: 4px solid var(--success-color);
        color: #065f46;
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        font-weight: 500;
    }

    /* Error message styling */
    .error-message {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 1px solid #fca5a5;
        border-left: 4px solid var(--error-color);
        color: #991b1b;
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        font-weight: 500;
    }

    /* Warning message styling */
    .warning-message {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 1px solid #fcd34d;
        border-left: 4px solid var(--warning-color);
        color: #92400e;
        padding: 1rem 1.5rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        font-weight: 500;
    }

    /* Info box styling */
    .info-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #93c5fd;
        border-left: 4px solid var(--primary-color);
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-sm);
        color: var(--text-primary);
    }

    .info-box h4 {
        color: var(--primary-color);
        margin-bottom: 0.75rem;
        font-weight: 600;
    }

    /* Card styling */
    .metric-container, .card {
        background: var(--background-primary);
        padding: 1.5rem;
        border-radius: var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }

    .metric-container:hover, .card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }

    /* Analysis results styling */
    .analysis-results {
        background: linear-gradient(135deg, var(--background-primary) 0%, var(--background-secondary) 100%);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: var(--shadow-md);
    }

    /* Button customization */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-hover) 0%, #1e40af 100%);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }

    /* Enhanced Text area styling with dark background */
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, var(--textarea-bg) 0%, #2d3748 100%) !important;
        border: 2px solid var(--textarea-border) !important;
        border-radius: var(--border-radius) !important;
        padding: 1.25rem !important;
        font-family: 'Inter', 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        color: var(--textarea-text) !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        resize: vertical !important;
    }

    .stTextArea > div > div > textarea:focus {
        background: linear-gradient(135deg, var(--textarea-bg-focus) 0%, #3c4858 100%) !important;
        border-color: var(--textarea-border-focus) !important;
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.1),
            0 0 0 3px rgba(14, 165, 233, 0.15) !important;
        outline: none !important;
        transform: translateY(-1px) !important;
    }

    .stTextArea > div > div > textarea::placeholder {
        color: var(--textarea-placeholder) !important;
        opacity: 0.8 !important;
        font-style: italic !important;
    }

    /* Text area label styling */
    .stTextArea > label {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 0.75rem !important;
    }

    /* Character counter styling with better contrast */
    .char-counter {
        font-size: 0.875rem;
        font-weight: 500;
        margin-top: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
    }

    .char-counter.valid {
        color: var(--success-color);
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-color: #a7f3d0;
    }

    .char-counter.invalid {
        color: var(--error-color);
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-color: #fca5a5;
    }

    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
        border-radius: var(--border-radius);
    }

    /* Image styling */
    .stImage > img {
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
    }

    /* Footer styling */
    .footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.875rem;
        padding: 2rem 0;
        background: linear-gradient(135deg, var(--background-secondary) 0%, var(--background-tertiary) 100%);
        border-radius: var(--border-radius);
        margin-top: 3rem;
        border: 1px solid var(--border-color);
    }

    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }

    .status-success {
        background-color: var(--success-color);
    }

    .status-warning {
        background-color: var(--warning-color);
    }

    .status-error {
        background-color: var(--error-color);
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1.5rem 0;
        }

        .upload-section {
            padding: 2rem 1rem;
            min-height: 150px;
        }

        .info-box, .metric-container, .card {
            padding: 1rem;
        }

        .stTextArea > div > div > textarea {
            font-size: 0.9rem !important;
            padding: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state with better organization
def init_session_state():
    defaults = {
        'report_submitted': False,
        'result': None,
        'uploaded_image': None,
        'accident_description': "",
        'processing': False,
        'form_errors': []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# Validation functions
def validate_image(uploaded_file):
    """Validate uploaded image file"""
    errors = []

    if uploaded_file is None:
        errors.append("Please upload an image file")
        return errors

    # Check file size (limit to 10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        errors.append("Image file size should be less than 10MB")

    # Check file type
    allowed_types = ['jpg', 'jpeg', 'png', 'webp']
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in allowed_types:
        errors.append(f"File type '{file_extension}' not supported. Please use: {', '.join(allowed_types)}")

    return errors


def validate_description(description):
    """Validate accident description"""
    errors = []

    if not description or not description.strip():
        errors.append("Please provide an accident description")
        return errors

    if len(description.strip()) < 20:
        errors.append("Description should be at least 20 characters long")

    if len(description.strip()) > 2000:
        errors.append("Description should not exceed 2000 characters")

    return errors


# Results page with enhanced UI
def show_results_page():
    st.markdown('<h1 class="main-header">📊 Analysis Results</h1>', unsafe_allow_html=True)

    # Display analysis results first
    st.markdown('<div class="analysis-results">', unsafe_allow_html=True)
    st.subheader("🔍 Damage Analysis Report")
    if st.session_state.result:
        # Display the natural English report
        st.markdown(st.session_state.result)
    else:
        st.markdown("""
        <div class="warning-message">
            <span class="status-indicator status-warning"></span>
            No analysis results available
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Show processed/edited image after results
    if st.session_state.uploaded_image:
        st.subheader("📷 Processed Image")
        st.image(
            st.session_state.uploaded_image,
            caption="Analyzed Image (scaled for display)",
            use_column_width=False,
            width=400  # Fixed width to scale down the image
        )

        # Image details in an expander
        with st.expander("📋 Image Details", expanded=False):
            img = st.session_state.uploaded_image
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Display Width", f"{img.size[0]}px")
                st.metric("Format", img.format or "Unknown")
            with col_b:
                st.metric("Display Height", f"{img.size[1]}px")
                st.metric("Mode", img.mode)

    st.divider()

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📝 Submit Another Report", type="primary", use_container_width=True):
            reset_session_state()
            st.rerun()


# Input page with enhanced UI
def show_input_page():
    st.markdown('<h1 class="main-header">🚗 Car Accident Report System</h1>', unsafe_allow_html=True)

    # Introduction
    st.markdown("""
    <div class="info-box">
        <h4>📋 Report Instructions</h4>
        <p>Please provide a clear image of the damaged vehicle and detailed description of the accident. 
        This information will be analyzed to generate a comprehensive accident report.</p>
    </div>
    """, unsafe_allow_html=True)

    # Create two columns for better layout
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("📷 Upload Car Image")

        # Custom upload area that replaces the white box
        st.markdown("""
        <div class="upload-section">
            <div class="upload-icon">📷</div>
            <div class="upload-text">Click to upload or drag and drop</div>
            <div class="upload-subtext">Select your car damage image</div>
            <div class="upload-formats">Supported: JPG, JPEG, PNG, WEBP (Max: 10MB)</div>
        </div>
        """, unsafe_allow_html=True)

        # Hidden file uploader that works with our custom styling
        uploaded_image = st.file_uploader(
            "Upload car image",
            type=['jpg', 'jpeg', 'png', 'webp'],
            label_visibility="hidden",
            key="image_uploader"
        )

        # Display uploaded image with validation
        if uploaded_image is not None:
            image_errors = validate_image(uploaded_image)

            if not image_errors:
                try:
                    image = Image.open(uploaded_image)
                    st.image(image, caption="Preview", use_column_width=True)

                    # Image info
                    st.markdown(f"""
                    <div class="success-message">
                        <span class="status-indicator status-success"></span>
                        Image uploaded successfully ({uploaded_image.size:,} bytes)
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        <span class="status-indicator status-error"></span>
                        Error loading image: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
                    uploaded_image = None
            else:
                for error in image_errors:
                    st.markdown(f"""
                    <div class="error-message">
                        <span class="status-indicator status-error"></span>
                        {error}
                    </div>
                    """, unsafe_allow_html=True)
                uploaded_image = None

    with col2:
        st.subheader("📝 Accident Description")

        # Standard Streamlit text area with enhanced CSS styling
        accident_description = st.text_area(
            "Describe the accident and damaged parts",
            placeholder="""Please provide detailed information about:
• What happened during the accident
• Which parts of the vehicle are damaged
• Location and time of the incident
• Weather conditions
• Other vehicles involved
• Any other relevant information

Example: "At 3:30 PM on Main Street, I was rear-ended while stopped at a red light. The impact damaged my rear bumper, trunk, and both taillights. The other vehicle hit me at approximately 25 mph..."
""",
            height=300,
            max_chars=2000,
            help="Provide at least 20 characters for a meaningful description"
        )

        # Character counter with enhanced styling
        char_count = len(accident_description) if accident_description else 0
        counter_class = "valid" if char_count >= 20 else "invalid"
        st.markdown(f"""
        <div class="char-counter {counter_class}">
            <span class="status-indicator status-{'success' if char_count >= 20 else 'error'}"></span>
            Characters: {char_count}/2000 (minimum: 20)
        </div>
        """, unsafe_allow_html=True)

        # Validation for description
        if accident_description:
            desc_errors = validate_description(accident_description)
            for error in desc_errors:
                st.markdown(f"""
                <div class="error-message">
                    <span class="status-indicator status-error"></span>
                    {error}
                </div>
                """, unsafe_allow_html=True)

    st.divider()

    # Submit section
    st.subheader("🚀 Submit Report")

    # Final validation before submit
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        submit_button = st.button(
            "📊 Generate Analysis Report",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.processing
        )

        if submit_button:
            # Comprehensive validation
            all_errors = []

            if uploaded_image:
                all_errors.extend(validate_image(uploaded_image))
            else:
                all_errors.append("Please upload an image")

            all_errors.extend(validate_description(accident_description))

            if all_errors:
                st.markdown("""
                <div class="error-message">
                    <span class="status-indicator status-error"></span>
                    Please fix the following issues:
                </div>
                """, unsafe_allow_html=True)
                for error in all_errors:
                    st.markdown(f"""
                    <div class="error-message">
                        • {error}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Process the report
                st.session_state.processing = True

                with st.spinner("🔄 Processing your accident report..."):
                    progress_bar = st.progress(0)

                    try:
                        # Simulate processing steps
                        progress_bar.progress(25)
                        time.sleep(0.5)

                        # Import and process
                        import car
                        progress_bar.progress(50)

                        result_text, processed_image = car.process_accident_report(uploaded_image, accident_description)
                        progress_bar.progress(75)

                        # Save to session state
                        st.session_state.result = result_text
                        st.session_state.uploaded_image = processed_image
                        st.session_state.accident_description = accident_description
                        st.session_state.report_submitted = True

                        progress_bar.progress(100)
                        time.sleep(0.5)

                        st.markdown("""
                        <div class="success-message">
                            <span class="status-indicator status-success"></span>
                            Report processed successfully!
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()

                    except ImportError:
                        st.markdown("""
                        <div class="error-message">
                            <span class="status-indicator status-error"></span>
                            Error: 'car' module not found. Please ensure the processing module is available.
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"""
                        <div class="error-message">
                            <span class="status-indicator status-error"></span>
                            Error processing report: {str(e)}
                        </div>
                        """, unsafe_allow_html=True)
                    finally:
                        st.session_state.processing = False


def reset_session_state():
    """Reset all session state variables"""
    st.session_state.report_submitted = False
    st.session_state.result = None
    st.session_state.uploaded_image = None
    st.session_state.accident_description = ""
    st.session_state.processing = False
    st.session_state.form_errors = []


# Main application logic
def main():
    init_session_state()

    # Navigation
    if st.session_state.report_submitted and st.session_state.uploaded_image and st.session_state.accident_description:
        show_results_page()
    else:
        show_input_page()

    # Footer
    st.divider()
    st.markdown("""
    <div class="footer">
        Built with ❤️ using Streamlit 🎈<br>
        <strong>Car Accident Report System v2.0</strong><br>
        <small>Professional accident analysis and reporting</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()