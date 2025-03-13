import streamlit as st
import requests
import json
from PIL import Image
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Elegance - Design Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for elegant styling
st.markdown("""
<style>
    /* Main styles */
    .main {
        background-color: #fafafa;
    }
    
    /* Custom title styling */
    .title-container {
        background: linear-gradient(90deg, #f8f4e6, #f1e8cb);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    /* Soft gold accents */
    .gold-accent {
        color: #c6a96c;
        font-weight: 500;
    }
    
    /* Cards for sections */
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #c6a96c;
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #b09252;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background-color: #c6a96c !important;
    }
    
    /* Gallery styling */
    .image-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: center;
    }
    
    .image-card {
        border: 1px solid #f0f0f0;
        border-radius: 5px;
        padding: 10px;
        transition: transform 0.3s;
    }
    
    .image-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* Reduce sidebar width */
    [data-testid=stSidebar] {
        background-color: #f8f4e6;
    }
</style>
""", unsafe_allow_html=True)

# API endpoints
API_URL = "http://localhost:8000"  # Update with your actual FastAPI server URL

# Helper functions
def display_images(images_data):
    if not images_data:
        st.error("No images to display")
        return
    
    try:
        # Parse the image URLs from the response
        image_urls = []
        
        # Check what kind of structure we got
        if isinstance(images_data, dict):
            # If output is directly in the response
            if "output" in images_data:
                output = images_data["output"]
                
                # If output is a list, use it directly
                if isinstance(output, list):
                    image_urls = output
                # If output is a dict with 'images' key
                elif isinstance(output, dict) and "images" in output:
                    image_urls = output["images"]
                # If output is a dict with 'image' key
                elif isinstance(output, dict) and "image" in output:
                    image_urls = [output["image"]]
        
        # If we couldn't find images, show the raw data
        if not image_urls:
            st.warning("Couldn't automatically extract image URLs from the response:")
            st.json(images_data)
            return
        
        # Display the images
        cols = st.columns(len(image_urls))
        for i, (col, img_url) in enumerate(zip(cols, image_urls)):
            if img_url:
                col.image(img_url, use_column_width=True)
                col.download_button(
                    label=f"Download Image {i+1}",
                    data=requests.get(img_url).content,
                    file_name=f"design_{i+1}.png",
                    mime="image/png"
                )
    except Exception as e:
        st.error(f"Error displaying images: {e}")
        st.json(images_data)
        
# Sidebar - App Navigation
with st.sidebar:
    st.title("✨ Elegance Studio")
    st.markdown("### Design Tools")
    selected_tool = st.radio(
        "Select Tool",
        ["Watch Generator", "Background Changer", "Model Pose Generator"]
    )
    
    st.markdown("---")
    st.markdown("### Recent Designs")
    # This could display thumbnails of recent designs
    # Placeholder for now
    st.image("https://placehold.co/100x100/f8f4e6/c6a96c?text=Recent", width=100)
    st.image("https://placehold.co/100x100/f8f4e6/c6a96c?text=Designs", width=100)
    
    st.markdown("---")
    st.markdown("<p class='gold-accent'>Elegance Studio v1.0</p>", unsafe_allow_html=True)

# Main content area
if selected_tool == "Watch Generator":
    st.markdown("<div class='title-container'><h1>Watch Design Studio</h1><p>Create stunning watch visualizations with AI assistance</p></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        # Input form
        prompt = st.text_area(
            "Design Description",
            "Hann_timeless of rectangular shape with golden wristwatch bracelet placed on a marble table",
            help="Describe the watch design and setting you want to generate"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            num_images = st.slider("Number of Variations", min_value=1, max_value=4, value=2)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            generate_button = st.button("Generate Designs", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    

# Inside your Streamlit app, replace the generate_button logic with this:
if generate_button:
    with st.spinner("Submitting image generation request..."):
        try:
            response = requests.post(
                f"{API_URL}/generate-image",
                json={"prompt": prompt, "number_of_images": num_images}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if the job is in queue
                if "status" in data and data["status"] == "IN_QUEUE":
                    job_id = data.get("id", "unknown")
                    st.info(f"Design generation is queued. Job ID: {job_id}")
                    st.json(data)
                else:
                    # Direct response with results
                    st.success("Designs generated successfully!")
                    st.markdown("<div class='card'><h3>Generated Designs</h3>", unsafe_allow_html=True)
                    display_images(data)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {response.status_code}")
                st.json(response.json())
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
elif selected_tool == "Background Changer":
    st.markdown("<div class='title-container'><h1>Background Studio</h1><p>Change or enhance the background of your product images</p></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
                # Convert to base64 for API
                image_bytes = uploaded_file.getvalue()
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                image_url = f"data:image/{uploaded_file.type.split('/')[1]};base64,{image_b64}"
        
        with col2:
            background_prompt = st.text_area(
                "Describe New Background",
                "Luxury marble surface with soft side lighting",
                help="Describe the background setting you want"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            change_bg_button = st.button("Change Background", 
                                         use_container_width=True,
                                         disabled=not uploaded_file)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Results area
    if uploaded_file and change_bg_button:
        with st.spinner("Changing background..."):
            try:
                response = requests.post(
                    f"{API_URL}/change-background",
                    json={"prompt": background_prompt, "input_image": image_url}
                )
                if response.status_code == 200:
                    st.success("Background changed successfully!")
                    st.markdown("<div class='card'><h3>Result</h3>", unsafe_allow_html=True)
                    display_images(response.json())
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(f"Error: {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"Error connecting to API: {e}")

elif selected_tool == "Model Pose Generator":
    st.markdown("<div class='title-container'><h1>Model Visualization Studio</h1><p>Create realistic model images wearing your jewelry designs</p></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            uploaded_file = st.file_uploader("Upload Jewelry Image", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Jewelry", use_column_width=True)
                # Convert to base64 for API
                image_bytes = uploaded_file.getvalue()
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                image_url = f"data:image/{uploaded_file.type.split('/')[1]};base64,{image_b64}"
        
        with col2:
            model_description = st.text_area(
                "Describe Model",
                "A middle-aged elegant woman with stylish outfit",
                help="Describe the model who will wear your jewelry"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            generate_model_button = st.button("Generate Model Image", 
                                            use_container_width=True,
                                            disabled=not uploaded_file)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Results area
    if uploaded_file and generate_model_button:
        with st.spinner("Generating model image..."):
            try:
                response = requests.post(
                    f"{API_URL}/generate-pose",
                    json={"prompt": model_description, "input_image": image_url}
                )
                if response.status_code == 200:
                    st.success("Model image generated successfully!")
                    st.markdown("<div class='card'><h3>Result</h3>", unsafe_allow_html=True)
                    display_images(response.json())
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(f"Error: {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"Error connecting to API: {e}")

# Footer
st.markdown("---")
st.markdown("<center>© 2025 Elegance Design Studio</center>", unsafe_allow_html=True)