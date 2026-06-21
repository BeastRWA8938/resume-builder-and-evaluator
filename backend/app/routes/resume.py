from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.app.services.resume.generator import tailor_and_compile_resume

router = APIRouter(prefix="/api/generate", tags=["resume"])

class ResumeGenerateRequest(BaseModel):
    companyName: str
    jobTitle: str
    jobDescription: str
    geminiApiKey: Optional[str] = None

@router.post("")
async def generate_resume(request: ResumeGenerateRequest):
    if not request.companyName or not request.jobTitle or not request.jobDescription:
        raise HTTPException(
            status_code=400,
            detail="Company Name, Job Title, and Job Description are required."
        )
        
    try:
        result = await tailor_and_compile_resume(
            company_name=request.companyName,
            job_title=request.jobTitle,
            job_description=request.jobDescription,
            user_api_key=request.geminiApiKey
        )
        return result
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Exception during resume generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
