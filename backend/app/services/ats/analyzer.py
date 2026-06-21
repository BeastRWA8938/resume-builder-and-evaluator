import json
import google.generativeai as genai
from backend.app.core.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from backend.app.core.models import ATSAnalysisResult

# Configure the Gemini API client
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = (
    "You are an expert Applicant Tracking System (ATS) and Senior Technical Recruiter.\n"
    "Your task is to analyze the provided resume text against the job description and evaluate their compatibility.\n"
    "You must be objective, analytical, and provide highly detailed, constructive insights.\n\n"
    "Provide:\n"
    "1. An honest, objective ATS match score (0 to 100).\n"
    "2. A concise candidate fit summary.\n"
    "3. Lists of matched and missing keywords/skills.\n"
    "4. A categorized Skill Gap Analysis, grouping matched/missing skills (e.g., 'Languages', 'Frameworks', 'Design', 'Soft Skills').\n"
    "5. Highly actionable, specific strengths and weaknesses relative to the role.\n"
    "6. Clear and direct formatting/ATS parsing feedback (e.g. advice on bullet points, columns, key sections).\n\n"
    "Output must match the specified schema format precisely."
)

async def analyze_resume_compatibility(resume_text: str, job_description: str, user_api_key: str = None) -> dict:
    """Uses Google's Gemini LLM to analyze the compatibility between the resume and the job description."""
    api_key = user_api_key or GEMINI_API_KEY
    if not api_key:
        raise ValueError("Google Gemini API key is not configured. Please set the GEMINI_API_KEY environment variable or enter it in the web interface.")
        
    genai.configure(api_key=api_key)
        
    prompt = f"""
    --- JOB DESCRIPTION ---
    {job_description}
    
    --- RESUME TEXT ---
    {resume_text}
    """
    
    # We load the configured Gemini model (defaults to gemini-2.5-flash)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL_NAME,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": ATSAnalysisResult,
            "temperature": 0.2,
        },
        system_instruction=SYSTEM_INSTRUCTION
    )
    
    response = await model.generate_content_async(prompt)
    
    try:
        # Parse the structured JSON response
        result_dict = json.loads(response.text)
        return result_dict
    except Exception as e:
        # In case of any json decoding issue, attempt to log or raise
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw response: {response.text}")
        raise ValueError("Failed to retrieve a properly structured analysis from the AI service. Please try again.")
