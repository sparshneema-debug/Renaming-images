import streamlit as st
import pandas as pd
from io import BytesIO

# --- Template Section ---
st.header("Download CSV or Excel Template")
template_df = pd.DataFrame([["oldname.jpg", "newname.jpg"]], columns=["oldname", "newname"])

# CSV:
csv_bytes = template_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download CSV Template",
    data=csv_bytes,
    file_name="template.csv",
    mime="text/csv"
)

# Excel:
excel_buffer = BytesIO()
template_df.to_excel(excel_buffer, index=False, engine="openpyxl")
excel_bytes = excel_buffer.getvalue()
st.download_button(
    "Download Excel Template",
    data=excel_bytes,
    file_name="template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
