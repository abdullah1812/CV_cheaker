#select the right port

import PyPDF2
import os
import json
from groq import Groq
from flask import Flask, request, jsonify
from dotenv import load_dotenv


# Initialize Flask app
app = Flask(__name__)

# Load configuration with better error handling
try:
    api_key = os.environ['GROQ_API_KEY']
    client = Groq(api_key=api_key)
except KeyError:
    raise RuntimeError("GROQ_API_KEY environment variable is missing")
except Exception as e:
    raise RuntimeError(f"Failed to initialize Groq client: {str(e)}")


# Define the directory to store uploaded PDF files
UPLOAD_DIR = "./uploaded_pdfs"  # Relative to /app in the container

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            if not text.strip():
                return None
            return text
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        return None
    finally:
        # Clean up: Delete the uploaded file after processing
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

# Function to analyze CV with LLaMA via Groq
def analyze_cv(cv_text):
    if not cv_text:
        return {"error": "No text extracted from PDF"}

    prompt = f"""
You are an AI assistant evaluating a CV to determine if the candidate is suitable to be a mentor. A mentor must have:
- At least 3 years of professional experience in software engineering or a related field.
- IF he buid some projects add them with experience.
- Demonstrated leadership or mentoring experience (e.g., leading teams, training others).
- Strong communication skills (e.g., presentations, workshops).
- Relevant education or certifications (e.g., Bachelor's in Computer Science, coaching certifications).
- Evidence of soft skills like empathy or problem-solving.
- Compute the experience from projects also.

CV Text: {cv_text}

Provide a JSON response with:
1. A summary of the candidate’s relevant qualifications.
2. A score (0–100) for mentor eligibility based on the criteria.
3. If score >= 75, the candidate can be a mentor.
4. Specific strengths (list of qualifications that match the criteria).
5. Specific gaps (list of missing or weak criteria).
6. A recommendation: Is this can be a mentor? Why or why not?

{{"summary": "", "score": 0, "strengths": [], "gaps": [], "recommendation": ""}}
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.6,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        return {"error": f"Groq API processing failed: {e}"}

# Endpoint to receive PDF files via POST
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        # Check if a file is included in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Check if the file is a PDF
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400
        
        # Save the file to the upload directory
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(file_path)

        text = extract_text_from_pdf(file_path)
        if not text:
            return jsonify({"error": "Failed to extract text from PDF"}), 400
        result = analyze_cv(text)
        
        return jsonify({ 
                       "analysis": result}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
