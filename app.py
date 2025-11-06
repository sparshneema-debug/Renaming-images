import streamlit as st
import os
import csv
import zipfile
import tempfile
import pandas as pd

def find_file(root_dir, filename):
    for dirpath, _, files in os.walk(root_dir):
        if filename in files:
            return os.path.join(dirpath, filename)
    return None

def safe_rename(src, dst):
    """Safe rename: don't overwrite existing files."""
    if os.path.exists(dst):
        return False
    os.rename(src, dst)
    return True

st.title("Bulk File Renamer inside ZIP")
st.write("Upload a ZIP file and a CSV/Excel mapping (oldname,newname), and get back a renamed ZIP.")

# --- Downloadable Template Section ---
st.header("Download CSV or Excel Template")
template_df = pd.DataFrame([["oldname.jpg", "newname.jpg"]], columns=["oldname", "newname"])
csv_bytes = template_df.to_csv(index=False).encode("utf-8")
excel_bytes = template_df.to_excel(index=False, engine="openpyxl")
st.download_button("Download CSV Template", csv_bytes, "template.csv", "text/csv")
st.download_button("Download Excel Template", excel_bytes, "template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.header("Bulk Rename Tool")

zip_file = st.file_uploader("Upload ZIP file", type=["zip"])
map_file = st.file_uploader("Upload Mapping File (CSV or XLSX)", type=["csv", "xlsx"])

if zip_file and map_file:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract ZIP
            zip_path = os.path.join(temp_dir, "input.zip")
            with open(zip_path, "wb") as f:
                f.write(zip_file.read())
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            except zipfile.BadZipFile:
                st.error("Uploaded ZIP file is invalid or corrupted.")
                st.stop()

            # Read mapping
            rename_map = {}
            try:
                if map_file.name.lower().endswith(".csv"):
                    map_file.seek(0)
                    df = pd.read_csv(map_file)
                else:
                    # Assume Excel
                    df = pd.read_excel(map_file)
                if "oldname" not in df.columns or "newname" not in df.columns:
                    st.error("Mapping file must contain columns 'oldname' and 'newname'.")
                    st.stop()
                for _, row in df.iterrows():
                    rename_map[str(row["oldname"])] = str(row["newname"])
            except Exception as e:
                st.error(f"Could not parse mapping file: {e}")
                st.stop()

            # Rename files
            log = []
            for old_name, new_name in rename_map.items():
                src = find_file(temp_dir, old_name)
                if src:
                    dst = os.path.join(os.path.dirname(src), new_name)
                    if safe_rename(src, dst):
                        log.append(f"Renamed: {old_name} → {new_name}")
                    else:
                        log.append(f"Skipped (target exists): {old_name} → {new_name}")
                else:
                    log.append(f"File not found: {old_name}")

            st.write("**Rename Log:**")
            for line in log:
                st.write(line)

            # Output ZIP
            output_zip_path = os.path.join(temp_dir, "renamed_output.zip")
            with zipfile.ZipFile(output_zip_path, "w") as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        abs_file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_file_path, temp_dir)
                        if rel_path not in ["input.zip", "renamed_output.zip"]:
                            zipf.write(abs_file_path, arcname=rel_path)
            with open(output_zip_path, "rb") as f:
                st.download_button("Download Renamed ZIP", f, "renamed.zip", "application/zip")
    except Exception as e:
        st.error(f"An error occurred: {e}")
