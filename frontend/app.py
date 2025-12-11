import streamlit as st
import requests
from PIL import Image
import io
import time

# Configure page
st.set_page_config(
    page_title="MediSafe - AI Medical Prescription Verification",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for healthcare-focused design

st.markdown("""
<style>
    /* Import healthcare-friendly fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styling */
    .main {
        padding: 2rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
        color: black; /* Added font color */
    }
    
    /* Custom styling for better readability */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(135deg, #f8faff 0%, #e8f4f8 100%);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: grey;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        color: #000000; /* Added font color */
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #000080;  /* Changed to black */
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        color: white;  /* Changed to white */
        font-weight: 400;
    }
    
    /* Section styling */
    .section-container {
        background: black;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        border: 1px solid #e5f3ff;
        text-align: center;
        color: #ffffff; /* Added font color */
        transition: transform 0.2s ease, box-shadow 0.3s ease;
    }

    

    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: white;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        justify-content: center;
    }

    /* Form styling */
    .stNumberInput label, .stSelectbox label, .stTextArea label, .stFileUploader label, .stTextInput label {
        font-size: 4rem !important;
        font-weight: 900 !important;
        color: #000000 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stNumberInput > div > div > input, .stTextInput > div > div > input {
        font-size: 1.2rem !important;
        padding: 1rem !important;
        border: 2px solid #d1d5db !important;
        border-radius: 12px !important;
        height: auto !important;
        background-color: white !important;
        color: #000000 !important;
    }
    
    .stSelectbox > div > div > select {
        font-size: 1.2rem !important;
        padding: 1rem !important;
        border: 2px solid #d1d5db !important;
        border-radius: 12px !important;
        color: #000000 !important;
    }
    
    .stTextArea > div > div > textarea {
        font-size: 1.1rem !important;
        padding: 1rem !important;
        border: 2px solid #d1d5db !important;
        border-radius: 12px !important;
        min-height: 120px !important;
        background-color: white !important;
        color: #000000 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%) !important;
        color: black !important;
        padding: 1rem 3rem !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 2rem 0 !important;
        
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(59, 130, 246, 0.4) !important;
        color: white !important;
    }
    
    /* File upload styling */
    .stFileUploader {
        border: 3px dashed #93c5fd !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        text-align: center !important;
        background: #f8faff !important;
        color: #000000 !important;
    }
    
    /* Alert styling */
    .success-alert {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border-left: 6px solid #22c55e;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #000000;
    }
    
    .warning-alert {
        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
        border-left: 6px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #000000;
    }
    
    .error-alert {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 6px solid #ef4444;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: #000000;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: black;
        padding: 1rem;
        border-radius: 12px;
        border: 2px solid #e5f3ff;
        color: #ffffff;
    }
    
    .stRadio label {
        color: #000000 !important;
        font-weight: 500;
    }
    
    /* Results styling */
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        border-left: 6px solid #3b82f6;
        color: #000000;
    }
    
    .confidence-score {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #000000;
    }
    
    .confidence-high { background: #dcfce7; color: #166534; }
    .confidence-medium { background: #fef3c7; color: #92400e; }
    .confidence-low { background: #fee2e2; color: #991b1b; }
    
    /* Expander styling */
    .streamlit-expanderContent {
    background: black !important;
    color: white !important;
    padding: 1rem !important;
    border-radius: 0 0 12px 12px !important;
    }

    .streamlit-expanderContent p, 
    .streamlit-expanderContent ul, 
    .streamlit-expanderContent ol, 
    .streamlit-expanderContent li {
        color: white !important;
    }
            
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-title { font-size: 2rem; }
        .section-container { padding: 1.5rem; }
    }
    
    /* Text area label styling */
    .stTextArea label {
        font-size: 1.3rem !important;
        color: #000000 !important;
    }
    
    /* Input placeholder styling */
    input::placeholder, textarea::placeholder {
        color: #6b7280 !important;
        font-size: 1.1rem !important;
    }
    
    /* AI Analysis block styling */
    .ai-analysis-block {
        background: black;
        padding: 0.8rem;
        border-radius: 16px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.3);
        margin-bottom: 1rem;
        border: 1px solid #e5f3ff;
        text-align: center;
        color: #ffffff; /* Added font color */
        transition: transform 0.2s ease, box-shadow 0.3s ease;
    }

    .ai-analysis-block:hover {
        box-shadow: 0 8px 32px rgba(94, 139, 126, 0.18);
        transform: translateY(-3px) scale(1.01);
        border-color: #5e8b7e;
    }

    /* Override Streamlit expander title colors */
.streamlit-expanderHeader {
    color: #fff !important;
    background: #000 !important;
    font-weight: bold !important;
    padding: 0.8rem 1rem !important;
    border-radius: 10px 10px 0 0 !important;
}

/* Image quality tips styling */
.image-tips {
    background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
    border: 2px solid #93c5fd;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    color: #000000;
}

.image-tips h4 {
    color: #1e40af;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.image-tips ul {
    text-align: left;
    margin: 0;
    padding-left: 1.5rem;
}

.image-tips li {
    margin-bottom: 0.5rem;
    color: #000000;
}
</style>
""", unsafe_allow_html=True)

# Helper functions
def extract_text_from_image_api(image_file):
    """Send image to backend for OCR processing"""
    try:
        files = {"image_file": (image_file.name, image_file.getvalue(), image_file.type)}
        response = requests.post("http://localhost:8000/extract-text", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                return result["extracted_text"], None
            else:
                return None, result.get("error", "Extraction failed")
        else:
            return None, f"API Error: {response.status_code}"
            
    except Exception as e:
        return None, f"Connection failed: {str(e)}"

def verify_prescription_api(prescription_data):
    """Send prescription to backend for verification"""
    API_URL = "http://localhost:8000/verify"
    try:
        response = requests.post(API_URL, json=prescription_data, timeout=30)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Connection failed: {str(e)}"

# Initialize session state
if 'analysis_step' not in st.session_state:
    st.session_state.analysis_step = 0
if 'prescription_analyzed' not in st.session_state:
    st.session_state.prescription_analyzed = False

# Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🏥 MediSafe</h1>
    <p class="main-subtitle">AI-Powered Prescription Verification & Drug Interaction Analysis</p>
</div>
""", unsafe_allow_html=True)



# Patient Information Section
st.markdown("""
<div class="section-container">
    <h2 class="section-title">👤 Patient Information</h2>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    age = st.number_input(
        "Patient Age (Required)*",
        min_value=0,
        max_value=120,
        value=25,
        help="Age is required for accurate dosage recommendations",
        key="age_input"
    )
    
    weight = st.number_input(
        "Patient Weight (kg)",
        min_value=0.0,
        value=75.0,
        step=0.1,
        help="Weight helps provide more accurate dosage calculations",
        key="weight_input"
    )

with col2:
    allergies = st.text_input(
        "Known Allergies",
        value="",
        placeholder="Enter Known Allergies",
        help="Include all known drug and food allergies",
        key="allergies_input"
    )
    
    conditions = st.text_input(
        "Medical Conditions",
        value="",
        placeholder="Enter Medical Conditions",
        help="Include all current medical conditions",
        key="conditions_input"
    )

# Prescription Input Section
st.markdown("""
<div class="section-container">
    <h2 class="section-title">💊 Prescription Input</h2>
</div>
""", unsafe_allow_html=True)

input_method = st.radio(
    "Choose input method:",
    ["📷 Upload Prescription Image", "✍️ Manual Text Entry"],
    horizontal=True,
    help="Select how you'd like to input the prescription information",
    key="input_method"
)

prescription_text = ""

if input_method == "📷 Upload Prescription Image":
    uploaded_file = st.file_uploader(
        "Upload Prescription Image",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Supported formats: JPG, PNG, BMP, TIFF. Ensure the image is clear and readable.",
        key="image_uploader"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Prescription", use_column_width=True)
        
        if st.button("🔍 Extract Text from Image", key="extract_btn"):
            with st.spinner("🔍 Extracting text from image using AI..."):
                extracted_text, error = extract_text_from_image_api(uploaded_file)
                if extracted_text:
                    st.session_state.extracted_text = extracted_text
                    st.markdown("""
                    <div class="success-alert">
                        <strong>✅ Text Extracted Successfully!</strong> Review and edit the extracted text below if needed.
                    </div>
                    """, unsafe_allow_html=True)
                    prescription_text = extracted_text
                else:
                    st.markdown(f"""
                    <div class="error-alert">
                        <strong>❌ Extraction Error:</strong> {error}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Show extracted text if available
        if 'extracted_text' in st.session_state:
            prescription_text = st.text_area(
                "✏️ Extracted Text (Review & Edit if Needed):",
                value=st.session_state.extracted_text,
                height=150,
                help="Review the extracted text and make any necessary corrections for accurate analysis",
                key="extracted_text_area"
            )
            
            st.info("🔍 **Please review the text above and correct any errors before analysis**")

else:
    prescription_text = st.text_area(
        "Enter Prescription Details",
        height=200,
        placeholder="Please enter:\n• Drug names and dosages\n• Frequency (e.g., twice daily)\n• Duration of treatment\n• Special instructions from your doctor",
        help="Be as detailed as possible for accurate analysis",
        key="manual_text_area"
    )

# Analysis Section
if age and age > 0:
    st.markdown("""
    <div class="ai-analysis-block">
        <h2 class="section-title">🔍 Analyse Prescription</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have prescription data
    has_prescription_data = prescription_text.strip()
    
    if has_prescription_data:
        if st.button("🚀 View Analysed Prescription", key="verify_btn"):
            # Prepare the request payload
            prescription_data = {
                "patient": {
                    "age": age,
                    "weight_kg": weight,
                    "allergies": [a.strip() for a in allergies.split(',') if a.strip()],
                    "conditions": [c.strip() for c in conditions.split(',') if c.strip()]
                },
                "drugs": [],  # Will be extracted from text by backend
                "text_input": prescription_text
            }
            
            # Simulate analysis process with progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            steps = [
                "Connecting to AI analysis engine...",
                "Extracting drug information...",
                "Analyzing drug interactions...",
                "Checking dosage recommendations...",
                "Generating safety report..."
            ]
            
            for i, step in enumerate(steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(steps))
                time.sleep(0.5)
            
            # Call the API
            with st.spinner("🧠 AI is analyzing your prescription for safety and interactions..."):
                result, error = verify_prescription_api(prescription_data)
            
            status_text.empty()
            progress_bar.empty()
            
            if error:
                st.markdown(f"""
                <div class="error-alert">
                    <strong>❌ Analysis Error:</strong> {error}<br>
                    <strong>💡 Tip:</strong> Make sure the backend API is running on http://localhost:8000
                </div>
                """, unsafe_allow_html=True)
            else:
                st.session_state.prescription_analyzed = True
                st.session_state.analysis_step = 3
                
                # Display Results
                st.markdown("""
                <div class="section-container">
                    <h2 class="section-title">📋 Analysis Results</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Overall Safety Status
                if result.get("is_safe"):
                    st.markdown("""
                    <div class="success-alert">
                        <strong>✅ Prescription Safety Status: SAFE</strong><br>
                        This prescription appears to be safe based on our comprehensive AI analysis.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-alert">
                        <strong>⚠️ Prescription Safety Status: REQUIRES REVIEW</strong><br>
                        Please consult with your healthcare provider about the concerns identified below.
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create columns for organized results
                col1, col2 = st.columns(2)
                
                with col1:
                    # Extracted Drugs
                    if result.get("extracted_drugs"):
                        st.markdown("""
                        <div class="result-card">
                            <h3 style="color: #000000; margin-bottom: 1rem;">💊 Identified Medications</h3>
                        """, unsafe_allow_html=True)
                        
                        for drug in result["extracted_drugs"]:
                            dosage = drug.get('dosage', 'N/A')
                            frequency = drug.get('frequency', 'N/A')
                            st.markdown(f"• **{drug['name']}** - {dosage}, {frequency}")
                        
                        st.markdown("""
                            <span class="confidence-score confidence-high">Extraction Confidence: High</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Drug Interactions
                    if result.get("interactions"):
                        st.markdown("""
                        <div class="result-card">
                            <h3 style="color: #000000; margin-bottom: 1rem;">⚠️ Drug Interactions</h3>
                        """, unsafe_allow_html=True)
                        
                        for interaction in result["interactions"]:
                            severity = interaction['severity'].title()
                            severity_color = "#ef4444" if severity == "High" else "#f59e0b" if severity == "Medium" else "#22c55e"
                            
                            st.markdown(f"""
                            <div style="padding: 1rem; background: #fef3c7; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid {severity_color}; color: #000000;">
                                <strong>{interaction['drug_a']} + {interaction['drug_b']}</strong><br>
                                <em>Severity: {severity}</em><br>
                                {interaction['description']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="result-card">
                            <h3 style="color: #000000; margin-bottom: 1rem;">✅ Drug Interactions</h3>
                            <p style="color: #000000; font-size: 1.1rem;">
                                <strong>No significant drug interactions detected.</strong><br>
                                The medications in this prescription are compatible with each other.
                            </p>
                            <span class="confidence-score confidence-high">Safety Score: Excellent</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    # Dosage Alerts
                    if result.get("dosage_alerts"):
                        st.markdown("""
                        <div class="result-card">
                            <h3 style="color: #000000; margin-bottom: 1rem;">💉 Dosage Recommendations</h3>
                        """, unsafe_allow_html=True)
                        
                        for alert in result["dosage_alerts"]:
                            recommended = alert.get('recommended_dosage', '')
                            alert_type = "info" if recommended else "warning"
                            
                            st.markdown(f"""
                            <div style="padding: 1rem; background: {'#e0f2fe' if alert_type == 'info' else '#fef3c7'}; border-radius: 8px; margin-bottom: 1rem; color: #000000;">
                                <strong>{alert['drug']}</strong><br>
                                {alert['issue']}<br>
                                {f"<em>Recommended: {recommended}</em>" if recommended else ""}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Alternative Medications
                    if result.get("alternatives"):
                        st.markdown("""
                        <div class="result-card">
                            <h3 style="color: #000000; margin-bottom: 1rem;">🔄 Alternative Medications</h3>
                        """, unsafe_allow_html=True)
                        
                        for alt in result["alternatives"]:
                            st.markdown(f"""
                            <div style="padding: 1rem; background: #f0f9ff; border-radius: 8px; margin-bottom: 1rem; color: #000000;">
                                <strong>Consider replacing {alt['original_drug']}</strong><br>
                                <strong>Alternative: {alt['suggested_drug']}</strong><br>
                                <em>Reason: {alt['reason']}</em>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Download report section
                st.markdown("""
                <div style="text-align: center; margin-top: 2rem;">
                    <div class="result-card">
                        <h3 style="color: #000000; margin-bottom: 1rem;">📄 Detailed Report</h3>
                        <p style="color: #000000; margin-bottom: 1rem;">
                            Get a comprehensive PDF report to share with your healthcare provider
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-alert">
            <strong style="color: #000000;">📝 Prescription Required:</strong> 
            <span style="color: #000000;">Please upload a prescription image or enter prescription details manually to proceed with analysis.</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="warning-alert">
        <strong style="color: #000000;">⚠️ Patient Information Required:</strong> 
        <span style="color: #000000;">Please enter the patient's age to proceed with analysis.</span>
    </div>
    """, unsafe_allow_html=True)

# Footer with important disclaimers
st.markdown("""
---
<div style="text-align: center; padding: 2rem; background: #f8faff; border-radius: 16px; margin-top: 2rem;">
    <h4 style="color: #000000; margin-bottom: 1rem;">⚠️ Important Medical Disclaimer</h4>
    <p style="color: #000000; font-size: 1rem; line-height: 1.6; max-width: 800px; margin: 0 auto;">
        This AI-powered tool is designed to assist healthcare professionals and patients by providing drug interaction analysis 
        and dosage recommendations. <strong>This tool is not a substitute for professional medical advice, diagnosis, or treatment.</strong> 
        Always consult with qualified healthcare professionals before making any changes to your medication regimen.
    </p>
    <div style="margin-top: 1.5rem; padding: 1rem; background: white; border-radius: 12px; display: inline-block;">
        <p style="color: #000000; font-weight: 600; margin: 0;">
            🔒 Your data is secure and confidential | 🤖 Powered by AI Technology
        </p>
    </div>
</div>
""", unsafe_allow_html=True)