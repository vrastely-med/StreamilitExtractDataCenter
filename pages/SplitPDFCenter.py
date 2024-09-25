import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io

st.title("PDF Splitter")

st.write("""
This app splits a selected PDF file into one or more PDF files based on the page ranges you specify.

- Upload a PDF file.
- Choose how many parts you want to split the PDF into.
- Specify the page ranges for each part.
- Download the split PDF files.

**Note:** Ensure that `PyPDF2` is installed in your Python environment.
""")

# Upload a single PDF file
uploaded_file = st.file_uploader(
    "Upload a PDF file to split:",
    type=["pdf"]
)

if uploaded_file:
    # Read the uploaded PDF file
    pdf_reader = PdfReader(uploaded_file)
    total_pages = len(pdf_reader.pages)
    st.write(f"The uploaded PDF has **{total_pages}** pages.")

    # Input: Number of parts to split into
    num_parts = st.number_input(
        "Enter the number of parts you want to split the PDF into:",
        min_value=1,
        max_value=total_pages,
        step=1,
        value=2
    )

    if num_parts:
        # Dynamic input for page ranges
        page_ranges = []
        st.write("Specify the page ranges for each part (e.g., 1-3, 4, 5-7):")
        for i in range(num_parts):
            page_range = st.text_input(
                f"Page range for Part {i+1}:", key=f"page_range_{i}"
            )
            page_ranges.append(page_range)

        # Button to trigger the split
        if st.button("Split PDF"):
            split_success = True
            split_files = []
            try:
                for idx, page_range in enumerate(page_ranges):
                    if page_range:
                        # Parse the page range
                        pages_to_extract = []
                        ranges = [r.strip() for r in page_range.split(',')]
                        for r in ranges:
                            if '-' in r:
                                start, end = r.split('-')
                                start = int(start)
                                end = int(end)
                                pages_to_extract.extend(range(start, end + 1))
                            else:
                                pages_to_extract.append(int(r))
                        # Adjust page numbers (PyPDF2 uses zero-based indexing)
                        pages_to_extract = [p - 1 for p in pages_to_extract]

                        # Create a PdfWriter for each split part
                        pdf_writer = PdfWriter()
                        for page_num in pages_to_extract:
                            if 0 <= page_num < total_pages:
                                pdf_writer.add_page(pdf_reader.pages[page_num])
                            else:
                                st.error(f"Page number {page_num + 1} is out of range.")
                                split_success = False
                                break

                        if split_success:
                            # Save the split PDF to a BytesIO object
                            split_pdf = io.BytesIO()
                            pdf_writer.write(split_pdf)
                            split_pdf.seek(0)
                            split_files.append((f"Part_{idx+1}.pdf", split_pdf))
                    else:
                        st.error(f"Please specify a page range for Part {idx+1}.")
                        split_success = False
                        break

                if split_success and split_files:
                    st.success("PDF file split successfully!")
                    for filename, pdf_file in split_files:
                        st.download_button(
                            label=f"Download {filename}",
                            data=pdf_file,
                            file_name=filename,
                            mime="application/pdf"
                        )
            except Exception as e:
                st.error(f"An error occurred while splitting the PDF: {e}")
else:
    st.info("Please upload a PDF file to split.")
