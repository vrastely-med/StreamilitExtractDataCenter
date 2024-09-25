import streamlit as st
import pandas as pd
import tabula.io
from tabula.io import read_pdf
import os
import tempfile
from io import BytesIO

from pathlib import Path
from docxtpl import DocxTemplate
from tqdm import tqdm
import shutil
import send2trash

st.title("Extract Tables from PDF Files")

# Initialize session state variables if they don't exist
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'excel_data' not in st.session_state:
    st.session_state.excel_data = None

# Add a button to clear all previous inputs
if st.button("Clear All"):
    st.session_state.uploader_key += 1  # Increment to reset the uploader
    st.session_state.excel_data = None  # Clear the Excel data

# Allow the user to upload multiple PDF files
uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.uploader_key}"
)

if uploaded_files:
    with st.spinner("Processing PDF files..."):
        # A dictionary to store DataFrames and sheet names
        excel_sheets = {}
        for uploaded_file in uploaded_files:
            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            # Read tables from the PDF file using tabula
            try:
                dfs = tabula.read_pdf(temp_file_path, pages='all', multiple_tables=True)
                if dfs:
                    # For each table extracted, add it to the dictionary
                    for idx, df in enumerate(dfs):
                        # Clean up the sheet name to be Excel-compatible
                        base_name = os.path.splitext(uploaded_file.name)[0]
                        sheet_name = f"{base_name[:20]}_{idx}"
                        sheet_name = sheet_name.replace(':', '_').replace('/', '_').replace('\\', '_')
                        excel_sheets[sheet_name] = df
                else:
                    st.warning(f"No tables found in {uploaded_file.name}")
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")
            finally:
                # Delete the temporary file
                os.remove(temp_file_path)

        if excel_sheets:
            # Save all DataFrames to an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for sheet_name, df in excel_sheets.items():
                    # Limit sheet_name to 31 characters for Excel compatibility
                    sheet_name = sheet_name[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                writer.save()
                st.session_state.excel_data = output.getvalue()

        else:
            st.info("No tables extracted from the uploaded PDF files.")

# Provide a download button if Excel data is available
if st.session_state.excel_data:
    st.download_button(
        label="Download Extracted Tables as Excel",
        data=st.session_state.excel_data,
        file_name="extracted_tables.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
