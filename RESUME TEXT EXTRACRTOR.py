import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
from docx import Document

def pdf_to_text(input_file, output_file):
    pdf_reader = PdfReader(input_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)

def doc_to_text(input_file, output_file):
    doc = Document(input_file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(text)

def convert_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf"), ("DOC Files", "*.doc;*.docx")])
    output_folder = "dsg"
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_path in file_paths:
        filename = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(filename)
        output_file = os.path.join(output_folder, file_name + ".txt")

        if file_extension.lower() == ".pdf":
            pdf_to_text(file_path, output_file)
        elif file_extension.lower() in [".doc", ".docx"]:
            doc_to_text(file_path, output_file)

    print("Conversion complete.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    convert_files()
