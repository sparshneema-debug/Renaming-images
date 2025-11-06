import streamlit as st
import os
import csv
import zipfile
import tempfile

def find_file(root_dir, filename):
    for dirpath, _, files in os.walk(root_dir):
        if filename in files:
            return os.path.join(dirpath, filename)
    return None

st.title("Bulk File Renamer inside ZIP")
st.write("Upload a ZIP file and a CSV mapping (oldname,newname), and get back a renamed ZIP.")

zip_file = st.file_uploader("Upload ZIP file", type=["zip"])
csv_file = st.file_uploader("Upload CSV mapping", type=["csv"])

if zip_file and csv_file:
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save ZIP
        zip_path = os.path.join(temp_dir, "input.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_file.read())
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Parse the CSV map
        rename_map = {}
        csv_file.seek(0)
        reader = csv.reader((line.decode("utf-8") for line in csv_file))
        for row in reader:
            if len(row) == 2:
                rename_map[row[0]] = row[1]

        # Rename files
        for old_name, new_name in rename_map.items():
            src = find_file(temp_dir, old_name)
            if src:
                dst = os.path.join(os.path.dirname(src), new_name)
                if not os.path.exists(dst):
                    os.rename(src, dst)

        # Create output ZIP
        output_zip_path = os.path.join(temp_dir, "output.zip")
        with zipfile.ZipFile(output_zip_path, "w") as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    abs_file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_file_path, temp_dir)
                    if rel_path not in ["input.zip", "output.zip"]:
                        zipf.write(abs_file_path, arcname=rel_path)

        # Serve the ZIP for download
        with open(output_zip_path, "rb") as f:
            st.download_button("Download Renamed ZIP", f, "renamed.zip", "application/zip")