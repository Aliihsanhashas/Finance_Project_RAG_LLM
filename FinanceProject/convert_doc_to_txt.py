
import os
import subprocess



def convert_doc_to_docx_libre(doc_path):
    doc_path = os.path.abspath(doc_path)
    out_dir = os.path.dirname(doc_path)

    if not doc_path.endswith(".doc") or doc_path.endswith(".docx"):
        print(f"⚠️ Skipping non-.doc file: {doc_path}")
        return

    cmd = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        #"--headless",
        "--convert-to", "txt:Text",
        "--outdir", out_dir,
        doc_path
    ]

    print("📤 Converting:", doc_path)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("📝 STDOUT:", result.stdout)
        print("⚠️ STDERR:", result.stderr)

        # Check if .docx actually created
        expected_docx = doc_path + "x"
        if os.path.exists(expected_docx):
            print("✅ Successfully created:", expected_docx)
        else:
            print("❌ Conversion command succeeded but no .docx file was created.")
    except subprocess.CalledProcessError as e:
        print("❌ Conversion failed:", e.stderr)


def batch_convert_all_doc_files(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".doc") and not file.endswith(".docx"):
                full_path = os.path.join(root, file)
                convert_doc_to_docx_libre(full_path)


chromadb_dir = "chromadb_store"  # or whatever folder you use

# Step 1: Convert all .doc → .docx in-place
batch_convert_all_doc_files(chromadb_dir)

# Step 2: Run your existing ingestion script (now safely only .docx)
# ✅ Use the docx-only version we discussed above
