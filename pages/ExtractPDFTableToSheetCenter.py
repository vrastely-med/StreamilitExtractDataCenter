import streamlit as st
import pandas as pd
import tabula
import io

st.title("PDF Table Extractor")

st.write("""
This app extracts tables from all PDF files you upload and saves them into a single Excel file.

- For each PDF file, all tables will be saved in a single sheet.
- Each sheet is named after the PDF file.

**Note:** Ensure that `tabula-py` is installed and that Java is available on your system.
""")

# Upload multiple PDF files
uploaded_files = st.file_uploader(
    "Upload PDF files:",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    for uploaded_file in uploaded_files:
        try:
            st.write(f"Processing file: {uploaded_file.name}")

            # Read tables from PDF
            dfs = tabula.read_pdf(uploaded_file, pages='all', multiple_tables=True)

            if dfs:
                # Concatenate all tables from the PDF into a single DataFrame
                combined_df = pd.DataFrame()
                for idx, df in enumerate(dfs):
                    df['Table_Number'] = idx + 1  # Add a column to indicate table number
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

                # Write the DataFrame to a sheet named after the PDF file
                # Sheet names can't be longer than 31 characters
                sheet_name = uploaded_file.name[:31]
                combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
                st.success(f"Extracted tables from {uploaded_file.name}")
            else:
                st.warning(f"No tables found in {uploaded_file.name}")

        except Exception as e:
            st.error(f"An error occurred while processing {uploaded_file.name}: {e}")

    # Save the Excel file
    writer.save()
    processed_data = output.getvalue()

    # Offer the Excel file for download
    st.download_button(
        label="Download Excel file with extracted tables",
        data=processed_data,
        file_name="extracted_tables.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please upload PDF files to extract tables.")
