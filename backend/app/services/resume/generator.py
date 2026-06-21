import os
import re
import subprocess
import shutil
from pathlib import Path
import google.generativeai as genai
from pydantic import BaseModel, Field
from backend.app.core.config import ROOT_DIR, GEMINI_API_KEY, GEMINI_MODEL_NAME

class ResumeTailoringResult(BaseModel):
    companyResearch: str = Field(description="Short summary of company research and resume tailoring strategy.")
    latexCode: str = Field(description="The complete customized LaTeX document contents based on the template.")

def sanitize_path_name(name: str) -> str:
    """Sanitizes name for file path safety."""
    sanitized = re.sub(r'[^a-zA-Z0-9_\- ]', '', name).strip()
    return sanitized if sanitized else "unnamed"

def get_markdown_files(directory: Path) -> list:
    """Recursively fetches all markdown files in a directory."""
    if not directory.exists():
        return []
    return list(directory.rglob("*.md"))

def compile_knowledge_base() -> str:
    """Compiles all markdown knowledge base files into a single context string."""
    kb_dir = ROOT_DIR / "Knowledge Base"
    projects_dir = kb_dir / "Projects"
    work_dir = kb_dir / "Work"
    
    kb_content = ""
    
    # Read Projects
    if projects_dir.exists():
        kb_content += "=== PROJECTS KNOWLEDGE BASE ===\n\n"
        for file in get_markdown_files(projects_dir):
            try:
                rel_path = file.relative_to(projects_dir)
                content = file.read_text(encoding="utf-8")
                kb_content += f"--- Project: {rel_path} ---\n{content}\n\n"
            except Exception as e:
                print(f"Error reading project file {file}: {e}")
                
    # Read Work
    if work_dir.exists():
        kb_content += "=== WORK/INTERNSHIP KNOWLEDGE BASE ===\n\n"
        for file in get_markdown_files(work_dir):
            try:
                rel_path = file.relative_to(work_dir)
                content = file.read_text(encoding="utf-8")
                kb_content += f"--- Experience: {rel_path} ---\n{content}\n\n"
            except Exception as e:
                print(f"Error reading work file {file}: {e}")
                
    return kb_content

async def tailor_and_compile_resume(
    company_name: str,
    job_title: str,
    job_description: str,
    user_api_key: str = None
) -> dict:
    """Uses Gemini API to tailor candidate's resume and compiles it using XeLaTeX."""
    api_key = user_api_key or GEMINI_API_KEY
    if not api_key:
        raise ValueError("Google Gemini API Key is missing. Please configure it in the application.")
    
    # 1. Compile Knowledge Base
    kb_context = compile_knowledge_base()
    
    # 2. Read LaTeX Template
    template_path = ROOT_DIR / "Resume-Latex" / "PlushCV.tex"
    if not template_path.exists():
        raise FileNotFoundError(f"LaTeX template not found at {template_path}")
    
    latex_template = template_path.read_text(encoding="utf-8")
    
    # 3. Configure Gemini
    genai.configure(api_key=api_key)
    
    # We use gemini-3.5-flash for compatibility and speed (matching the model configurations)
    model = genai.GenerativeModel(
        model_name="gemini-3.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": ResumeTailoringResult,
            "temperature": 0.2,
        }
    )
    
    prompt = f"""
You are an expert technical recruiter and LaTeX developer. Your task is to customize a resume for a candidate based on their Knowledge Base (projects and work experience details) to tailor it perfectly for a target job at a specific company.

Company Name: {company_name}
Target Job Title: {job_title}
Job Description:
{job_description}

Candidate Knowledge Base:
{kb_context}

Original LaTeX Template (PlushCV structure):
{latex_template}

Instructions:
1. Conduct a background check on the target company ({company_name}) using your knowledge (or search if available) to align the resume with their engineering culture, values, tech stack, and products.
2. Provide a 2-3 sentence summary of your research on the company and your tailoring strategy under the "companyResearch" field.
3. Tailor the LaTeX code to fit the target role, returning it in the "latexCode" field. Follow these formatting guidelines:
   - **Name & Contact Details**: Keep the name "Rushikesh Waghmode" formatted exactly as '\\namesection{{\\fontsize{{35}}{{45}}\\selectfont Rushikesh}}{{\\fontsize{{35}}{{45}}\\selectfont Waghmode}}{{<role>}}{{<contact>}}' to ensure equal font sizes. Keep the GitHub link, LinkedIn link, email, and phone number exactly as they are in the template.
   - **Professional Headline**: Adjust the subtitle in the \\namesection command (e.g. "AI/ML Engineer", "Software Engineer", etc.) to match or align with the target job title.
   - **Experience Section**: Customize bullet points using the candidate's detailed experience in the KB (QodeAris, Arusan Automation, Think of It Foundation). Focus on achievements, tools, and technical challenges relevant to the target job description. Limit to 3 bullet points per experience to ensure it fits on one page.
   - **Projects Section**: Select the top 2-3 most relevant projects from the projects KB (e.g. Multi Agent Reinforcement Learning on Warehouse, Cane Vision, Home Server, Pac Man, Space Sense). Rewrite their descriptions to emphasize skills and outcomes relevant to the job. Limit to 2-3 bullet points per project.
   - **Skills Section**: Reorder and adjust the skills under Programming, AI/ML, Libraries, and Tools to highlight the skills requested in the job description. Do not invent skills that do not exist in the candidate's KB.
   - **Education & Awards Sections**: Keep them identical to the template structure but verify LaTeX syntactical correctness.
   - **CRITICAL - SINGLE PAGE LIMIT**: PlushCV is a one-page, two-column resume. If the text is too long, the document will overflow onto a second page, breaking the layout. Keep the descriptions and bullets extremely concise (maximum 1-2 lines per bullet). Do not add extra vertical whitespace.
   - **LaTeX Syntactical Rules**: 
     - Escape all special characters correctly (e.g. use \\& instead of &, \\% instead of %, \\_ instead of _, \\# instead of #, etc.).
     - Do not use markdown bold/italic (**bold**) inside the LaTeX code; use LaTeX commands like \\textbf{{...}}.
     - Do not change the class file packages or references. Keep the exact class commands like \\runsubsection, \\descript, \\location, and the tightemize environment.
"""

    print("Sending tailored resume generation request to Gemini...")
    # Add Google Search Grounding to Gemini 3.5 Flash where supported
    try:
        response = model.generate_content(
            prompt,
            tools=[{"google_search": {}}]
        )
    except Exception as e:
        print(f"Failing back to standard generation: {e}")
        response = model.generate_content(prompt)
        
    import json
    try:
        result_dict = json.loads(response.text)
    except Exception as e:
        print(f"Error parsing Gemini JSON response: {e}")
        print(f"Raw response: {response.text}")
        raise ValueError("Failed to retrieve a properly structured resume from Gemini API.")
        
    company_research = result_dict.get("companyResearch", "Tailored resume based on job description details.")
    tailored_latex = result_dict.get("latexCode")
    
    if not tailored_latex:
        raise ValueError("Failed to retrieve tailored LaTeX code from Gemini.")
        
    # 4. Compile temporary LaTeX file
    latex_dir = ROOT_DIR / "Resume-Latex"
    temp_tex_path = latex_dir / "temp_resume.tex"
    temp_pdf_path = latex_dir / "temp_resume.pdf"
    
    print("Writing temporary LaTeX file...")
    temp_tex_path.write_text(tailored_latex, encoding="utf-8")
    
    print("Compiling LaTeX to PDF via XeLaTeX...")
    compile_cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "--disable-installer",
        "-jobname=temp_resume",
        "temp_resume.tex"
    ]
    
    try:
        # Run XeLaTeX compiler with a 30s timeout
        result = subprocess.run(
            compile_cmd,
            cwd=str(latex_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, compile_cmd, output=result.stdout, stderr=result.stderr)
        print("XeLaTeX compilation succeeded.")
    except Exception as compile_error:
        print(f"XeLaTeX compilation failed: {compile_error}")
        log_snippet = ""
        try:
            log_path = latex_dir / "temp_resume.log"
            if log_path.exists():
                log_content = log_path.read_text(encoding="utf-8", errors="ignore")
                lines = log_content.split("\n")
                error_lines = [l for l in lines if l.startswith("!") or "Error" in l]
                log_snippet = "\n".join(error_lines[-10:]) if error_lines else "\n".join(lines[-20:])
            else:
                log_snippet = f"Could not find log file. Compiler Output:\n{getattr(compile_error, 'output', '')}"
        except Exception as e:
            log_snippet = f"Could not read log file: {e}"
            
        # Cleanup temp tex
        if temp_tex_path.exists():
            try:
                temp_tex_path.unlink()
            except:
                pass
                
        raise RuntimeError(f"LaTeX Compilation Failed: {log_snippet}")
        
    # 5. Organize output files
    clean_company = sanitize_path_name(company_name)
    clean_role = sanitize_path_name(job_title)
    output_dir = ROOT_DIR / "Resumes" / clean_company / clean_role
    
    print(f"Creating output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    dest_tex_path = output_dir / "resume.tex"
    dest_pdf_path = output_dir / "resume.pdf"
    
    print("Moving compiled files to target directory...")
    shutil.copy2(temp_tex_path, dest_tex_path)
    shutil.copy2(temp_pdf_path, dest_pdf_path)
    
    # 6. Clean up temporary files
    files_to_clean = [
        temp_tex_path,
        temp_pdf_path,
        latex_dir / "temp_resume.aux",
        latex_dir / "temp_resume.log",
        latex_dir / "temp_resume.out",
        latex_dir / "temp_resume.xdv"
    ]
    
    for f in files_to_clean:
        if f.exists():
            try:
                f.unlink()
            except Exception as e:
                print(f"Failed to delete temp file {f}: {e}")
                
    # Web urls
    web_pdf_url = f"/resumes/{clean_company}/{clean_role}/resume.pdf"
    web_tex_url = f"/resumes/{clean_company}/{clean_role}/resume.tex"
    
    return {
        "success": True,
        "companyResearch": company_research,
        "pdfUrl": web_pdf_url,
        "texUrl": web_tex_url,
        "companyName": clean_company,
        "jobTitle": clean_role
    }
