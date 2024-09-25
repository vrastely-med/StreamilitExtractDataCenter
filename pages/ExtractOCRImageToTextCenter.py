import streamlit as st
import pytesseract
from PIL import Image

# Configure the path to the Tesseract executable
tesseract_path = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_path

st.title("OCR Text Extraction from Images")

# Initialize session state variables if they don't exist
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'total_text' not in st.session_state:
    st.session_state.total_text = ""

# Add a button to clear all previous inputs
if st.button("Clear All"):
    st.session_state.uploader_key += 1  # Increment to reset the uploader
    st.session_state.total_text = ""    # Clear the extracted text

# Allow the user to upload multiple image files
uploaded_files = st.file_uploader(
    "Upload Images (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    total_text = ""
    for uploaded_file in uploaded_files:
        # Open the image file
        image = Image.open(uploaded_file)

        # Convert the image to RGB (if necessary)
        image = image.convert("RGB")

        # Extract text from the image using Tesseract OCR
        text = pytesseract.image_to_string(image, lang="eng")

        # Append the extracted text
        total_text += f"Text from {uploaded_file.name}:\n{text}\n\n"

    # Store the total_text in session state
    st.session_state.total_text = total_text

    # Display the extracted text in a text area
    st.subheader("Extracted Text")
    st.text_area("OCR Output", st.session_state.total_text, height=300)

    # Provide a download button for the extracted text
    st.download_button(
        label="Download Extracted Text",
        data=st.session_state.total_text,
        file_name="extracted_text.txt",
        mime="text/plain",
    )
elif st.session_state.total_text:
    # Display the extracted text if it exists in session state
    st.subheader("Extracted Text")
    st.text_area("OCR Output", st.session_state.total_text, height=300)

    # Provide a download button for the extracted text
    st.download_button(
        label="Download Extracted Text",
        data=st.session_state.total_text,
        file_name="extracted_text.txt",
        mime="text/plain",
    )
else:
    st.info("Please upload image files to extract text.")
 