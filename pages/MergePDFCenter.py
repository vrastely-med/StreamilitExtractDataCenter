import streamlit as st
from PyPDF2 import PdfMerger
import io

st.title("PDF Merger")

st.write("""
This app merges selected PDF files into a single PDF file.

- Upload multiple PDF files.
- Select the files you want to merge.
- Download the merged PDF file.

**Note:** Ensure that `PyPDF2` is installed in your Python environment.
""")

# Upload multiple PDF files
uploaded_files = st.file_uploader(
    "Upload PDF files to merge:",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    # Display the list of uploaded files with checkboxes for selection
    st.write("Select the PDF files you want to merge (in the desired order):")
    file_selection = []
    for file in uploaded_files:
        if st.checkbox(file.name, key=file.name):
            file_selection.append(file)
    
    if file_selection:
        # Button to trigger the merge
        if st.button("Merge PDFs"):
            merger = PdfMerger()
            try:
                for pdf_file in file_selection:
                    # Read the PDF file
                    pdf_bytes = pdf_file.read()
                    pdf_stream = io.BytesIO(pdf_bytes)
                    merger.append(pdf_stream)
                
                # Write out the merged PDF
                merged_pdf = io.BytesIO()
                merger.write(merged_pdf)
                merger.close()
                merged_pdf.seek(0)
                
                st.success("PDF files merged successfully!")
                
                # Provide download button
                st.download_button(
                    label="Download Merged PDF",
                    data=merged_pdf,
                    file_name="merged.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"An error occurred while merging PDFs: {e}")
    else:
        st.info("Please select at least two PDF files to merge.")
else:
    st.info("Please upload PDF files to merge.")
