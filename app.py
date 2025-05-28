
import os
import csv
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import fitz  
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CSV_FILE = 'extracted_data.csv'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_pdf_data(filepath, filename):
    text = ""
    with fitz.open(filepath) as doc:
        for page in doc:
            text += page.get_text()
    
    details = {
        "File Name": filename,
        "Name": extract_name(text),
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "LinkedIn": extract_linkedin(text),
        "Education": extract_education(text),
        "Experience": extract_experience(text),
        "Skills": extract_skills(text),
        "Certifications": extract_certifications(text)
    }
    return details

def extract_name(text):

    try:
        if not text or not isinstance(text, str):
            return None
            
        
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        if not lines:
            return None
            
        
        first_line = lines[0]
        
    
        words = first_line.split()
        if (len(words) >= 2 and 
            words[0][0].isupper() and 
            words[-1][0].isupper() and
            not any(word.lower() in ['cv', 'resume', 'curriculum', 'vitae'] for word in words)):
            return first_line
            
        
        for line in lines[:5]:
            words = line.split()
            if (len(words) >= 2 and 
                words[0][0].isupper() and 
                words[-1][0].isupper() and
                not any(word.lower() in ['cv', 'resume', 'curriculum', 'vitae'] for word in words)):
                return line
                
        return None  
        
    except Exception as e:
        print(f"Error extracting name: {str(e)}")
        return None

def extract_phone(text):
    match = re.search(r'(\+91[-\s]?)?[6-9]\d{9}', text)
    return match.group() if match else ""

def extract_email(text):
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return match.group() if match else ""

def extract_linkedin(text):
    match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/\S+', text)
    return match.group() if match else ""

def extract_education(text):
    education = []
    lines = text.split('\n')
    for line in lines:
        if any(word in line.lower() for word in [ 'bachelor', 'master', 'phd','B.Tech','CMA','CA']):
            education.append(line.strip())
    return ' | '.join(education[:1])  


import re

def extract_experience(text):
    experience = []
    lines = text.split('\n')
    
    experience_keywords = ['intern', 'pvt ltd', 'private limited', 'developer', 
                         'worked', 'manager', 'employee','analyst']
    
    for line in lines:
        if any(re.search(rf'\b{re.escape(keyword)}\b', line.lower()) for keyword in experience_keywords):
            experience.append(line.strip())
    return ' | '.join(experience[:3]) if experience else ""



def extract_skills(text):
    skills = []
    lines = text.splitlines()

    capturing = False
    for line in lines:
        lower_line = line.lower()

        
        if any(keyword in lower_line for keyword in ["skills", "technical skills", "key skills","proficient with","Languages",]):
            capturing = True
            inline_skills = line.split(":")[-1] if ":" in line else line
            skills.extend(re.findall(r'\b[A-Za-z+#]+\b', inline_skills))
            continue

        
        if capturing:
            if line.strip() == " " or ":" in line:
                break
            skills.extend(re.findall(r'\b[A-Za-z+#]+\b', line))
    return skills

def extract_certifications(text):
    certs = []
    lines = text.split('\n')
    for line in lines:
        if any(word in line.lower() for word in ['certification', 'certificate', 'award']):
            certs.append(line.strip())
    return ' | '.join(certs[:3]) 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    results = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            data = extract_pdf_data(filepath, filename)
            results.append(data)
    
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        
        fieldnames = [
            "Certifications",
            "Education", 
            "Email",
            "Experience",
            "File Name",
            "LinkedIn",
            "Name",
            "Phone",
            "Skills"
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        
        for result in results:
            writer.writerow({
                "Certifications": result.get("Certifications", ""),
                "Education": result.get("Education", ""),
                "Email": result.get("Email", ""),
                "Experience": result.get("Experience", ""),
                "File Name": result.get("File Name", ""),
                "LinkedIn": result.get("LinkedIn", ""),
                "Name": result.get("Name", ""),
                "Phone": result.get("Phone", ""),
                "Skills": ', '.join(result.get("Skills", [])) if isinstance(result.get("Skills"), list) else result.get("Skills", "")
            })
    
    return jsonify({
        'message': f'{len(results)} files processed',
        'files': [f.filename for f in files if allowed_file(f.filename)],
        'data': results
    })
@app.route('/download')
def download():
    return send_file(
        CSV_FILE,
        as_attachment=True,
        mimetype='text/csv',
        download_name='resume_data.csv'
    )

if __name__ == '__main__':
    app.run(debug=True)