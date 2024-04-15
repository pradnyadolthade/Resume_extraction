from flask import Flask, render_template, request, send_file
import os
import re
import pandas as pd
from docx import Document
import PyPDF2

app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text
    return text

def extract_email(text):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_regex, text)
    return emails[0] if emails else None

def extract_phone_number(text):
    phone_regex = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
    phone_numbers = re.findall(phone_regex, text)
    return phone_numbers[0] if phone_numbers else None


@app.route('/')
def index():
    return render_template('index.html')

import os
from werkzeug.utils import secure_filename

# Add a configuration for the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('file')
    all_data = []
    
    # Create the uploads folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    for file in uploaded_files:
        if file.filename.endswith('.pdf'):
            # Save the file to the upload folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            # Save the file to the upload folder
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            text = extract_text_from_docx(file_path)
        else:
            continue
        email = extract_email(text)
        phone = extract_phone_number(text)
        all_data.append({'Email': email, 'Phone': phone, 'Text': text})
    
    df = pd.DataFrame(all_data)
    output_file = 'output.xlsx'
    df.to_excel(output_file, index=False)

    return send_file(output_file, as_attachment=True)

if __name__=='__main__':
    app.run(debug=True)


"""

def process_cv_folder(folder_path):
    data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            text = extract_text_from_pdf(os.path.join(folder_path, file_name))
        elif file_name.endswith('.docx'):
            text = extract_text_from_docx(os.path.join(folder_path, file_name))
        else:
            continue

        email = extract_email(text)
        phone = extract_phone_number(text)
        data.append({'File': file_name, 'Email': email, 'Phone': phone, 'Text': text})
    return data

def export_to_excel(data, output_path):
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)

if __name__ == "__main__":
    folder_path = 'C:/Users/Admin/Projects/cv_parser/Sample2'
    output_path = '/cv_parser/output.xlsx'

    extracted_data = process_cv_folder(folder_path)
    export_to_excel(extracted_data, output_path)
    print("Extraction complete. Data saved to", output_path)
"""