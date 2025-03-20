import streamlit as st
import requests
from PIL import Image
import io
import base64
import os
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Mosaic Art Image Processor",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        color: white;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .upload-section {
        padding: 2rem;
        border-radius: 0.7rem;
        background-color: black;
        border: 2px dashed #dee2e6;
        margin-bottom: 2rem;
        text: white;    
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: black;
        border: 1px solid #90caf9;
        margin-bottom: 1rem;
    
    }
    .download-btn {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    .image-container {
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: white;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://13.61.17.106:8000/process-image/"

# App title
st.markdown("<div class='main-header'>Mosaic Art Image Processor</div>", unsafe_allow_html=True)

# Create a function to get a download link for an image
def get_image_download_link(img, filename, text):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:file/png;base64,{img_str}" download="{filename}" class="download-btn">{text}</a>'
    return href

# Create a function for SVG download
def get_svg_download_link(svg_data, filename, text):
    b64 = base64.b64encode(svg_data.encode()).decode()
    href = f'<a href="data:image/svg+xml;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'
    return href

# Create a session state to track if processing is completed
if 'processed' not in st.session_state:
    st.session_state.processed = False
    st.session_state.original_image = None
    st.session_state.processed_image = None
    st.session_state.svg_data = None

# Upload section
st.markdown("<div class='sub-header'>Upload Image</div>", unsafe_allow_html=True)
st.markdown("<div class='info-box'>Upload an image to create mosaic art. Supported formats: JPG, PNG, JPEG.</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    st.markdown("</div>", unsafe_allow_html=True)

# Process the uploaded image
if uploaded_file is not None:
    # Display original image
    original_image = Image.open(uploaded_file)
    
    # Save original image to session state
    st.session_state.original_image = original_image
    
    # Prepare the file for the API
    files = {'file': ('image.jpg', uploaded_file.getvalue(), 'image/jpeg')}
    
    # Show a spinner while processing
    with st.spinner('Processing image... Please wait.'):
        try:
            # Send request to the API
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                # Process successful, display the result
                processed_image = Image.open(io.BytesIO(response.content))
                
                # Save processed image to session state
                st.session_state.processed_image = processed_image
                st.session_state.processed = True
                
                # Try to get SVG version
                try:
                    svg_response = requests.post(f"{API_URL}?format=svg", files=files)
                    if svg_response.status_code == 200:
                        st.session_state.svg_data = svg_response.text
                except Exception as e:
                    st.error(f"Could not get SVG version: {e}")
                    st.session_state.svg_data = None
                
            else:
                st.error(f"Error: API returned status code {response.status_code}")
                st.session_state.processed = False
        except Exception as e:
            st.error(f"Error connecting to the API: {e}")
            st.session_state.processed = False

# Display results if processing is complete
if st.session_state.processed:
    st.markdown("<div class='sub-header'>Results</div>", unsafe_allow_html=True)
    
    # Display images side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='image-container'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Original Image</h3>", unsafe_allow_html=True)
        st.image(st.session_state.original_image, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='image-container'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Processed Image</h3>", unsafe_allow_html=True)
        st.image(st.session_state.processed_image, use_column_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Download section
    st.markdown("<div class='sub-header'>Download Options</div>", unsafe_allow_html=True)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # PNG Download
        png_filename = f"mosaic_art_{timestamp}.png"
        st.markdown(get_image_download_link(st.session_state.processed_image, png_filename, "Download as PNG"), unsafe_allow_html=True)
    
    with col2:
        # JPG Download
        jpg_filename = f"mosaic_art_{timestamp}.jpg"
        st.markdown(get_image_download_link(st.session_state.processed_image, jpg_filename, "Download as JPG"), unsafe_allow_html=True)
    
    with col3:
        # SVG Download (if available)
        if st.session_state.svg_data:
            svg_filename = f"mosaic_art_{timestamp}.svg"
            st.markdown(get_svg_download_link(st.session_state.svg_data, svg_filename, "Download as SVG"), unsafe_allow_html=True)
        else:
            st.button("SVG not available", disabled=True)

# Add information about the mosaic art system
st.markdown("---")
