import os
import fitz  # PyMuPDF for PDF extraction
import google.generativeai as genai
import re
import nltk
from datetime import datetime
from docx import Document  # DOCX support

# Ensure NLTK tokenizer is ready
nltk.download('punkt')

# Configure Google Gemini API Key
os.environ["GEMINI_API_KEY"] = "AIzaSyBY0bcSaO-DK3A72g0GhdzNCWk6I_1RSqo"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Function to read text from a PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()

# Function to read text from a TXT file
def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text.strip()



# Function to calculate experience duration based on start & end date
def calculate_experience(start_date, end_date="Present"):
    """Calculate experience in years and months based on date ranges."""
    try:
        start_date = datetime.strptime(start_date, "%B %Y")  # Example: "February 2023"

        # If "Present", use current date
        if end_date.lower() == "present":
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%B %Y")  # Example: "August 2023"

        # Calculate months difference
        total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        years, months = divmod(total_months, 12)

        return total_months  # Return months for summation
    except Exception as e:
        print(f"Error in experience calculation: {e}")
        return 0  # Default to 0 months if parsing fails

# Function to extract experience dynamically from the text
def extract_experience(text):
    experience_sections = re.findall(r"(\w+\s\d{4})\s*-\s*(\w+\s\d{4}|Present)", text, re.IGNORECASE)

    total_months = 0
    for start, end in experience_sections:
        total_months += calculate_experience(start, end)

    # Convert total months back to years and months
    years, months = divmod(total_months, 12)
    if years > 0 and months > 0:
        return f"{years} years, {months} months"
    elif years > 0:
        return f"{years} years"
    else:
        return f"{months} months"

# Function to extract resume details using Google Gemini API
def extract_resume_details_with_gemini(text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    query = f"""
    Extract the following details from the resume:
    - Full Name
    - Total Experience (calculate dynamically up to today’s date with year)
    - Key Skills (list them)
    - Degree and field of study
    - Location

    For experience:
    - Donot add educations as experience
    - Identify each job with a start and end date.
    - If the end date is "Present," use today’s year: {datetime.today().strftime("%Y")}.
    - Sum all durations correctly and display total experience in **years and months** format.
    - If the above is not given return Fresher or 0-1 experiance

    Resume Content:
    {text}
    """
    response = model.generate_content(query)

    if hasattr(response, 'candidates') and len(response.candidates) > 0:
        return response.candidates[0].content.parts[0].text
    else:
        return "Error: Unable to extract details."

# Function to extract resume details using Regex & NLP
def extract_resume_details_with_regex(resume_text):
    details = {}

    # Extract Name (First non-empty line)
    lines = [line.strip() for line in resume_text.split("\n") if line.strip()]
    details['Name'] = lines[0] if lines else "Not found"

    # Extract Experience using dynamic calculation
    details['Experience'] = extract_experience(resume_text)

    # Extract Skills (Looking for bullet points or comma-separated lists)
    skills_match = re.findall(r"•\s*([\w\s]+)", resume_text)
    if not skills_match:
        skills_match = re.findall(r"Skills?:\s*([\w\s,]+)", resume_text, re.IGNORECASE)

    details['Skills'] = ", ".join(skills_match) if skills_match else "Not found"

    # Extract Degree (Handles variations like "Bachelor of Science in Computer Science")
    degree_match = re.search(r"(Bachelor|Master|PhD|Diploma)\s*(of|in)?\s*([\w\s]+)", resume_text, re.IGNORECASE)
    if degree_match:
        details['Degree'] = f"{degree_match.group(1)} in {degree_match.group(3).strip()}"
    else:
        details['Degree'] = "Not found"

    return details

# Function to process the resume from a given file path
def process_resume(file_path):
    # Extract text based on file type
    if file_path.endswith(".pdf"):
        resume_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".txt"):
        resume_text = extract_text_from_txt(file_path)
    elif file_path.endswith(".docx"):
        resume_text = extract_text_from_docx(file_path)
    else:
        print("Unsupported file format. Please provide a PDF, DOCX, or TXT file.")
        return

    # Get structured details using Gemini
    print("\nExtracting details using Gemini API...\n" + "-"*50)
    gemini_result = extract_resume_details_with_gemini(resume_text)
    return gemini_result

# Function to refine extracted details
def extract_filtered_details_with_gemini(full_gemini_output):
    """
    Send the full Gemini output back to Gemini and ask it to extract only Name, Experience, Skills, and Education.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    query = f"""
    From the following extracted resume details, provide only the following:
    
    - Full Name
    - Total Experience
    - Key Skills (list only)
    - Degree 
    - Additional Qualification 
    - Location
    
    Ensure the output is structured clearly.if the experience is not mentioned return 0 - 1 Year
    
    Resume Details:
    {full_gemini_output}
    """
    
    response = model.generate_content(query)
    return response.text if response else "Error: Unable to extract details."
