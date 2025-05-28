Resume Parser Web App


This is a Flask-based web application that extracts useful information from uploaded PDF resumes and generates a downloadable CSV file containing structured data such as name, email, phone number, education, experience, skills, certifications, and more.

🔍 Features
Upload multiple PDF resumes at once

Automatically extract:

Name

Email

Phone Number

LinkedIn URL

Education details

Work Experience

Skills

Certifications / Awards

Download structured data as a CSV file



🗂 Output Format (CSV Columns)
File Name

Name

Email

Phone

LinkedIn

Education

Experience

Skills

Certifications



🧑‍💻 User Guide
Step 1: Open the Web App
Go to http://localhost:5000 in your browser after running the app.

Step 2: Upload PDF Resumes
Click the file input box.

Select one or more PDF files.

Click the "Upload" button.

Step 3: Wait for Extraction
The backend processes each file and extracts relevant details.

A confirmation message will appear after successful parsing.

Step 4: Download CSV
Click the "Download CSV" button to get all parsed data in a structured CSV format (resume_data.csv).




🧾 File Structure

task/

├── app.py                  # Main Flask app

├── templates/

│   └── index.html          # Web UI

├── uploads/                # Uploaded PDF files (auto-created)

├── extracted_data.csv      # Generated CSV file      

└── README.md               # Project documentation




📦 Dependencies
Flask

PyMuPDF (fitz)

werkzeug


📌 Notes
Ensure uploaded files are in .pdf format only.

Results depend on the formatting of resumes; OCR-based PDFs may not extract well.
