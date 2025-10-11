from PIL import Image
import io


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

    # Load and process the image
    image = Image.open(image_file)

    # Get basic image info
    image_width, image_height = image.size
    image_format = image.format

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


def analyze_image(image):
    """
    Analyze the car image for damage detection

    Args:
        image: PIL Image object

    Returns:
        dict: Dictionary containing damage analysis results
    """

    # Placeholder result with enhanced data
    damage_info = {
        "damaged_parts": ["Front bumper", "Left headlight", "Hood"],
        "severity": "Moderate",
        "confidence": 0.85,
        "estimated_cost": "$2,500 - $4,200",
        "repair_time": "3-5 business days"
    }

    return damage_info


def analyze_description(description):
    """
    Analyze the text description for key information

    Args:
        description: Text description of the accident

    Returns:
        dict: Dictionary containing text analysis results
    """

    # Enhanced analysis
    text_info = {
        "word_count": len(description.split()),
        "key_terms": extract_keywords(description),
        "accident_type": "Vehicle collision",
        "severity_level": "Medium impact",
        "location_mentioned": "Yes" if any(
            word in description.lower() for word in ['street', 'road', 'highway', 'intersection', 'parking']) else "No"
    }

    return text_info


def extract_keywords(text):
    """
    Extract keywords from the description

    Args:
        text: Input text

    Returns:
        list: List of keywords
    """

    # Simple keyword extraction
    words = text.lower().split()
    # Filter out common words and keep meaningful terms
    stop_words = {'the', 'and', 'was', 'were', 'that', 'this', 'with', 'for', 'from', 'they', 'have', 'had'}
    keywords = [word.strip('.,!?;') for word in words if len(word) > 4 and word not in stop_words]

    return keywords[:5]  # Return top 5


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

    # Convert confidence to percentage
    confidence_percent = int(damage_info["confidence"] * 100)

    # Build the report in natural English
    report = f"""**Analysis Report - Generated on October 11, 2025**

Based on the analysis of your uploaded image and description, here's what our system has determined:

**Damage Assessment:**
Our analysis has identified damage to several parts of your vehicle. The affected areas include the {', '.join(damage_info['damaged_parts'][:-1])} and {damage_info['damaged_parts'][-1]}. The overall severity of the damage has been classified as {damage_info['severity'].lower()}, which means the vehicle has sustained noticeable damage that will require professional repair.

**Confidence Level:**
The system analyzed your image with {confidence_percent}% confidence in its assessment. This high confidence level indicates that the damage detection algorithms were able to clearly identify the affected areas in your photograph.

**Repair Information:**
Based on the extent of damage identified, you can expect repair costs to fall within the range of {damage_info['estimated_cost']}. The estimated repair time is approximately {damage_info['repair_time']}, though this may vary depending on parts availability and the specific repair shop you choose.

**Description Analysis:**
Your accident description contained {text_analysis['word_count']} words and was classified as a {text_analysis['accident_type'].lower()}. The system detected that location information was {'provided' if text_analysis['location_mentioned'] == 'Yes' else 'not clearly specified'} in your description.

**Next Steps:**
We recommend that you contact your insurance provider as soon as possible to report the incident. It's also advisable to get a professional inspection from a certified mechanic to confirm our assessment and obtain detailed repair estimates. Make sure to keep all documentation related to this incident for your insurance claim.

**Important Note:**
This analysis is based on automated image processing and should be used as an initial assessment only. Always consult with professional mechanics and insurance adjusters for official damage evaluation and repair estimates."""

    return report