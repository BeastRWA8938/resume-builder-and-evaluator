import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import google.generativeai as genai

from backend.app.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from backend.app.models import KnowledgeExtractionResponse
from backend.app.database import (
    save_project, 
    save_experience, 
    get_projects, 
    get_experiences, 
    delete_project, 
    delete_experience
)

router = APIRouter(prefix="/api/vault", tags=["vault"])

class ExtractRequest(BaseModel):
    raw_text: str
    gemini_api_key: Optional[str] = None

class SaveRequest(BaseModel):
    entity_type: str
    data: dict

SYSTEM_INSTRUCTION = (
    "You are an expert career intelligence agent.\n"
    "Your task is to parse the raw text inputted by the user and extract structured career knowledge.\n"
    "Classify the entity type as either 'project' or 'experience'.\n"
    "Create high-quality, professional bullet points following the STAR methodology (Situation, Task, Action, Result) where possible.\n"
    "Explicitly identify technical skills and technologies mentioned, and do not invent any skills not supported by the context.\n"
    "Output must match the specified schema format precisely."
)

@router.post("/extract")
async def extract_knowledge(request: ExtractRequest):
    api_key = request.gemini_api_key or GEMINI_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Gemini API Key is missing. Please set it in your environment or supply it in the header."
        )
    
    genai.configure(api_key=api_key)
    
    prompt = f"""
    --- USER RAW CAREER INPUT ---
    {request.raw_text}
    """
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": KnowledgeExtractionResponse,
                "temperature": 0.2,
            },
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        response = model.generate_content(prompt)
        result_dict = json.loads(response.text)
        return result_dict
    except Exception as e:
        print(f"Exception during extraction with gemini-3.5-flash: {e}")
        try:
            # Fallback to configured model
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL_NAME,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": KnowledgeExtractionResponse,
                    "temperature": 0.2,
                },
                system_instruction=SYSTEM_INSTRUCTION
            )
            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"AI extraction failed: {str(fallback_error)}"
            )

@router.post("/save")
async def save_knowledge(request: SaveRequest):
    if not request.entity_type or not request.data:
        raise HTTPException(status_code=400, detail="entity_type and data are required fields.")
        
    try:
        if request.entity_type == "project":
            proj_id = save_project(request.data)
            return {"success": True, "id": proj_id}
        elif request.entity_type == "experience":
            exp_id = save_experience(request.data)
            return {"success": True, "id": exp_id}
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported entity type: {request.entity_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database save failed: {str(e)}")

@router.get("/projects")
async def fetch_projects():
    try:
        return get_projects()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")

@router.get("/experiences")
async def fetch_experiences():
    try:
        return get_experiences()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch experiences: {str(e)}")

@router.delete("/projects/{project_id}")
async def remove_project(project_id: int):
    try:
        success = delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found.")
        return {"status": "success", "message": f"Project {project_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/experiences/{experience_id}")
async def remove_experience(experience_id: int):
    try:
        success = delete_experience(experience_id)
        if not success:
            raise HTTPException(status_code=404, detail="Experience not found.")
        return {"status": "success", "message": f"Experience {experience_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
