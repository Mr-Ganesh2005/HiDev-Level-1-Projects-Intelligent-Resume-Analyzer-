import os
import re
import json
import pdfplumber
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
# In a real application, use a secure, randomly generated secret key
app.secret_key = "super_secret_key_resume_analyzer" 

UPLOAD_FOLDER = 'resumes'
DATA_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Predefined skills database as specified
SKILLS_DB = [
    "python", "java", "machine learning", "deep learning", "sql",
    "html", "css", "javascript", "react", "tensorflow", "pytorch",
    "docker", "aws", "git"
]

def allowed_file(filename):
    """Check if the file type is allowed (PDF)."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_email(text):
    """Extract email address using regex."""
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else "Not Found"

def extract_phone(text):
    """Extract phone number using regex."""
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    matches = re.findall(phone_pattern, text)
    return matches[0] if matches else "Not Found"

def extract_skills(text):
    """Detect which skills from SKILLS_DB appear in the resume."""
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        # Looking for the exact word boundary for the skill
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            display_skill = skill.title()
            if skill == "sql": display_skill = "SQL"
            elif skill == "aws": display_skill = "AWS"
            elif skill == "html": display_skill = "HTML"
            elif skill == "css": display_skill = "CSS"
            found_skills.append(display_skill)
    return found_skills

def extract_experience(text):
    """Extract years of experience using regex heuristics."""
    exp_pattern = r'(\d+)\s*(?:[-to]+\s*\d+\s*)?(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)'
    match = re.search(exp_pattern, text.lower())
    if match:
        return f"{match.group(1)} years"
        
    fallback_pattern = r'(\d+)\+?\s*years?'
    match2 = re.search(fallback_pattern, text.lower())
    if match2:
        return f"{match2.group(1)} years"
        
    return "Not Found"

def calculate_match_score(resume_skills, job_skills):
    """Calculate match score between 0 and 100 based on required skills."""
    if not job_skills:
        return 0, [], []
        
    resume_skills_lower = [s.lower() for s in resume_skills]
    job_skills_lower = [s.lower() for s in job_skills]
    
    matched_skills = [s for s in job_skills_lower if s in resume_skills_lower]
    missing_skills = [s for s in job_skills_lower if s not in resume_skills_lower]
    
    score = (len(matched_skills) / len(job_skills_lower)) * 100
    
    return round(score, 2), matched_skills, missing_skills

def get_recommendation(score):
    """Generate hiring recommendation based on score."""
    if score >= 85:
        return "Strong Hire"
    elif score >= 70:
        return "Hire"
    elif score >= 50:
        return "Consider"
    else:
        return "Not Recommended"

def process_resume(file_path, required_skills):
    """Process a single resume text and return analysis."""
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise ValueError(f"Could not extract text from the PDF: {os.path.basename(file_path)}")
        
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    name = lines[0] if lines else "Unknown Candidate"
    if '@' in name or len(name.split()) > 5:
        name = "Candidate"
        
    email = extract_email(text)
    phone = extract_phone(text)
    resume_skills = extract_skills(text)
    experience = extract_experience(text)
    
    score, matched, missing = calculate_match_score(resume_skills, required_skills)
    recommendation = get_recommendation(score)
    
    def format_skill(s):
        s_lower = s.lower()
        if s_lower == "sql": return "SQL"
        if s_lower == "aws": return "AWS"
        if s_lower == "html": return "HTML"
        if s_lower == "css": return "CSS"
        return s.title()
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": [format_skill(s) for s in resume_skills],
        "matched_skills": [format_skill(s) for s in matched],
        "missing_skills": [format_skill(s) for s in missing],
        "experience": experience,
        "score": score,
        "recommendation": recommendation
    }

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file part is present
        if 'resumes' not in request.files:
            flash('No resume files found.')
            return redirect(request.url)
            
        files = request.files.getlist('resumes')
        
        # Parse the required skills from the form
        req_skills_raw = request.form.get('required_skills', '')
        job_skills = [s.strip().lower() for s in re.split(r'[,\n]', req_skills_raw) if s.strip()]
        
        if not job_skills:
            flash('Please specify the required skills.')
            return redirect(request.url)
            
        if not files or files[0].filename == '':
            flash('No selected file(s).')
            return redirect(request.url)

        all_results = []
        errors = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    result = process_resume(filepath, job_skills)
                    all_results.append(result)
                except Exception as e:
                    errors.append(str(e))
            else:
                errors.append(f"Invalid file format for {file.filename}")

        if errors:
            for error in errors:
                flash(error)

        if all_results:
            # Sort all_results by score in descending order
            all_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Save the entire array in JSON
            json_path = os.path.join(DATA_FOLDER, 'analysis_results.json')
            with open(json_path, 'w') as f:
                json.dump(all_results, f, indent=4)
                
            return redirect(url_for('results'))
            
    return render_template('index.html')

@app.route('/results')
def results():
    json_path = os.path.join(DATA_FOLDER, 'analysis_results.json')
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return render_template('results.html', data=data)
    except FileNotFoundError:
        flash('No analysis results found. Please upload and analyze resumes first.')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error loading results: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
