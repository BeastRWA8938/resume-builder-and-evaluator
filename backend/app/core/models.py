from pydantic import BaseModel, Field
from typing import List, Optional

class SkillGap(BaseModel):
    category: str = Field(description="Category of skills, e.g., 'Programming Languages', 'Tools', 'Soft Skills'")
    missing_skills: List[str] = Field(description="List of skills/keywords that are in the job description but missing in the resume")
    matched_skills: List[str] = Field(description="List of skills/keywords that are successfully matched in the resume")

class ATSAnalysisResult(BaseModel):
    score: int = Field(description="Overall ATS match score from 0 to 100 based on keyword match, experience relevance, and requirements.")
    summary: str = Field(description="A concise summary (3-4 sentences) evaluating the candidate's fit for the role.")
    matched_keywords: List[str] = Field(description="Keywords and skills present in the resume that match the job description.")
    missing_keywords: List[str] = Field(description="Important keywords and skills present in the job description but missing in the resume.")
    skill_gap_analysis: List[SkillGap] = Field(description="Detailed analysis of skill gaps categorized by technical, soft skills, or domain expertise.")
    strengths: List[str] = Field(description="List of 3-5 key strengths or strong alignments identified in the resume for this position.")
    weaknesses: List[str] = Field(description="List of 3-5 key gaps or areas of improvement to make the resume match better.")
    formatting_feedback: List[str] = Field(description="Feedback on resume structure, readability, action verbs, or formatting issues.")

class AnalysisResponse(BaseModel):
    id: int
    filename: str
    job_title: str
    created_at: str
    result: ATSAnalysisResult

# --- Knowledge Vault Validation & Response Schemas ---

class ProjectCreate(BaseModel):
    experience_id: Optional[int] = Field(None, description="Linked Job Experience ID")
    title: str = Field(..., min_length=2, max_length=150)
    description: str = Field(..., min_length=10)
    repository_url: Optional[str] = Field(None)

class ProjectResponse(BaseModel):
    id: int
    experience_id: Optional[int]
    title: str
    description: str
    repository_url: Optional[str]

class AchievementCreate(BaseModel):
    action_taken: str = Field(..., min_length=5)
    outcome_metric: Optional[str] = Field(None)
    raw_bullet_text: str = Field(..., min_length=10)
    technologies: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)

class ExperienceCreate(BaseModel):
    company_name: str = Field(..., min_length=2)
    role_title: str = Field(..., min_length=2)
    start_date: str = Field(..., description="Format: YYYY-MM")
    end_date: Optional[str] = Field(None, description="Format: YYYY-MM")
    employment_type: str = Field(..., description="Must be 'Full-time', 'Contract', 'Part-time', or 'Internship'")

class ExperienceResponse(BaseModel):
    id: int
    company_name: str
    role_title: str
    start_date: str
    end_date: Optional[str]
    employment_type: str

class ExtractedAchievement(BaseModel):
    action_taken: str = Field(description="The technical task or action completed.")
    outcome_metric: Optional[str] = Field(description="Quantifiable business metric or system optimization.")
    raw_bullet_text: str = Field(description="The formatted STAR bullet point.")
    technologies: List[str] = Field(description="Technologies used in this achievement.")
    skills: List[str] = Field(description="High-level capabilities demonstrated.")

class KnowledgeExtractionResponse(BaseModel):
    entity_type: str = Field(description="Must be 'project', 'experience', or 'credential'.")
    title: str = Field(description="Extracted title of the entry.")
    description: str = Field(description="Extracted description of the entry.")
    technologies: List[str] = Field(description="All technologies used.")
    skills: List[str] = Field(description="All general skills used.")
    achievements: List[ExtractedAchievement] = Field(description="List of structured achievements.")

