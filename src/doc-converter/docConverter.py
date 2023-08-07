import sys
import glob
import subprocess

def convert_doc_to_docx():
	#try:
	for doc in glob.iglob("*.doc"):
		subprocess.call(['libreoffice', '--headless', '--convert-to', 'docx', doc])
		print(f"File converted successfully! Saved as '{docx_file}'")

    #except Exception as e:
    #    print(f"Error occurred: {e}")

if __name__ == "__main__":
    #if len(sys.argv) != 2:
     #   print("Usage: python convert_doc_to_docx.py input.doc")
    #else:
    #    input_file = sys.argv[1]
        convert_doc_to_docx()
