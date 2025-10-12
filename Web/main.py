import streamlit as st
from PIL import Image
import time
import io
from datetime import datetime
from car import process_and_save_accident_report, get_vehicle_accident_history, search_accidents_by_criteria
from database import AccidentDatabase

# Initialize database
db = AccidentDatabase()

# Configure the page with enhanced settings
st.set_page_config(
    page_title="Car Accident Report System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS styling with better framed results
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

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
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 10px 10px -5px rgb(0 0 0 / 0.04);
        --border-radius: 0.5rem;
        --border-radius-lg: 0.75rem;
        --border-radius-xl: 1rem;

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

    /* Enhanced Analysis Results Frame */
    .analysis-results {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        border: 3px solid transparent;
        border-radius: var(--border-radius-xl);
        padding: 0;
        margin: 2rem 0;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
        background-clip: padding-box;
    }

    .analysis-results::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 25%, #10b981 50%, #f59e0b 75%, #ef4444 100%);
        border-radius: var(--border-radius-xl);
        padding: 3px;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
        z-index: -1;
    }

    .analysis-header {
        background: linear-gradient(135deg, #1e40af 0%, #0ea5e9 100%);
        padding: 1.5rem 2rem;
        border-radius: var(--border-radius-xl) var(--border-radius-xl) 0 0;
        margin: 0;
        position: relative;
        overflow: hidden;
    }

    .analysis-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    .analysis-header h3 {
        color: #ffffff;
        margin: 0;
        font-weight: 600;
        font-size: 1.5rem;
        text-align: center;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .analysis-content {
        padding: 2rem;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 0 0 var(--border-radius-xl) var(--border-radius-xl);
    }

    .report-section {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid #475569;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
        position: relative;
    }

    .report-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
        border-radius: var(--border-radius) var(--border-radius) 0 0;
    }

    .section-title {
        color: #60a5fa;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .report-text {
        color: #e2e8f0;
        font-family: 'JetBrains Mono', 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        font-size: 0.9rem;
        line-height: 1.7;
        white-space: pre-wrap;
        word-wrap: break-word;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        margin: 0;
    }

    .highlight-value {
        color: #fbbf24;
        font-weight: 600;
    }

    .highlight-important {
        color: #34d399;
        font-weight: 600;
    }

    .highlight-warning {
        color: #fb7185;
        font-weight: 600;
    }

    /* Section header styling */
    .section-header {
        color: var(--text-primary);
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
        padding-bottom: 0.5rem;
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

    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1.5rem 0;
        }

        .info-box, .metric-container, .card {
            padding: 1rem;
        }

        .stTextArea > div > div > textarea {
            font-size: 0.9rem !important;
            padding: 1rem !important;
        }

        .analysis-content {
            padding: 1.5rem;
        }

        .report-section {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# [Keep all the initialization and validation functions the same as before]

def init_session_state():
    defaults = {
        'report_submitted': False,
        'result': None,
        'uploaded_image': None,
        'accident_description': "",
        'processing': False,
        'form_errors': [],
        'form_submitted': False,
        'accident_id': None,
        'license_number': ""
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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


def format_analysis_report(report_text):
    """Format the analysis report into structured sections with highlighting"""
    if not report_text:
        return ""

    # Split the report into sections
    lines = report_text.strip().split('\n')
    formatted_sections = []
    current_section = []
    current_title = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this is a section header
        if line.endswith(':') and len(line.split()) <= 4:
            # Save previous section
            if current_section and current_title:
                section_content = '\n'.join(current_section)
                # Apply highlighting
                section_content = apply_text_highlighting(section_content)
                formatted_sections.append({
                    'title': current_title,
                    'content': section_content,
                    'icon': get_section_icon(current_title)
                })

            # Start new section
            current_title = line.replace(':', '').strip()
            current_section = []
        else:
            current_section.append(line)

    # Add the last section
    if current_section and current_title:
        section_content = '\n'.join(current_section)
        section_content = apply_text_highlighting(section_content)
        formatted_sections.append({
            'title': current_title,
            'content': section_content,
            'icon': get_section_icon(current_title)
        })

    # If no sections found, treat as single section
    if not formatted_sections:
        formatted_sections.append({
            'title': 'Analysis Report',
            'content': apply_text_highlighting(report_text),
            'icon': '📊'
        })

    return formatted_sections


def apply_text_highlighting(text):
    """Apply color highlighting to important values in the text"""
    import re

    # Highlight dollar amounts
    text = re.sub(r'(\$[\d,]+ - \$[\d,]+|\$[\d,]+)', r'<span class="highlight-value">\1</span>', text)

    # Highlight percentages
    text = re.sub(r'(\d+\.?\d*%)', r'<span class="highlight-value">\1</span>', text)

    # Highlight severity levels
    text = re.sub(r'\b(Minor|Moderate|Severe|High|Medium|Low)\b', r'<span class="highlight-important">\1</span>', text)

    # Highlight important keywords
    keywords = ['damaged', 'impact', 'collision', 'repair', 'estimate', 'confidence', 'analysis']
    for keyword in keywords:
        pattern = f'\\b({keyword})\\b'
        text = re.sub(pattern, r'<span class="highlight-warning">\1</span>', text, flags=re.IGNORECASE)

    return text


def get_section_icon(title):
    """Get appropriate icon for section title"""
    title_lower = title.lower()
    if 'image' in title_lower:
        return '🖼️'
    elif 'damage' in title_lower:
        return '🔧'
    elif 'incident' in title_lower or 'accident' in title_lower:
        return '🚗'
    elif 'recommendation' in title_lower:
        return '💡'
    elif 'key' in title_lower or 'terms' in title_lower:
        return '🔑'
    else:
        return '📋'


def main():
    init_session_state()

    # Header
    st.markdown('<h1 class="main-header">🚗 Car Accident Report System</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar for navigation
    with st.sidebar:
        st.title("📋 Navigation")
        page = st.selectbox("Choose Page", ["New Report", "View History", "Search Reports", "Statistics"])

        st.markdown("---")
        st.markdown("**System Info:**")
        st.write("📊 Database: SQLite")
        st.write("🕒 Session Active")

    if page == "New Report":
        show_new_report_form()
    elif page == "View History":
        show_accident_history()
    elif page == "Search Reports":
        show_search_page()
    elif page == "Statistics":
        show_statistics_page()


# [Keep all the form functions the same until show_report_results]

def show_new_report_form():
    # Check if results should be shown
    if st.session_state.form_submitted and st.session_state.accident_id:
        show_report_results()
        return

    st.header("📝 Submit New Accident Report")

    # Introduction
    st.markdown("""
    <div class="info-box">
        <h4>📋 Report Instructions</h4>
        <p>Please provide a clear image of the damaged vehicle and detailed description of the accident. 
        This information will be analyzed to generate a comprehensive accident report and saved to the database.</p>
    </div>
    """, unsafe_allow_html=True)

    # Create two columns for better layout
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-header">🚗 Vehicle Information</div>', unsafe_allow_html=True)

        # Vehicle Information Form (Simplified - removed insurance provider)
        license_number = st.text_input(
            "License Plate Number *",
            placeholder="e.g., ABC-1234",
            help="Enter the license plate number of the vehicle involved"
        )

        owner_name = st.text_input(
            "Vehicle Owner Name",
            placeholder="e.g., John Doe"
        )

        col_make, col_model = st.columns(2)
        with col_make:
            vehicle_make = st.text_input("Make", placeholder="e.g., Toyota")
        with col_model:
            vehicle_model = st.text_input("Model", placeholder="e.g., Camry")

        col_year, col_color = st.columns(2)
        with col_year:
            vehicle_year = st.number_input("Year", min_value=1900, max_value=2025, value=2020)
        with col_color:
            vehicle_color = st.text_input("Color", placeholder="e.g., Blue")

    with col2:
        st.markdown('<div class="section-header">📍 Accident Details</div>', unsafe_allow_html=True)

        # Simplified Accident Information
        location = st.text_input(
            "Accident Location *",
            placeholder="e.g., Main St & 1st Ave",
            help="Provide the specific location where the accident occurred"
        )

        # Image Upload Section
        st.markdown('<div class="section-header">📷 Upload Car Image</div>', unsafe_allow_html=True)

        uploaded_image = st.file_uploader(
            "Choose an image file *",
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Upload a clear image of the damaged vehicle (Max: 10MB)"
        )

        # Display uploaded image with validation
        if uploaded_image is not None:
            image_errors = validate_image(uploaded_image)

            if not image_errors:
                try:
                    image = Image.open(uploaded_image)
                    st.image(image, caption="Preview", use_column_width=True)

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

    # Accident Description Section
    st.markdown('<div class="section-header">📝 Accident Description</div>', unsafe_allow_html=True)

    accident_description = st.text_area(
        "Describe the accident and damaged parts *",
        placeholder="""Please provide detailed information about:
• What happened during the accident
• Which parts of the vehicle are damaged
• Time of the incident
• Other vehicles involved
• Any other relevant information

Example: "At 3:30 PM on Main Street, I was rear-ended while stopped at a red light. The impact damaged my rear bumper, trunk, and both taillights. The other vehicle hit me at approximately 25 mph..."
""",
        height=200,
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

    # Form validation and submission
    st.markdown("---")
    st.subheader("🚀 Submit Report")

    # Display form validation status
    required_fields = [license_number, accident_description, uploaded_image, location]
    required_field_names = ["License Number", "Description", "Photo", "Location"]
    missing_fields = [name for field, name in zip(required_fields, required_field_names) if not field]

    if missing_fields:
        st.markdown(f"""
        <div class="warning-message">
            <span class="status-indicator status-warning"></span>
            Required fields missing: {', '.join(missing_fields)}
        </div>
        """, unsafe_allow_html=True)

    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button(
            "📊 Generate Analysis Report & Save to Database",
            type="primary",
            disabled=bool(missing_fields) or st.session_state.processing,
            use_container_width=True
        )

    if submit_button and not missing_fields:
        st.session_state.processing = True

        with st.spinner("🔄 Processing your accident report..."):
            progress_bar = st.progress(0)

            try:
                # Comprehensive validation
                all_errors = []
                all_errors.extend(validate_image(uploaded_image))
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
                    return

                progress_bar.progress(25)
                time.sleep(0.5)

                # Prepare vehicle information (simplified)
                vehicle_info = {
                    'owner_name': owner_name if owner_name.strip() else None,
                    'vehicle_make': vehicle_make if vehicle_make.strip() else None,
                    'vehicle_model': vehicle_model if vehicle_model.strip() else None,
                    'vehicle_year': vehicle_year if vehicle_year else None,
                    'vehicle_color': vehicle_color if vehicle_color.strip() else None,
                    'insurance_provider': None  # Removed field
                }

                progress_bar.progress(50)

                progress_bar.progress(75)

                # Process and save the accident report (simplified parameters)
                accident_id, result_text, processed_image = process_and_save_accident_report(
                    license_number=license_number.upper().strip(),
                    image_file=uploaded_image,
                    description=accident_description,
                    location=location,
                    weather_conditions=None,  # Removed field
                    road_conditions=None,  # Removed field
                    vehicle_info=vehicle_info,
                    other_vehicles=None,  # Removed field
                    witnesses=None,  # Removed field
                    police_report_number=None,  # Removed field
                    submitted_by="ParthSharma901"
                )

                progress_bar.progress(100)
                time.sleep(0.5)

                if accident_id:
                    # Store results in session state
                    st.session_state.form_submitted = True
                    st.session_state.accident_id = accident_id
                    st.session_state.result = result_text
                    st.session_state.uploaded_image = processed_image
                    st.session_state.license_number = license_number.upper().strip()

                    st.markdown(f"""
                    <div class="success-message">
                        <span class="status-indicator status-success"></span>
                        <strong>Accident report processed and saved successfully!</strong><br>
                        Report ID: <strong>{accident_id}</strong><br>
                        License Plate: <strong>{license_number.upper()}</strong>
                    </div>
                    """, unsafe_allow_html=True)

                    time.sleep(1)
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="error-message">
                        <span class="status-indicator status-error"></span>
                        <strong>Error:</strong> Failed to save accident report. Please try again.
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


def show_report_results():
    """Display the accident report results with enhanced framing and formatting"""
    st.markdown('<h1 class="main-header">📊 Analysis Results</h1>', unsafe_allow_html=True)

    # Display success message
    if st.session_state.accident_id:
        st.markdown(f"""
        <div class="success-message">
            <span class="status-indicator status-success"></span>
            <strong>Report Successfully Saved to Database!</strong><br>
            Accident ID: <strong>{st.session_state.accident_id}</strong> | 
            License: <strong>{st.session_state.license_number}</strong>
        </div>
        """, unsafe_allow_html=True)

    # Display analysis results with enhanced framing
    if st.session_state.result:
        formatted_sections = format_analysis_report(st.session_state.result)

        st.markdown('<div class="analysis-results">', unsafe_allow_html=True)

        # Header
        st.markdown('''
        <div class="analysis-header">
            <h3>🔍 Damage Analysis Report</h3>
        </div>
        ''', unsafe_allow_html=True)

        # Content
        st.markdown('<div class="analysis-content">', unsafe_allow_html=True)

        for section in formatted_sections:
            st.markdown(f'''
            <div class="report-section">
                <div class="section-title">
                    {section["icon"]} {section["title"]}
                </div>
                <div class="report-text">{section["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # Close analysis-content
        st.markdown('</div>', unsafe_allow_html=True)  # Close analysis-results

    else:
        st.markdown("""
        <div class="warning-message">
            <span class="status-indicator status-warning"></span>
            No analysis results available
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Show processed/edited image after results
    if st.session_state.uploaded_image:
        st.subheader("📷 Processed Image")
        st.image(
            st.session_state.uploaded_image,
            caption="Analyzed Image (scaled for display)",
            use_column_width=False,
            width=400
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


# [Keep all other functions the same...]

def show_accident_history():
    """Show accident history for a specific vehicle"""
    st.header("📋 Vehicle Accident History")

    license_search = st.text_input("Enter License Plate Number", placeholder="e.g., ABC-1234")

    if license_search:
        license_search = license_search.upper().strip()

        with st.spinner("Retrieving accident history..."):
            history = get_vehicle_accident_history(license_search)

            if history['vehicle_info']:
                # Display vehicle information
                st.subheader(f"🚗 Vehicle Information - {license_search}")
                vehicle = history['vehicle_info']

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Owner", vehicle.get('owner_name', 'N/A'))
                    st.metric("Make", vehicle.get('vehicle_make', 'N/A'))
                with col2:
                    st.metric("Model", vehicle.get('vehicle_model', 'N/A'))
                    st.metric("Year", vehicle.get('vehicle_year', 'N/A'))
                with col3:
                    st.metric("Color", vehicle.get('vehicle_color', 'N/A'))

                # Display statistics
                st.subheader("📊 Accident Statistics")
                stats = history['statistics']

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Accidents", stats.get('total_accidents', 0))
                with col2:
                    st.metric("Minor", stats.get('minor_accidents', 0))
                with col3:
                    st.metric("Moderate", stats.get('moderate_accidents', 0))
                with col4:
                    st.metric("Severe", stats.get('severe_accidents', 0))

                # Display accident list
                if history['accidents']:
                    st.subheader("🗂️ Accident Records")

                    for i, accident in enumerate(history['accidents']):
                        # Safely access accident data
                        accident_id = accident[0] if len(accident) > 0 else 'N/A'
                        license_num = accident[1] if len(accident) > 1 else 'N/A'
                        accident_date = accident[2] if len(accident) > 2 else 'N/A'
                        description = accident[3] if len(accident) > 3 else 'N/A'
                        location = accident[4] if len(accident) > 4 else 'N/A'
                        severity = accident[7] if len(accident) > 7 else 'N/A'
                        estimated_cost = accident[10] if len(accident) > 10 else 'N/A'
                        repair_time = accident[11] if len(accident) > 11 else 'N/A'
                        accident_type = accident[12] if len(accident) > 12 else 'N/A'
                        status = accident[20] if len(accident) > 20 else 'Open'
                        submitted_by = accident[21] if len(accident) > 21 else 'N/A'

                        with st.expander(f"Accident #{accident_id} - {str(accident_date)[:19]} - Severity: {severity}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write(f"**Description:** {description}")
                                st.write(f"**Location:** {location}")
                                st.write(f"**Submitted by:** {submitted_by}")

                            with col2:
                                st.write(f"**Estimated Cost:** {estimated_cost}")
                                st.write(f"**Repair Time:** {repair_time}")
                                st.write(f"**Accident Type:** {accident_type}")
                                st.write(f"**Status:** {status}")
                                st.write(f"**Date:** {str(accident_date)[:19]}")
                else:
                    st.info("No accidents found for this vehicle.")
            else:
                st.warning(f"No vehicle found with license plate: {license_search}")


def show_search_page():
    """Show search functionality"""
    st.header("🔍 Search Accident Reports")

    search_term = st.text_input("Search Term", placeholder="Enter search term...")
    search_type = st.selectbox("Search By", ["description", "location", "license", "severity"])

    if st.button("Search") and search_term:
        with st.spinner("Searching..."):
            results = search_accidents_by_criteria(search_term, search_type)

            if results:
                st.success(f"Found {len(results)} results")

                for result in results:
                    # Safely access result data
                    accident_id = result[0] if len(result) > 0 else 'N/A'
                    license_num = result[1] if len(result) > 1 else 'N/A'
                    accident_date = result[2] if len(result) > 2 else 'N/A'
                    description = result[3] if len(result) > 3 else 'N/A'
                    location = result[4] if len(result) > 4 else 'N/A'
                    severity = result[7] if len(result) > 7 else 'N/A'
                    estimated_cost = result[10] if len(result) > 10 else 'N/A'

                    # Vehicle info (from JOIN)
                    owner_name = result[-6] if len(result) > 6 else 'N/A'
                    vehicle_make = result[-5] if len(result) > 5 else 'N/A'
                    vehicle_model = result[-4] if len(result) > 4 else 'N/A'

                    with st.expander(f"Accident #{accident_id} - {license_num} - {str(accident_date)[:19]}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**License:** {license_num}")
                            st.write(f"**Description:** {description}")
                            st.write(f"**Location:** {location}")
                            st.write(f"**Severity:** {severity}")

                        with col2:
                            st.write(f"**Owner:** {owner_name}")
                            st.write(f"**Vehicle:** {vehicle_make} {vehicle_model}")
                            st.write(f"**Estimated Cost:** {estimated_cost}")
                            st.write(f"**Date:** {str(accident_date)[:19]}")
            else:
                st.info("No results found.")


def show_statistics_page():
    """Show overall statistics"""
    st.header("📈 System Statistics")

    stats = db.get_accident_statistics()

    if stats and stats.get('total_accidents', 0) > 0:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Accidents", stats.get('total_accidents', 0))
            st.metric("Open Cases", stats.get('open_cases', 0))

        with col2:
            st.metric("Total Vehicles", stats.get('total_vehicles', 0))
            st.metric("Closed Cases", stats.get('closed_cases', 0))

        with col3:
            st.metric("Minor Accidents", stats.get('minor_accidents', 0))
            st.metric("Moderate Accidents", stats.get('moderate_accidents', 0))

        with col4:
            st.metric("Severe Accidents", stats.get('severe_accidents', 0))
            completion_rate = (stats.get('closed_cases', 0) / max(stats.get('total_accidents', 1), 1)) * 100
            st.metric("Completion Rate", f"{completion_rate:.1f}%")

        # Recent activity
        st.subheader("📊 Quick Overview")
        st.info(
            f"System is tracking {stats.get('total_vehicles', 0)} vehicles with {stats.get('total_accidents', 0)} total accident records.")
    else:
        st.info("No statistics available yet. Submit your first accident report to see data here.")


def reset_session_state():
    """Reset all session state variables"""
    st.session_state.report_submitted = False
    st.session_state.result = None
    st.session_state.uploaded_image = None
    st.session_state.accident_description = ""
    st.session_state.processing = False
    st.session_state.form_errors = []
    st.session_state.form_submitted = False
    st.session_state.accident_id = None
    st.session_state.license_number = ""


if __name__ == "__main__":
    # Footer with enhanced styling
    main()

    st.divider()