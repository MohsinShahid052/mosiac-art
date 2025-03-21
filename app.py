

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

# Custom CSS for better styling with automatic dark/light theme detection
st.markdown("""
<style>
    /* Base theme variables */
    :root {
      --background-color: #ffffff;
      --text-color: #222222;
      --header-color: #222222;
      --card-background: #ffffff;
      --card-border: #dee2e6;
      --info-background: #F8F9FA;
      --info-border: #90caf9;
      --upload-background: rgba(0, 0, 0, 0.8);
      --upload-border: #dee2e6;
      --upload-text: white;
      --button-background: #007bff;
      --button-text: white;
      --debug-background: #f1f1f1;
      --debug-text: #333333;
      --image-container-background: white;
      --image-container-text: black;
    }
    
    /* Dark theme override */
    @media (prefers-color-scheme: dark) {
      :root {
        --background-color: #121212;
        --text-color: #f1f1f1;
        --header-color: #ffffff;
        --card-background: #1e1e1e;
        --card-border: #444444;
        --info-background: #2d2d2d;
        --info-border: #3a6ea5;
        --upload-background: rgba(40, 40, 40, 0.9);
        --upload-border: #555555;
        --upload-text: #f1f1f1;
        --button-background: #0066cc;
        --button-text: white;
        --debug-background: #2d2d2d;
        --debug-text: #e0e0e0;
        --image-container-background: #2d2d2d;
        --image-container-text: #f1f1f1;
      }
    }
    
    /* Apply the variables to elements */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        color: var(--header-color);
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: var(--header-color);
    }
    .upload-section {
        padding: 2rem;
        border-radius: 0.7rem;
        background-color: var(--upload-background);
        border: 2px dashed var(--upload-border);
        margin-bottom: 2rem;
        color: var(--upload-text);
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: var(--info-background);
        border: 1px solid var(--info-border);
        margin-bottom: 1rem;
        color: var(--text-color);
    }
    .download-btn {
        width: 100%;
        margin-bottom: 0.5rem;
        background-color: var(--button-background);
        color: var(--button-text);
        text-decoration: none;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        display: block;
    }
    .image-container {
        border: 1px solid var(--card-border);
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: var(--image-container-background);
        color: var(--image-container-text);
    }
    .stButton button {
        width: 100%;
        background-color: var(--button-background);
        color: var(--button-text);
    }
    .debug-box {
        background-color: var(--debug-background);
        border: 1px solid var(--card-border);
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
        overflow-x: auto;
        color: var(--debug-text);
    }
    
    /* Override some Streamlit elements to match theme */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .stMarkdown, .stText {
        color: var(--text-color);
    }
    
    /* File uploader styling */
    .st-dd {
        background-color: var(--upload-background);
        color: var(--upload-text);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--card-background);
    }
</style>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://13.48.67.116:8000/process-image/"

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
    st.session_state.debug_info = None

# Debug section toggle
show_debug = st.sidebar.checkbox("Show Debug Information", value=False)

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
            
            # Store debug information
            debug_info = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_type": response.headers.get('content-type', 'Not specified'),
                "content_length": len(response.content),
                "first_bytes": ', '.join([f'{b:02x}' for b in response.content[:20]]) if response.content else 'Empty',
                "text_preview": response.text[:500] if hasattr(response, 'text') else 'No text content'
            }
            st.session_state.debug_info = debug_info
            
            if response.status_code == 200:
                try:
                    # Check if content type is an image
                    content_type = response.headers.get('content-type', '')
                    
                    if content_type and 'image' in content_type:
                        # It's an image, try to open it
                        processed_image = Image.open(io.BytesIO(response.content))
                        st.session_state.processed_image = processed_image
                        st.session_state.processed = True
                    else:
                        # Try to open it anyway as different image formats
                        try:
                            for format_ext in ['JPEG', 'PNG', 'GIF']:
                                try:
                                    processed_image = Image.open(io.BytesIO(response.content), formats=[format_ext])
                                    st.session_state.processed_image = processed_image
                                    st.session_state.processed = True
                                    break
                                except:
                                    continue
                            
                            # If we still don't have a processed image, raise an exception
                            if not st.session_state.processed:
                                raise Exception("Content is not recognized as an image")
                        except Exception as img_error:
                            st.error(f"Could not process response as an image: {img_error}")
                            st.session_state.processed = False
                    
                    # Try to get SVG version if processing succeeded
                    if st.session_state.processed:
                        try:
                            svg_response = requests.post(f"{API_URL}?format=svg", files=files)
                            if svg_response.status_code == 200:
                                st.session_state.svg_data = svg_response.text
                        except Exception as e:
                            if show_debug:
                                st.warning(f"Could not get SVG version: {e}")
                            st.session_state.svg_data = None
                
                except Exception as e:
                    st.error(f"Error processing the response: {e}")
                    st.session_state.processed = False
            else:
                st.error(f"Error: API returned status code {response.status_code}")
                st.session_state.processed = False
        except Exception as e:
            st.error(f"Error connecting to the API: {e}")
            st.session_state.processed = False

# Display debug information if requested
if show_debug and st.session_state.debug_info:
    st.markdown("<div class='sub-header'>Debug Information</div>", unsafe_allow_html=True)
    with st.expander("API Response Details", expanded=True):
        debug = st.session_state.debug_info
        st.markdown(f"""
        <div class='debug-box'>
        <p><strong>Status Code:</strong> {debug['status_code']}</p>
        <p><strong>Content Type:</strong> {debug['content_type']}</p>
        <p><strong>Content Length:</strong> {debug['content_length']} bytes</p>
        <p><strong>First Bytes (hex):</strong> {debug['first_bytes']}</p>
        <p><strong>Headers:</strong></p>
        <pre>{debug['headers']}</pre>
        <p><strong>Content Preview:</strong></p>
        <pre>{debug['text_preview']}</pre>
        </div>
        """, unsafe_allow_html=True)
        
        # Option to save raw response for offline analysis
        if st.button("Save Raw Response to File"):
            try:
                # Create a debug directory if it doesn't exist
                os.makedirs("debug", exist_ok=True)
                # Save the raw response
                with open(f"debug/response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin", "wb") as f:
                    f.write(response.content)
                st.success("Raw response saved to debug folder")
            except Exception as e:
                st.error(f"Error saving response: {e}")

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
