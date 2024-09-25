import streamlit as st
import pandas as pd
import pdfplumber
from docx import Document
from io import StringIO
import re

st.title("Extract and Merge Text from Files")

# Initialize session state variables if they don't exist
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'merged_text' not in st.session_state:
    st.session_state.merged_text = ""

# Add a button to clear all previous inputs
if st.button("Clear All"):
    st.session_state.uploader_key += 1  # Increment to reset the uploader
    st.session_state.merged_text = ""   # Clear the merged text

# Allow the user to upload multiple files
uploaded_files = st.file_uploader(
    "Upload files (TXT, DOCX, PDF)",
    type=["txt", "docx", "pdf"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}"
)

# Option to remove extra line breaks
remove_line_breaks = st.checkbox("Remove extra line breaks", value=False)

if uploaded_files:
    all_texts = []
    for uploaded_file in uploaded_files:
        file_type = uploaded_file.type
        file_name = uploaded_file.name.lower()

        try:
            if file_name.endswith('.txt'):
                # Read text from TXT file
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                text = stringio.read()
            elif file_name.endswith('.docx'):
                # Read text from DOCX file
                doc = Document(uploaded_file)
                text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            elif file_name.endswith('.pdf'):
                # Read text from PDF file
                text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + '\n'
            else:
                st.warning(f"Unsupported file type: {file_name}")
                continue

            # Optionally remove extra line breaks
            if remove_line_breaks:
                text = re.sub(r'\n+', '\n', text)

            all_texts.append(text)
            st.success(f"Text extracted from {uploaded_file.name}")

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    # Merge all texts into a single string
    if all_texts:
        merged_text = '\n\n'.join(all_texts)
        st.session_state.merged_text = merged_text

    else:
        st.info("No text extracted from the uploaded files.")

# Display the merged text in a text area
if st.session_state.merged_text:
    st.subheader("Merged Text")
    st.text_area("Merged Output", st.session_state.merged_text, height=300)

    # Provide a download button for the merged text
    st.download_button(
        label="Download Merged Text",
        data=st.session_state.merged_text,
        file_name="merged_text.txt",
        mime="text/plain",
    )


