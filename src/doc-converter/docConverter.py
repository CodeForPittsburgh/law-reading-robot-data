import os
import sys
import glob
import subprocess

def convert_doc_to_docx(file_path):
    try:
        subprocess.call(['libreoffice', '--headless', '--convert-to', 'docx', file_path])
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' could not be found.")

def covert_all_doc_to_docx(path):
    os.chdir(path)
    for doc in glob.iglob("*.DOC"):
        convert_doc_to_docx(doc)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_doc_to_docx.py input.doc")
    else:
        input_file_path = sys.argv[1]
        if os.path.isdir(input_file_path):
            convert_all_doc_to_docx(input_file_path)
        elif os.path.isfile(input_file_path) and input_file_path.endswith(".DOC"):
            convert_doc_to_docx(input_file_path)
