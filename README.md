# Intelligent Resume Analyzer

A Python-based web application that automates resume screening by parsing resumes, matching candidate skills with job requirements, and generating detailed analysis reports.

## Features

* Upload and analyze PDF resumes
* Extract candidate information such as:

  * Name
  * Email
  * Skills
  * Experience
* Compare candidate skills with job requirements
* Calculate match score (0–100)
* Provide hiring recommendations
* Save results in JSON format
* Generate a detailed analysis report
* Support multiple resume uploads and ranking

## Technologies Used

Frontend:

* HTML
* CSS
* JavaScript

Backend:

* Python
* Flask

Libraries:

* pdfplumber / PyPDF2 (PDF parsing)
* re (Regular Expressions)
* json

Visualization:

* Chart.js

Development Tools:

* VS Code
* Git
* Firebase Studio / Antigravity

## Project Structure

```
resume_analyzer_project
│
├── app.py
├── requirements.txt
│
├── templates
│   ├── index.html
│   ├── results.html
│
├── static
│   ├── css
│   └── js
│
├── resumes
│
└── data
    └── analysis_results.json
```

## Installation

1. Clone the repository

```
git clone https://github.com/your-username/resume-analyzer.git
```

2. Navigate to the project folder

```
cd resume_analyzer_project
```

3. Install dependencies

```
pip install -r requirements.txt
```

## Running the Application

Run the following command:

```
cd H1/resume_analyzer_project && pip3 install -r requirements.txt && python3 app.py

```

The Flask server will start and open the application in your browser.

Open:

```
http://127.0.0.1:5000
```

## How It Works

1. Upload a PDF resume
2. Enter required job skills
3. The system extracts text from the resume
4. It identifies candidate skills
5. Matches skills with job requirements
6. Calculates a match score
7. Generates a hiring recommendation
8. Displays the analysis dashboard

## Example Output

Match Score: 82%

Recommendation: Hire

Skills Found:
Python, SQL, Machine Learning

Missing Skills:
Docker, AWS

## Future Improvements

* AI-based skill extraction
* NLP-based resume parsing
* Cloud deployment
* Improved ATS scoring

## Author

Ganesh Mahato
