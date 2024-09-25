import streamlit as st
import os
import fitz  # PyMuPDF
import io
from pathlib import Path
from PIL import Image
import zipfile

st.title("PDF Image Extractor")

st.write("""
This app extracts all images from selected PDF files and saves them into new subfolders.

- **Upload** one or more PDF files.
- The app **extracts all images** from each PDF.
- Images are saved in a **new subfolder** named after the PDF file.
- Each image file is named with the **PDF file name**, **page number**, and **image number**.

**Note:** Ensure that `PyMuPDF` and `Pillow` are installed in your Python environment.
""")

# Function to extract images from a PDF file
def extract_images_from_pdf(pdf_file, output_dir):
    pdf_name = os.path.splitext(pdf_file.name)[0]
    pdf_data = pdf_file.read()
    pdf_stream = io.BytesIO(pdf_data)
    pdf_doc = fitz.open(stream=pdf_stream, filetype='pdf')
    total_pages = len(pdf_doc)
    
    # Create a subfolder for the images
    images_folder_name = pdf_name.replace(' ', '_')
    images_folder_path = os.path.join(output_dir, images_folder_name)
    if not os.path.exists(images_folder_path):
        os.makedirs(images_folder_path)
    
    image_count = 0
    for page_index in range(total_pages):
        page = pdf_doc.load_page(page_index)
        image_list = page.get_images(full=True)
        if image_list:
            for img_index, img in enumerate(image_list, start=1):
                xref = img[0]
                base_image = pdf_doc.extract_image(xref)
                image_bytes = base_image['image']
                image_ext = base_image['ext']
                image = Image.open(io.BytesIO(image_bytes))
                # Create image file name
                image_filename = f"{pdf_name}_page{page_index+1}_img{img_index}.{image_ext}"
                image_filepath = os.path.join(images_folder_path, image_filename)
                # Save the image
                image.save(image_filepath)
                image_count += 1
    return images_folder_path, image_count

# Main app
uploaded_files = st.file_uploader(
    "Upload PDF files to extract images:",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    # Create a temporary directory to store images
    output_dir = "extracted_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    total_images_extracted = 0
    folders_created = []
    
    for pdf_file in uploaded_files:
        st.write(f"Processing file: {pdf_file.name}")
        try:
            images_folder_path, image_count = extract_images_from_pdf(pdf_file, output_dir)
            total_images_extracted += image_count
            folders_created.append(images_folder_path)
            st.success(f"Extracted {image_count} images from {pdf_file.name}")
        except Exception as e:
            st.error(f"An error occurred while processing {pdf_file.name}: {e}")
    
    if total_images_extracted > 0:
        # Create a zip file of the output directory
        zip_filename = "extracted_images.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in folders_created:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)
        
        # Provide download link for the zip file
        with open(zip_path, "rb") as f:
            bytes_data = f.read()
            st.download_button(
                label="Download All Extracted Images as ZIP",
                data=bytes_data,
                file_name=zip_filename,
                mime="application/zip"
            )
    else:
        st.warning("No images were extracted from the uploaded PDF files.")
else:
    st.info("Please upload PDF files to extract images.")
